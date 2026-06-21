"""LiteLLM-backed LLM provider.

LiteLLM exposes a single OpenAI-compatible interface to 100+ model
providers, plus built-in fallback chains, retries, and cost accounting.
This adapter lets the council route any provider/model through LiteLLM
while keeping the existing :class:`LLMProvider` contract intact.

Model names follow LiteLLM conventions, e.g. ``openai/gpt-4o``,
``anthropic/claude-sonnet-4-6``, ``openrouter/google/gemini-2.0-flash-exp:free``,
``ollama/llama3``.
"""

from __future__ import annotations

import logging
import time
from collections.abc import AsyncIterator, Sequence

try:
    import litellm
except ImportError:
    litellm = None

from council.llm.provider import LLMProvider, LLMResponse
from council.llm.retry import retry_with_backoff

logger = logging.getLogger(__name__)


def _litellm_non_retryable() -> tuple[type[Exception], ...]:
    """Return deterministic LiteLLM exception types that must not be retried."""
    types: list[type[Exception]] = [ValueError]
    if litellm is not None:
        for name in (
            "AuthenticationError",
            "PermissionDeniedError",
            "NotFoundError",
            "BadRequestError",
            "UnprocessableEntityError",
        ):
            exc_type = getattr(litellm, name, None)
            if isinstance(exc_type, type) and issubclass(exc_type, Exception):
                types.append(exc_type)
    return tuple(types)


class LiteLLMProvider(LLMProvider):
    """LLM provider that routes calls through LiteLLM.

    Parameters
    ----------
    model:
        LiteLLM model identifier (``provider/model`` form).
    api_key / api_base:
        Optional overrides; when omitted LiteLLM reads provider-specific
        environment variables.
    fallbacks:
        Ordered list of fallback model identifiers tried when the primary
        model fails. Deterministic order, capped to keep requests bounded.
    num_retries:
        LiteLLM-internal retry count for transient errors.
    """

    _MAX_FALLBACKS = 5

    def __init__(
        self,
        model: str = "openai/gpt-4o",
        *,
        api_key: str | None = None,
        api_base: str | None = None,
        fallbacks: Sequence[str] | None = None,
        num_retries: int = 2,
    ) -> None:
        if litellm is None:
            raise ImportError(
                "LiteLLM not installed.\n"
                "  Fix: pip install 'council[litellm]' (or: pip install litellm)"
            )

        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        self.fallbacks: list[str] = list(fallbacks or [])[: self._MAX_FALLBACKS]
        self.num_retries = num_retries

        # Keep LiteLLM quiet and resilient to provider-specific params.
        litellm.drop_params = True
        litellm.telemetry = False

    def _build_messages(self, prompt: str, system: str | None) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return messages

    def _completion_kwargs(
        self,
        model_name: str,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> dict[str, object]:
        kwargs: dict[str, object] = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "num_retries": self.num_retries,
        }
        if self.api_key is not None:
            kwargs["api_key"] = self.api_key
        if self.api_base is not None:
            kwargs["api_base"] = self.api_base
        if self.fallbacks:
            kwargs["fallbacks"] = self.fallbacks
        return kwargs

    @staticmethod
    def _estimate_cost(response: object) -> float:
        """Best-effort cost from LiteLLM's pricing tables."""
        if litellm is None:
            return 0.0
        try:
            cost = litellm.completion_cost(completion_response=response)
            return float(cost) if cost else 0.0
        except Exception:  # pragma: no cover - cost tables are best-effort
            return 0.0

    @retry_with_backoff(
        max_retries=3,
        exceptions=(Exception,),
        non_retryable_exceptions=_litellm_non_retryable(),
    )
    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: str | None = None,
    ) -> LLMResponse:
        assert litellm is not None
        model_name = model or self.model
        messages = self._build_messages(prompt, system)
        start = time.time()
        response = await litellm.acompletion(
            **self._completion_kwargs(model_name, messages, temperature, max_tokens)
        )
        latency = (time.time() - start) * 1000

        choice = response.choices[0]
        content = choice.message.content or ""
        usage = getattr(response, "usage", None)
        tokens_prompt = getattr(usage, "prompt_tokens", 0) or 0
        tokens_completion = getattr(usage, "completion_tokens", 0) or 0

        return LLMResponse(
            content=content,
            model=getattr(response, "model", model_name) or model_name,
            tokens_prompt=int(tokens_prompt),
            tokens_completion=int(tokens_completion),
            cost_usd=self._estimate_cost(response),
            latency_ms=latency,
        )

    async def stream(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: str | None = None,
    ) -> AsyncIterator[str]:
        assert litellm is not None
        model_name = model or self.model
        messages = self._build_messages(prompt, system)
        kwargs = self._completion_kwargs(model_name, messages, temperature, max_tokens)
        kwargs["stream"] = True
        stream = await litellm.acompletion(**kwargs)
        async for chunk in stream:
            try:
                delta = chunk.choices[0].delta.content
            except (AttributeError, IndexError):
                delta = None
            if delta:
                yield delta

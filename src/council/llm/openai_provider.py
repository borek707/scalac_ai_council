from __future__ import annotations

import logging
import time
from collections.abc import AsyncIterator

try:
    import openai
except ImportError:
    openai = None  # type: ignore[assignment]

from council.llm.provider import LLMProvider, LLMResponse
from council.llm.retry import retry_with_backoff
from council.llm.secrets import resolve_api_key

logger = logging.getLogger(__name__)


def _openai_non_retryable() -> tuple[type[Exception], ...]:
    """Return non-retryable OpenAI exception types when the SDK is available.

    These errors are deterministic (auth, bad model, bad request) and will
    never succeed on a retry.  We also include ValueError to guard against
    invalid parameter combinations caught before the network call.
    """
    types: list[type[Exception]] = [ValueError]
    if openai is not None:
        # 401 Unauthorized / invalid API key
        types.append(openai.AuthenticationError)
        # 403 Forbidden
        types.append(openai.PermissionDeniedError)
        # 404 Not Found (e.g. invalid model name)
        types.append(openai.NotFoundError)
        # 400 Bad Request (malformed payload)
        types.append(openai.BadRequestError)
    return tuple(types)


class OpenAIProvider(LLMProvider):
    """LLM provider implementation for OpenAI API."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str = "gpt-4o",
    ) -> None:
        self.model = model
        self.api_key = resolve_api_key("openai", api_key)
        self.base_url = base_url

        if not self.api_key:
            raise RuntimeError(
                "OpenAI API key missing.\n" "  Set OPENAI_API_KEY env var or pass --api-key"
            )

        if openai is None:
            raise ImportError("OpenAI package not installed. " "Install with: pip install openai")

        self._client = openai.AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    @retry_with_backoff(
        max_retries=3,
        exceptions=(Exception,),
        non_retryable_exceptions=_openai_non_retryable(),
    )
    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: str | None = None,
    ) -> LLMResponse:
        """Generate a response using OpenAI API."""
        model_name = model or self.model
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        start = time.time()
        try:
            response = await self._client.chat.completions.create(
                model=model_name,
                messages=messages,  # type: ignore[arg-type]
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as exc:
            logger.error("OpenAI API error: %s", exc)
            raise

        latency = (time.time() - start) * 1000
        choice = response.choices[0]
        content = choice.message.content or ""
        usage = response.usage

        cost = self._estimate_cost(
            model_name,
            usage.prompt_tokens if usage else 0,
            usage.completion_tokens if usage else 0,
        )

        return LLMResponse(
            content=content,
            model=model_name,
            tokens_prompt=usage.prompt_tokens if usage else 0,
            tokens_completion=usage.completion_tokens if usage else 0,
            cost_usd=cost,
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
        """Stream response chunks from OpenAI API."""
        model_name = model or self.model
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            stream = await self._client.chat.completions.create(
                model=model_name,
                messages=messages,  # type: ignore[arg-type]
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            async for chunk in stream:  # type: ignore[union-attr]
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception as exc:
            logger.error("OpenAI streaming error: %s", exc)
            raise

    def _estimate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Estimate API cost based on token usage."""
        rates: dict[str, tuple[float, float]] = {
            "gpt-4o": (5.0 / 1_000_000, 15.0 / 1_000_000),
            "gpt-4o-mini": (0.15 / 1_000_000, 0.6 / 1_000_000),
            "gpt-4": (30.0 / 1_000_000, 60.0 / 1_000_000),
        }
        prompt_rate, completion_rate = rates.get(model, rates["gpt-4o"])
        return (prompt_tokens * prompt_rate) + (completion_tokens * completion_rate)

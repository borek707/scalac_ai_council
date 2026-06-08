from __future__ import annotations

import logging
import time
from collections.abc import AsyncIterator

try:
    import anthropic
except ImportError:
    anthropic = None  # type: ignore

from council.llm.provider import LLMProvider, LLMResponse
from council.llm.retry import retry_with_backoff
from council.llm.secrets import resolve_api_key

logger = logging.getLogger(__name__)


def _anthropic_non_retryable() -> tuple[type[Exception], ...]:
    """Return non-retryable Anthropic exception types when the SDK is available.

    These errors are deterministic (auth, bad model, bad request) and will
    never succeed on a retry.  ValueError guards against invalid parameters
    caught before the network call.
    """
    types: list[type[Exception]] = [ValueError]
    if anthropic is not None:
        # 401 Unauthorized / invalid API key
        types.append(anthropic.AuthenticationError)
        # 403 Forbidden
        types.append(anthropic.PermissionDeniedError)
        # 404 Not Found (e.g. invalid model name)
        types.append(anthropic.NotFoundError)
        # 400 Bad Request (malformed payload)
        types.append(anthropic.BadRequestError)
    return tuple(types)


class AnthropicProvider(LLMProvider):
    """LLM provider implementation for Anthropic Claude API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-sonnet-4-6",
    ) -> None:
        self.model = model
        self.api_key = resolve_api_key("anthropic", api_key)

        if not self.api_key:
            raise RuntimeError(
                "Anthropic API key missing.\n" "  Set ANTHROPIC_API_KEY env var or pass --api-key"
            )

        if anthropic is None:
            raise ImportError(
                "Anthropic package not installed. " "Install with: pip install anthropic"
            )

        self._client = anthropic.AsyncAnthropic(api_key=self.api_key)

    @retry_with_backoff(
        max_retries=3,
        exceptions=(Exception,),
        non_retryable_exceptions=_anthropic_non_retryable(),
    )
    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: str | None = None,
    ) -> LLMResponse:
        """Generate a response using Anthropic Claude API."""
        model_name = model or self.model

        start = time.time()
        try:
            response = await self._client.messages.create(
                model=model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system or "",
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as exc:
            logger.error("Anthropic API error: %s", exc)
            raise

        latency = (time.time() - start) * 1000
        content_blocks = response.content
        text = ""
        for block in content_blocks:
            if block.type == "text":
                text += block.text

        usage = response.usage
        cost = self._estimate_cost(
            model_name,
            usage.input_tokens if usage else 0,
            usage.output_tokens if usage else 0,
        )

        return LLMResponse(
            content=text,
            model=model_name,
            tokens_prompt=usage.input_tokens if usage else 0,
            tokens_completion=usage.output_tokens if usage else 0,
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
        """Stream response chunks from Anthropic Claude API."""
        model_name = model or self.model
        try:
            async with self._client.messages.stream(
                model=model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system or "",
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as exc:
            logger.error("Anthropic streaming error: %s", exc)
            raise

    def _estimate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Estimate API cost based on token usage."""
        rates: dict[str, tuple[float, float]] = {
            "claude-3-opus-20240229": (15.0 / 1_000_000, 75.0 / 1_000_000),
            "claude-3-sonnet-20240229": (3.0 / 1_000_000, 15.0 / 1_000_000),
            "claude-3-haiku-20240307": (0.25 / 1_000_000, 1.25 / 1_000_000),
            "claude-sonnet-4-6": (3.0 / 1_000_000, 15.0 / 1_000_000),
            "claude-opus-4-6": (5.0 / 1_000_000, 25.0 / 1_000_000),
            "claude-opus-4-7": (5.0 / 1_000_000, 25.0 / 1_000_000),
            "claude-haiku-4-5": (1.0 / 1_000_000, 5.0 / 1_000_000),
        }
        if model not in rates:
            logger.warning(
                "AnthropicProvider: unknown model %r for cost estimate — using Sonnet 4 rates",
                model,
            )
        prompt_rate, completion_rate = rates.get(model, rates["claude-sonnet-4-6"])
        return (prompt_tokens * prompt_rate) + (completion_tokens * completion_rate)

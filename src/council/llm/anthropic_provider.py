from __future__ import annotations

import logging
import os
import time
from typing import AsyncGenerator, Optional

try:
    import anthropic
except ImportError:
    anthropic = None  # type: ignore[assignment]

from council.llm.provider import LLMProvider, LLMResponse
from council.llm.retry import retry_with_backoff

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    """LLM provider implementation for Anthropic Claude API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-sonnet-20240229",
    ) -> None:
        self.model = model
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")

        if anthropic is None:
            raise ImportError(
                "Anthropic package not installed. "
                "Install with: pip install anthropic"
            )

        self._client = anthropic.AsyncAnthropic(api_key=self.api_key)

    @retry_with_backoff(max_retries=3, exceptions=(Exception,))
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: Optional[str] = None,
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
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
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
        }
        prompt_rate, completion_rate = rates.get(model, rates["claude-3-sonnet-20240229"])
        return (prompt_tokens * prompt_rate) + (completion_tokens * completion_rate)

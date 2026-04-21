from __future__ import annotations

import logging
import os
import time
from typing import AsyncGenerator, Optional

try:
    import openai
except ImportError:
    openai = None  # type: ignore[assignment]

from council.llm.provider import LLMProvider, LLMResponse
from council.llm.retry import retry_with_backoff

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """LLM provider implementation for OpenAI API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4o",
    ) -> None:
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = base_url

        if openai is None:
            raise ImportError(
                "OpenAI package not installed. "
                "Install with: pip install openai"
            )

        self._client = openai.AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    @retry_with_backoff(max_retries=3, exceptions=(Exception,))
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: Optional[str] = None,
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
                messages=messages,
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
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream response chunks from OpenAI API."""
        model_name = model or self.model
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            stream = await self._client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            async for chunk in stream:
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

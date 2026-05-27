from __future__ import annotations

import json
import logging
import os
import urllib.request
from typing import Optional

from council.llm.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


class OpenRouterProvider(OpenAIProvider):
    """LLM provider for OpenRouter (unified API for many models).

    OpenRouter exposes an OpenAI-compatible chat-completions endpoint,
    so we reuse ``OpenAIProvider`` and only change the base URL and
    default model.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        free_tier: bool = False,
    ) -> None:
        self._explicit_model = model
        resolved_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not resolved_key:
            raise RuntimeError(
                "OpenRouter API key missing.\n"
                "  Set OPENROUTER_API_KEY env var or pass --api-key"
            )
        resolved_url = base_url or os.environ.get("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1"
        resolved_model = model or os.environ.get("OPENROUTER_MODEL") or "anthropic/claude-3.5-sonnet"
        logger.info(
            "OpenRouterProvider: model=%s, base_url=%s, free_tier=%s",
            resolved_model,
            resolved_url,
            free_tier,
        )
        super().__init__(
            api_key=resolved_key,
            base_url=resolved_url,
            model=resolved_model,
        )
        self._free_tier = free_tier
        self._fallback_models: list[str] = []
        if free_tier:
            self._fallback_models = self._fetch_free_models(resolved_key, resolved_url)
            if self._fallback_models:
                logger.info(
                    "OpenRouter free-tier fallback models (%d): %s",
                    len(self._fallback_models),
                    ", ".join(self._fallback_models[:5]) + ("..." if len(self._fallback_models) > 5 else ""),
                )

    @staticmethod
    def _fetch_free_models(api_key: str, base_url: str) -> list[str]:
        """Fetch current free-tier models from OpenRouter API."""
        url = f"{base_url}/models"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {api_key}"})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            logger.warning("Failed to fetch free models from OpenRouter: %s", exc)
            return []

        free: list[str] = []
        for m in data.get("data", []):
            pricing = m.get("pricing", {})
            if pricing.get("prompt") == "0" and pricing.get("completion") == "0":
                free.append(m["id"])
        return free

    def _extra_body(self) -> dict | None:
        """Return extra_body with fallback models if free-tier is enabled."""
        if self._free_tier and self._fallback_models:
            return {"models": self._fallback_models}
        return None

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: Optional[str] = None,
    ) -> LLMResponse:
        """Generate a response using OpenRouter API with optional free-tier fallbacks."""
        import time

        model_name = model or self.model
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        kwargs: dict = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        extra = self._extra_body()
        if extra:
            kwargs["extra_body"] = extra

        start = time.time()
        try:
            response = await self._client.chat.completions.create(**kwargs)
        except Exception as exc:
            logger.error("OpenRouter API error: %s", exc)
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

        from council.llm.provider import LLMResponse
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
        """Stream response chunks from OpenRouter API with optional free-tier fallbacks."""
        model_name = model or self.model
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        kwargs: dict = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        extra = self._extra_body()
        if extra:
            kwargs["extra_body"] = extra

        try:
            stream = await self._client.chat.completions.create(**kwargs)
            async for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception as exc:
            logger.error("OpenRouter streaming error: %s", exc)
            raise

    def _estimate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """OpenRouter pricing varies by model; we return 0.0 and let the user check their dashboard."""
        return 0.0

from __future__ import annotations

import json
import logging
import os
import time
from collections.abc import AsyncIterator
from typing import Any

from council.llm.openai_provider import OpenAIProvider
from council.llm.provider import LLMResponse

logger = logging.getLogger(__name__)

# Preferred free models on OpenRouter (in order of preference)
_PREFERRED_FREE = [
    "google/gemini-2.0-flash-exp:free",
    "deepseek/deepseek-chat:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "nvidia/llama-3.1-nemotron-70b-instruct:free",
    "qwen/qwen-2.5-72b-instruct:free",
]


class OpenRouterProvider(OpenAIProvider):
    """LLM provider for OpenRouter (unified API for many models).

    Uses the OpenAI SDK with OpenRouter's base URL.
    Supports models from Anthropic, OpenAI, Google, Meta, etc.
    Automatically picks a free model if no model is specified and free_tier is enabled.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        free_tier: bool = False,
    ) -> None:
        raw_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        resolved_key = raw_key.strip() if raw_key else None
        if not resolved_key:
            raise RuntimeError(
                "OpenRouter API key missing.\n" "  Set OPENROUTER_API_KEY env var or pass --api-key"
            )

        resolved_url = (
            base_url or os.environ.get("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1"
        )
        self._free_tier = free_tier
        self._fallback_models: list[str] = []
        self.auto_selected = False
        self._resolved_key = resolved_key
        self._resolved_url = resolved_url
        self._needs_model_resolution = False

        if model in (None, "default"):
            if free_tier:
                self._needs_model_resolution = True
            resolved_model = "anthropic/claude-3-5-sonnet-20241022"
        else:
            assert model is not None
            resolved_model = model

        logger.info(
            "OpenRouterProvider: model=%s, base_url=%s, free_tier=%s",
            resolved_model or "(lazy-resolve)",
            resolved_url,
            free_tier,
        )
        super().__init__(
            api_key=resolved_key,
            base_url=resolved_url,
            model=resolved_model,
        )

    async def _resolve_model(self) -> None:
        """Lazy-resolve free-tier model on first use to avoid blocking the event loop."""
        if not self._needs_model_resolution:
            return
        self._needs_model_resolution = False
        try:
            resolved_model = await self._pick_free_model(self._resolved_key, self._resolved_url)
            logger.info("OpenRouter: auto-selected free model %s", resolved_model)
            self.auto_selected = True
            self.model = resolved_model
        except Exception as exc:
            logger.warning("OpenRouter: could not fetch free models (%s), falling back", exc)
            self.model = "anthropic/claude-3-5-sonnet-20241022"

        self._fallback_models = await self._fetch_free_models(
            self._resolved_key, self._resolved_url
        )
        if self._fallback_models:
            logger.info(
                "OpenRouter free-tier fallback models (%d): %s",
                len(self._fallback_models),
                ", ".join(self._fallback_models[:5])
                + ("..." if len(self._fallback_models) > 5 else ""),
            )

    @staticmethod
    async def _fetch_free_models(api_key: str, base_url: str) -> list[str]:
        """Fetch current free-tier models from OpenRouter API (async)."""
        import aiohttp

        url = f"{base_url}/models"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    data = json.loads(await resp.text())
        except Exception as exc:
            logger.warning("Failed to fetch free models from OpenRouter: %s", exc)
            return []

        free: list[str] = []
        for m in data.get("data", []):
            pricing = m.get("pricing", {})
            if pricing.get("prompt") == "0" and pricing.get("completion") == "0":
                free.append(m["id"])
        return free

    @staticmethod
    async def _pick_free_model(api_key: str, base_url: str) -> str:
        """Fetch model list and return the best free one from preferred list."""
        free_models = await OpenRouterProvider._fetch_free_models(api_key, base_url)
        for pref in _PREFERRED_FREE:
            if pref in free_models:
                return pref
        if free_models:
            return free_models[0]
        raise RuntimeError("No free models available on OpenRouter")

    def _extra_body(self) -> dict[str, Any] | None:
        """Return extra_body with fallback models if free-tier is enabled."""
        if self._free_tier and self._fallback_models:
            return {"models": self._fallback_models}
        return None

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: str | None = None,
    ) -> LLMResponse:
        """Generate a response using OpenRouter API with optional free-tier fallbacks."""
        await self._resolve_model()

        model_name = model or self.model
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        kwargs: dict[str, Any] = {
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
        """Stream response chunks from OpenRouter API with optional free-tier fallbacks."""
        await self._resolve_model()

        model_name = model or self.model
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        kwargs: dict[str, Any] = {
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

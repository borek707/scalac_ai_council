from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from collections.abc import AsyncIterator
from typing import Any

from council.llm.openai_provider import OpenAIProvider
from council.llm.provider import LLMResponse
from council.llm.secrets import resolve_api_key

logger = logging.getLogger(__name__)

# Soft preference order when multiple free models are available from the API.
# Models not in this list are appended after, sorted alphabetically.
_PREFERRED_FREE: tuple[str, ...] = (
    "moonshotai/kimi-k2.6:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "deepseek/deepseek-chat:free",
    "meta-llama/llama-3.3-70b-instruct:free",
)

# OpenRouter rejects extra_body.models arrays longer than 3 items.
_MAX_ROUTER_FALLBACKS = 3

_PAID_DEFAULT_MODEL = "anthropic/claude-sonnet-4.5"

_UNAVAILABLE_MARKERS = (
    "rate limit",
    "rate-limit",
    "rate_limit",
    "too many requests",
    "overloaded",
    "capacity",
    "unavailable",
    "temporarily",
    "no available providers",
    "all providers",
)


class OpenRouterProvider(OpenAIProvider):
    """LLM provider for OpenRouter (unified API for many models).

    Uses the OpenAI SDK with OpenRouter's base URL.
    With ``free_tier=True``, fetches the current free model catalog from
    OpenRouter, picks a primary model, and passes the rest as automatic
    fallbacks. If every fallback in one request fails, tries the next primary
    after refreshing the catalog.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        free_tier: bool = False,
    ) -> None:
        raw_key = resolve_api_key("openrouter", api_key)
        if not raw_key:
            raise RuntimeError(
                "OpenRouter API key missing.\n" "  Set OPENROUTER_API_KEY env var or pass --api-key"
            )

        resolved_url = (
            base_url or os.environ.get("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1"
        )
        self._free_tier = free_tier
        self._model_chain: list[str] = []
        self.auto_selected = False
        self._resolved_key = raw_key
        self._resolved_url = resolved_url
        self._needs_model_resolution = False
        self._explicit_model = model not in (None, "default")
        self._resolve_lock = asyncio.Lock()

        if model in (None, "default"):
            if free_tier:
                self._needs_model_resolution = True
                resolved_model = ""
            else:
                resolved_model = _PAID_DEFAULT_MODEL
        else:
            assert model is not None
            resolved_model = model
            if free_tier:
                self._needs_model_resolution = True

        logger.info(
            "OpenRouterProvider: model=%s, base_url=%s, free_tier=%s",
            resolved_model or "(lazy-resolve)",
            resolved_url,
            free_tier,
        )
        super().__init__(
            api_key=raw_key,
            base_url=resolved_url,
            model=resolved_model or _PAID_DEFAULT_MODEL,
        )

    async def ensure_ready(self) -> None:
        """Resolve free-tier models before parallel agent calls."""
        await self._resolve_model()

    async def _resolve_model(self) -> None:
        """Lazy-resolve free-tier model chain on first use."""
        if not self._needs_model_resolution:
            return
        async with self._resolve_lock:
            if not self._needs_model_resolution:
                return
            await self._refresh_free_model_chain(
                force_primary=self.model if self._explicit_model else None
            )
            self._needs_model_resolution = False

    async def _refresh_free_model_chain(self, *, force_primary: str | None = None) -> None:
        """Fetch current free models from OpenRouter and rebuild primary + fallbacks."""
        free_models = await self._fetch_free_models(self._resolved_key, self._resolved_url)
        if not free_models:
            raise RuntimeError(
                "No free models available on OpenRouter right now.\n"
                "  Check https://openrouter.ai/models?order=pricing-low-to-high for ':free' models\n"
                "  or disable --free-tier and pass an explicit --model."
            )

        primary = (
            force_primary if force_primary and force_primary in free_models else free_models[0]
        )
        if force_primary and force_primary not in free_models:
            logger.warning(
                "OpenRouter: requested model %s is not currently free; using %s",
                force_primary,
                primary,
            )

        chain = [primary]
        chain.extend(m for m in free_models if m != primary)
        self._model_chain = chain
        self.model = primary
        if not self._explicit_model:
            self.auto_selected = True

        logger.info(
            "OpenRouter free-tier chain (%d models): primary=%s, fallbacks=%s",
            len(chain),
            primary,
            ", ".join(chain[1:5]) + ("..." if len(chain) > 5 else ""),
        )

    @staticmethod
    def _is_free_pricing(value: object) -> bool:
        if value is None:
            return False
        try:
            if isinstance(value, bool):
                return False
            if isinstance(value, int | float):
                return float(value) == 0.0
            return float(str(value).strip()) == 0.0
        except (TypeError, ValueError):
            return str(value).strip() in {"0", "0.0"}

    @classmethod
    def _is_free_model_entry(cls, entry: dict[str, Any]) -> bool:
        model_id = entry.get("id", "")
        if isinstance(model_id, str) and model_id.endswith(":free"):
            return True
        pricing = entry.get("pricing", {})
        if not isinstance(pricing, dict):
            return False
        return cls._is_free_pricing(pricing.get("prompt")) and cls._is_free_pricing(
            pricing.get("completion")
        )

    @classmethod
    def _sort_free_models(cls, model_ids: list[str]) -> list[str]:
        preferred = [model_id for model_id in _PREFERRED_FREE if model_id in model_ids]
        rest = sorted(model_id for model_id in model_ids if model_id not in preferred)
        return preferred + rest

    @staticmethod
    async def _fetch_free_models(api_key: str, base_url: str) -> list[str]:
        """Fetch and sort the current free-tier models from OpenRouter."""
        import aiohttp

        url = f"{base_url.rstrip('/')}/models"
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
                    if resp.status >= 400:
                        text = await resp.text()
                        raise RuntimeError(
                            f"OpenRouter /models returned HTTP {resp.status}: {text[:200]}"
                        )
                    data = json.loads(await resp.text())
        except Exception as exc:
            logger.warning("Failed to fetch free models from OpenRouter: %s", exc)
            return []

        free_ids: list[str] = []
        for entry in data.get("data", []):
            if isinstance(entry, dict) and OpenRouterProvider._is_free_model_entry(entry):
                model_id = entry.get("id")
                if isinstance(model_id, str) and model_id:
                    free_ids.append(model_id)

        return OpenRouterProvider._sort_free_models(free_ids)

    def _fallback_models_for(self, primary: str) -> list[str]:
        if not self._free_tier or not self._model_chain:
            return []
        fallbacks = [model_id for model_id in self._model_chain if model_id != primary]
        return fallbacks[:_MAX_ROUTER_FALLBACKS]

    @staticmethod
    def _is_model_unavailable_error(exc: Exception) -> bool:
        if OpenRouterProvider._is_auth_or_bad_request(exc):
            return False

        status_code = getattr(exc, "status_code", None)
        if status_code in {408, 429, 500, 502, 503, 504}:
            return True

        response = getattr(exc, "response", None)
        if response is not None:
            response_status = getattr(response, "status_code", None)
            if response_status in {408, 429, 500, 502, 503, 504}:
                return True

        message = str(exc).lower()
        return any(marker in message for marker in _UNAVAILABLE_MARKERS)

    @staticmethod
    def _is_auth_or_bad_request(exc: Exception) -> bool:
        try:
            import openai
        except ImportError:
            openai = None  # type: ignore[assignment]

        if openai is not None and isinstance(
            exc,
            openai.AuthenticationError
            | openai.PermissionDeniedError
            | openai.NotFoundError
            | openai.BadRequestError,
        ):
            return True

        status_code = getattr(exc, "status_code", None)
        if status_code in {400, 401, 403, 404}:
            return True
        response = getattr(exc, "response", None)
        if response is not None:
            response_status = getattr(response, "status_code", None)
            if response_status in {400, 401, 403, 404}:
                return True
        return False

    async def _create_completion(
        self,
        *,
        model_name: str,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
        stream: bool,
    ) -> Any:
        kwargs: dict[str, Any] = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if stream:
            kwargs["stream"] = True

        fallbacks = self._fallback_models_for(model_name)
        if fallbacks:
            kwargs["extra_body"] = {"models": fallbacks}

        return await self._client.chat.completions.create(**kwargs)

    async def _iter_model_chain(self) -> list[str]:
        if self._free_tier:
            await self._resolve_model()
            if self._model_chain:
                return list(self._model_chain)
            raise RuntimeError(
                "OpenRouter free-tier model chain is empty after resolution.\n"
                "  Try again later or pass --no-free-tier with a paid --model."
            )
        return [self.model]

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: str | None = None,
    ) -> LLMResponse:
        """Generate using OpenRouter with live free-model fallbacks when enabled."""
        if model and model != self.model:
            if self._free_tier:
                await self._refresh_free_model_chain(force_primary=model)
            else:
                self.model = model

        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        chain = await self._iter_model_chain()
        if model and not self._free_tier:
            chain = [model]

        last_exc: Exception | None = None
        for attempt, model_name in enumerate(chain):
            start = time.time()
            try:
                response = await self._create_completion(
                    model_name=model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=False,
                )
            except Exception as exc:
                last_exc = exc
                can_retry = (
                    self._free_tier
                    and self._is_model_unavailable_error(exc)
                    and attempt < len(chain) - 1
                )
                if not can_retry:
                    logger.error("OpenRouter API error on %s: %s", model_name, exc)
                    raise
                logger.warning(
                    "OpenRouter model %s unavailable (%s); trying next free model",
                    model_name,
                    exc,
                )
                if attempt == len(chain) - 2:
                    refreshed = await self._fetch_free_models(
                        self._resolved_key, self._resolved_url
                    )
                    if refreshed:
                        self._model_chain = refreshed
                        chain = refreshed
                continue

            latency = (time.time() - start) * 1000
            choice = response.choices[0]
            content = choice.message.content or ""
            usage = response.usage
            used_model = getattr(response, "model", None) or model_name
            if used_model != self.model:
                logger.info("OpenRouter routed request to %s", used_model)
                self.model = used_model

            return LLMResponse(
                content=content,
                model=used_model,
                tokens_prompt=usage.prompt_tokens if usage else 0,
                tokens_completion=usage.completion_tokens if usage else 0,
                cost_usd=0.0,
                latency_ms=latency,
            )

        if last_exc is not None:
            raise last_exc
        raise RuntimeError("OpenRouter generate failed without a specific error")

    async def stream(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream from OpenRouter with the same free-model fallback behavior."""
        if model and model != self.model:
            if self._free_tier:
                await self._refresh_free_model_chain(force_primary=model)
            else:
                self.model = model

        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        chain = await self._iter_model_chain()
        if model and not self._free_tier:
            chain = [model]

        last_exc: Exception | None = None
        for attempt, model_name in enumerate(chain):
            try:
                stream = await self._create_completion(
                    model_name=model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                )
                async for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        yield delta
                if model_name != self.model:
                    self.model = model_name
                return
            except Exception as exc:
                last_exc = exc
                can_retry = (
                    self._free_tier
                    and self._is_model_unavailable_error(exc)
                    and attempt < len(chain) - 1
                )
                if not can_retry:
                    logger.error("OpenRouter streaming error on %s: %s", model_name, exc)
                    raise
                logger.warning(
                    "OpenRouter stream on %s unavailable (%s); trying next free model",
                    model_name,
                    exc,
                )
                if attempt == len(chain) - 2:
                    refreshed = await self._fetch_free_models(
                        self._resolved_key, self._resolved_url
                    )
                    if refreshed:
                        self._model_chain = refreshed
                        chain = refreshed

        if last_exc is not None:
            raise last_exc
        raise RuntimeError("OpenRouter stream failed without a specific error")

    def _estimate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """OpenRouter pricing varies by model; free-tier runs stay at zero."""
        return 0.0

from __future__ import annotations

import json
import logging
import time
from collections.abc import AsyncIterator

try:
    import aiohttp
except ImportError:
    aiohttp = None  # type: ignore

from council.llm.provider import LLMProvider, LLMResponse
from council.llm.retry import retry_with_backoff

logger = logging.getLogger(__name__)


class _OllamaDeterministicError(Exception):
    """Raised instead of aiohttp.ClientResponseError for 4xx responses from Ollama.

    Using a dedicated exception type lets the retry decorator identify
    deterministic failures without importing aiohttp at module level.
    """


class OllamaProvider(LLMProvider):
    """LLM provider implementation for Ollama (local models)."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3",
    ) -> None:
        if aiohttp is None:
            raise ImportError(
                "aiohttp is required for OllamaProvider. " "Install with: pip install aiohttp"
            )
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def verify_reachable(self) -> None:
        """Ping Ollama before a council run; fail fast when the daemon is down."""
        url = f"{self.base_url}/api/tags"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status >= 400:
                        body = await response.text()
                        raise RuntimeError(
                            f"Cannot reach Ollama at {self.base_url} "
                            f"(HTTP {response.status}): {body[:200]}"
                        )
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Is 'ollama serve' running?\n"
                f"  {exc}"
            ) from exc

    @staticmethod
    async def _raise_on_client_error(response: object) -> None:
        """Map deterministic 4xx responses to a non-retryable error."""
        status = getattr(response, "status", None)
        if status in (400, 401, 403, 404):
            text_fn = getattr(response, "text", None)
            body = await text_fn() if callable(text_fn) else ""
            raise _OllamaDeterministicError(f"Ollama returned HTTP {status}: {str(body)[:200]}")

    @retry_with_backoff(
        max_retries=3,
        exceptions=(Exception,),
        non_retryable_exceptions=(_OllamaDeterministicError, ValueError),
    )
    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: str | None = None,
    ) -> LLMResponse:
        """Generate a response using Ollama API."""
        model_name = model or self.model
        url = f"{self.base_url}/api/generate"

        payload: dict[str, object] = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if system:
            payload["system"] = system

        start = time.time()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    await self._raise_on_client_error(response)
                    response.raise_for_status()
                    data = await response.json()
        except _OllamaDeterministicError:
            raise
        except Exception as exc:
            logger.error("Ollama API error: %s", exc)
            raise

        latency = (time.time() - start) * 1000
        content = data.get("response", "")
        eval_count = data.get("eval_count", 0)
        prompt_count = data.get("prompt_eval_count", 0)

        return LLMResponse(
            content=content,
            model=model_name,
            tokens_prompt=prompt_count,
            tokens_completion=eval_count,
            cost_usd=0.0,  # Local model, no API cost
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
        """Stream response chunks from Ollama API."""
        model_name = model or self.model
        url = f"{self.base_url}/api/generate"

        payload: dict[str, object] = {
            "model": model_name,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if system:
            payload["system"] = system

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    await self._raise_on_client_error(response)
                    response.raise_for_status()
                    async for line in response.content:
                        if not line.strip():
                            continue
                        try:
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue
        except Exception as exc:
            logger.error("Ollama streaming error: %s", exc)
            raise

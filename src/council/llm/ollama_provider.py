from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import AsyncGenerator, Optional

try:
    import aiohttp
except ImportError:
    aiohttp = None  # type: ignore[assignment]

from council.llm.provider import LLMProvider, LLMResponse
from council.llm.retry import retry_with_backoff

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """LLM provider implementation for Ollama (local models)."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3",
    ) -> None:
        if aiohttp is None:
            raise ImportError(
                "aiohttp is required for OllamaProvider. "
                "Install with: pip install aiohttp"
            )
        self.base_url = base_url.rstrip("/")
        self.model = model

    @retry_with_backoff(max_retries=3, exceptions=(Exception,))
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: Optional[str] = None,
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
                    response.raise_for_status()
                    data = await response.json()
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
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
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

from __future__ import annotations

import logging
import os
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
            "OpenRouterProvider: model=%s, base_url=%s",
            resolved_model,
            resolved_url,
        )
        super().__init__(
            api_key=resolved_key,
            base_url=resolved_url,
            model=resolved_model,
        )

    def _estimate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """OpenRouter pricing varies by model; we return 0.0 and let the user check their dashboard."""
        return 0.0

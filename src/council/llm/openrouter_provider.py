from __future__ import annotations

import json
import logging
import os
import urllib.request
from typing import Optional

from council.llm.openai_provider import OpenAIProvider

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
    """LLM provider implementation for OpenRouter (universal API proxy).

    Uses the OpenAI SDK with OpenRouter's base URL.
    Supports models from Anthropic, OpenAI, Google, Meta, etc.
    Automatically picks a free model if no model is specified.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "default",
    ) -> None:
        key = api_key or os.environ.get("OPENROUTER_API_KEY")
        resolved_model = model
        if model in (None, "default"):
            try:
                resolved_model = self._pick_free_model(key)
                logger.info("OpenRouter: auto-selected free model %s", resolved_model)
            except Exception as exc:
                logger.warning("OpenRouter: could not fetch free models (%s), falling back", exc)
                resolved_model = "anthropic/claude-sonnet-4"

        super().__init__(
            api_key=key,
            base_url="https://openrouter.ai/api/v1",
            model=resolved_model,
        )
        self.auto_selected = model in (None, "default")

    def _pick_free_model(self, api_key: Optional[str]) -> str:
        """Fetch model list from OpenRouter and return the best free one."""
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/models",
            headers={
                "Authorization": f"Bearer {api_key or ''}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())

        models = data.get("data", [])
        free_ids = [
            m["id"] for m in models
            if m.get("pricing", {}).get("prompt") == "0"
            and m.get("pricing", {}).get("completion") == "0"
        ]

        for pref in _PREFERRED_FREE:
            if pref in free_ids:
                return pref

        if free_ids:
            return free_ids[0]

        raise RuntimeError("No free models available on OpenRouter")

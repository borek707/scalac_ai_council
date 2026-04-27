from __future__ import annotations

import os
from typing import Optional

from council.llm.openai_provider import OpenAIProvider


class OpenRouterProvider(OpenAIProvider):
    """LLM provider implementation for OpenRouter (universal API proxy).

    Uses the OpenAI SDK with OpenRouter's base URL.
    Supports models from Anthropic, OpenAI, Google, Meta, etc.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "anthropic/claude-sonnet-4",
    ) -> None:
        super().__init__(
            api_key=api_key or os.environ.get("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            model=model,
        )

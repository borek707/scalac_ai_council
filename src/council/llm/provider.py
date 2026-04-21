from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncGenerator, Optional


@dataclass
class LLMResponse:
    """Response from an LLM provider."""

    content: str
    model: str
    tokens_prompt: int = 0
    tokens_completion: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: Optional[str] = None,
    ) -> LLMResponse:
        """Generate a complete response from the LLM."""
        ...

    @abstractmethod
    async def stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream response chunks from the LLM."""
        ...

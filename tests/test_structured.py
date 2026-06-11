from __future__ import annotations

from collections.abc import AsyncIterator

import pytest

from council.llm.provider import LLMProvider, LLMResponse
from council.schemas import FinalDeliverable
from council.structured import (
    StructuredOutputError,
    generate_structured,
    parse_model,
)


class _ScriptedProvider(LLMProvider):
    """Returns a scripted sequence of responses, one per generate() call."""

    def __init__(self, responses: list[str]) -> None:
        self._responses = responses
        self.calls = 0

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: str | None = None,
    ) -> LLMResponse:
        text = self._responses[min(self.calls, len(self._responses) - 1)]
        self.calls += 1
        return LLMResponse(content=text, model="mock")

    async def stream(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: str | None = None,
    ) -> AsyncIterator[str]:
        yield ""


_VALID = (
    '{"agent": "Marcus", "title": "Offer", "summary": "Crisp.", '
    '"sections": [{"heading": "Pricing", "content": "GBB"}], '
    '"recommendations": ["Ship it"]}'
)


class TestParseModel:
    def test_parses_fenced_json(self) -> None:
        text = f"Here you go:\n```json\n{_VALID}\n```\nThanks!"
        d = parse_model(text, FinalDeliverable)
        assert d.agent == "Marcus"

    def test_parses_bare_json_with_prose(self) -> None:
        text = f"Sure. {_VALID} Done."
        d = parse_model(text, FinalDeliverable)
        assert d.title == "Offer"


class TestGenerateStructured:
    @pytest.mark.asyncio
    async def test_success_on_first_attempt(self) -> None:
        provider = _ScriptedProvider([_VALID])
        result = await generate_structured(provider, "make offer", FinalDeliverable)
        assert isinstance(result, FinalDeliverable)
        assert provider.calls == 1

    @pytest.mark.asyncio
    async def test_repairs_after_invalid_then_valid(self) -> None:
        provider = _ScriptedProvider(["not json at all", _VALID])
        result = await generate_structured(
            provider, "make offer", FinalDeliverable, max_retries=2
        )
        assert result.agent == "Marcus"
        assert provider.calls == 2

    @pytest.mark.asyncio
    async def test_raises_after_exhausting_retries(self) -> None:
        provider = _ScriptedProvider(["nope"])
        with pytest.raises(StructuredOutputError):
            await generate_structured(
                provider, "make offer", FinalDeliverable, max_retries=1
            )
        assert provider.calls == 2

from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from council.llm.litellm_provider import LiteLLMProvider, _litellm_non_retryable


def _fake_response(content: str = "hello", model: str = "openai/gpt-4o") -> SimpleNamespace:
    message = SimpleNamespace(content=content)
    choice = SimpleNamespace(message=message)
    usage = SimpleNamespace(prompt_tokens=11, completion_tokens=22)
    return SimpleNamespace(choices=[choice], usage=usage, model=model)


class TestLiteLLMProvider:
    def test_init_requires_litellm(self) -> None:
        with patch("council.llm.litellm_provider.litellm", None):
            with pytest.raises(ImportError, match="LiteLLM not installed"):
                LiteLLMProvider(model="openai/gpt-4o")

    def test_fallbacks_capped(self) -> None:
        provider = LiteLLMProvider(
            model="openai/gpt-4o",
            fallbacks=[f"m{i}" for i in range(10)],
        )
        assert len(provider.fallbacks) == LiteLLMProvider._MAX_FALLBACKS

    @pytest.mark.asyncio
    async def test_generate_maps_response(self) -> None:
        provider = LiteLLMProvider(model="openai/gpt-4o")
        fake = _fake_response(content="generated text")
        with patch(
            "council.llm.litellm_provider.litellm.acompletion",
            new=AsyncMock(return_value=fake),
        ):
            with patch(
                "council.llm.litellm_provider.litellm.completion_cost",
                return_value=0.0123,
            ):
                resp = await provider.generate("prompt", system="sys")
        assert resp.content == "generated text"
        assert resp.tokens_prompt == 11
        assert resp.tokens_completion == 22
        assert resp.cost_usd == pytest.approx(0.0123)
        assert resp.model == "openai/gpt-4o"

    @pytest.mark.asyncio
    async def test_generate_forwards_fallbacks_and_base(self) -> None:
        provider = LiteLLMProvider(
            model="openai/gpt-4o",
            api_base="https://proxy.local",
            fallbacks=["anthropic/claude-sonnet-4-6"],
        )
        captured: dict[str, Any] = {}

        async def fake_acompletion(**kwargs: Any) -> SimpleNamespace:
            captured.update(kwargs)
            return _fake_response()

        with patch(
            "council.llm.litellm_provider.litellm.acompletion",
            new=fake_acompletion,
        ):
            with patch(
                "council.llm.litellm_provider.litellm.completion_cost",
                return_value=0.0,
            ):
                await provider.generate("prompt")
        assert captured["fallbacks"] == ["anthropic/claude-sonnet-4-6"]
        assert captured["api_base"] == "https://proxy.local"
        assert captured["model"] == "openai/gpt-4o"

    @pytest.mark.asyncio
    async def test_stream_yields_deltas(self) -> None:
        provider = LiteLLMProvider(model="openai/gpt-4o")

        def _chunk(text: str | None) -> SimpleNamespace:
            return SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=text))])

        async def fake_stream(**kwargs: Any):
            for piece in ["Hel", "lo", None, "!"]:
                yield _chunk(piece)

        with patch(
            "council.llm.litellm_provider.litellm.acompletion",
            new=AsyncMock(return_value=fake_stream()),
        ):
            chunks = [c async for c in provider.stream("prompt")]
        assert chunks == ["Hel", "lo", "!"]

    def test_non_retryable_includes_value_error(self) -> None:
        assert ValueError in _litellm_non_retryable()

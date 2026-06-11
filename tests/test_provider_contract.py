"""Shared provider contract tests.

Every ``LLMProvider`` implementation must satisfy the same behavioural
contract for ``generate`` and ``stream``.  These tests run the contract
against the in-repo mock provider and the LiteLLM adapter (with the network
call mocked) so provider migrations have regression protection without
requiring real API keys.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from council.llm.litellm_provider import LiteLLMProvider
from council.llm.provider import LLMProvider, LLMResponse


class _ContractMock(LLMProvider):
    """Minimal compliant provider used as the contract baseline."""

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: str | None = None,
    ) -> LLMResponse:
        return LLMResponse(
            content="contract response",
            model=model or "mock",
            tokens_prompt=5,
            tokens_completion=7,
            cost_usd=0.01,
            latency_ms=1.0,
        )

    async def stream(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: str | None = None,
    ) -> AsyncIterator[str]:
        for piece in ["contract ", "response"]:
            yield piece


def _fake_litellm_response() -> SimpleNamespace:
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="contract response"))],
        usage=SimpleNamespace(prompt_tokens=5, completion_tokens=7),
        model="openai/gpt-4o",
    )


def _make_litellm() -> LiteLLMProvider:
    return LiteLLMProvider(model="openai/gpt-4o")


PROVIDER_FACTORIES = {
    "mock": lambda: _ContractMock(),
    "litellm": _make_litellm,
}


@pytest.fixture(params=list(PROVIDER_FACTORIES))
def provider(request: pytest.FixtureRequest) -> LLMProvider:
    return PROVIDER_FACTORIES[request.param]()


class TestProviderContract:
    @pytest.mark.asyncio
    async def test_generate_returns_llmresponse(self, provider: LLMProvider) -> None:
        async def fake_acompletion(**kwargs: Any) -> SimpleNamespace:
            return _fake_litellm_response()

        with patch(
            "council.llm.litellm_provider.litellm.acompletion",
            new=fake_acompletion,
        ):
            with patch(
                "council.llm.litellm_provider.litellm.completion_cost",
                return_value=0.0,
            ):
                resp = await provider.generate("Say hello", system="be brief")

        assert isinstance(resp, LLMResponse)
        assert resp.content.strip()
        assert isinstance(resp.model, str) and resp.model
        assert resp.tokens_prompt >= 0
        assert resp.tokens_completion >= 0
        assert resp.cost_usd >= 0.0

    @pytest.mark.asyncio
    async def test_stream_yields_nonempty_chunks(self, provider: LLMProvider) -> None:
        def _chunk(text: str) -> SimpleNamespace:
            return SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=text))])

        async def fake_stream(**kwargs: Any):
            for piece in ["contract ", "response"]:
                yield _chunk(piece)

        with patch(
            "council.llm.litellm_provider.litellm.acompletion",
            new=AsyncMock(return_value=fake_stream()),
        ):
            chunks = [c async for c in provider.stream("Say hello")]

        assert chunks, "provider must yield at least one chunk"
        assert "".join(chunks).strip()

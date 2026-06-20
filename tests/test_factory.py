from __future__ import annotations

import pytest

from council.llm.factory import SUPPORTED_PROVIDERS, create_provider


class TestProviderFactory:
    def test_unknown_provider_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown provider"):
            create_provider("nope", None)

    def test_supported_providers_includes_litellm(self) -> None:
        assert "litellm" in SUPPORTED_PROVIDERS
        assert "openai" in SUPPORTED_PROVIDERS

    def test_litellm_provider_constructed(self) -> None:
        provider = create_provider(
            "litellm",
            "openai/gpt-4o",
            litellm_fallbacks=["anthropic/claude-sonnet-4-6"],
        )
        from council.llm.litellm_provider import LiteLLMProvider

        assert isinstance(provider, LiteLLMProvider)
        assert provider.model == "openai/gpt-4o"
        assert provider.fallbacks == ["anthropic/claude-sonnet-4-6"]

    def test_openai_missing_key_raises_actionable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(RuntimeError, match="No API key found for openai"):
            create_provider("openai", None)

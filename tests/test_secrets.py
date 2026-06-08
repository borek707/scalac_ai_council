from __future__ import annotations

from council.llm.secrets import (
    KEY_REQUIRED_PROVIDERS,
    env_key_is_set,
    resolve_api_key,
)


class TestResolveApiKey:
    def test_explicit_key_is_stripped(self) -> None:
        assert resolve_api_key("openai", "  sk-test  ") == "sk-test"

    def test_blank_explicit_key_returns_none(self) -> None:
        assert resolve_api_key("openai", "   ") is None

    def test_reads_provider_env_var(self, monkeypatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "env-key")

        assert resolve_api_key("openai", None) == "env-key"

    def test_unknown_provider_returns_none(self) -> None:
        assert resolve_api_key("ollama", None) is None

    def test_empty_env_var_returns_none(self, monkeypatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "   ")

        assert resolve_api_key("anthropic", None) is None


class TestEnvKeyIsSet:
    def test_true_when_key_present(self, monkeypatch) -> None:
        monkeypatch.setenv("OPENROUTER_API_KEY", "token")

        assert env_key_is_set("openrouter") is True

    def test_false_when_missing(self, monkeypatch) -> None:
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

        assert env_key_is_set("openrouter") is False


class TestKeyRequiredProviders:
    def test_includes_cloud_providers(self) -> None:
        assert "openai" in KEY_REQUIRED_PROVIDERS
        assert "openrouter" in KEY_REQUIRED_PROVIDERS

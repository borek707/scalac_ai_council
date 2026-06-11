"""LLM provider factory.

Centralizes construction of every supported provider so the CLI (and any
other front-end) does not need to know provider-specific constructors.
Adding a new provider means adding a branch here (or, ideally, a registry
entry) instead of editing the CLI run flow.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from council.llm.provider import LLMProvider

# Provider -> (env var, signup URL) for actionable "missing key" errors.
PROVIDER_KEY_HELP: dict[str, tuple[str, str]] = {
    "openai": ("OPENAI_API_KEY", "https://platform.openai.com/api-keys"),
    "anthropic": ("ANTHROPIC_API_KEY", "https://console.anthropic.com/settings/keys"),
    "openrouter": ("OPENROUTER_API_KEY", "https://openrouter.ai/keys"),
}

# Providers selectable on the CLI.
SUPPORTED_PROVIDERS: tuple[str, ...] = (
    "openai",
    "anthropic",
    "ollama",
    "openrouter",
    "kimi-code",
    "claude-code",
    "litellm",
)


def _missing_key_error(provider_name: str) -> RuntimeError:
    env_var, url = PROVIDER_KEY_HELP[provider_name]
    return RuntimeError(
        f"No API key found for {provider_name}.\n\n"
        f"  Set env var:   export {env_var}=<your-key>\n"
        f"  Or pass flag:  --api-key <your-key>\n"
        f"  Get a key at:  {url}\n"
        f"  No key needed? Use --demo for a zero-config demo run."
    )


def create_provider(
    provider_name: str,
    model: str | None,
    *,
    free_tier: bool = False,
    api_key: str | None = None,
    call_timeout: float = 120.0,
    executable_path: str | None = None,
    litellm_fallbacks: Sequence[str] | None = None,
    litellm_api_base: str | None = None,
) -> LLMProvider:
    """Create an LLM provider instance for *provider_name*."""
    if provider_name == "openai":
        try:
            from council.llm.openai_provider import OpenAIProvider
        except ImportError as exc:
            raise ImportError(
                "OpenAI package not installed.\n"
                "  Fix: pip install openai\n"
                "  Then: export OPENAI_API_KEY=sk-..."
            ) from exc
        try:
            return OpenAIProvider(model=model or "gpt-4o", api_key=api_key)
        except RuntimeError:
            raise _missing_key_error(provider_name) from None
    elif provider_name == "anthropic":
        try:
            from council.llm.anthropic_provider import AnthropicProvider
        except ImportError as exc:
            raise ImportError(
                "Anthropic package not installed.\n"
                "  Fix: pip install anthropic\n"
                "  Then: export ANTHROPIC_API_KEY=sk-ant-..."
            ) from exc
        try:
            return AnthropicProvider(model=model or "claude-sonnet-4-6", api_key=api_key)
        except RuntimeError:
            raise _missing_key_error(provider_name) from None
    elif provider_name == "openrouter":
        try:
            from council.llm.openrouter_provider import OpenRouterProvider
        except ImportError as exc:
            raise ImportError(
                "OpenAI package not installed (needed for OpenRouter).\n"
                "  Fix: pip install openai\n"
                "  Then: export OPENROUTER_API_KEY=sk-or-..."
            ) from exc
        try:
            return OpenRouterProvider(model=model, free_tier=free_tier, api_key=api_key)
        except RuntimeError:
            raise _missing_key_error(provider_name) from None
    elif provider_name == "ollama":
        try:
            from council.llm.ollama_provider import OllamaProvider
        except ImportError as exc:
            raise ImportError(
                "aiohttp not installed (needed for Ollama).\n"
                "  Fix: pip install aiohttp\n"
                "  Also ensure Ollama is running: ollama serve"
            ) from exc
        try:
            return OllamaProvider(model=model or "llama3")
        except RuntimeError as exc:
            raise RuntimeError(
                f"Failed to initialize Ollama provider: {exc}\n"
                "  Check that Ollama is running (ollama serve) and the model is pulled."
            ) from exc
    elif provider_name == "kimi-code":
        from council.llm.kimi_code_provider import KimiCodeProvider

        try:
            return KimiCodeProvider(
                executable_path=executable_path,
                model=model or "kimi-for-coding",
                call_timeout=call_timeout,
            )
        except RuntimeError as exc:
            raise RuntimeError(
                f"Failed to initialize Kimi Code provider: {exc}\n"
                "  Make sure you are running inside the Kimi Code IDE,\n"
                "  or that ~/.kimi/credentials/kimi-code.json exists."
            ) from exc
    elif provider_name == "claude-code":
        from council.llm.claude_code_provider import ClaudeCodeProvider

        try:
            return ClaudeCodeProvider(
                executable_path=executable_path,
                model=model or "claude-sonnet-4-6",
                call_timeout=call_timeout,
            )
        except RuntimeError as exc:
            raise RuntimeError(
                f"Failed to initialize Claude Code provider: {exc}\n"
                "  Make sure you are running inside Claude Code IDE,\n"
                "  or that the 'claude' CLI is installed (npm install -g @anthropic-ai/claude-code),\n"
                "  or that ~/.claude/.credentials.json exists."
            ) from exc
    elif provider_name == "litellm":
        try:
            from council.llm.litellm_provider import LiteLLMProvider
        except ImportError as exc:
            raise ImportError(
                "LiteLLM not installed.\n"
                "  Fix: pip install 'council[litellm]' (or: pip install litellm)\n"
                "  Then set the upstream provider key, e.g. export OPENAI_API_KEY=sk-..."
            ) from exc
        return LiteLLMProvider(
            model=model or "openai/gpt-4o",
            api_key=api_key,
            api_base=litellm_api_base,
            fallbacks=litellm_fallbacks,
        )
    else:
        raise ValueError(f"Unknown provider: {provider_name}")


__all__ = [
    "PROVIDER_KEY_HELP",
    "SUPPORTED_PROVIDERS",
    "create_provider",
]

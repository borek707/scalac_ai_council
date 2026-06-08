from __future__ import annotations

import os

PROVIDER_ENV_KEYS: dict[str, str] = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}

KEY_REQUIRED_PROVIDERS: frozenset[str] = frozenset(PROVIDER_ENV_KEYS)


def resolve_api_key(provider: str, explicit: str | None) -> str | None:
    """Resolve an API key from explicit input or the provider env var."""
    if explicit is not None:
        stripped = explicit.strip()
        return stripped or None
    env_var = PROVIDER_ENV_KEYS.get(provider)
    if env_var is None:
        return None
    raw = os.environ.get(env_var)
    if not raw:
        return None
    stripped = raw.strip()
    return stripped or None


def env_key_is_set(provider: str) -> bool:
    """Return True when the provider's env var is set to a non-empty value."""
    return resolve_api_key(provider, None) is not None

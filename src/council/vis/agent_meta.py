from __future__ import annotations

from council.agents.registry import AGENT_REGISTRY

# Derived from the agent registry so colors/emoji live in one place.
AGENT_META: dict[str, dict[str, str]] = {
    name: {"color": spec.color, "emoji": spec.emoji, "key": spec.key}
    for name, spec in AGENT_REGISTRY.items()
}

AGENT_COLORS: dict[str, str] = {name: meta["color"] for name, meta in AGENT_META.items()}

__all__ = ["AGENT_COLORS", "AGENT_META"]

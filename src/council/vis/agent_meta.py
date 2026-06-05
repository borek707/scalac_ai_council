from __future__ import annotations

AGENT_META: dict[str, dict[str, str]] = {
    "Marcus": {"color": "cyan", "emoji": "🏗️", "key": "marcus"},
    "Elena": {"color": "magenta", "emoji": "🎯", "key": "elena"},
    "Kai": {"color": "green", "emoji": "✍️", "key": "kai"},
    "David": {"color": "yellow", "emoji": "🎣", "key": "david"},
}

AGENT_COLORS: dict[str, str] = {name: meta["color"] for name, meta in AGENT_META.items()}

__all__ = ["AGENT_COLORS", "AGENT_META"]

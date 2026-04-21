from __future__ import annotations

import logging
from collections import defaultdict
from typing import Optional

from .provider import LLMResponse

logger = logging.getLogger(__name__)


class CostTracker:
    """Tracks LLM usage costs per agent, round, and overall run."""

    def __init__(self) -> None:
        self._entries: list[dict[str, object]] = []
        self._by_agent: dict[str, float] = defaultdict(float)
        self._total: float = 0.0

    def add(
        self,
        agent: str,
        round_num: int,
        response: LLMResponse,
    ) -> None:
        """Record a cost entry for an agent's LLM call."""
        entry = {
            "agent": agent,
            "round": round_num,
            "cost_usd": response.cost_usd,
            "tokens_prompt": response.tokens_prompt,
            "tokens_completion": response.tokens_completion,
            "model": response.model,
        }
        self._entries.append(entry)
        self._by_agent[agent] += response.cost_usd
        self._total += response.cost_usd

    def get_total(self) -> float:
        """Return total cost across all agents and rounds."""
        return self._total

    def get_by_agent(self, agent: str) -> float:
        """Return total cost for a specific agent."""
        return self._by_agent.get(agent, 0.0)

    def get_by_round(self, round_num: int) -> float:
        """Return total cost for a specific round."""
        return sum(
            float(entry["cost_usd"])
            for entry in self._entries
            if int(entry["round"]) == round_num
        )

    def report(self) -> str:
        """Generate a human-readable cost report."""
        lines = ["=== Cost Report ===", f"Total: ${self._total:.6f}", ""]
        if self._by_agent:
            lines.append("By Agent:")
            for agent, cost in sorted(self._by_agent.items()):
                lines.append(f"  {agent}: ${cost:.6f}")
        lines.append(f"\nTotal calls: {len(self._entries)}")
        return "\n".join(lines)

    def get_entries(self) -> list[dict[str, object]]:
        """Return all recorded entries."""
        return list(self._entries)

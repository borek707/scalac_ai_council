"""Central registry of council agents.

A single source of truth for which agents exist, their display metadata,
their output filenames, and how to construct them.  Adding a new agent
should only require a new :class:`BaseAgent` subclass, its Jinja2 template,
and one :data:`AGENT_REGISTRY` entry — not edits scattered across the CLI,
TUI, orchestrator, and visualization modules.

Agent classes are resolved lazily (by module/class name) so that this
module can be imported by low-level modules such as ``vis.agent_meta``
without creating an import cycle with ``agents.base``.
"""

from __future__ import annotations

import importlib
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from council.agents.base import BaseAgent
    from council.config.documents import Document
    from council.config.schema import CompanyConfig, LLMProvider


@dataclass(frozen=True)
class AgentSpec:
    """Static definition of a single council agent."""

    name: str
    role: str
    module: str
    class_name: str
    color: str
    emoji: str
    output_filename: str

    @property
    def key(self) -> str:
        """Lowercase identifier used for filenames and config keys."""
        return self.name.lower()

    def load_class(self) -> type[BaseAgent]:
        """Import and return the concrete agent class."""
        mod = importlib.import_module(self.module)
        return getattr(mod, self.class_name)  # type: ignore[no-any-return]


# Ordered registry — iteration order is the canonical agent order everywhere.
AGENT_REGISTRY: dict[str, AgentSpec] = {
    "Marcus": AgentSpec(
        name="Marcus",
        role="Offer Architect",
        module="council.agents.marcus",
        class_name="MarcusAgent",
        color="cyan",
        emoji="🏗️",
        output_filename="marcus_offer.md",
    ),
    "Elena": AgentSpec(
        name="Elena",
        role="Funnel Architect",
        module="council.agents.elena",
        class_name="ElenaAgent",
        color="magenta",
        emoji="🎯",
        output_filename="elena_funnel.md",
    ),
    "Kai": AgentSpec(
        name="Kai",
        role="Copywriter",
        module="council.agents.kai",
        class_name="KaiAgent",
        color="green",
        emoji="✍️",
        output_filename="kai_copy.md",
    ),
    "David": AgentSpec(
        name="David",
        role="Lead Strategist",
        module="council.agents.david",
        class_name="DavidAgent",
        color="yellow",
        emoji="🎣",
        output_filename="david_abm.md",
    ),
}


def agent_names() -> list[str]:
    """Return the canonical, ordered list of agent names."""
    return list(AGENT_REGISTRY.keys())


def agent_specs() -> list[AgentSpec]:
    """Return the ordered list of agent specs."""
    return list(AGENT_REGISTRY.values())


def final_filenames() -> dict[str, str]:
    """Map agent name -> final deliverable filename."""
    return {name: spec.output_filename for name, spec in AGENT_REGISTRY.items()}


def build_agents(
    workspace: Path,
    config: CompanyConfig,
    provider: LLMProvider,
    documents: Sequence[Document] | None = None,
    *,
    stream_output: bool = False,
) -> list[BaseAgent]:
    """Construct all registered agents in canonical order.

    This is the single entry point used by the CLI and service layer so
    that agent wiring lives in one place.
    """
    docs = list(documents) if documents is not None else None
    agents: list[BaseAgent] = []
    for spec in AGENT_REGISTRY.values():
        agent_class = spec.load_class()
        agent = agent_class(
            workspace=workspace,
            config=config,
            provider=provider,
            documents=docs,
        )
        agent.stream_output = stream_output
        agents.append(agent)
    return agents


__all__ = [
    "AGENT_REGISTRY",
    "AgentSpec",
    "agent_names",
    "agent_specs",
    "build_agents",
    "final_filenames",
]

"""Council service layer.

Encapsulates the core run flow — building agents, running the orchestrator,
and writing artifacts — independently of the CLI argument parsing and the
Textual TUI.  This makes the product runnable and testable without invoking
``cli.main`` or rendering a dashboard.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from council.agents.registry import agent_names as registry_agent_names
from council.agents.registry import build_agents

if TYPE_CHECKING:
    from council.agents.base import BaseAgent
    from council.config.documents import Document
    from council.config.schema import CompanyConfig
    from council.llm.provider import LLMProvider
    from council.platform.base import PlatformAdapter


@dataclass
class CouncilRunConfig:
    """Everything the service needs to run a council debate.

    This is intentionally decoupled from ``argparse.Namespace`` so the
    service can be driven from tests, scripts, or other front-ends.
    """

    company_config: CompanyConfig
    provider_name: str
    workspace: Path
    provider_model: str | None = None
    rounds: int = 3
    round_timeout: float = 300.0
    documents: list[Document] = field(default_factory=list)
    stream_output: bool = False
    sequential_finals: bool = False
    use_filesystem_barrier: bool = False


@dataclass
class CouncilRunResult:
    """Outcome of a completed council run."""

    workspace: Path
    rounds: int
    artifacts: dict[str, Path]
    agent_names: list[str]


class CouncilService:
    """Runs a council debate end-to-end for a prepared provider."""

    def __init__(
        self,
        provider: LLMProvider,
        *,
        progress_callback: Callable[..., None] | None = None,
        adapter: PlatformAdapter | None = None,
    ) -> None:
        self.provider = provider
        self.progress_callback = progress_callback
        self.adapter = adapter

    def build_agents(self, config: CouncilRunConfig) -> list[BaseAgent]:
        """Construct the agents for a run via the central registry."""
        return build_agents(
            workspace=config.workspace,
            config=config.company_config,
            provider=self.provider,
            documents=config.documents,
            stream_output=config.stream_output,
        )

    async def run(self, config: CouncilRunConfig) -> CouncilRunResult:
        """Execute all rounds and final deliverables, then write artifacts."""
        from council.orchestration.orchestrator import AsyncOrchestrator

        agents = self.build_agents(config)
        orchestrator = AsyncOrchestrator(
            agents=agents,
            config=config.company_config,
            provider=self.provider,
            provider_name=config.provider_name,
            provider_model=config.provider_model,
            max_rounds=config.rounds,
            round_timeout=config.round_timeout,
            workspace=config.workspace,
            progress_callback=self.progress_callback,
            use_filesystem_barrier=config.use_filesystem_barrier,
            sequential_finals=config.sequential_finals,
        )

        if self.adapter is not None:
            await self.adapter.spawn_agents(orchestrator)
        else:
            await orchestrator.run()

        artifacts = orchestrator.write_artifacts(config.workspace / "output")
        return CouncilRunResult(
            workspace=config.workspace,
            rounds=config.rounds,
            artifacts=artifacts,
            agent_names=registry_agent_names(),
        )


__all__ = [
    "CouncilRunConfig",
    "CouncilRunResult",
    "CouncilService",
]

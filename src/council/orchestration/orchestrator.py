from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from council.agents.base import BaseAgent
    from council.config.schema import CompanyConfig
    from council.llm.provider import LLMProvider

from council.orchestration.barrier import FilesystemBarrier
from council.orchestration.state_machine import AgentState, AgentStateMachine

logger = logging.getLogger(__name__)


class AsyncOrchestrator:
    """Main controller for running multi-agent marketing council debates.

    Orchestrates agents to run in parallel within each round,
    with all rounds executing sequentially. Uses a filesystem barrier
    to synchronize agents between rounds.
    """

    def __init__(
        self,
        agents: list[BaseAgent],
        config: CompanyConfig,
        provider: LLMProvider,
        provider_name: str = "openai",
        provider_model: Optional[str] = None,
        max_rounds: int = 3,
        round_timeout: float = 300.0,
        workspace: Optional[Path] = None,
        progress_callback: Optional[Callable[..., None]] = None,
    ) -> None:
        self.agents = agents
        self.config = config
        self.provider = provider
        self.provider_name = provider_name
        self.provider_model = provider_model
        self.max_rounds = max_rounds
        self.round_timeout = round_timeout
        self.workspace = workspace or Path("./output")
        self.progress_callback = progress_callback

        # Inject callback into every agent so they can report live progress
        if progress_callback:
            for agent in agents:
                agent.progress_callback = progress_callback

        discussion_dir = self.workspace / "shared" / "discussion"
        discussion_dir.mkdir(parents=True, exist_ok=True)

        self.barrier = FilesystemBarrier(
            discussion_dir=discussion_dir,
            expected_agents=[a.name for a in agents],
            timeout=round_timeout,
        )
        self.state_machine = AgentStateMachine()
        for agent in agents:
            self.state_machine.register(agent.name)

        self._round_results: dict[int, dict[str, Path]] = {}

    async def run_round(self, round_num: int) -> dict[str, Path]:
        """Run all agents in parallel for a round, with barrier synchronization.

        Args:
            round_num: The round number to run (1-based).

        Returns:
            Mapping of agent_name -> file_path for completed agents.

        Raises:
            Exception: If any agent fails and the error propagates.
        """
        logger.info("=== Starting Round %d ===", round_num)

        for agent in self.agents:
            self.state_machine.transition(
                agent.name,
                self.state_machine.get_state(agent.name),
                AgentState.WRITING,
            )

        tasks = [agent.run_round(round_num) for agent in self.agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for agent, result in zip(self.agents, results):
            if isinstance(result, Exception):
                logger.error("Agent %s failed in round %d: %s", agent.name, round_num, result)
                self.state_machine.force_state(agent.name, AgentState.ERROR)
            else:
                self.state_machine.force_state(agent.name, AgentState.DONE)

        barrier_results = await self.barrier.wait(round_num)

        for agent in self.agents:
            if self.state_machine.get_state(agent.name) != AgentState.ERROR:
                self.state_machine.force_state(agent.name, AgentState.PENDING)

        successful: dict[str, Path] = {}
        for agent, result in zip(self.agents, results):
            if isinstance(result, Path):
                successful[agent.name] = result

        self._round_results[round_num] = successful
        logger.info(
            "=== Round %d Complete: %d/%d agents succeeded ===",
            round_num,
            len(successful),
            len(self.agents),
        )
        return successful

    async def run(self) -> dict[str, Path]:
        """Run full debate: all rounds sequentially, agents parallel within each round.

        Returns:
            Final collected outputs from the last round.
        """
        logger.info(
            "Starting council run: %d agents, %d rounds",
            len(self.agents),
            self.max_rounds,
        )
        for round_num in range(1, self.max_rounds + 1):
            results = await self.run_round(round_num)
            if self._check_consensus(round_num):
                logger.info("Consensus reached at round %d, stopping early.", round_num)
                break

        return await self._collect_final_outputs()

    def _check_consensus(self, round_num: int) -> bool:
        """Check if agents have reached consensus.

        Default implementation returns False (run all rounds).
        Override for custom consensus detection.
        """
        return False

    async def _collect_final_outputs(self) -> dict[str, Path]:
        """Collect final outputs from all agents."""
        outputs: dict[str, Path] = {}
        for agent in self.agents:
            final_path = self.workspace / "output" / agent.get_output_filename()
            if final_path.exists():
                outputs[agent.name] = final_path
        return outputs

    def aggregate_proposal(self) -> str:
        """Aggregate all agent outputs into a single proposal.

        Reads all round outputs and produces a combined markdown document.
        """
        lines: list[str] = [
            "# Universal AI Marketing Council — Aggregated Proposal",
            "",
            f"**Company:** {self.config.name}",
            f"**Product:** {self.config.product}",
            f"**Rounds:** {len(self._round_results)}",
            "",
            "---",
            "",
        ]

        for round_num in sorted(self._round_results):
            lines.append(f"## Round {round_num}")
            lines.append("")
            results = self._round_results[round_num]
            for agent_name in sorted(results):
                path = results[agent_name]
                try:
                    content = path.read_text(encoding="utf-8")
                except OSError as exc:
                    content = f"*Error reading file: {exc}*"
                lines.append(f"### {agent_name}")
                lines.append("")
                lines.append(content)
                lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def get_state_snapshot(self) -> dict[str, AgentState]:
        """Return current state snapshot of all agents."""
        return self.state_machine.get_snapshot()

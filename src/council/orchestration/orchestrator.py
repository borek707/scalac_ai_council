from __future__ import annotations

import asyncio
import json
import logging
import re
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from council.agents.base import BaseAgent
    from council.config.schema import CompanyConfig
    from council.llm.provider import LLMProvider

from council.orchestration.barrier import FilesystemBarrier
from council.orchestration.state_machine import AgentState, AgentStateMachine

logger = logging.getLogger(__name__)

_CONSENSUS_JACCARD_THRESHOLD = 0.25
_WORD_PATTERN = re.compile(r"[a-z]{5,}")


class AsyncOrchestrator:
    """Main controller for running multi-agent marketing council debates.

    Orchestrates agents to run in parallel within each round,
    with all rounds executing sequentially. Cross-process platforms
    (e.g. Kimi ``sessions_spawn``) use :class:`FilesystemBarrier` directly;
    in-process ``asyncio.gather`` runs do not need a post-gather barrier.
    """

    def __init__(
        self,
        agents: list[BaseAgent],
        config: CompanyConfig,
        provider: LLMProvider,
        provider_name: str = "openai",
        provider_model: str | None = None,
        max_rounds: int = 3,
        round_timeout: float = 300.0,
        workspace: Path | None = None,
        progress_callback: Callable[..., None] | None = None,
        use_filesystem_barrier: bool = False,
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
        self.use_filesystem_barrier = use_filesystem_barrier

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
        self._final_results: dict[str, Path] = {}
        self.agent_errors: list[tuple[str, str, str]] = []

    def _record_agent_error(self, phase: str, agent_name: str, exc: Exception) -> None:
        entry = (phase, agent_name, str(exc))
        if entry not in self.agent_errors:
            self.agent_errors.append(entry)

    def _safe_transition(self, agent_name: str, to_state: AgentState) -> None:
        current = self.state_machine.get_state(agent_name)
        if not self.state_machine.transition(agent_name, current, to_state):
            logger.warning(
                "Agent %s: rejected transition %s -> %s",
                agent_name,
                current.name,
                to_state.name,
            )

    def _emit_progress(self, agent_name: str, event: str, **kwargs: Any) -> None:
        if self.progress_callback:
            self.progress_callback(agent_name, event, **kwargs)

    async def run_round(self, round_num: int) -> dict[str, Path]:
        """Run all agents in parallel for a round."""
        logger.info("=== Starting Round %d ===", round_num)

        for agent in self.agents:
            self._safe_transition(agent.name, AgentState.WRITING)
            self._emit_progress(
                agent.name,
                "round_start",
                round_num=round_num,
                activity="Starting round...",
            )

        tasks = [agent.run_round(round_num) for agent in self.agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        failed_agents: dict[str, Exception] = {}
        for agent, result in zip(self.agents, results):
            if isinstance(result, Exception):
                logger.error("Agent %s failed in round %d: %s", agent.name, round_num, result)
                self._safe_transition(agent.name, AgentState.ERROR)
                self._emit_progress(
                    agent.name,
                    "error",
                    message=str(result),
                )
                self._record_agent_error(f"round_{round_num}", agent.name, result)
                failed_agents[agent.name] = result
            else:
                if self.use_filesystem_barrier:
                    self._safe_transition(agent.name, AgentState.WAITING)
                    self._emit_progress(agent.name, "waiting", activity="Waiting for peers...")
                else:
                    self._safe_transition(agent.name, AgentState.DONE)

        if self.use_filesystem_barrier:
            if failed_agents:
                self.barrier.expected_agents = [
                    a.name for a in self.agents if a.name not in failed_agents
                ]
            try:
                await self.barrier.wait(round_num)
            except TimeoutError as exc:
                if failed_agents:
                    causes = "; ".join(f"{name}: {err}" for name, err in failed_agents.items())
                    raise TimeoutError(f"{exc} — underlying agent failures: {causes}") from exc
                raise
            finally:
                self.barrier.expected_agents = [a.name for a in self.agents]

            for agent in self.agents:
                if self.state_machine.get_state(agent.name) == AgentState.WAITING:
                    self._safe_transition(agent.name, AgentState.DONE)
                    self._emit_progress(agent.name, "done", activity="Round complete")

        for agent in self.agents:
            if self.state_machine.get_state(agent.name) != AgentState.ERROR:
                self._safe_transition(agent.name, AgentState.PENDING)

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
        """Run full debate: all rounds sequentially, agents parallel within each round."""
        logger.info(
            "Starting council run: %d agents, %d rounds",
            len(self.agents),
            self.max_rounds,
        )
        for round_num in range(1, self.max_rounds + 1):
            try:
                await asyncio.wait_for(
                    self.run_round(round_num),
                    timeout=self.round_timeout,
                )
            except TimeoutError:
                raise TimeoutError(f"Round {round_num} exceeded the {self.round_timeout}s timeout")
            if self._check_consensus(round_num):
                logger.info("Consensus reached at round %d, stopping early.", round_num)
                break

        self._final_results = await self._run_final_all()
        if self.agent_errors:
            detail = "\n".join(
                f"  • {name} ({phase}): {msg}" for phase, name, msg in self.agent_errors
            )
            raise RuntimeError(
                f"Council run finished with agent failures ({len(self.agent_errors)}):\n{detail}"
            )
        return await self._collect_final_outputs()

    async def _run_final_all(self) -> dict[str, Path]:
        """Call run_final() on every agent in parallel and return agent_name -> Path."""
        logger.info("=== Generating final agent deliverables ===")
        tasks = [agent.run_final() for agent in self.agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        final: dict[str, Path] = {}
        for agent, result in zip(self.agents, results):
            if isinstance(result, Exception):
                logger.error("Agent %s failed during run_final: %s", agent.name, result)
                self._record_agent_error("final", agent.name, result)
                self._emit_progress(agent.name, "error", message=str(result))
            elif isinstance(result, Path):
                final[agent.name] = result
                logger.info("Agent %s final deliverable: %s", agent.name, result)
        logger.info(
            "=== Final deliverables complete: %d/%d agents succeeded ===",
            len(final),
            len(self.agents),
        )
        return final

    def _check_consensus(self, round_num: int) -> bool:
        """Return True when agent round outputs share enough topical overlap."""
        results = self._round_results.get(round_num)
        if not results or len(results) < 2:
            return False

        token_sets: list[set[str]] = []
        for path in results.values():
            try:
                text = path.read_text(encoding="utf-8").lower()
            except OSError:
                continue
            words = set(_WORD_PATTERN.findall(text))
            if words:
                token_sets.append(words)

        if len(token_sets) < 2:
            return False

        intersection = set.intersection(*token_sets)
        union = set.union(*token_sets)
        if not union:
            return False

        jaccard = len(intersection) / len(union)
        if jaccard >= _CONSENSUS_JACCARD_THRESHOLD:
            logger.info(
                "Consensus detected at round %d (Jaccard=%.2f, shared_terms=%d)",
                round_num,
                jaccard,
                len(intersection),
            )
            return True
        return False

    async def _collect_final_outputs(self) -> dict[str, Path]:
        """Collect final outputs from all agents."""
        outputs: dict[str, Path] = {}
        for agent in self.agents:
            filename = agent.get_output_filename()
            preferred = self.workspace / "output" / "agents" / filename
            if preferred.exists():
                outputs[agent.name] = preferred
                continue
            fallback = self.workspace / "output" / filename
            if fallback.exists():
                outputs[agent.name] = fallback
        return outputs

    def aggregate_proposal(self) -> str:
        """Aggregate all agent outputs into a single proposal."""
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

    def write_artifacts(self, output_dir: Path | None = None) -> dict[str, Path]:
        """Write proposal.md and manifest.json to output_dir after a completed run."""
        out = output_dir or (self.workspace / "output")
        out.mkdir(parents=True, exist_ok=True)

        agents_dir = out / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)

        proposal_path = out / "proposal.md"
        proposal_path.write_text(self.aggregate_proposal(), encoding="utf-8")

        manifest: dict[str, Any] = {
            "generated_at": datetime.now(UTC).isoformat(),
            "company": self.config.name,
            "product": self.config.product,
            "provider": self.provider_name,
            "model": self.provider_model,
            "rounds_completed": len(self._round_results),
            "max_rounds": self.max_rounds,
            "agents": [a.name for a in self.agents],
            "files": {
                "proposal": str(proposal_path),
                "agents_dir": str(agents_dir),
                "agent_outputs": {
                    name: str(path)
                    for round_results in self._round_results.values()
                    for name, path in round_results.items()
                },
                "final_deliverables": {
                    name: str(path) for name, path in self._final_results.items()
                },
            },
        }
        manifest_path = out / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        logger.info("Artifacts written: %s, %s", proposal_path, manifest_path)
        return {"proposal": proposal_path, "manifest": manifest_path, "agents_dir": agents_dir}

    def get_state_snapshot(self) -> dict[str, AgentState]:
        """Return current state snapshot of all agents."""
        return self.state_machine.get_snapshot()


def write_workspace_artifacts(
    workspace: Path,
    config: CompanyConfig,
    *,
    provider_name: str,
    provider_model: str | None,
    max_rounds: int,
    agent_names: tuple[str, ...] = ("Marcus", "Elena", "Kai", "David"),
) -> dict[str, Path]:
    """Build proposal/manifest from files already on disk (demo or recovery path)."""
    from collections.abc import AsyncIterator

    from council.llm.provider import LLMProvider, LLMResponse

    class _NoOpProvider(LLMProvider):
        async def generate(
            self,
            prompt: str,
            model: str | None = None,
            temperature: float = 0.7,
            max_tokens: int = 4000,
            system: str | None = None,
        ) -> LLMResponse:
            raise NotImplementedError

        async def stream(
            self,
            prompt: str,
            model: str | None = None,
            temperature: float = 0.7,
            max_tokens: int = 4000,
            system: str | None = None,
        ) -> AsyncIterator[str]:
            raise NotImplementedError
            yield ""  # type: ignore[unreachable]

    orchestrator = AsyncOrchestrator(
        agents=[],
        config=config,
        provider=_NoOpProvider(),
        provider_name=provider_name,
        provider_model=provider_model,
        max_rounds=max_rounds,
        workspace=workspace,
    )

    discussion_dir = workspace / "shared" / "discussion"
    for round_num in range(1, max_rounds + 1):
        round_paths: dict[str, Path] = {}
        for name in agent_names:
            path = discussion_dir / f"{name.lower()}_round_{round_num}.md"
            if path.exists():
                round_paths[name] = path
        if round_paths:
            orchestrator._round_results[round_num] = round_paths

    agents_dir = workspace / "output" / "agents"
    final_files = {
        "Marcus": "marcus_offer.md",
        "Elena": "elena_funnel.md",
        "Kai": "kai_copy.md",
        "David": "david_abm.md",
    }
    for name, filename in final_files.items():
        path = agents_dir / filename
        if path.exists():
            orchestrator._final_results[name] = path

    return orchestrator.write_artifacts(workspace / "output")

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import pytest

from council.config.schema import CompanyConfig
from council.llm.provider import LLMProvider, LLMResponse
from council.orchestration.barrier import FilesystemBarrier
from council.orchestration.orchestrator import AsyncOrchestrator
from council.orchestration.state_machine import AgentState, AgentStateMachine


class MockLLMProvider(LLMProvider):
    """Minimal mock LLM provider used by the new orchestration tests."""

    def __init__(self, response_text: str = "Mock response") -> None:
        self.response_text = response_text
        self._call_count = 0

    async def generate(
        self,
        prompt: str,
        model: Any = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: Any = None,
    ) -> LLMResponse:
        self._call_count += 1
        return LLMResponse(
            content=f"{self.response_text} (call #{self._call_count})",
            model="mock-model",
            tokens_prompt=len(prompt) // 4,
            tokens_completion=50,
            cost_usd=0.0,
            latency_ms=1.0,
        )

    async def stream(self, prompt: str, **kwargs: Any):  # type: ignore[override]
        yield self.response_text


class TestAgentState:
    """Tests for AgentState enum."""

    def test_state_values(self) -> None:
        assert AgentState.PENDING.name == "PENDING"
        assert AgentState.WRITING.name == "WRITING"
        assert AgentState.WAITING.name == "WAITING"
        assert AgentState.DONE.name == "DONE"
        assert AgentState.ERROR.name == "ERROR"


class TestAgentStateMachine:
    """Tests for AgentStateMachine."""

    def test_register_agent(self) -> None:
        sm = AgentStateMachine()
        sm.register("marcus")
        assert sm.get_state("marcus") == AgentState.PENDING

    def test_valid_transition_pending_to_writing(self) -> None:
        sm = AgentStateMachine()
        sm.register("marcus")
        result = sm.transition("marcus", AgentState.PENDING, AgentState.WRITING)
        assert result is True
        assert sm.get_state("marcus") == AgentState.WRITING

    def test_valid_transition_writing_to_done(self) -> None:
        sm = AgentStateMachine()
        sm.register("marcus")
        sm.force_state("marcus", AgentState.WRITING)
        result = sm.transition("marcus", AgentState.WRITING, AgentState.DONE)
        assert result is True
        assert sm.get_state("marcus") == AgentState.DONE

    def test_invalid_transition(self) -> None:
        sm = AgentStateMachine()
        sm.register("marcus")
        result = sm.transition("marcus", AgentState.PENDING, AgentState.DONE)
        assert result is False
        assert sm.get_state("marcus") == AgentState.PENDING

    def test_transition_wrong_from_state(self) -> None:
        sm = AgentStateMachine()
        sm.register("marcus")
        sm.force_state("marcus", AgentState.WRITING)
        result = sm.transition("marcus", AgentState.PENDING, AgentState.WRITING)
        assert result is False

    def test_unregistered_agent(self) -> None:
        sm = AgentStateMachine()
        result = sm.transition("unknown", AgentState.PENDING, AgentState.WRITING)
        assert result is False

    def test_all_in_state_true(self) -> None:
        sm = AgentStateMachine()
        sm.register("a")
        sm.register("b")
        sm.force_state("a", AgentState.DONE)
        sm.force_state("b", AgentState.DONE)
        assert sm.all_in_state(AgentState.DONE) is True

    def test_all_in_state_false(self) -> None:
        sm = AgentStateMachine()
        sm.register("a")
        sm.register("b")
        sm.force_state("a", AgentState.DONE)
        sm.force_state("b", AgentState.WRITING)
        assert sm.all_in_state(AgentState.DONE) is False

    def test_all_in_state_empty(self) -> None:
        sm = AgentStateMachine()
        assert sm.all_in_state(AgentState.PENDING) is False

    def test_any_in_state(self) -> None:
        sm = AgentStateMachine()
        sm.register("a")
        sm.register("b")
        sm.force_state("a", AgentState.DONE)
        sm.force_state("b", AgentState.WRITING)
        assert sm.any_in_state(AgentState.DONE) is True
        assert sm.any_in_state(AgentState.ERROR) is False

    def test_agents_in_state(self) -> None:
        sm = AgentStateMachine()
        sm.register("marcus")
        sm.register("elena")
        sm.force_state("marcus", AgentState.WRITING)
        assert sm.agents_in_state(AgentState.WRITING) == ["marcus"]

    def test_get_snapshot(self) -> None:
        sm = AgentStateMachine()
        sm.register("a")
        sm.register("b")
        snapshot = sm.get_snapshot()
        assert snapshot == {"a": AgentState.PENDING, "b": AgentState.PENDING}

    def test_force_state(self) -> None:
        sm = AgentStateMachine()
        sm.register("a")
        sm.force_state("a", AgentState.ERROR)
        assert sm.get_state("a") == AgentState.ERROR

    def test_pending_to_error_valid(self) -> None:
        sm = AgentStateMachine()
        sm.register("a")
        result = sm.transition("a", AgentState.PENDING, AgentState.ERROR)
        assert result is True

    def test_error_to_pending_recovery(self) -> None:
        sm = AgentStateMachine()
        sm.register("a")
        sm.force_state("a", AgentState.ERROR)
        result = sm.transition("a", AgentState.ERROR, AgentState.PENDING)
        assert result is True


class TestFilesystemBarrier:
    """Tests for FilesystemBarrier."""

    def test_is_complete_all_present(self, temp_workspace: Path) -> None:
        discussion_dir = temp_workspace / "shared" / "discussion"
        agents = ["marcus", "elena", "kai"]
        barrier = FilesystemBarrier(discussion_dir, agents, timeout=5.0)

        for agent in agents:
            (discussion_dir / f"{agent}_round_1.md").write_text("done", encoding="utf-8")

        assert barrier.is_complete(1) is True

    def test_is_complete_some_missing(self, temp_workspace: Path) -> None:
        discussion_dir = temp_workspace / "shared" / "discussion"
        agents = ["marcus", "elena", "kai"]
        barrier = FilesystemBarrier(discussion_dir, agents, timeout=5.0)

        (discussion_dir / "marcus_round_1.md").write_text("done", encoding="utf-8")

        assert barrier.is_complete(1) is False

    def test_get_status(self, temp_workspace: Path) -> None:
        discussion_dir = temp_workspace / "shared" / "discussion"
        agents = ["marcus", "elena"]
        barrier = FilesystemBarrier(discussion_dir, agents, timeout=5.0)

        (discussion_dir / "marcus_round_1.md").write_text("done", encoding="utf-8")

        status = barrier.get_status(1)
        assert status == {"marcus": True, "elena": False}

    @pytest.mark.asyncio
    async def test_wait_success(self, temp_workspace: Path) -> None:
        discussion_dir = temp_workspace / "shared" / "discussion"
        agents = ["marcus", "elena"]
        barrier = FilesystemBarrier(discussion_dir, agents, timeout=5.0)

        for agent in agents:
            (discussion_dir / f"{agent}_round_1.md").write_text("done", encoding="utf-8")

        result = await barrier.wait(1)
        assert len(result) == 2
        assert "marcus" in result
        assert "elena" in result

    @pytest.mark.asyncio
    async def test_wait_timeout(self, temp_workspace: Path) -> None:
        discussion_dir = temp_workspace / "shared" / "discussion"
        agents = ["marcus", "elena"]
        barrier = FilesystemBarrier(discussion_dir, agents, timeout=0.5, poll_interval=0.1)

        with pytest.raises(TimeoutError):
            await barrier.wait(1)

    @pytest.mark.asyncio
    async def test_wait_with_delayed_files(self, temp_workspace: Path) -> None:
        discussion_dir = temp_workspace / "shared" / "discussion"
        agents = ["marcus", "elena"]
        barrier = FilesystemBarrier(discussion_dir, agents, timeout=5.0, poll_interval=0.1)

        (discussion_dir / "marcus_round_1.md").write_text("done", encoding="utf-8")

        async def delayed_write() -> None:
            await asyncio.sleep(0.2)
            (discussion_dir / "elena_round_1.md").write_text("done", encoding="utf-8")

        asyncio.create_task(delayed_write())
        result = await barrier.wait(1)
        assert len(result) == 2

    def test_collect_files(self, temp_workspace: Path) -> None:
        discussion_dir = temp_workspace / "shared" / "discussion"
        agents = ["marcus", "elena"]
        barrier = FilesystemBarrier(discussion_dir, agents, timeout=5.0)

        (discussion_dir / "marcus_round_1.md").write_text("a", encoding="utf-8")
        (discussion_dir / "elena_round_1.md").write_text("b", encoding="utf-8")

        files = barrier._collect_files(1)
        assert len(files) == 2
        assert files["marcus"].exists()
        assert files["elena"].exists()


class TestAsyncOrchestrator:
    """Tests for AsyncOrchestrator."""

    @pytest.mark.asyncio
    async def test_run_round_parallel(
        self,
        orchestrator: AsyncOrchestrator,
        temp_workspace: Path,
    ) -> None:
        results = await orchestrator.run_round(1)
        assert len(results) == 4
        for agent_name, path in results.items():
            assert path.exists()
            assert path.name == f"{agent_name}_round_1.md"

    @pytest.mark.asyncio
    async def test_run_multiple_rounds(
        self,
        orchestrator: AsyncOrchestrator,
    ) -> None:
        results = await orchestrator.run()
        assert len(results) >= 0
        # After run, discussion files should exist for round 1
        discussion_dir = orchestrator.workspace / "shared" / "discussion"
        files = list(discussion_dir.glob("*_round_1.md"))
        assert len(files) == 4

    @pytest.mark.asyncio
    async def test_run_round_state_machine(
        self,
        orchestrator: AsyncOrchestrator,
    ) -> None:
        await orchestrator.run_round(1)
        snapshot = orchestrator.get_state_snapshot()
        # After round completes, agents return to PENDING
        for state in snapshot.values():
            assert state == AgentState.PENDING

    def test_aggregate_proposal(
        self,
        orchestrator: AsyncOrchestrator,
        temp_workspace: Path,
    ) -> None:
        # Manually set round results for testing aggregation
        discussion_dir = temp_workspace / "shared" / "discussion"
        orchestrator._round_results[1] = {
            "marcus": discussion_dir / "marcus_round_1.md",
            "elena": discussion_dir / "elena_round_1.md",
        }
        (discussion_dir / "marcus_round_1.md").write_text(
            "# Marcus Strategy\n\nTest content.", encoding="utf-8"
        )
        (discussion_dir / "elena_round_1.md").write_text(
            "# Elena Content\n\nMore content.", encoding="utf-8"
        )

        proposal = orchestrator.aggregate_proposal()
        assert "TestCorp" in proposal
        assert "AI-Powered Analytics Platform" in proposal
        assert "Marcus Strategy" in proposal
        assert "Elena Content" in proposal

    def test_orchestrator_init(
        self,
        orchestrator: AsyncOrchestrator,
    ) -> None:
        assert orchestrator.max_rounds == 3
        assert orchestrator.round_timeout == 30.0
        assert len(orchestrator.agents) == 4
        assert orchestrator.barrier is not None
        assert orchestrator.state_machine is not None

    @pytest.mark.asyncio
    async def test_check_consensus_default(self, orchestrator: AsyncOrchestrator) -> None:
        # Default implementation always returns False
        assert orchestrator._check_consensus(1) is False

    @pytest.mark.asyncio
    async def test_collect_final_outputs_empty(self, orchestrator: AsyncOrchestrator) -> None:
        outputs = await orchestrator._collect_final_outputs()
        assert outputs == {}

    @pytest.mark.asyncio
    async def test_run_single_round_only(
        self,
        orchestrator: AsyncOrchestrator,
    ) -> None:
        orchestrator.max_rounds = 1
        await orchestrator.run()
        # Only round 1 files should exist
        discussion_dir = orchestrator.workspace / "shared" / "discussion"
        files = list(discussion_dir.glob("*_round_1.md"))
        assert len(files) == 4
        files_r2 = list(discussion_dir.glob("*_round_2.md"))
        assert len(files_r2) == 0

    # ── Issue #8 ──────────────────────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_run_creates_final_deliverables(
        self,
        sample_config: CompanyConfig,
        temp_workspace: Path,
    ) -> None:
        """run() must call run_final() for every agent and persist deliverables
        under workspace/output/agents/<filename> (issue #8)."""
        from council.agents.base import BaseAgent
        from council.config.schema import RoundContext

        class SimpleFinalAgent(BaseAgent):
            """Agent that writes trivial round and final files without an LLM."""

            def get_system_prompt(self) -> str:
                return f"You are {self.name}."

            def get_output_filename(self) -> str:
                return f"{self.name}_final.md"

            def get_template_name(self) -> str:
                # not used — generate_round and run_final are overridden
                return "marcus.j2"

            async def generate_round(self, ctx: RoundContext) -> str:
                return f"# {self.name} — Round {ctx.round_num}\n\nContent."

            async def run_final(self) -> Path:
                content = f"# {self.name} — Final Deliverable\n\nDone."
                return self.write_final(content, self.get_output_filename())

        agents = [
            SimpleFinalAgent(
                name="alpha",
                role="Test Agent",
                workspace=temp_workspace,
                config=sample_config,
                provider=MockLLMProvider(),
            ),
            SimpleFinalAgent(
                name="beta",
                role="Test Agent",
                workspace=temp_workspace,
                config=sample_config,
                provider=MockLLMProvider(),
            ),
        ]

        orc = AsyncOrchestrator(
            agents=agents,
            config=sample_config,
            provider=MockLLMProvider(),
            max_rounds=1,
            round_timeout=10.0,
            workspace=temp_workspace,
        )

        await orc.run()

        agents_dir = temp_workspace / "output" / "agents"
        for agent in agents:
            expected_file = agents_dir / agent.get_output_filename()
            assert (
                expected_file.exists()
            ), f"Final deliverable missing for agent '{agent.name}': {expected_file}"

    # ── Issue #11 ─────────────────────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_agent_failure_surfaced_in_timeout_error(
        self,
        sample_config: CompanyConfig,
        temp_workspace: Path,
    ) -> None:
        """When an agent fails and the barrier times out, the TimeoutError must
        include the underlying agent failure reason (issue #11)."""
        from council.agents.base import BaseAgent
        from council.config.schema import RoundContext

        class CrashingAgent(BaseAgent):
            """Agent that immediately raises RuntimeError in run_round."""

            def get_system_prompt(self) -> str:
                return "crasher"

            def get_output_filename(self) -> str:
                return "crasher_final.md"

            def get_template_name(self) -> str:
                return "marcus.j2"

            async def generate_round(self, ctx: RoundContext) -> str:
                raise RuntimeError("agent crashed")

        class PhantomAgent(BaseAgent):
            """Agent whose run_round returns immediately but never writes a
            discussion file, causing the barrier to time out."""

            def get_system_prompt(self) -> str:
                return "phantom"

            def get_output_filename(self) -> str:
                return "phantom_final.md"

            def get_template_name(self) -> str:
                return "marcus.j2"

            async def run_round(self, round_num: int) -> Path:
                # Return a non-existent path — the discussion file is never written
                # so the barrier cannot find it and will time out.
                return temp_workspace / "shared" / "discussion" / f"phantom_round_{round_num}.md"

            async def run_final(self) -> Path:
                return self.write_final("phantom final", self.get_output_filename())

        crasher = CrashingAgent(
            name="crasher",
            role="Test Crasher",
            workspace=temp_workspace,
            config=sample_config,
            provider=MockLLMProvider(),
        )
        phantom = PhantomAgent(
            name="phantom",
            role="Test Phantom",
            workspace=temp_workspace,
            config=sample_config,
            provider=MockLLMProvider(),
        )

        orc = AsyncOrchestrator(
            agents=[crasher, phantom],
            config=sample_config,
            provider=MockLLMProvider(),
            max_rounds=1,
            round_timeout=30.0,
            workspace=temp_workspace,
            use_filesystem_barrier=True,
        )
        # Make the barrier time out quickly so the test does not stall.
        orc.barrier.timeout = 0.3
        orc.barrier.poll_interval = 0.05

        with pytest.raises(TimeoutError) as exc_info:
            await orc.run_round(1)

        error_message = str(exc_info.value)
        assert (
            "agent crashed" in error_message or "crasher" in error_message
        ), f"Expected 'agent crashed' or 'crasher' in TimeoutError message, got: {error_message!r}"

    # ── Issue #18 ─────────────────────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_round_timeout_raises(
        self,
        sample_config: CompanyConfig,
        temp_workspace: Path,
    ) -> None:
        """run() must raise TimeoutError when a round exceeds round_timeout
        seconds (issue #18)."""
        from council.agents.base import BaseAgent
        from council.config.schema import RoundContext

        class HangingAgent(BaseAgent):
            """Agent that sleeps indefinitely during generate_round."""

            def get_system_prompt(self) -> str:
                return "hanger"

            def get_output_filename(self) -> str:
                return "hanger_final.md"

            def get_template_name(self) -> str:
                return "marcus.j2"

            async def generate_round(self, ctx: RoundContext) -> str:
                await asyncio.sleep(999)
                return "never reached"

        agent = HangingAgent(
            name="hanger",
            role="Test Hanger",
            workspace=temp_workspace,
            config=sample_config,
            provider=MockLLMProvider(),
        )

        orc = AsyncOrchestrator(
            agents=[agent],
            config=sample_config,
            provider=MockLLMProvider(),
            max_rounds=1,
            round_timeout=0.1,
            workspace=temp_workspace,
        )

        with pytest.raises(TimeoutError):
            await orc.run()

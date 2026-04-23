from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
import pytest_asyncio

from council.orchestration.barrier import FilesystemBarrier
from council.orchestration.orchestrator import AsyncOrchestrator
from council.orchestration.state_machine import AgentState, AgentStateMachine


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
        barrier = FilesystemBarrier(
            discussion_dir, agents, timeout=0.5, poll_interval=0.1
        )

        with pytest.raises(TimeoutError):
            await barrier.wait(1)

    @pytest.mark.asyncio
    async def test_wait_with_delayed_files(self, temp_workspace: Path) -> None:
        discussion_dir = temp_workspace / "shared" / "discussion"
        agents = ["marcus", "elena"]
        barrier = FilesystemBarrier(
            discussion_dir, agents, timeout=5.0, poll_interval=0.1
        )

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

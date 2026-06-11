from __future__ import annotations

from pathlib import Path

import pytest

from council.config.schema import CompanyConfig
from council.service import CouncilRunConfig, CouncilRunResult, CouncilService


class TestCouncilService:
    @pytest.mark.asyncio
    async def test_run_writes_artifacts_without_cli(
        self, sample_config: CompanyConfig, temp_workspace: Path, mock_provider
    ) -> None:
        service = CouncilService(mock_provider)
        config = CouncilRunConfig(
            company_config=sample_config,
            provider_name="mock",
            workspace=temp_workspace,
            rounds=1,
        )
        result = await service.run(config)

        assert isinstance(result, CouncilRunResult)
        assert result.rounds == 1
        assert result.agent_names == ["Marcus", "Elena", "Kai", "David"]
        # Discussion files for round 1 should exist for every agent.
        discussion = temp_workspace / "shared" / "discussion"
        round_files = list(discussion.glob("*_round_1.md"))
        assert len(round_files) == 4

    @pytest.mark.asyncio
    async def test_build_agents_uses_registry(
        self, sample_config: CompanyConfig, temp_workspace: Path, mock_provider
    ) -> None:
        service = CouncilService(mock_provider)
        config = CouncilRunConfig(
            company_config=sample_config,
            provider_name="mock",
            workspace=temp_workspace,
            rounds=1,
        )
        agents = service.build_agents(config)
        assert [a.name for a in agents] == ["Marcus", "Elena", "Kai", "David"]

    @pytest.mark.asyncio
    async def test_progress_callback_is_forwarded(
        self, sample_config: CompanyConfig, temp_workspace: Path, mock_provider
    ) -> None:
        events: list[tuple[str, str]] = []

        def cb(agent_name: str, state: str, **kwargs: object) -> None:
            events.append((agent_name, state))

        service = CouncilService(mock_provider, progress_callback=cb)
        config = CouncilRunConfig(
            company_config=sample_config,
            provider_name="mock",
            workspace=temp_workspace,
            rounds=1,
        )
        await service.run(config)
        assert events, "expected progress events to be emitted"
        assert {name for name, _ in events} == {"Marcus", "Elena", "Kai", "David"}

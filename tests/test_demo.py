from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from council.demo import (
    DemoProvider,
    get_scenario,
    list_scenarios,
    run_demo,
)
from council.llm.provider import LLMResponse


class TestScenarios:
    """Tests for demo scenario registry."""

    def test_list_scenarios_has_four(self) -> None:
        scenarios = list_scenarios()
        assert len(scenarios) == 4
        keys = {s.key for s in scenarios}
        assert keys == {"saas-launch", "ecommerce-rebrand", "fintech-scale", "healthcare-app"}

    def test_get_scenario_by_key(self) -> None:
        s = get_scenario("saas-launch")
        assert s.key == "saas-launch"
        assert "TaskFlow" in s.config.name

    def test_get_scenario_invalid_raises(self) -> None:
        with pytest.raises(KeyError):
            get_scenario("nonexistent")

    def test_scenario_config_valid(self) -> None:
        for s in list_scenarios():
            assert s.config.name
            assert s.config.product
            assert len(s.responses) == 4
            assert set(s.responses.keys()) == {"Marcus", "Elena", "Kai", "David"}


class TestDemoProvider:
    """Tests for DemoProvider mock LLM."""

    @pytest.fixture
    def provider(self) -> DemoProvider:
        return DemoProvider(
            {
                "Marcus": ["Marcus round 1", "Marcus round 2"],
                "Elena": ["Elena round 1"],
            }
        )

    @pytest.mark.asyncio
    async def test_returns_scripted_response(self, provider: DemoProvider) -> None:
        resp = await provider.generate(prompt="test", system="You are Marcus")
        assert resp.content == "Marcus round 1"
        assert resp.model == "demo"
        assert resp.cost_usd == 0.0

    @pytest.mark.asyncio
    async def test_tracks_calls(self, provider: DemoProvider) -> None:
        await provider.generate(prompt="p1", system="Marcus")
        await provider.generate(prompt="p2", system="Marcus")
        assert len(provider.calls) == 2
        assert provider.calls[0]["prompt"] == "p1"

    @pytest.mark.asyncio
    async def test_cycles_on_exhaustion(self, provider: DemoProvider) -> None:
        # Marcus has 2 entries; third call should repeat last
        await provider.generate(prompt="", system="Marcus")
        await provider.generate(prompt="", system="Marcus")
        resp = await provider.generate(prompt="", system="Marcus")
        assert resp.content == "Marcus round 2"

    @pytest.mark.asyncio
    async def test_fallback_when_agent_unknown(self, provider: DemoProvider) -> None:
        resp = await provider.generate(prompt="", system="UnknownAgent")
        assert resp.content == "Demo response"

    @pytest.mark.asyncio
    async def test_stream_yields_content(self, provider: DemoProvider) -> None:
        chunks = []
        async for chunk in provider.stream(prompt="", system="Marcus"):
            chunks.append(chunk)
        assert chunks == ["Marcus round 1"]


class TestRunDemo:
    """Integration tests for the full demo run."""

    @pytest.mark.asyncio
    async def test_run_demo_creates_round_files(self, tmp_path: Path) -> None:
        ws = tmp_path / "workspace"
        ws.mkdir()
        await run_demo("saas-launch", rounds=2, workspace=ws)

        discussion = ws / "shared" / "discussion"
        for agent in ("marcus", "elena", "kai", "david"):
            assert (discussion / f"{agent}_round_1.md").exists()
            assert (discussion / f"{agent}_round_2.md").exists()

    @pytest.mark.asyncio
    async def test_run_demo_creates_final_outputs(self, tmp_path: Path) -> None:
        ws = tmp_path / "workspace"
        ws.mkdir()
        results = await run_demo("ecommerce-rebrand", rounds=1, workspace=ws)

        assert "Marcus" in results
        assert "Elena" in results
        assert "Kai" in results
        assert "David" in results

        output_dir = ws / "output"
        assert (output_dir / "marcus_offer.md").exists()
        assert (output_dir / "elena_funnel.md").exists()
        assert (output_dir / "kai_copy.md").exists()
        assert (output_dir / "david_abm.md").exists()

    @pytest.mark.asyncio
    async def test_run_demo_content_has_markdown(self, tmp_path: Path) -> None:
        ws = tmp_path / "workspace"
        ws.mkdir()
        await run_demo("fintech-scale", rounds=1, workspace=ws)

        for agent in ("marcus", "elena", "kai", "david"):
            path = ws / "shared" / "discussion" / f"{agent}_round_1.md"
            text = path.read_text(encoding="utf-8")
            assert "#" in text  # markdown header

    @pytest.mark.asyncio
    async def test_run_demo_progress_callback(self, tmp_path: Path) -> None:
        ws = tmp_path / "workspace"
        ws.mkdir()
        events: list[tuple[str, str]] = []

        def callback(name: str, event: str, **kwargs: object) -> None:
            events.append((name, event))

        await run_demo("healthcare-app", rounds=1, workspace=ws, progress_callback=callback)

        # Should see at least generating/done events for each agent
        names = {n for n, _ in events}
        assert names == {"Marcus", "Elena", "Kai", "David"}

    @pytest.mark.asyncio
    async def test_run_demo_is_deterministic(self, tmp_path: Path) -> None:
        ws1 = tmp_path / "ws1"
        ws1.mkdir()
        ws2 = tmp_path / "ws2"
        ws2.mkdir()

        await run_demo("saas-launch", rounds=1, workspace=ws1)
        await run_demo("saas-launch", rounds=1, workspace=ws2)

        for agent in ("marcus", "elena", "kai", "david"):
            p1 = ws1 / "shared" / "discussion" / f"{agent}_round_1.md"
            p2 = ws2 / "shared" / "discussion" / f"{agent}_round_1.md"
            assert p1.read_text(encoding="utf-8") == p2.read_text(encoding="utf-8")


class TestDemoCLI:
    """Tests for CLI demo argument parsing."""

    def test_parse_demo_flag(self) -> None:
        from council.cli import parse_args

        args = parse_args(["--demo", "--scenario", "saas-launch", "--rounds", "2"])
        assert args.demo is True
        assert args.scenario == "saas-launch"
        assert args.rounds == 2
        assert args.config is None

    def test_parse_demo_allows_no_config(self) -> None:
        from council.cli import parse_args

        args = parse_args(["--demo"])
        assert args.demo is True
        assert args.config is None

    def test_parse_demo_rejects_invalid_scenario(self) -> None:
        from council.cli import parse_args

        with pytest.raises(SystemExit):
            parse_args(["--demo", "--scenario", "invalid"])

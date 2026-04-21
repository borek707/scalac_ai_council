from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from council.agents.base import BaseAgent, Brief, RoundContext
from council.agents.david import DavidAgent
from council.agents.elena import ElenaAgent
from council.agents.kai import KaiAgent
from council.agents.marcus import MarcusAgent
from council.config.schema import CompanyConfig
from council.llm.provider import LLMResponse
from council.orchestration.state_machine import AgentState
from tests.conftest import MockLLMProvider


class TestBaseAgent:
    """Tests for BaseAgent abstract class."""

    def test_init(self, temp_workspace: Path, sample_config: CompanyConfig) -> None:
        brief = Brief(workspace=temp_workspace)
        agent = MarcusAgent(brief=brief, config=sample_config)
        assert agent.name == "marcus"
        assert agent.role == "Senior Market Positioning Strategist"
        assert agent.state == AgentState.PENDING
        assert agent.workspace == temp_workspace

    def test_ensure_dirs(self, temp_workspace: Path, sample_config: CompanyConfig) -> None:
        brief = Brief(workspace=temp_workspace)
        agent = MarcusAgent(brief=brief, config=sample_config)
        agent._ensure_dirs()
        assert agent.discussion_dir.exists()
        assert agent.output_dir.exists()

    def test_write_round(self, temp_workspace: Path, sample_config: CompanyConfig) -> None:
        brief = Brief(workspace=temp_workspace)
        agent = MarcusAgent(brief=brief, config=sample_config)
        path = agent.write_round(1, "# Test content")
        assert path.exists()
        assert path.name == "round_1_marcus.md"
        assert "# Test content" in path.read_text(encoding="utf-8")

    def test_write_final(self, temp_workspace: Path, sample_config: CompanyConfig) -> None:
        brief = Brief(workspace=temp_workspace)
        agent = MarcusAgent(brief=brief, config=sample_config)
        path = agent.write_final("Final output", "final.md")
        assert path.exists()
        assert path.read_text(encoding="utf-8") == "Final output"

    def test_read_empty_discussion(self, temp_workspace: Path, sample_config: CompanyConfig) -> None:
        brief = Brief(workspace=temp_workspace)
        agent = MarcusAgent(brief=brief, config=sample_config)
        result = agent.read_discussion()
        assert result == ""

    def test_read_discussion_with_files(self, temp_workspace: Path, sample_config: CompanyConfig) -> None:
        brief = Brief(workspace=temp_workspace)
        agent = MarcusAgent(brief=brief, config=sample_config)
        agent.write_round(1, "Round 1 content")

        brief2 = Brief(workspace=temp_workspace)
        agent2 = ElenaAgent(brief=brief2, config=sample_config)
        result = agent2.read_discussion()
        assert "round_1_marcus.md" in result
        assert "Round 1 content" in result

    def test_read_brief_missing(self, temp_workspace: Path, sample_config: CompanyConfig) -> None:
        brief = Brief(workspace=temp_workspace)
        agent = MarcusAgent(brief=brief, config=sample_config)
        result = agent.read_brief()
        assert result == ""

    def test_read_brief_present(self, temp_workspace: Path, sample_config: CompanyConfig) -> None:
        brief_path = temp_workspace / "shared" / "brief.md"
        brief_path.parent.mkdir(parents=True, exist_ok=True)
        brief_path.write_text("Project brief content", encoding="utf-8")
        brief = Brief(workspace=temp_workspace)
        agent = MarcusAgent(brief=brief, config=sample_config)
        result = agent.read_brief()
        assert result == "Project brief content"

    @pytest.mark.asyncio
    async def test_run_round_with_mock(
        self,
        temp_workspace: Path,
        sample_config: CompanyConfig,
        mock_provider: MockLLMProvider,
    ) -> None:
        brief = Brief(workspace=temp_workspace)
        agent = MarcusAgent(brief=brief, config=sample_config, provider=mock_provider)
        path = await agent.run_round(1)
        assert path.exists()
        assert path.name == "round_1_marcus.md"
        assert agent.state == AgentState.DONE

    @pytest.mark.asyncio
    async def test_run_round_state_transitions(
        self,
        temp_workspace: Path,
        sample_config: CompanyConfig,
    ) -> None:
        brief = Brief(workspace=temp_workspace)
        agent = MarcusAgent(brief=brief, config=sample_config)
        assert agent.state == AgentState.PENDING
        await agent.run_round(1)
        assert agent.state == AgentState.DONE

    @pytest.mark.asyncio
    async def test_generate_round_without_provider(
        self,
        temp_workspace: Path,
        sample_config: CompanyConfig,
    ) -> None:
        brief = Brief(workspace=temp_workspace)
        agent = MarcusAgent(brief=brief, config=sample_config)
        ctx = RoundContext(
            round_num=1,
            brief="test brief",
            discussion_history="",
            company_config=sample_config,
        )
        content = await agent.generate_round(ctx)
        assert "Marcus" in content
        assert "Round 1" in content

    @pytest.mark.asyncio
    async def test_run_round_error_state(
        self,
        temp_workspace: Path,
        sample_config: CompanyConfig,
    ) -> None:
        class BrokenAgent(BaseAgent):
            def get_system_prompt(self) -> str:
                return "broken"

            def get_output_filename(self) -> str:
                return "broken.md"

            async def generate_round(self, ctx: RoundContext) -> str:
                raise RuntimeError("Simulated failure")

        brief = Brief(workspace=temp_workspace)
        agent = BrokenAgent(brief=brief, config=sample_config)
        assert agent.state == AgentState.PENDING
        with pytest.raises(RuntimeError):
            await agent.run_round(1)
        assert agent.state == AgentState.ERROR

    def test_abstract_methods(self) -> None:
        with pytest.raises(TypeError):
            BaseAgent("test", "role", Brief(), CompanyConfig(name="Test", product="P"))


class TestMarcusAgent:
    """Tests for MarcusAgent."""

    def test_system_prompt(self, temp_workspace: Path, sample_config: CompanyConfig) -> None:
        brief = Brief(workspace=temp_workspace)
        agent = MarcusAgent(brief=brief, config=sample_config)
        prompt = agent.get_system_prompt()
        assert "Marcus" in prompt
        assert "Market Positioning Strategist" in prompt

    def test_output_filename(self, temp_workspace: Path, sample_config: CompanyConfig) -> None:
        brief = Brief(workspace=temp_workspace)
        agent = MarcusAgent(brief=brief, config=sample_config)
        assert agent.get_output_filename() == "marcus_strategy.md"

    @pytest.mark.asyncio
    async def test_generate_with_provider(
        self,
        temp_workspace: Path,
        sample_config: CompanyConfig,
        mock_provider: MockLLMProvider,
    ) -> None:
        brief = Brief(workspace=temp_workspace)
        agent = MarcusAgent(brief=brief, config=sample_config, provider=mock_provider)
        ctx = RoundContext(
            round_num=1, brief="", discussion_history="",
            company_config=sample_config,
        )
        content = await agent.generate_round(ctx)
        assert "Mock response" in content
        assert len(mock_provider.calls) == 1


class TestElenaAgent:
    """Tests for ElenaAgent."""

    def test_system_prompt(self, temp_workspace: Path, sample_config: CompanyConfig) -> None:
        brief = Brief(workspace=temp_workspace)
        agent = ElenaAgent(brief=brief, config=sample_config)
        prompt = agent.get_system_prompt()
        assert "Elena" in prompt
        assert "Content Marketing Director" in prompt

    def test_output_filename(self, temp_workspace: Path, sample_config: CompanyConfig) -> None:
        brief = Brief(workspace=temp_workspace)
        agent = ElenaAgent(brief=brief, config=sample_config)
        assert agent.get_output_filename() == "elena_content_strategy.md"


class TestKaiAgent:
    """Tests for KaiAgent."""

    def test_system_prompt(self, temp_workspace: Path, sample_config: CompanyConfig) -> None:
        brief = Brief(workspace=temp_workspace)
        agent = KaiAgent(brief=brief, config=sample_config)
        prompt = agent.get_system_prompt()
        assert "Kai" in prompt
        assert "Growth Marketing Manager" in prompt

    def test_output_filename(self, temp_workspace: Path, sample_config: CompanyConfig) -> None:
        brief = Brief(workspace=temp_workspace)
        agent = KaiAgent(brief=brief, config=sample_config)
        assert agent.get_output_filename() == "kai_growth_strategy.md"


class TestDavidAgent:
    """Tests for DavidAgent."""

    def test_system_prompt(self, temp_workspace: Path, sample_config: CompanyConfig) -> None:
        brief = Brief(workspace=temp_workspace)
        agent = DavidAgent(brief=brief, config=sample_config)
        prompt = agent.get_system_prompt()
        assert "David" in prompt
        assert "Sales Enablement Lead" in prompt

    def test_output_filename(self, temp_workspace: Path, sample_config: CompanyConfig) -> None:
        brief = Brief(workspace=temp_workspace)
        agent = DavidAgent(brief=brief, config=sample_config)
        assert agent.get_output_filename() == "david_sales_enablement.md"

    @pytest.mark.asyncio
    async def test_generate_round_with_provider(
        self,
        temp_workspace: Path,
        sample_config: CompanyConfig,
        mock_provider: MockLLMProvider,
    ) -> None:
        brief = Brief(workspace=temp_workspace)
        agent = DavidAgent(brief=brief, config=sample_config, provider=mock_provider)
        ctx = RoundContext(
            round_num=2, brief="", discussion_history="",
            company_config=sample_config,
        )
        content = await agent.generate_round(ctx)
        assert "Mock response" in content


class TestAgentRoundContext:
    """Tests for RoundContext dataclass."""

    def test_context_creation(self, sample_config: CompanyConfig) -> None:
        ctx = RoundContext(
            round_num=1,
            brief="Test brief",
            discussion_history="Previous rounds",
            company_config=sample_config,
            battlecards="Competitor data",
        )
        assert ctx.round_num == 1
        assert ctx.brief == "Test brief"
        assert ctx.discussion_history == "Previous rounds"
        assert ctx.battlecards == "Competitor data"
        assert ctx.content_plan == ""

    def test_context_defaults(self, sample_config: CompanyConfig) -> None:
        ctx = RoundContext(
            round_num=1,
            brief="",
            discussion_history="",
            company_config=sample_config,
        )
        assert ctx.battlecards == ""
        assert ctx.content_plan == ""
        assert ctx.target_accounts == ""


class TestBrief:
    """Tests for Brief dataclass."""

    def test_default_workspace(self) -> None:
        brief = Brief()
        assert brief.workspace == Path("./output")

    def test_custom_workspace(self, tmp_path: Path) -> None:
        brief = Brief(workspace=tmp_path / "custom")
        assert brief.workspace == tmp_path / "custom"

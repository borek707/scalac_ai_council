from __future__ import annotations

from pathlib import Path

import pytest

from council.agents.base import BaseAgent
from council.agents.david import DavidAgent
from council.agents.elena import ElenaAgent
from council.agents.kai import KaiAgent
from council.agents.marcus import MarcusAgent
from council.config.documents import Document
from council.config.schema import CompanyConfig, RoundContext
from council.llm.provider import LLMResponse
from council.orchestration.state_machine import AgentState
from tests.conftest import MockLLMProvider


class TestBaseAgent:
    """Tests for BaseAgent abstract class."""

    def test_init(
        self, temp_workspace: Path, sample_config: CompanyConfig, mock_provider: MockLLMProvider
    ) -> None:
        workspace = temp_workspace
        agent = MarcusAgent(workspace=workspace, config=sample_config, provider=mock_provider)
        assert agent.name == "Marcus"
        assert agent.role == "Offer Architect"
        assert agent.state == AgentState.PENDING
        assert agent.workspace == temp_workspace

    def test_ensure_dirs(
        self, temp_workspace: Path, sample_config: CompanyConfig, mock_provider: MockLLMProvider
    ) -> None:
        workspace = temp_workspace
        agent = MarcusAgent(workspace=workspace, config=sample_config, provider=mock_provider)
        agent._ensure_dirs()
        assert agent.discussion_dir.exists()
        assert agent.output_dir.exists()

    def test_write_round(
        self, temp_workspace: Path, sample_config: CompanyConfig, mock_provider: MockLLMProvider
    ) -> None:
        workspace = temp_workspace
        agent = MarcusAgent(workspace=workspace, config=sample_config, provider=mock_provider)
        path = agent.write_round(1, "# Test content")
        assert path.exists()
        assert path.name == "marcus_round_1.md"
        assert "# Test content" in path.read_text(encoding="utf-8")

    def test_write_final(
        self, temp_workspace: Path, sample_config: CompanyConfig, mock_provider: MockLLMProvider
    ) -> None:
        workspace = temp_workspace
        agent = MarcusAgent(workspace=workspace, config=sample_config, provider=mock_provider)
        path = agent.write_final("Final output", "final.md")
        assert path.exists()
        assert path.read_text(encoding="utf-8") == "Final output"

    def test_read_empty_discussion(
        self, temp_workspace: Path, sample_config: CompanyConfig, mock_provider: MockLLMProvider
    ) -> None:
        workspace = temp_workspace
        agent = MarcusAgent(workspace=workspace, config=sample_config, provider=mock_provider)
        result = agent.read_discussion()
        assert result == ""

    def test_read_discussion_with_files(
        self, temp_workspace: Path, sample_config: CompanyConfig, mock_provider: MockLLMProvider
    ) -> None:
        workspace = temp_workspace
        agent = MarcusAgent(workspace=workspace, config=sample_config, provider=mock_provider)
        agent.write_round(1, "Round 1 content")

        workspace2 = temp_workspace
        agent2 = ElenaAgent(workspace=workspace2, config=sample_config, provider=mock_provider)
        result = agent2.read_discussion()
        assert "Round 1 content" in result

    def test_read_discussion_skips_stale_files_from_previous_run(
        self, temp_workspace: Path, sample_config: CompanyConfig, mock_provider: MockLLMProvider
    ) -> None:
        """Files older than the .run_started_at marker must be ignored."""
        import os
        import time

        workspace = temp_workspace
        agent = MarcusAgent(workspace=workspace, config=sample_config, provider=mock_provider)

        stale_path = agent.write_round(1, "Stale content from a previous run")
        old_time = time.time() - 3600
        os.utime(stale_path, (old_time, old_time))

        marker = workspace / "shared" / ".run_started_at"
        marker.write_text(str(time.time() - 60), encoding="utf-8")

        agent.write_round(2, "Fresh content from current run")

        result = agent.read_discussion()
        assert "Fresh content from current run" in result
        assert "Stale content from a previous run" not in result

    def test_read_discussion_without_marker_reads_everything(
        self, temp_workspace: Path, sample_config: CompanyConfig, mock_provider: MockLLMProvider
    ) -> None:
        """Backward compat: no marker means no mtime filtering."""
        workspace = temp_workspace
        agent = MarcusAgent(workspace=workspace, config=sample_config, provider=mock_provider)
        agent.write_round(1, "Some round content")
        assert "Some round content" in agent.read_discussion()

    def test_read_discussion_respects_max_round_exclusive(
        self, temp_workspace: Path, sample_config: CompanyConfig, mock_provider: MockLLMProvider
    ) -> None:
        """Round N context must only include rounds < N."""
        workspace = temp_workspace
        agent = MarcusAgent(workspace=workspace, config=sample_config, provider=mock_provider)
        agent.write_round(1, "Round one content")
        agent.write_round(2, "Round two content")
        agent.write_round(3, "Round three content")

        result = agent.read_discussion(max_round_exclusive=3)
        assert "Round one content" in result
        assert "Round two content" in result
        assert "Round three content" not in result

        # No cap → everything
        full = agent.read_discussion()
        assert "Round three content" in full

    def test_parse_round_number(
        self, temp_workspace: Path, sample_config: CompanyConfig, mock_provider: MockLLMProvider
    ) -> None:
        from council.agents.base import BaseAgent

        assert BaseAgent._parse_round_number("marcus_round_1.md") == 1
        assert BaseAgent._parse_round_number("elena_round_12.md") == 12
        assert BaseAgent._parse_round_number("weird_file.md") is None

    def test_read_brief_missing(
        self, temp_workspace: Path, sample_config: CompanyConfig, mock_provider: MockLLMProvider
    ) -> None:
        workspace = temp_workspace
        agent = MarcusAgent(workspace=workspace, config=sample_config, provider=mock_provider)
        result = agent.read_brief()
        assert result == ""

    def test_read_brief_present(
        self, temp_workspace: Path, sample_config: CompanyConfig, mock_provider: MockLLMProvider
    ) -> None:
        brief_path = temp_workspace / "shared" / "brief.md"
        brief_path.parent.mkdir(parents=True, exist_ok=True)
        brief_path.write_text("Project brief content", encoding="utf-8")
        workspace = temp_workspace
        agent = MarcusAgent(workspace=workspace, config=sample_config, provider=mock_provider)
        result = agent.read_brief()
        assert result == "Project brief content"

    @pytest.mark.asyncio
    async def test_run_round_with_mock(
        self,
        temp_workspace: Path,
        sample_config: CompanyConfig,
        mock_provider: MockLLMProvider,
    ) -> None:
        workspace = temp_workspace
        agent = MarcusAgent(workspace=workspace, config=sample_config, provider=mock_provider)
        path = await agent.run_round(1)
        assert path.exists()
        assert path.name == "marcus_round_1.md"
        assert agent.state == AgentState.DONE

    @pytest.mark.asyncio
    async def test_run_round_state_transitions(
        self,
        temp_workspace: Path,
        sample_config: CompanyConfig,
        mock_provider: MockLLMProvider,
    ) -> None:
        workspace = temp_workspace
        agent = MarcusAgent(workspace=workspace, config=sample_config, provider=mock_provider)
        assert agent.state == AgentState.PENDING
        await agent.run_round(1)
        assert agent.state == AgentState.DONE

    @pytest.mark.asyncio
    async def test_generate_round_without_provider(
        self,
        temp_workspace: Path,
        sample_config: CompanyConfig,
        mock_provider: MockLLMProvider,
    ) -> None:
        workspace = temp_workspace
        agent = MarcusAgent(workspace=workspace, config=sample_config, provider=mock_provider)
        ctx = RoundContext(
            round_num=1,
            brief="",
            discussion_history="",
            company_config=sample_config,
        )
        content = await agent.generate_round(ctx)
        assert "Mock response" in content
        assert "call #1" in content

    @pytest.mark.asyncio
    async def test_run_round_error_state(
        self,
        temp_workspace: Path,
        sample_config: CompanyConfig,
        mock_provider: MockLLMProvider,
    ) -> None:
        class BrokenAgent(BaseAgent):
            def __init__(self, workspace, config, provider):
                super().__init__(
                    name="broken",
                    role="broken role",
                    workspace=workspace,
                    config=config,
                    provider=provider,
                )

            def get_system_prompt(self) -> str:
                return "broken"

            def get_output_filename(self) -> str:
                return "broken.md"

            def get_template_name(self) -> str:
                return "broken.j2"

            async def generate_round(self, ctx: RoundContext) -> str:
                raise RuntimeError("Simulated failure")

        workspace = temp_workspace
        agent = BrokenAgent(workspace=workspace, config=sample_config, provider=mock_provider)
        assert agent.state == AgentState.PENDING
        with pytest.raises(RuntimeError):
            await agent.run_round(1)
        assert agent.state == AgentState.ERROR

    def test_abstract_methods(self, mock_provider: MockLLMProvider) -> None:
        with pytest.raises(TypeError):
            BaseAgent(
                "test", "role", Path("/tmp"), CompanyConfig(name="Test", product="P"), mock_provider
            )

    @pytest.mark.asyncio
    async def test_documents_appear_in_prompt(
        self,
        temp_workspace: Path,
        sample_config: CompanyConfig,
        mock_provider: MockLLMProvider,
    ) -> None:
        """#9 — Document content must appear in the rendered prompt sent to the LLM."""
        doc = Document(
            name="secret_doc",
            path=Path("inline://secret_doc.md"),
            content="SECRET_MARKER_TEXT",
            doc_type="brief",
        )
        agent = MarcusAgent(
            workspace=temp_workspace,
            config=sample_config,
            provider=mock_provider,
            documents=[doc],
        )
        ctx = RoundContext(
            round_num=1,
            brief="",
            discussion_history="",
            company_config=sample_config,
        )
        await agent.generate_round(ctx)
        assert mock_provider.calls, "provider should have been called"
        sent_prompt = mock_provider.calls[-1]["prompt"]
        assert "SECRET_MARKER_TEXT" in sent_prompt

    @pytest.mark.asyncio
    async def test_empty_response_raises_value_error(
        self,
        temp_workspace: Path,
        sample_config: CompanyConfig,
        mock_provider: MockLLMProvider,
    ) -> None:
        """#21 — Empty LLM response must raise ValueError."""
        from collections.abc import AsyncGenerator as _AG

        from council.llm.provider import LLMProvider, LLMResponse

        class EmptyProvider(LLMProvider):
            async def generate(
                self, prompt, model=None, temperature=0.7, max_tokens=4000, system=None
            ) -> LLMResponse:
                return LLMResponse(content="", model="mock-model")

            async def stream(
                self, prompt, model=None, temperature=0.7, max_tokens=4000, system=None
            ) -> _AG[str, None]:
                return
                yield  # pragma: no cover — make this an async generator

        agent = MarcusAgent(
            workspace=temp_workspace,
            config=sample_config,
            provider=EmptyProvider(),
        )
        with pytest.raises(ValueError):
            await agent.run_round(1)

    @pytest.mark.asyncio
    async def test_whitespace_only_response_raises(
        self,
        temp_workspace: Path,
        sample_config: CompanyConfig,
        mock_provider: MockLLMProvider,
    ) -> None:
        """#21 — Whitespace-only LLM response must also raise ValueError."""
        from collections.abc import AsyncGenerator as _AG

        from council.llm.provider import LLMProvider, LLMResponse

        class WhitespaceProvider(LLMProvider):
            async def generate(
                self, prompt, model=None, temperature=0.7, max_tokens=4000, system=None
            ) -> LLMResponse:
                return LLMResponse(content="   \n  ", model="mock-model")

            async def stream(
                self, prompt, model=None, temperature=0.7, max_tokens=4000, system=None
            ) -> _AG[str, None]:
                return
                yield  # pragma: no cover — make this an async generator

        agent = MarcusAgent(
            workspace=temp_workspace,
            config=sample_config,
            provider=WhitespaceProvider(),
        )
        with pytest.raises(ValueError):
            await agent.run_round(1)


class TestMarcusAgent:
    """Tests for MarcusAgent."""

    def test_system_prompt(
        self, temp_workspace: Path, sample_config: CompanyConfig, mock_provider: MockLLMProvider
    ) -> None:
        workspace = temp_workspace
        agent = MarcusAgent(workspace=workspace, config=sample_config, provider=mock_provider)
        prompt = agent.get_system_prompt()
        assert "Marcus" in prompt
        assert "Offer Architect" in prompt

    def test_output_filename(
        self, temp_workspace: Path, sample_config: CompanyConfig, mock_provider: MockLLMProvider
    ) -> None:
        workspace = temp_workspace
        agent = MarcusAgent(workspace=workspace, config=sample_config, provider=mock_provider)
        assert agent.get_output_filename() == "marcus_offer.md"

    @pytest.mark.asyncio
    async def test_generate_with_provider(
        self,
        temp_workspace: Path,
        sample_config: CompanyConfig,
        mock_provider: MockLLMProvider,
    ) -> None:
        workspace = temp_workspace
        agent = MarcusAgent(workspace=workspace, config=sample_config, provider=mock_provider)
        ctx = RoundContext(
            round_num=1,
            brief="",
            discussion_history="",
            company_config=sample_config,
        )
        content = await agent.generate_round(ctx)
        assert "Mock response" in content
        assert len(mock_provider.calls) == 1


class TestElenaAgent:
    """Tests for ElenaAgent."""

    def test_system_prompt(
        self, temp_workspace: Path, sample_config: CompanyConfig, mock_provider: MockLLMProvider
    ) -> None:
        workspace = temp_workspace
        agent = ElenaAgent(workspace=workspace, config=sample_config, provider=mock_provider)
        prompt = agent.get_system_prompt()
        assert "Elena" in prompt
        assert "Funnel Architect" in prompt

    def test_output_filename(
        self, temp_workspace: Path, sample_config: CompanyConfig, mock_provider: MockLLMProvider
    ) -> None:
        workspace = temp_workspace
        agent = ElenaAgent(workspace=workspace, config=sample_config, provider=mock_provider)
        assert agent.get_output_filename() == "elena_funnel.md"


class TestKaiAgent:
    """Tests for KaiAgent."""

    def test_system_prompt(
        self, temp_workspace: Path, sample_config: CompanyConfig, mock_provider: MockLLMProvider
    ) -> None:
        workspace = temp_workspace
        agent = KaiAgent(workspace=workspace, config=sample_config, provider=mock_provider)
        prompt = agent.get_system_prompt()
        assert "Kai" in prompt
        assert "copywriter" in prompt.lower()

    def test_output_filename(
        self, temp_workspace: Path, sample_config: CompanyConfig, mock_provider: MockLLMProvider
    ) -> None:
        workspace = temp_workspace
        agent = KaiAgent(workspace=workspace, config=sample_config, provider=mock_provider)
        assert agent.get_output_filename() == "kai_copy.md"


class TestDavidAgent:
    """Tests for DavidAgent."""

    def test_system_prompt(
        self, temp_workspace: Path, sample_config: CompanyConfig, mock_provider: MockLLMProvider
    ) -> None:
        workspace = temp_workspace
        agent = DavidAgent(workspace=workspace, config=sample_config, provider=mock_provider)
        prompt = agent.get_system_prompt()
        assert "David" in prompt
        assert "lead generation" in prompt.lower()

    def test_output_filename(
        self, temp_workspace: Path, sample_config: CompanyConfig, mock_provider: MockLLMProvider
    ) -> None:
        workspace = temp_workspace
        agent = DavidAgent(workspace=workspace, config=sample_config, provider=mock_provider)
        assert agent.get_output_filename() == "david_abm.md"

    @pytest.mark.asyncio
    async def test_generate_round_with_provider(
        self,
        temp_workspace: Path,
        sample_config: CompanyConfig,
        mock_provider: MockLLMProvider,
    ) -> None:
        workspace = temp_workspace
        agent = DavidAgent(workspace=workspace, config=sample_config, provider=mock_provider)
        ctx = RoundContext(
            round_num=2,
            brief="",
            discussion_history="",
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

    def test_context_is_frozen(self, sample_config: CompanyConfig) -> None:
        import dataclasses

        ctx = RoundContext(
            round_num=1,
            brief="",
            discussion_history="",
            company_config=sample_config,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            ctx.round_num = 2  # type: ignore[misc]

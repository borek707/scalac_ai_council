from __future__ import annotations

from pathlib import Path

from council.agents.base import BaseAgent
from council.agents.registry import (
    AGENT_REGISTRY,
    AgentSpec,
    agent_names,
    agent_specs,
    build_agents,
    final_filenames,
)
from council.config.schema import CompanyConfig


class TestAgentRegistry:
    def test_canonical_agent_order(self) -> None:
        assert agent_names() == ["Marcus", "Elena", "Kai", "David"]

    def test_specs_match_names(self) -> None:
        specs = agent_specs()
        assert [s.name for s in specs] == agent_names()
        assert all(isinstance(s, AgentSpec) for s in specs)

    def test_keys_are_lowercase(self) -> None:
        assert AGENT_REGISTRY["Marcus"].key == "marcus"

    def test_final_filenames_mapping(self) -> None:
        mapping = final_filenames()
        assert mapping["Marcus"] == "marcus_offer.md"
        assert mapping["Elena"] == "elena_funnel.md"
        assert mapping["Kai"] == "kai_copy.md"
        assert mapping["David"] == "david_abm.md"

    def test_load_class_returns_baseagent_subclass(self) -> None:
        for spec in agent_specs():
            cls = spec.load_class()
            assert issubclass(cls, BaseAgent)
            assert cls.__name__ == spec.class_name

    def test_build_agents_constructs_all_in_order(
        self, sample_config: CompanyConfig, temp_workspace: Path, mock_provider
    ) -> None:
        agents = build_agents(temp_workspace, sample_config, mock_provider)
        assert [a.name for a in agents] == agent_names()
        assert all(a.provider is mock_provider for a in agents)

    def test_build_agents_sets_stream_flag(
        self, sample_config: CompanyConfig, temp_workspace: Path, mock_provider
    ) -> None:
        agents = build_agents(temp_workspace, sample_config, mock_provider, stream_output=True)
        assert all(a.stream_output for a in agents)

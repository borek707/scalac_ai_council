from __future__ import annotations

from pathlib import Path

import pytest

from council.config.schema import CompanyConfig
from council.prompts.generator import PromptGenerator


class TestPromptGenerator:
    """Tests for PromptGenerator."""

    @pytest.fixture
    def template_dir(self, tmp_path: Path) -> Path:
        """Create a temporary template directory with test templates."""
        templates = tmp_path / "templates"
        templates.mkdir()

        # Create a test template
        (templates / "test_agent.j2").write_text(
            "Company: {{ company.name }}\n"
            "Product: {{ company.product }}\n"
            "Round: {{ round }}\n"
            "{% if is_first_round %}First round!{% endif %}\n"
            "{% if discussion_history %}History: {{ discussion_history }}{% endif %}\n",
            encoding="utf-8",
        )

        # Create a template that uses all context fields
        (templates / "full_agent.j2").write_text(
            "# {{ company.name }} — Round {{ round }}\n"
            "\n"
            "Pricing: {{ company.pricing_tier }}\n"
            "Value Prop: {{ company.value_proposition }}\n"
            "Differentiators: {{ company.differentiators | join(', ') }}\n"
            "Competitors: {% for c in company.competitors %}{{ c.name }} {% endfor %}\n"
            "Target: {{ company.target.segment }}\n"
            "Timeline: {{ company.constraints.timeline_days }} days\n"
            "Budget: {{ company.constraints.budget_pln }} PLN\n"
            "Case Studies: {% for cs in company.case_studies %}{{ cs.name }} {% endfor %}\n",
            encoding="utf-8",
        )

        # Create template with missing-field handling
        (templates / "safe_agent.j2").write_text(
            "Company: {{ company.name | default('Unknown') }}\n",
            encoding="utf-8",
        )

        return templates

    @pytest.fixture
    def generator(self, template_dir: Path) -> PromptGenerator:
        return PromptGenerator(template_dir)

    def test_init_creates_directory(self, tmp_path: Path) -> None:
        new_dir = tmp_path / "new_templates"
        assert not new_dir.exists()
        PromptGenerator(new_dir)
        assert new_dir.exists()

    def test_generate_basic_prompt(
        self,
        generator: PromptGenerator,
        sample_config: CompanyConfig,
    ) -> None:
        result = generator.generate_agent_prompt(
            agent_name="test_agent",
            company_config=sample_config,
            round_num=1,
        )
        assert "TestCorp" in result
        assert "AI-Powered Analytics Platform" in result
        assert "Round: 1" in result
        assert "First round!" in result

    def test_generate_with_history(
        self,
        generator: PromptGenerator,
        sample_config: CompanyConfig,
    ) -> None:
        result = generator.generate_agent_prompt(
            agent_name="test_agent",
            company_config=sample_config,
            round_num=2,
            discussion_history="Previous discussion here",
        )
        assert "TestCorp" in result
        assert "Round: 2" in result
        assert "History: Previous discussion here" in result

    def test_generate_full_context(
        self,
        generator: PromptGenerator,
        sample_config: CompanyConfig,
    ) -> None:
        result = generator.generate_agent_prompt(
            agent_name="full_agent",
            company_config=sample_config,
            round_num=1,
        )
        assert "TestCorp" in result
        assert "Enterprise" in result
        assert "Real-time insights" in result
        assert "Speed, Ease of use, API-first" in result
        assert "CompetitorX CompetitorY" in result
        assert "Enterprise Data Teams" in result
        assert "90 days" in result
        assert "100000 PLN" in result
        assert "ClientA" in result

    def test_generate_missing_template_fallback(
        self,
        generator: PromptGenerator,
        sample_config: CompanyConfig,
    ) -> None:
        """When template is missing, fallback template should be used."""
        result = generator.generate_agent_prompt(
            agent_name="nonexistent_agent",
            company_config=sample_config,
            round_num=1,
        )
        assert "TestCorp" in result
        assert "AI-Powered Analytics Platform" in result
        assert "Round 1" in result

    def test_generate_safe_defaults(
        self,
        generator: PromptGenerator,
        sample_config: CompanyConfig,
    ) -> None:
        result = generator.generate_agent_prompt(
            agent_name="safe_agent",
            company_config=sample_config,
            round_num=1,
        )
        assert "Company: TestCorp" in result

    def test_load_template(self, generator: PromptGenerator) -> None:
        template = generator._load_template("test_agent")
        assert template is not None

    def test_build_context(
        self,
        generator: PromptGenerator,
        sample_config: CompanyConfig,
    ) -> None:
        ctx = generator._build_context(sample_config, 2, "some history")
        assert ctx["company"]["name"] == "TestCorp"
        assert ctx["company"]["product"] == "AI-Powered Analytics Platform"
        assert ctx["round"] == 2
        assert ctx["discussion_history"] == "some history"
        assert ctx["is_first_round"] is False
        assert ctx["is_final_round"] is False
        assert isinstance(ctx["company"]["competitors"], list)
        assert isinstance(ctx["company"]["target"], dict)
        assert isinstance(ctx["company"]["constraints"], dict)

    def test_build_context_with_case_studies(
        self,
        generator: PromptGenerator,
        sample_config: CompanyConfig,
    ) -> None:
        ctx = generator._build_context(sample_config, 1)
        assert ctx["company"]["case_studies"] == [
            {"name": "ClientA", "result": "3x ROI in 6 months"},
        ]

    def test_generate_different_rounds(
        self,
        generator: PromptGenerator,
        sample_config: CompanyConfig,
    ) -> None:
        r1 = generator.generate_agent_prompt("test_agent", sample_config, 1)
        r2 = generator.generate_agent_prompt("test_agent", sample_config, 2)
        assert "First round!" in r1
        assert "First round!" not in r2

    def test_fallback_template_structure(self, generator: PromptGenerator) -> None:
        fallback = generator._fallback_template("my_agent")
        assert "my_agent" in fallback
        assert "company.name" in fallback
        assert "company.product" in fallback

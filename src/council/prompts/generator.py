from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, Template

from council.config.schema import CompanyConfig

logger = logging.getLogger(__name__)


class PromptGenerator:
    """Generates prompts for agents using Jinja2 templates."""

    def __init__(self, template_dir: Path) -> None:
        self.template_dir = template_dir
        if not self.template_dir.exists():
            self.template_dir.mkdir(parents=True, exist_ok=True)
            logger.warning(
                "Template directory %s did not exist, created it",
                self.template_dir,
            )
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate_agent_prompt(
        self,
        agent_name: str,
        company_config: CompanyConfig,
        round_num: int,
        discussion_history: str = "",
    ) -> str:
        """Generate a prompt for the specified agent.

        Args:
            agent_name: Name of the agent (e.g., 'marcus', 'elena').
            company_config: The company configuration.
            round_num: Current round number (1-based).
            discussion_history: Previous discussion content.

        Returns:
            Rendered prompt string.
        """
        template = self._load_template(agent_name)
        context = self._build_context(company_config, round_num, discussion_history)
        return template.render(**context)

    def _load_template(self, agent_name: str) -> Template:
        """Load a Jinja2 template for the specified agent."""
        template_file = f"{agent_name.lower()}.j2"
        try:
            return self.env.get_template(template_file)
        except Exception as exc:
            logger.warning(
                "Template %s not found, using fallback. Error: %s",
                template_file,
                exc,
            )
            return self.env.from_string(self._fallback_template(agent_name))

    def _build_context(
        self,
        company_config: CompanyConfig,
        round_num: int,
        discussion_history: str = "",
    ) -> dict[str, object]:
        """Build the template context from company configuration."""
        return {
            "company": {
                "name": company_config.name,
                "product": company_config.product,
                "pricing_tier": company_config.pricing_tier,
                "value_proposition": company_config.value_proposition,
                "differentiators": company_config.differentiators,
                "competitors": [
                    c.model_dump() for c in company_config.competitors
                ],
                "target": company_config.target.model_dump(),
                "constraints": company_config.constraints.model_dump(),
                "case_studies": company_config.case_studies,
            },
            "round": round_num,
            "discussion_history": discussion_history,
            "is_first_round": round_num == 1,
            "is_final_round": False,  # Set by caller if needed
        }

    def _fallback_template(self, agent_name: str) -> str:
        """Return a fallback template when a specific one is not found."""
        return """# {{ company.name }} — Round {{ round }}

You are {{ agent_name }}, an expert marketing strategist.

## Company Context
- **Company:** {{ company.name }}
- **Product:** {{ company.product }}
- **Value Proposition:** {{ company.value_proposition }}
{% if company.differentiators %}
- **Differentiators:** {{ company.differentiators | join(", ") }}
{% endif %}

{% if discussion_history %}
## Previous Discussion
{{ discussion_history }}
{% endif %}

Please provide your strategic recommendations for this round.
"""

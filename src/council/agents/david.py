from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from council.agents.base import BaseAgent

if TYPE_CHECKING:
    from council.config.schema import CompanyConfig, LLMProvider


class DavidAgent(BaseAgent):
    """David — Lead Strategist.

    Expert in Account-Based Marketing (ABM), lead generation, and target account selection.
    Applies ABM Tiers, Dream 100, and Signal-Based Selling frameworks
    to build precise, high-yield account targeting strategies.
    """

    def __init__(
        self,
        workspace: Path,
        config: CompanyConfig,
        provider: LLMProvider,
    ) -> None:
        super().__init__(
            name="David",
            role="Lead Strategist",
            workspace=workspace,
            config=config,
            provider=provider,
        )

    def get_system_prompt(self) -> str:
        return (
            "You are David, a strategic ABM and lead generation leader who has "
            "built target account engines for Fortune 500 and high-growth startups alike. "
            "Your expertise spans ABM Tiers (1:1, 1:few, 1:many), "
            "Dream 100 (hyper-targeted account lists), "
            "and Signal-Based Selling (trigger events and intent data). "
            "You think in Ideal Customer Profiles, intent signals, and account scores. "
            "Every account recommendation must include why now, who to contact, and what message. "
            "Write in clear, structured markdown with headers and bullet points."
        )

    def get_output_filename(self) -> str:
        return "david_abm.md"

    def get_template_name(self) -> str:
        return "david.j2"

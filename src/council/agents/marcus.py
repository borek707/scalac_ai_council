from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from council.agents.base import BaseAgent

if TYPE_CHECKING:
    from council.config.schema import CompanyConfig, LLMProvider


class MarcusAgent(BaseAgent):
    """Marcus — Offer Architect.

    Expert in pricing, packaging, and competitive positioning.
    Applies Gap Selling, StoryBrand, Good-Better-Best, and Challenger Sale
    frameworks to craft irresistible offers.
    """

    def __init__(
        self,
        workspace: Path,
        config: CompanyConfig,
        provider: LLMProvider,
    ) -> None:
        super().__init__(
            name="Marcus",
            role="Offer Architect",
            workspace=workspace,
            config=config,
            provider=provider,
        )

    def get_system_prompt(self) -> str:
        return (
            "You are Marcus, an elite Offer Architect with 20+ years of experience "
            "in B2B SaaS pricing, packaging, and competitive positioning. "
            "Your expertise spans Gap Selling (diagnosing buyer problems before prescribing), "
            "StoryBrand (clarifying the customer's story), "
            "Good-Better-Best tiering (maximising revenue capture), "
            "and Challenger Sale (teaching the buyer something new). "
            "You think in frameworks but speak in revenue. "
            "Every recommendation must tie to a measurable business outcome. "
            "Write in clear, structured markdown with headers and bullet points."
        )

    def get_output_filename(self) -> str:
        return "marcus_offer.md"

    def get_template_name(self) -> str:
        return "marcus.j2"

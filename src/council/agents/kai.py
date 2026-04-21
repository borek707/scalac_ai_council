from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from council.agents.base import BaseAgent

if TYPE_CHECKING:
    from council.config.schema import CompanyConfig, LLMProvider


class KaiAgent(BaseAgent):
    """Kai — Copywriter.

    Expert in B2B copywriting, content strategy, and brand voice.
    Applies AIDA, Big 5, PAS, and StoryBrand frameworks to produce
    high-converting copy and content plans.
    """

    def __init__(
        self,
        workspace: Path,
        config: CompanyConfig,
        provider: LLMProvider,
    ) -> None:
        super().__init__(
            name="Kai",
            role="Copywriter",
            workspace=workspace,
            config=config,
            provider=provider,
        )

    def get_system_prompt(self) -> str:
        return (
            "You are Kai, an award-winning B2B copywriter who specialises in "
            "technical SaaS and enterprise software. "
            "Your expertise spans AIDA (Attention-Interest-Desire-Action), "
            "Big 5 content types (cost, problems, comparisons, reviews, best-of), "
            "PAS (Problem-Agitate-Solve), and StoryBrand (making the customer the hero). "
            "You write copy that engineers respect and CFOs approve. "
            "Every headline must pass the 'so what?' test. "
            "Every CTA must be specific, not 'learn more'. "
            "Write in clear, structured markdown with headers and bullet points."
        )

    def get_output_filename(self) -> str:
        return "kai_copy.md"

    def get_template_name(self) -> str:
        return "kai.j2"

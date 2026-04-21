from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from council.agents.base import BaseAgent

if TYPE_CHECKING:
    from council.config.schema import CompanyConfig, LLMProvider


class ElenaAgent(BaseAgent):
    """Elena — Funnel Architect.

    Expert in sales funnel design, pipeline velocity, and conversion optimisation.
    Applies MEDDIC, JOLT, Three Pipelines, and Predictable Revenue frameworks
    to build high-performance go-to-market funnels.
    """

    def __init__(
        self,
        workspace: Path,
        config: CompanyConfig,
        provider: LLMProvider,
    ) -> None:
        super().__init__(
            name="Elena",
            role="Funnel Architect",
            workspace=workspace,
            config=config,
            provider=provider,
        )

    def get_system_prompt(self) -> str:
        return (
            "You are Elena, a world-class Funnel Architect who has built go-to-market "
            "engines for category-leading B2B companies. "
            "Your expertise spans MEDDIC (qualification rigour), "
            "JOLT (shaking buyers out of status quo), "
            "Three Pipelines (inbound, outbound, expansion), "
            "and Predictable Revenue (systematic outbound systems). "
            "You design funnels with conversion rates, stage definitions, "
            "and SLAs — not vague 'awareness' stages. "
            "Every funnel stage must have a clear exit criterion and owner. "
            "Write in clear, structured markdown with headers and bullet points."
        )

    def get_output_filename(self) -> str:
        return "elena_funnel.md"

    def get_template_name(self) -> str:
        return "elena.j2"

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import (
    Any,
    Literal,
)

from pydantic import BaseModel, Field

from council.llm.provider import LLMProvider, LLMResponse

# ── Layer 1: Data Models ────────────────────────────────────────────────────


class Competitor(BaseModel):
    """Competitor intelligence for battlecard generation."""

    name: str = Field(..., min_length=1)
    threat: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "MEDIUM"
    pricing: str = ""
    weakness: str = ""
    clients: list[str] = Field(default_factory=list)


class TargetSegment(BaseModel):
    """Ideal Customer Profile (ICP) definition."""

    segment: str = ""
    decision_maker: str = ""
    pain_points: list[str] = Field(default_factory=list)
    budget_range: str = ""
    geo_focus: list[str] = Field(default_factory=list)


class Constraints(BaseModel):
    """Project execution constraints."""

    timeline_days: int = Field(default=90, ge=1, le=365)
    budget_pln: int = Field(default=0, ge=0)
    team_size: int = Field(default=2, ge=1)
    focus_areas: list[str] = Field(default_factory=list)


class CompanyConfig(BaseModel):
    """Complete company configuration — the single source of truth
    for all agent prompts. ZERO hardcoded data allowed in agents.
    """

    name: str = Field(..., min_length=1, max_length=100)
    product: str = Field(..., min_length=1)
    pricing_tier: str = ""
    value_proposition: str = ""
    competitors: list[Competitor] = Field(default_factory=list)
    target: TargetSegment = Field(default_factory=TargetSegment)
    constraints: Constraints = Field(default_factory=Constraints)
    differentiators: list[str] = Field(default_factory=list)
    case_studies: list[dict[str, Any]] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Acme Corp",
                "product": "AI-powered analytics platform",
                "pricing_tier": "Enterprise ($50k+/year)",
                "value_proposition": "Reduce churn by 40%",
            }
        }
    }


@dataclass(frozen=True)
class RoundContext:
    """Immutable context passed to each agent for a given round.
    Contains everything an agent needs to generate its response.
    """

    round_num: int
    brief: str
    discussion_history: str
    company_config: CompanyConfig
    battlecards: str = ""
    content_plan: str = ""
    target_accounts: str = ""


# ── Orchestration Models ────────────────────────────────────────────────────


class AgentState(Enum):
    """Finite states for agent lifecycle tracking."""

    PENDING = auto()  # Agent created, not started
    WRITING = auto()  # Currently generating output
    WAITING = auto()  # Waiting at barrier for other agents
    DONE = auto()  # Round completed successfully
    ERROR = auto()  # Error occurred


__all__ = [
    "AgentState",
    "CompanyConfig",
    "Competitor",
    "Constraints",
    "LLMProvider",
    "LLMResponse",
    "RoundContext",
    "TargetSegment",
]

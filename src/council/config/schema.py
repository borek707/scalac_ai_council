from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import (
    Any,
    AsyncGenerator,
    Dict,
    List,
    Literal,
    Optional,
)

from pydantic import BaseModel, Field


# ── Layer 1: Data Models ────────────────────────────────────────────────────


class Competitor(BaseModel):
    """Competitor intelligence for battlecard generation."""

    name: str = Field(..., min_length=1)
    threat: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "MEDIUM"
    pricing: str = ""
    weakness: str = ""
    clients: List[str] = Field(default_factory=list)


class TargetSegment(BaseModel):
    """Ideal Customer Profile (ICP) definition."""

    segment: str = ""
    decision_maker: str = ""
    pain_points: List[str] = Field(default_factory=list)
    budget_range: str = ""
    geo_focus: List[str] = Field(default_factory=list)


class Constraints(BaseModel):
    """Project execution constraints."""

    timeline_days: int = Field(default=90, ge=1, le=365)
    budget_pln: int = Field(default=0, ge=0)
    team_size: int = Field(default=2, ge=1)
    focus_areas: List[str] = Field(default_factory=list)


class CompanyConfig(BaseModel):
    """Complete company configuration — the single source of truth
    for all agent prompts. ZERO hardcoded data allowed in agents.
    """

    name: str = Field(..., min_length=1, max_length=100)
    product: str = Field(..., min_length=1)
    pricing_tier: str = ""
    value_proposition: str = ""
    competitors: List[Competitor] = Field(default_factory=list)
    target: TargetSegment = Field(default_factory=TargetSegment)
    constraints: Constraints = Field(default_factory=Constraints)
    differentiators: List[str] = Field(default_factory=list)
    case_studies: List[Dict[str, Any]] = Field(default_factory=list)

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


@dataclass
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
    DONE = auto()     # Round completed successfully
    ERROR = auto()    # Error occurred


# ── LLM Abstractions ────────────────────────────────────────────────────────


@dataclass
class LLMResponse:
    """Standardised response wrapper for any LLM provider."""

    content: str
    model: str
    tokens_prompt: int = 0
    tokens_completion: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0


class LLMProvider(ABC):
    """Abstract base for all LLM providers (OpenAI, Anthropic, Ollama, etc.).
    The Agent Layer depends on this abstraction — concrete providers
    are wired at orchestration time.
    """

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: Optional[str] = None,
    ) -> LLMResponse:
        """Generate a complete response from the LLM."""
        ...

    @abstractmethod
    async def stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens from the LLM."""
        ...

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from typing import Any, AsyncGenerator, Optional

import pytest

from council.agents.base import BaseAgent, Brief, RoundContext
from council.config.schema import (
    CompanyConfig,
    Competitor,
    Constraints,
    TargetSegment,
)
from council.llm.provider import LLMProvider, LLMResponse
from council.orchestration.orchestrator import AsyncOrchestrator


# ── Fixtures for configuration ──

@pytest.fixture
def sample_config() -> CompanyConfig:
    """Return a sample company configuration for testing."""
    return CompanyConfig(
        name="TestCorp",
        product="AI-Powered Analytics Platform",
        pricing_tier="Enterprise",
        value_proposition="Real-time insights for data-driven decisions",
        competitors=[
            Competitor(
                name="CompetitorX",
                threat="HIGH",
                pricing="$500/month",
                weakness="Slow onboarding",
            ),
            Competitor(
                name="CompetitorY",
                threat="MEDIUM",
                pricing="$300/month",
                weakness="Limited integrations",
            ),
        ],
        target=TargetSegment(
            segment="Enterprise Data Teams",
            decision_maker="CTO",
            pain_points=["Data silos", "Slow reporting", "Integration complexity"],
            budget_range="50k-100k PLN",
            geo_focus=["Poland", "Germany"],
        ),
        constraints=Constraints(
            timeline_days=90,
            budget_pln=100000,
            team_size=4,
            focus_areas=["Content", "Paid Ads", "Sales Enablement"],
        ),
        differentiators=["Speed", "Ease of use", "API-first"],
        case_studies=[
            {"name": "ClientA", "result": "3x ROI in 6 months"},
        ],
    )


@pytest.fixture
def temp_workspace(tmp_path: Path) -> Path:
    """Return a temporary workspace directory."""
    workspace = tmp_path / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "shared" / "discussion").mkdir(parents=True, exist_ok=True)
    (workspace / "output").mkdir(parents=True, exist_ok=True)
    return workspace


# ── Fixtures for LLM ──

class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing."""

    def __init__(
        self,
        response_text: str = "Mock response",
        fail_nth_call: Optional[int] = None,
        delay: float = 0.0,
    ) -> None:
        self.response_text = response_text
        self.fail_nth_call = fail_nth_call
        self.delay = delay
        self._call_count = 0
        self.calls: list[dict[str, Any]] = []

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: Optional[str] = None,
    ) -> LLMResponse:
        self._call_count += 1
        self.calls.append({
            "prompt": prompt,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "system": system,
        })

        if self.delay:
            await asyncio.sleep(self.delay)

        if self.fail_nth_call and self._call_count >= self.fail_nth_call:
            raise RuntimeError(f"Mock failure on call {self._call_count}")

        return LLMResponse(
            content=f"{self.response_text} (call #{self._call_count})",
            model=model or "mock-model",
            tokens_prompt=len(prompt) // 4,
            tokens_completion=100,
            cost_usd=0.001 * self._call_count,
            latency_ms=10.0,
        )

    async def stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        yield self.response_text


@pytest.fixture
def mock_provider() -> MockLLMProvider:
    """Return a mock LLM provider with default responses."""
    return MockLLMProvider()


@pytest.fixture
def failing_provider() -> MockLLMProvider:
    """Return a mock LLM provider that fails on first call."""
    return MockLLMProvider(fail_nth_call=1)


# ── Fixtures for agents ──

class DummyAgent(BaseAgent):
    """Minimal agent implementation for testing."""

    def __init__(
        self,
        name: str,
        brief: Brief,
        config: CompanyConfig,
        provider: Optional[MockLLMProvider] = None,
        delay: float = 0.0,
    ) -> None:
        super().__init__(
            name=name,
            role="Test Agent",
            brief=brief,
            config=config,
        )
        self.provider = provider
        self.delay = delay

    def get_system_prompt(self) -> str:
        return f"You are {self.name}, a test agent."

    def get_output_filename(self) -> str:
        return f"{self.name}_output.md"

    async def generate_round(self, ctx: RoundContext) -> str:
        if self.delay:
            await asyncio.sleep(self.delay)
        if self.provider:
            response = await self.provider.generate(
                prompt=f"Round {ctx.round_num} for {self.name}",
                system=self.get_system_prompt(),
            )
            return response.content
        return f"# {self.name} — Round {ctx.round_num}\n\nTest content."


@pytest.fixture
def dummy_agents(
    sample_config: CompanyConfig,
    temp_workspace: Path,
    mock_provider: MockLLMProvider,
) -> list[DummyAgent]:
    """Return a list of 4 dummy agents for testing."""
    brief = Brief(workspace=temp_workspace)
    return [
        DummyAgent("marcus", brief, sample_config, mock_provider),
        DummyAgent("elena", brief, sample_config, mock_provider),
        DummyAgent("kai", brief, sample_config, mock_provider),
        DummyAgent("david", brief, sample_config, mock_provider),
    ]


@pytest.fixture
def orchestrator(
    dummy_agents: list[DummyAgent],
    sample_config: CompanyConfig,
    mock_provider: MockLLMProvider,
    temp_workspace: Path,
) -> AsyncOrchestrator:
    """Return a configured AsyncOrchestrator for testing."""
    return AsyncOrchestrator(
        agents=dummy_agents,
        config=sample_config,
        provider=mock_provider,
        max_rounds=3,
        round_timeout=30.0,
        workspace=temp_workspace,
    )

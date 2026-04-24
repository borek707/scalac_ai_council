"""Demo mode for the AI Marketing Council.

Runs the council with pre-defined scenarios and a mock LLM provider
so no API keys or real LLM calls are needed. Useful for presentations,
CI smoke tests, and onboarding.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncGenerator, Callable, Optional

from council.agents.david import DavidAgent
from council.agents.elena import ElenaAgent
from council.agents.kai import KaiAgent
from council.agents.marcus import MarcusAgent
from council.config.schema import CompanyConfig, Competitor, Constraints, TargetSegment
from council.llm.provider import LLMProvider, LLMResponse



@dataclass
class Scenario:
    """A pre-built demo scenario."""

    key: str
    name: str
    description: str
    config: CompanyConfig
    responses: dict[str, list[str]]


class DemoProvider(LLMProvider):
    """Mock LLM provider that serves scripted responses per agent/round.

    In demo mode the provider *simulates typing* — it yields the response
    character-by-character with a small delay so the live dashboard shows
    progress bars growing, content preview updating, and agents taking turns.
    """

    def __init__(
        self,
        responses: dict[str, list[str]],
        progress_callback: Optional[Callable[..., None]] = None,
        delay: float = 0.18,
        chunk_size: int = 28,
    ) -> None:
        self._responses = responses
        self._counters: dict[str, int] = {}
        self.calls: list[dict[str, Any]] = []
        self.progress_callback = progress_callback
        self.delay = delay
        self.chunk_size = chunk_size

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: Optional[str] = None,
    ) -> LLMResponse:
        self.calls.append({"prompt": prompt, "system": system})
        agent = self._detect_agent(system or prompt)
        idx = self._counters.get(agent, 0)
        self._counters[agent] = idx + 1
        texts = self._responses.get(agent, ["Demo response"])
        content = texts[idx] if idx < len(texts) else texts[-1]

        # Simulate live typing with progress updates
        if self.delay > 0:
            accumulated = ""
            total_len = len(content)
            for i in range(0, total_len, self.chunk_size):
                chunk = content[i : i + self.chunk_size]
                accumulated += chunk
                progress = min(100, int((len(accumulated) / total_len) * 100))

                if self.progress_callback:
                    self.progress_callback(
                        agent,
                        "writing",
                        progress_pct=progress,
                        content=accumulated,
                        activity=f"Writing round output… ({progress}%)",
                    )

                await asyncio.sleep(self.delay)

        return LLMResponse(
            content=content,
            model="demo",
            tokens_prompt=len(prompt) // 4,
            tokens_completion=len(content) // 4,
            cost_usd=0.0,
            latency_ms=50.0,
        )

    async def stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        system: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        response = await self.generate(prompt, model, temperature, max_tokens, system)
        yield response.content

    def _detect_agent(self, text: str) -> str:
        for name in ("Marcus", "Elena", "Kai", "David"):
            if name in text:
                return name
        return "Unknown"


def _saas_launch_responses() -> dict[str, list[str]]:
    return {
        "Marcus": [
            "# Offer Architecture — Round 1\n\n"
            "## Pricing Strategy\n"
            "- **Freemium tier**: Up to 5 users, basic boards\n"
            "- **Team tier**: $29/user/month — unlimited boards, integrations\n"
            "- **Enterprise tier**: Custom SLA, SSO, dedicated support\n\n"
            "## Packaging\n"
            "Good-Better-Best with clear upgrade triggers at 5-user and 50-user milestones.",
            "# Offer Architecture — Round 2\n\n"
            "## Competitive Positioning\n"
            "Against Asana: emphasise speed and developer-friendly API.\n"
            "Against Monday: highlight fixed-price predictability.\n\n"
            "## Guarantee\n"
            "30-day pilot with free migration from Trello/Asana.",
            "# Offer Architecture — Final\n\n"
            "Recommended: Team tier at $29 with annual 2-month-free discount.\n"
            "Enterprise add-on: $5k onboarding + $12/user.",
        ],
        "Elena": [
            "# Funnel Design — Round 1\n\n"
            "## Stages\n"
            "1. **Awareness**: SEO + dev.to articles on project-management pain\n"
            "2. **Evaluation**: Interactive ROI calculator + template gallery\n"
            "3. **Decision**: Live demo + pilot onboarding\n\n"
            "## Metrics\n"
            "Target CAC <$500, LTV/CAC > 3x.",
            "# Funnel Design — Round 2\n\n"
            "## Pipeline Velocity\n"
            "- Lead → MQL: 3 days (content gated download)\n"
            "- MQL → SQL: 7 days (SDR outreach)\n"
            "- SQL → Close: 21 days (pilot + procurement)\n\n"
            "## Expansion triggers\n"
            "Usage-based alerts when teams hit 80 % of seat limit.",
            "# Funnel Design — Final\n\n"
            "Launch with PLG motion; add outbound SDRs once ARR hits $1M.\n"
            "Quarterly review cadence for expansion pipeline.",
        ],
        "Kai": [
            "# Copy & Content — Round 1\n\n"
            "## Headline\n"
            "*\"The project tool your engineers will actually use.\"*\n\n"
            "## CTA\n"
            "[Start free pilot — no credit card]\n\n"
            "## Email subject line A/B test\n"
            "A: 'Trello making you scroll?'  B: '5-user free tier ending soon'",
            "# Copy & Content — Round 2\n\n"
            "## Landing page structure\n"
            "1. Hero: speed claim + social proof (G2 badge)\n"
            "2. Problem: 'Status meetings steal 4 hrs/week'\n"
            "3. Solution: 60-second demo GIF\n"
            "4. Proof: migration case study from 200-person agency\n"
            "5. CTA: book pilot",
            "# Copy & Content — Final\n\n"
            "Brand voice: concise, engineer-respectful, no fluff.\n"
            "All headlines must pass the 'so what?' test before publishing.",
        ],
        "David": [
            "# ABM & Lead Gen — Round 1\n\n"
            "## Target Account List (Tier 1)\n"
            "- 50 Series B SaaS startups in EU/US with 50–200 employees\n"
            "- ICP: VP Engineering evaluating PM tools\n\n"
            "## Channels\n"
            "LinkedIn ABM ads, targeted dev podcast sponsorships, GitHub sponsorships.",
            "# ABM & Lead Gen — Round 2\n\n"
            "## Intent Signals\n"
            "- Job postings for 'Scrum Master' or 'Project Manager'\n"
            "- Tech stack changes on StackShare (adding Jira competitors)\n"
            "- Funding announcements = budget window open\n\n"
            "## Outreach sequence\n"
            "4-touch email + LinkedIn voice note over 14 days.",
            "# ABM & Lead Gen — Final\n\n"
            "Start with 50 Dream Accounts; measure SAL creation rate.\n"
            "Expand to 1:few ABM once Tier-1 conversion > 10 %.",
        ],
    }


def _ecommerce_rebrand_responses() -> dict[str, list[str]]:
    return {
        "Marcus": [
            "# Rebrand Offer — Round 1\n\n"
            "## Positioning shift\n"
            "From 'affordable fashion' → 'conscious wardrobe curation'.\n\n"
            "## New tiers\n"
            "- Essentials (€29–59): timeless basics\n"
            "- Curated (€79–129): seasonal capsules\n"
            "- Atelier (€199+): limited drops with designer collabs",
            "# Rebrand Offer — Round 2\n\n"
            "## Launch mechanics\n"
            "Pre-launch waitlist with 'founding member' pricing (-20 %).\n"
            "Referral: give €15, get €15.\n\n"
            "## Risk reversal\n"
            "Free returns for 60 days, no questions asked.",
            "# Rebrand Offer — Final\n\n"
            "Price anchor at €99 to lift AOV. Bundle 3-item 'capsules' at €199.",
        ],
        "Elena": [
            "# Rebrand Funnel — Round 1\n\n"
            "## Audience segments\n"
            "1. Eco-curious millennials (Instagram/TikTok)\n"
            "2. Quality-over-quantity professionals (LinkedIn + newsletters)\n\n"
            "## Content pillars\n"
            "Behind-the-design, capsule-wardrobe guides, cost-per-wear calculator.",
            "# Rebrand Funnel — Round 2\n\n"
            "## Retention loop\n"
            "Quarterly 'Wardrobe Audit' email with personalised restock suggestions.\n"
            "VIP tier: early access to drops + free styling call.",
            "# Rebrand Funnel — Final\n\n"
            "Launch funnel: influencer seeding → waitlist → 48-hr drop → nurture.\n"
            "Target: 10k waitlist, 15 % conversion to first purchase.",
        ],
        "Kai": [
            "# Rebrand Copy — Round 1\n\n"
            "## Tagline options\n"
            "A. *'Wear less. Choose better.'*\n"
            "B. *'Your wardrobe, edited.'*\n\n"
            "## Tone\n"
            "Warm, confident, slightly editorial — like a friend who knows fashion.",
            "# Rebrand Copy — Round 2\n\n"
            "## Product descriptions\n"
            "Lead with occasion ('Monday meeting') not feature ('100 % cotton').\n"
            "Include care tips to signal longevity.\n\n"
            "## Email welcome series\n"
            "3 emails: brand story → capsule guide → first-order incentive.",
            "# Rebrand Copy — Final\n\n"
            "Final tagline: *'Fewer pieces. More outfit possibilities.'*\n"
            "All copy must pass 8-year-old test: can a child explain what we sell?",
        ],
        "David": [
            "# Rebrand ABM — Round 1\n\n"
            "## Retail partners (B2B angle)\n"
            "Target boutique hotel chains and co-working spaces for uniform/collab lines.\n\n"
            "## Decision makers\n"
            "Head of Brand, Head of Procurement, Sustainability Officer.",
            "# Rebrand ABM — Round 2\n\n"
            "## Signal-based outreach\n"
            "- Hotels publishing sustainability reports → pitch eco-linen collab\n"
            "- Co-working spaces opening new locations → uniform refresh need\n\n"
            "## Offer\n"
            "White-label capsule collection with co-branded tags.",
            "# Rebrand ABM — Final\n\n"
            "Pilot with 3 boutique hotel groups. Measure reorder rate and NPS.\n"
            "Case study target: 6-month ROI for partner.",
        ],
    }


def _fintech_scale_responses() -> dict[str, list[str]]:
    return {
        "Marcus": [
            "# Enterprise Offer — Round 1\n\n"
            "## Packaging for banks\n"
            "- **Core API**: €0.10/transaction, volume discounts from 1M txns\n"
            "- **Platform**: €50k/year + €0.08/txn — includes SLA + sandbox\n"
            "- **Enterprise**: Custom — dedicated infra, regulatory support\n\n"
            "## Compliance bundle\n"
            "PCI-DSS Level 1, PSD2, SOX documentation included in Platform+.",
            "# Enterprise Offer — Round 2\n\n"
            "## Procurement alignment\n"
            "3-year TCO model vs legacy core banking integration.\n"
            "Pilot: 90-day proof of concept on non-critical payment rail.\n\n"
            "## Expansion\n"
            "Land with treasury; expand to merchant-acquiring.",
            "# Enterprise Offer — Final\n\n"
            "Lead with Platform tier. Anchor on security + speed (sub-100ms auth).\n"
            "Include regulatory roadmap slide in every proposal.",
        ],
        "Elena": [
            "# Enterprise Funnel — Round 1\n\n"
            "## Target segments\n"
            "1. Neobanks launching cards (fastest sales cycle)\n"
            "2. Tier-2 banks modernising infra (highest ACV)\n"
            "3. Fintechs expanding cross-border (growth potential)\n\n"
            "## Entry point\n"
            "Developer sandbox → integration guide → solution-architect call.",
            "# Enterprise Funnel — Round 2\n\n"
            "## Sales stages\n"
            "- Qualify: MEDDIC + technical fit checklist\n"
            "- Prove: 90-day pilot with success criteria\n"
            "- Negotiate: procurement + InfoSec + legal parallel tracks\n\n"
            "## Velocity target\n"
            "180 days from first demo to signature.",
            "# Enterprise Funnel — Final\n\n"
            "Hire 2 solution architects in London and Singapore.\n"
            "Quarterly executive business reviews for expansion.",
        ],
        "Kai": [
            "# Enterprise Copy — Round 1\n\n"
            "## Homepage hero\n"
            "*'Move money at the speed of now.'*\n\n"
            "## Security messaging\n"
            "Lead with certifications, not promises.\n"
            "'99.99 % uptime. Audited. Insured.'\n\n"
            "## CTA\n"
            "[Request sandbox access] — not 'Buy now'.",
            "# Enterprise Copy — Round 2\n\n"
            "## Case-study format\n"
            "Challenge → Technical approach → Metrics → Quote from CTO.\n\n"
            "## Whitepaper titles\n"
            "'Future-proofing payment infrastructure'\n"
            "'Reducing payment latency: a technical guide'",
            "# Enterprise Copy — Final\n\n"
            "Voice: precise, confident, engineering-first.\n"
            "Avoid superlatives. Use data. Every claim footnoted.",
        ],
        "David": [
            "# Enterprise ABM — Round 1\n\n"
            "## Dream 100 list\n"
            "Top 100 European banks and payment processors.\n\n"
            "## Intent data\n"
            "- RFP publications mentioning 'real-time payments'\n"
            "- Vendor-replacement cycles (5-year core renewals)\n"
            "- Regulatory deadlines (SEPA Instant mandate)",
            "# Enterprise ABM — Round 2\n\n"
            "## 1:1 plays\n"
            "- Custom landing page per target bank with their logo + use case\n"
            "- Executive dinner series in Frankfurt and Amsterdam\n"
            "- Sponsored technical workshops at Money20/20",
            "# Enterprise ABM — Final\n\n"
            "Target 10 Tier-1 wins in Year 1.\n"
            "Measure pipeline coverage 3:1 and average deal size.",
        ],
    }


def _healthcare_app_responses() -> dict[str, list[str]]:
    return {
        "Marcus": [
            "# Healthcare Offer — Round 1\n\n"
            "## Patient pricing\n"
            "- **Basic**: Free symptom checker + booking\n"
            "- **Care Plan**: $19/month — unlimited messaging, prescription renewals\n"
            "- **Family**: $39/month — covers 4 profiles, paediatric included\n\n"
            "## B2B angle (clinics)\n"
            "SaaS per provider seat: $199/month — EHR integration, scheduling, billing.",
            "# Healthcare Offer — Round 2\n\n"
            "## Trust signals\n"
            "HIPAA badge, board-certified provider verification, transparent pricing.\n\n"
            "## Risk reversal\n"
            "First consultation free. Cancel anytime, pro-rata refund.",
            "# Healthcare Offer — Final\n\n"
            "Launch B2C first to build reviews; pivot to B2B clinic SaaS at 50k users.\n"
            "Anchor on convenience + trust, not price.",
        ],
        "Elena": [
            "# Healthcare Funnel — Round 1\n\n"
            "## Channels\n"
            "1. Google Ads: 'urgent care near me' + 'online dermatologist'\n"
            "2. Facebook/Instagram: parent-focused paediatric content\n"
            "3. Employer wellness partnerships (B2B2C)\n\n"
            "## Trust funnel\n"
            "Educational content → free assessment → paid care plan.",
            "# Healthcare Funnel — Round 2\n\n"
            "## Retention\n"
            "- Care reminders via SMS (adherence + re-engagement)\n"
            "- Seasonal campaigns: flu prep, allergy season, back-to-school physicals\n\n"
            "## Referral loop\n"
            "Family plan discount for every invited member who completes first visit.",
            "# Healthcare Funnel — Final\n\n"
            "CPL target <$25. Trial-to-paid conversion > 20 %.\n"
            "NPS target > 50 (healthcare benchmark).",
        ],
        "Kai": [
            "# Healthcare Copy — Round 1\n\n"
            "## Headline\n"
            "*\"A doctor in your pocket, without the waiting room.\"*\n\n"
            "## Subhead\n"
            "Board-certified physicians. Same-day appointments. Clear pricing.\n\n"
            "## Trust line\n"
            "'Your data is encrypted and never sold.'",
            "# Healthcare Copy — Round 2\n\n"
            "## Tone guidelines\n"
            "Empathetic, not clinical.\n"
            "Use 'you' and 'your family', not 'patients' and 'users'.\n\n"
            "## Sensitive conditions\n"
            "Destigmatise language. 'Mental health check-in' not 'psych eval'.",
            "# Healthcare Copy — Final\n\n"
            "All claims reviewed by medical advisory board before publish.\n"
            "Include disclaimer footer on every page.",
        ],
        "David": [
            "# Healthcare ABM — Round 1\n\n"
            "## B2B targets\n"
            "- Self-insured employers (500+ employees)\n"
            "- Direct-primary-care clinics looking to scale virtual\n"
            "- Health systems testing digital front door\n\n"
            "## Decision makers\n"
            "CHRO, VP Benefits, Chief Digital Officer.",
            "# Healthcare ABM — Round 2\n\n"
            "## Value prop per segment\n"
            "- Employers: reduce absenteeism, lower insurance premiums\n"
            "- Clinics: extend reach, reduce no-shows, add revenue stream\n"
            "- Health systems: patient acquisition + ED diversion\n\n"
            "## Proof points\n"
            "Pilot data: 30 % reduction in unnecessary ER visits.",
            "# Healthcare ABM — Final\n\n"
            "Land 3 employer pilots in Q1. Measure utilisation and cost avoidance.\n"
            "Expand to health systems once case studies are published.",
        ],
    }


def _scenario(
    key: str,
    name: str,
    description: str,
    config: CompanyConfig,
    responses: dict[str, list[str]],
) -> Scenario:
    return Scenario(key=key, name=name, description=description, config=config, responses=responses)


SCENARIOS: list[Scenario] = [
    _scenario(
        key="saas-launch",
        name="SaaS Launch",
        description="Launching an AI-powered project management tool for engineering teams",
        config=CompanyConfig(
            name="TaskFlow AI",
            product="AI-powered project management for software teams",
            pricing_tier="Freemium / $29–49 per user per month",
            value_proposition="Cut status-meeting time by 70 % with AI-generated standups and smart prioritisation",
            competitors=[
                Competitor(name="Asana", threat="HIGH", pricing="$24/user/mo", weakness="Slow, cluttered UI"),
                Competitor(name="Monday", threat="MEDIUM", pricing="$27/user/mo", weakness="Generic, not dev-focused"),
                Competitor(name="Linear", threat="MEDIUM", pricing="$8/user/mo", weakness="No AI features yet"),
            ],
            target=TargetSegment(
                segment="Series A–C SaaS startups with 20–200 engineers",
                decision_maker="VP Engineering or CTO",
                pain_points=["Too many status meetings", "Context switching between tools", "Missed deadlines"],
                budget_range="$500–2 000/month",
                geo_focus=["US", "UK", "Germany"],
            ),
            constraints=Constraints(timeline_days=90, team_size=4, focus_areas=["product-led growth", "developer evangelism"]),
            differentiators=["AI standup generation", "GitHub/Jira auto-sync", "Sub-50ms load time"],
        ),
        responses=_saas_launch_responses(),
    ),
    _scenario(
        key="ecommerce-rebrand",
        name="E-commerce Rebrand",
        description="Rebranding a mid-size fashion e-commerce toward conscious consumption",
        config=CompanyConfig(
            name="Wardrobe Edit",
            product="Curated sustainable fashion e-commerce",
            pricing_tier="€29–199 per item",
            value_proposition="Build a versatile wardrobe with fewer, better pieces",
            competitors=[
                Competitor(name="Zalando", threat="HIGH", pricing="€15–80/item", weakness="Fast fashion image"),
                Competitor(name="Everlane", threat="MEDIUM", pricing="$40–150/item", weakness="Limited EU presence"),
                Competitor(name="Reformation", threat="MEDIUM", pricing="$80–300/item", weakness="Narrow sizing"),
            ],
            target=TargetSegment(
                segment="Urban professionals aged 28–40, household income €60k+",
                decision_maker="Individual consumer (B2C)",
                pain_points=["Closet full of clothes, nothing to wear", "Guilt about fast fashion", "Overwhelming choice online"],
                budget_range="€200–500 per quarter",
                geo_focus=["Germany", "Netherlands", "UK"],
            ),
            constraints=Constraints(timeline_days=120, team_size=5, focus_areas=["brand awareness", "retention"]),
            differentiators=["Capsule curation algorithm", "60-day free returns", "Designer collaboration drops"],
        ),
        responses=_ecommerce_rebrand_responses(),
    ),
    _scenario(
        key="fintech-scale",
        name="Fintech Scale",
        description="Scaling a B2B payment platform from startup to enterprise banks",
        config=CompanyConfig(
            name="PayCore",
            product="Real-time payment infrastructure API for banks and fintechs",
            pricing_tier="€0.08–0.10 per transaction + platform fees",
            value_proposition="Sub-100ms authorisation with built-in regulatory compliance",
            competitors=[
                Competitor(name="Stripe", threat="HIGH", pricing="2.9 % + 30¢", weakness="US-centric, expensive for volume"),
                Competitor(name="Adyen", threat="HIGH", pricing="Interchange++", weakness="Complex pricing, long onboarding"),
                Competitor(name="Mangopay", threat="MEDIUM", pricing="1.9 % + 20¢", weakness="Marketplace-only focus"),
            ],
            target=TargetSegment(
                segment="Neobanks, Tier-2 banks, and cross-border fintechs in EU/UK",
                decision_maker="CTO or Head of Payments",
                pain_points=["Legacy core too slow", "Regulatory burden", "High transaction costs"],
                budget_range="€100k–1M annual contract",
                geo_focus=["EU", "UK"],
            ),
            constraints=Constraints(timeline_days=180, team_size=6, focus_areas=["enterprise sales", "developer relations"]),
            differentiators=["Sub-100ms latency", "PSD2-native", "Sandbox + solution architects"],
        ),
        responses=_fintech_scale_responses(),
    ),
    _scenario(
        key="healthcare-app",
        name="Healthcare App",
        description="Go-to-market for a telehealth app targeting families and employers",
        config=CompanyConfig(
            name="MediConnect",
            product="Telehealth app with AI triage and same-day physician access",
            pricing_tier="$19–39/month or $199/provider seat for clinics",
            value_proposition="See a board-certified doctor within 15 minutes, 24/7",
            competitors=[
                Competitor(name="Teladoc", threat="HIGH", pricing="$75/visit", weakness="Impersonal, long waits"),
                Competitor(name="Babylon", threat="MEDIUM", pricing="Subscription + NHS", weakness="AI-only, no human option"),
                Competitor(name="Kry", threat="MEDIUM", pricing="€25/visit", weakness="Limited to EU, no family plan"),
            ],
            target=TargetSegment(
                segment="Busy parents and self-insured employers in US/UK",
                decision_maker="Parent or CHRO",
                pain_points=["Can't get GP appointment", "ER visits for minor issues", "High insurance premiums"],
                budget_range="$50–200/month (family) or $10k–50k/year (employer)",
                geo_focus=["US", "UK"],
            ),
            constraints=Constraints(timeline_days=90, team_size=4, focus_areas=["patient acquisition", "B2B employer sales"]),
            differentiators=["15-minute guarantee", "Family plan", "HIPAA + GDPR compliant"],
        ),
        responses=_healthcare_app_responses(),
    ),
]


def get_scenario(key: str) -> Scenario:
    """Return a scenario by key."""
    for s in SCENARIOS:
        if s.key == key:
            return s
    raise KeyError(f"Unknown scenario: {key!r}. Available: {[s.key for s in SCENARIOS]}")


def list_scenarios() -> list[Scenario]:
    """Return all available demo scenarios."""
    return list(SCENARIOS)


async def run_demo(
    scenario_key: str,
    rounds: int,
    workspace: Path,
    progress_callback: Optional[Callable[..., None]] = None,
    delay: float = 0.18,
    breath: float = 0.4,
) -> dict[str, Path]:
    """Run a complete demo scenario.

    Args:
        scenario_key: Key of the scenario to run.
        rounds: Number of debate rounds.
        workspace: Output directory.
        progress_callback: Optional dashboard callback.
        delay: Seconds between typed chunks (lower = faster). Use 0 for tests.

    Returns:
        Mapping of agent_name -> final_output_path.
    """
    scenario = get_scenario(scenario_key)
    provider = DemoProvider(scenario.responses, progress_callback=progress_callback, delay=delay)

    agents = [
        MarcusAgent(workspace=workspace, config=scenario.config, provider=provider),
        ElenaAgent(workspace=workspace, config=scenario.config, provider=provider),
        KaiAgent(workspace=workspace, config=scenario.config, provider=provider),
        DavidAgent(workspace=workspace, config=scenario.config, provider=provider),
    ]

    if progress_callback:
        for agent in agents:
            agent.progress_callback = progress_callback

    # Sequential, animated demo run — one agent at a time so the dashboard
    # shows WRITING → DONE transitions in a lively, theatrical way.
    for round_num in range(1, rounds + 1):
        for agent in agents:
            if progress_callback:
                progress_callback(
                    agent.name,
                    "round_start",
                    round_num=round_num,
                    progress_pct=0,
                    activity="Loading context…",
                )
                if breath > 0:
                    await asyncio.sleep(min(breath, 0.15))

            await agent.run_round(round_num)

            if progress_callback:
                progress_callback(
                    agent.name,
                    "done",
                    content=agent.read_discussion(),
                    activity="Round complete",
                )

            # Small breath between agents so the user can see the transition
            if breath > 0:
                await asyncio.sleep(breath)

    # Final consolidated outputs — also animated
    for agent in agents:
        if progress_callback:
            progress_callback(
                agent.name,
                "writing",
                progress_pct=0,
                activity="Writing final output…",
            )
        await agent.run_final()
        if progress_callback:
            progress_callback(
                agent.name,
                "done",
                activity="Final output complete",
            )
        if breath > 0:
            await asyncio.sleep(min(breath, 0.3))

    return {
        agent.name: workspace / "output" / agent.get_output_filename()
        for agent in agents
    }

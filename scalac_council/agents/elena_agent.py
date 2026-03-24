#!/usr/bin/env python3
"""
AGENT: Elena - Funnel Architect
Rola: Projektowanie lejków, kwalifikacja, eksperymenty

Usage w Kimi Code:
    Jako Elena, przeczytaj brief i prowadź debatę.
    Pisz do shared/discussion/round_X_elena.md
"""

import os
import sys
from pathlib import Path

WORKSPACE = Path("/root/.openclaw/workspace/scalac-council")
SHARED = WORKSPACE / "shared"
DISCUSSION = SHARED / "discussion"
OUTPUT = WORKSPACE / "output"

SYSTEM_PROMPT = """Jesteś Elena, Architektką Lejków w Scalac.

## Twoja Tożsamość
Była VP Growth w SaaS startup (0→10M ARR). Rozumiesz strategię i taktykę.
Twoja supermoc: zamiana oferty w działający lejek z przewidywalnym pipeline.

## Twoje Książki
- From Impossible to Inevitable: Hypergrowth phases
- Predictable Revenue: Seeds/Nets/Spears
- The JOLT Effect: Overcoming indecision
- Demand-Side Sales: Jobs-to-be-Done
- The Qualified Sales Leader: MEDDIC
- Never Split the Difference: Negotiation

## Twój Styl
- Procesowa, ale pragmatyczna
- Metryki > Instynkt (zawsze licz konwersje!)
- Testuj założenia Marcusa

## W Debacie
- Walcz o realistyczne konwersje (Marcus będzie optymistyczny)
- Pytaj o MEDDIC - czy potrafimy kwalifikować?
- Używaj JOLT na wahanie klientów
- Chroń lejek przed „za szybkim” oferowaniem

## Output Format
```markdown
# Stanowisko Eleny - Runda X

## Moja Teza
[1-2 zdania]

## Kalkulacje
- Pipeline needed: X
- Conversion rates: Y%
- Leads required: Z

## Co Sądzę o Innych
### Marcus: [agree/disagree + dlaczego]
### Kai: [...]
### David: [...]

## Propozycja
[kompromis lub utrwalenie]
```
"""


def read_file(path):
    if path.exists():
        return path.read_text()
    return ""


def read_discussion():
    posts = []
    if DISCUSSION.exists():
        for f in sorted(DISCUSSION.glob("*.md")):
            posts.append(f"\n\n--- {f.name} ---\n{f.read_text()}")
    return "\n".join(posts) if posts else "Brak wcześniejszych postów"


def write_round(round_num, content):
    DISCUSSION.mkdir(parents=True, exist_ok=True)
    round_file = DISCUSSION / f"round_{round_num}_elena.md"
    round_file.write_text(content)
    print(f"✅ Elena napisała rundę {round_num}")


def write_final():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    
    content = """# Funnel Design: Team Extension dla Fintechów Series B

## Target
- Pipeline: 500k PLN w 90 dni
- Average deal: 180k PLN
- Deals needed: 3 (conservative) / 2 (optimistic)
- Win rate target: 30%
- Opportunities needed: 10

## Lejek (5 Stages)

### 1. Lead (Architecture Review request)
- Definition: CTO downloaded case study OR requested Architecture Review
- Conversion to MQL: 25% (industry benchmark)
- Volume needed: 160 leads → 40 MQLs

### 2. MQL (Review completed)
- Definition: Architecture Review done, positive feedback
- Conversion to SQL: 20%
- Volume needed: 40 MQLs → 8 SQLs

### 3. SQL (Pricing discussion)
- Definition: MEDDIC qualified, budget confirmed
- Conversion to Opp: 50%
- Volume needed: 8 SQLs → 4 Opportunities

### 4. Opportunity (Proposal sent)
- Definition: Proposal delivered, stakeholders engaged
- Conversion to Closed: 50%
- Volume needed: 4 Opps → 2 Closed

### 5. Closed (Contract signed)
- Target: 2-3 deals / quarter
- ACV: 180k PLN
- Total: 360-540k PLN

## Three Pipelines

### Seeds (Inbound) - 40%
- Channels: SEO, case studies, referrals
- Expected: 64 leads
- Quality: Medium
- CAC: Low

### Nets (Marketing) - 30%
- Channels: Webinars, LinkedIn, conferences
- Expected: 48 leads
- Quality: Medium-High
- CAC: Medium

### Spears (Outbound ABM) - 30%
- Channels: Direct outreach to Dream 100
- Expected: 48 leads
- Quality: High
- CAC: High

## MEDDIC Qualification

### Metrics
- Team size needed: 5-10 devs
- Budget confirmed: 300-500k EUR/year
- Timeline: Start in 30-60 days
- Current cost of delay: Quantified

### Economic Buyer
- CTO / VP Engineering (must have)
- CFO approval for 500k+ (influence)

### Decision Criteria
- Can they work remote? (Must: Yes)
- How fast to onboard? (Must: <3 weeks)
- Scala expertise? (Must: Yes)
- References from fintech? (Nice: Yes)

### Decision Process
- Technical evaluation: Architecture Review
- Budget approval: CFO + CTO
- Legal review: Standard contract
- Timeline: 30-60 days typical

### Identify Pain
- Hiring takes 6+ months
- System scalability issues
- Board pressure
- Team burnout

### Champion
- Tech Lead who wants to solve the problem
- Has credibility with CTO

## JOLT Strategy (Overcoming Indecision)

### J - Judge prospects
- High indecision: "We're evaluating options" → Apply JOLT
- Low indecision: "We need to start yesterday" → Fast track

### O - Offer recommendation
- Don't: "Choose from Good/Better/Best"
- Do: "For your timeline, I recommend Better tier - gives you predictability"

### L - Limit exploration
- Don't: "We can do 1, 3, 5, 10 devs..."
- Do: "Start with 5 devs, expand in month 3"

### T - Take risk away
- "Replacement guarantee - swap dev in 48h if no fit"
- "2-week trial - if not working, no charge"
- "Architecture Review first - low commitment"

## Growth Experiments

### Experiment 1: Architecture Review as PQL
- Hypothesis: AR completion = higher intent than content download
- Test: Track AR → SQL conversion vs content → SQL
- Success: 40%+ conversion

### Experiment 2: JOLT in first call
- Hypothesis: Addressing indecision early speeds up sales
- Test: Use JOLT framework in discovery calls
- Success: 20% shorter sales cycle

### Experiment 3: Pricing transparency
- Hypothesis: Showing pricing early filters out tire-kickers
- Test: Include pricing range on landing page
- Success: Higher SQL quality score

## Forecast

| Month | Leads | MQLs | SQLs | Opps | Closed | Pipeline |
|-------|-------|------|------|------|--------|----------|
| 1 | 54 | 13 | 3 | 1 | 0 | 0 |
| 2 | 53 | 13 | 3 | 2 | 1 | 180k |
| 3 | 53 | 14 | 2 | 1 | 1 | 180k |
| **Total** | **160** | **40** | **8** | **4** | **2** | **360k** |

*Note: Conservative estimate. With optimization can reach 500k.*

---

*Wypracowane w Radzie AI Scalac przez Elenę, z inputem Marcusa, Kaia i Davida*
"""
    
    output_file = OUTPUT / "elena_funnel.md"
    output_file.write_text(content)
    print(f"✅ Elena zapisała finalny output: {output_file}")


def main():
    print("=" * 60)
    print("🎯 ELENA - Funnel Architect")
    print("=" * 60)
    
    existing = list(DISCUSSION.glob("round_*_elena.md")) if DISCUSSION.exists() else []
    round_num = len(existing) + 1
    
    print(f"\n💬 Dyskusja: {read_discussion()[:500]}...")
    
    if round_num <= 3:
        content = f"""# Runda {round_num} - Elena

## Moja Teza
Marcus ma dobry pricing, ale jego asumowane konwersje są ZA WYSOKIE.
Realistyczny lejek to 160 leads → 2 closed deals (nie 3).

## Kalkulacje
- Target: 500k PLN pipeline
- Average deal: 180k PLN (Marcus Best tier)
- Deals needed: 3
- Win rate: 30% (realistycznie dla fintech, nie 50%)
- Opps needed: 10
- SQLs needed: 20 (50% SQL→Opp)
- MQLs needed: 100 (20% MQL→SQL)
- Leads needed: 400 (25% Lead→MQL)

**ALARM:** Marcus zakłada 50% konwersję Lead→MQL. Realnie: 25%.

## Co Sądzę o Marcusia
Marcus: "2-week guarantee" jest świetne jako differentiator, ALE...
- Czy mamy capacity na 2-week guarantee przy 10+ teamach?
- Czy nie obniżamy za bardzo barriery wejścia (tyre-kickers)?

Proponuję: Architecture Review jako PQL (Product Qualified Lead) zamiast content download.

## Moja Propozycja
- Accept Marcus pricing: 75/80/85 EUR/h
- Add JOLT: "Replacement guarantee" jako risk reversal
- Realistic targets: 160 leads/quarter, nie 100
- Focus: Spears (ABM) > Seeds (inbound) dla fintech

## Moje Pytanie do Davida
Czy masz Dream 100 fintechów Series B gotowych do ABM?
Bez tego te 48 leads ze Spears to wishful thinking.
"""
        write_round(round_num, content)
    else:
        write_final()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
AGENT: Marcus - Offer Architect
Rola: Projektowanie oferty, pricing, positioning

Usage w Kimi Code:
    Jako Marcus, przeczytaj brief i prowadź debatę.
    Pisz do shared/discussion/round_X_marcus.md
"""

import os
import sys
from pathlib import Path

# Konfiguracja ścieżek
WORKSPACE = Path("/root/.openclaw/workspace/scalac-council")
SHARED = WORKSPACE / "shared"
DISCUSSION = SHARED / "discussion"
OUTPUT = WORKSPACE / "output"

# Twój system prompt (z AGENTS/marcus_offer_architect/)
SYSTEM_PROMPT = """Jesteś Marcus, Architekt Oferty w Scalac.

## Twoja Tożsamość
Były Principal Engineer który został PM w fintech unicorn. Rozumiesz tech i biznes.
Twoja supermoc: zamiana "potrzebujemy 10 devów" w konkretny biznes case z ROI.

## Twoje Książki (używaj!)
- Crossing the Chasm: Beachhead market
- Monetizing Innovation: Good-Better-Best pricing  
- Building a StoryBrand: SB7 Framework
- The Challenger Sale: Teach-Tailor-Take Control
- Gap Selling: Current vs Future State
- The Mom Test: Walidacja

## Twój Styl
- Bezpośredni, ale empatyczny
- Liczby > Opinie (zawsze licz ROI!)
- "Tak, i..." zamiast "Nie, bo..."

## W Debacie
- Bronij pricingu - Elena będzie chciała obniżyć
- Walcz o wartość, nie godzinówki
- Używaj case studies jako proof
- Jesteś pierwszy w chainie - Twoja oferta determinuje resztę

## Output Format
```markdown
# Stanowisko Marcusa - Runda X

## Moja Teza
[1-2 zdania głównej idei]

## Argumenty
1. [Argument z danymi/książką]
2. [Argument]

## Co Sądzę o Innych
### Elena: [agree/disagree + dlaczego]
### Kai: [...]
### David: [...]

## Moja Propozycja
[konkretna propozycja kompromisu lub utrwalenia stanowiska]
```
"""


def read_brief():
    """Przeczytaj brief projektu."""
    brief_path = SHARED / "brief.md"
    if brief_path.exists():
        return brief_path.read_text()
    return "Brak briefu"


def read_discussion():
    """Przeczytaj całą dyskusję."""
    posts = []
    if DISCUSSION.exists():
        for f in sorted(DISCUSSION.glob("*.md")):
            posts.append(f"\n\n--- {f.name} ---\n{f.read_text()}")
    return "\n".join(posts) if posts else "Brak wcześniejszych postów"


def write_round(round_num: int, content: str):
    """Napisz swoją rundę."""
    DISCUSSION.mkdir(parents=True, exist_ok=True)
    round_file = DISCUSSION / f"round_{round_num}_marcus.md"
    round_file.write_text(content)
    print(f"✅ Marcus napisał rundę {round_num}")
    return round_file


def write_final():
    """Napisz finalny output."""
    OUTPUT.mkdir(parents=True, exist_ok=True)
    
    # Pobierz całą dyskusję
    discussion = read_discussion()
    brief = read_brief()
    
    final_content = f"""# Offer Package: Team Extension dla Fintechów Series B

## Brief
{brief[:500]}...

## Dyskusja Rady (Streszczenie)
{discussion[:1000]}...

---

# FINALNA OFERTA (Marcus)

## 1. Gap Analysis
### Current State
Fintech Series B ma funding, musi dostarczyć roadmap, ale:
- Hiring senior Scala devów trwa 6-9 miesięcy
- System nie skaluje się pod load
- Board naciska na speed-to-market
- CTO nie śpi po nocach z stressu

### Future State (z Scalac)
- 10 senior devów w 2 tygodnie
- System skaluje się, roadmap na czas
- CTO bohaterem boardu

### The Gap
Brak 10 devów = opóźnienie 6 miesięcy = utrata competitive advantage

### Financial Impact
- Cost of delay: 2M EUR w straconym revenue
- Cost of failed hiring: 150k EUR
- **Total cost of inaction: 2.15M EUR**

## 2. BrandScript (StoryBrand)
**Hero:** CTO który musi dostarczyć roadmap
**Problem:** 
- External: System crash pod loadem, hiring trwa wieki
- Internal: Stres, pressure from board
- Philosophical: "To nie powinno być tak trudne"

**Guide:** Scalac - 10 lat, 89+ firm, Clutch 4.9, fintech expertise

**Plan:**
1. Architecture Review (5 dni, darmowa ocena)
2. Team extension (devs w 2 tygodnie)
3. Handoff z knowledge transfer

**CTA:** "Zacznijmy od Architecture Review"

**Success:** CTO deliveruje roadmap, board happy, system skaluje się
**Failure:** Missed deadline, system crash, CTO gets fired

## 3. Pricing (Good-Better-Best)
**Good (Entry):** 
- 1-2 senior devów, T&M, 85 EUR/h
- 2-week onboarding guarantee
- Dla: proof of concept

**Better (Popular):**
- Team 3-5 devs, dedicated PM, 80 EUR/h
- Monthly retainer, SLA 99.9%
- Weekly architecture reviews
- Dla: core development

**Best (Enterprise):**
- 10+ devs, embedded Team Lead, 75 EUR/h  
- Full knowledge transfer program
- 24/7 support, custom onboarding
- Dla: mission-critical systems

**Decoy:** Big4 consulting at 200 EUR/h (makes us look reasonable)

## 4. Challenger Pitch
**Teach:** "Większość firm myśli że Kubernetes rozwiąże skalowanie, ale 80% wydajności leży w application layer - w event sourcing, backpressure."

**Tailor:** "Widzieliśmy podobny case w Bexio - gradual migration, zero downtime. Możemy zrobić podobnie dla Was."

**Take Control:** "Zaczynamy od Architecture Review w przyszłym tygodniu. To 5 dni, dostaniecie raport z 3 bottleneckami. Potem decyzja."

## 5. Beachhead Market
**Target:** Fintechy Series B w EU (5-50M EUR funding)
**Problem:** Potrzebują 10→25 devów w 3 miesiące
**Competition:** Turing (daleko), BairesDev (jakość?), in-house hiring (wolne)
**Access:** LinkedIn ABM, fintech conferences, referrals
**Whole Product:** Devs + onboarding + KT + SLA

---

*Wypracowane w Radzie AI Scalac przez Marcusa, z inputem Eleny, Kaia i Davida*
"""
    
    output_file = OUTPUT / "marcus_offer.md"
    output_file.write_text(final_content)
    print(f"✅ Marcus zapisał finalny output: {output_file}")
    return output_file


def main():
    """Główna logika agenta."""
    print("=" * 60)
    print("🎯 MARCUS - Offer Architect")
    print("=" * 60)
    
    # Sprawdź na której rundzie jesteśmy
    existing_rounds = list(DISCUSSION.glob("round_*_marcus.md")) if DISCUSSION.exists() else []
    round_num = len(existing_rounds) + 1
    
    print(f"\n📖 Brief: {read_brief()[:200]}...")
    print(f"\n💬 Dyskusja:\n{read_discussion()[:500]}...")
    
    if round_num <= 3:
        # Napisz kolejną rundę
        content = f"""# Runda {round_num} - Marcus

## Moja Teza
Dla fintechów Series B kluczowa jest SPEED i REDUKCJA RYZYKA, nie cena.
Good-Better-Best z 2-week guarantee to nasz winning pattern.

## Argumenty
1. **Gap Selling:** Klient traci 2M EUR na opóźnieniu. Nasz koszt to ułamek.
2. **Challenger:** Musimy nauczyć że hiring in-house = większe ryzyko niż outsourcing
3. **Mom Test:** Pytanie "Jak ostatnio skalowaliście team?" zawsze wykrywa ból

## Co Sądzę o Innych
[Do uzupełnienia po przeczytaniu innych agentów]

## Moja Propozycja
- Pricing: Good (85 EUR/h), Better (80), Best (75)
- Lead with: "2-week onboarding guarantee" 
- Challenger insight: "Hiring seniorów trwa 6 miesięcy - my dajemy w 2 tygodnie"
"""
        write_round(round_num, content)
    else:
        # Napisz final
        write_final()


if __name__ == "__main__":
    main()

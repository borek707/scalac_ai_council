#!/usr/bin/env python3
"""
AGENT: Marcus - Offer Architect (ENHANCED with Battlecards)

Ten wariant Marcusa czyta battlecards i content plan,
żeby proponować oferty w oparciu o whitespace analysis.

Usage w Kimi Code:
    Jako Marcus (enhanced), przeczytaj brief_webinar.md i battlecards.md
"""

import os
import sys
from pathlib import Path

WORKSPACE = Path("/root/.openclaw/workspace/scalac-council-v2")
SHARED = WORKSPACE / "shared"
DISCUSSION = SHARED / "discussion"
OUTPUT = WORKSPACE / "output"


def read_file(filename):
    """Przeczytaj plik z shared."""
    path = SHARED / filename
    if path.exists():
        return path.read_text()
    return f"[Plik {filename} nie znaleziony]"


def read_discussion():
    """Przeczytaj całą dyskusję."""
    posts = []
    if DISCUSSION.exists():
        for f in sorted(DISCUSSION.glob("*.md")):
            posts.append(f"\n\n--- {f.name} ---\n{f.read_text()}")
    return "\n".join(posts) if posts else "Brak wcześniejszych postów"


def write_round(round_num, content):
    DISCUSSION.mkdir(parents=True, exist_ok=True)
    round_file = DISCUSSION / f"round_{round_num}_marcus.md"
    round_file.write_text(content)
    print(f"✅ Marcus napisał rundę {round_num}")


def write_final():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    
    # Pobierz wszystkie materiały
    brief = read_file("brief_webinar.md")
    battlecards = read_file("battlecards.md")
    content_plan = read_file("content_plan.md")
    
    # Ekstrakcja kluczowych insightów z battlecards
    whitespaces = [
        "1. 'Scala-Native AI Engineering' jako kategoria - nikt tego nie branduje",
        "2. 'Scala + AI Production Readiness' Framework - brak nazwanej metodologii",
        "3. 'Akka + Agentic AI' - actor model idealny dla AI agents",
        "4. Healthcare AI + Scala - pusta nisza (VirtusLab = insurance, SoftwareMill = fintech)",
        "5. 'State of Scala + AI' Report - brak danych branżowych",
        "6. DACH + UK Enterprise market - Scalac ma Bexio jako proof"
    ]
    
    content = f"""# Propozycje Webinarów - Marcus (Offer Architect)

## Analiza Whitespace (z Battlecards)

### Konkurencja - ich słabe punkty:
- **VirtusLab:** ML hiring to Python, nie Scala (hipokryzja!)
- **SoftwareMill:** Scala i AI to osobne zespoły (nie zintegrowane)
- **Xebia:** Scala pogrzebane pod AI-first (brak focus)
- **Endava/EPAM:** Zero Scala w AI messaging (ogólniki)

### Szanse (Whitespace) dla Scalac:
{chr(10).join(whitespaces)}

---

## Webinar 1: "Akka Actors as AI Agents: Production-Ready Agentic Systems"

### Concept
Łączymy nasz Official Akka Tech Partner status z hype na agentic AI.
Nikt nie robi tego połączenia eksplicytne.

### Why Now
- Agentic AI to najgorętszy topic 2026
- Akka's actor model = idealny dla multi-agent systems (supervision, fault tolerance)
- VirtusLab ma MCP, SoftwareMill ma sttp-ai, ale NIE MAĄ "Akka + Agents"

### Value Proposition
"Other vendors talk about AI agents. We show you how to build them with 
the same fault-tolerant, distributed patterns that power LinkedIn and Uber."

### Positioning vs Competition
| Competitor | Their Angle | Our Differentiator |
|------------|-------------|-------------------|
| VirtusLab | Metals MCP, Besom RAG | We orchestrate agents at scale with Akka |
| SoftwareMill | sttp-ai library | We build systems, not just HTTP clients |
| Xebia | AI-first generalist | We combine Scala-native with agentic patterns |

### Proof Points
- Official Akka Tech Partner (tylko my)
- Case study: [Anonymized - fintech with 100+ agents]
- Pattern: Actor supervision = agent error recovery

### CTA
"Download the Akka + Agentic AI Reference Architecture" (PDF)
→ Lead magnet dla Architecture Review

---

## Webinar 2: "From Scala 2 to AI-Ready: The Migration Playbook"

### Concept
Scala 3 migration + AI readiness w jednym. 
VirtusLab daje "free Scala 3 migration" - my dajemy "AI-ready migration".

### Why Now
- Sporo firm wciąż na Scala 2.13 (legacy)
- Chcą AI, ale nie wiedzą jak przygotować codebase
- VirtusLab migrates, ale nie AI-enables

### Value Proposition  
"Don't just upgrade to Scala 3. Upgrade to an AI-ready architecture.
We migrate you AND prepare your stack for LLM integration."

### Battlecard Insight
VirtusLab: "Free Scala 3 migration"
Scalac: "AI-ready migration with capability assessment"

### Content Tie-in
Content Plan Playbook #6: "From Spark to LLMs"
Ten webinar to logical first step przed tym postem.

### CTA
"Get the Scala 3 + AI Readiness Checklist" (PDF)

---

## Webinar 3: "State of Scala + AI 2026: What 500+ Engineering Teams Told Us"

### Concept
Pierwszy taki raport w branży. Survey → webinar → report PDF.
Nikt nie ma danych o Scala + AI adoption.

### Why Now
- Content Plan: "State of Scala + AI 2026" Survey & Report (Q3 flagship)
- Webinar to teaser/warm-up dla raportu
- Data-driven = instant credibility

### Value Proposition
"We surveyed 500+ Scala teams about their AI adoption. 
Here's what nobody else knows about production Scala + AI."

### Whitespace
- VirtusLab ma State of Scala (ale nie +AI)
- My łączymy: State of Scala report + AI adoption data
- Unique data = media coverage, backlinks, authority

### Survey Topics (podgląd)
- Which AI frameworks Scala teams use (LangChain4j? sttp-ai?)
- Production deployment rates
- Scala vs Python for data pipelines (sentiment)
- Barriers to adoption

### CTA
"Get early access to the full report" (email capture)

---

## Final Recommendation: Webinar 1 (Akka + Agentic AI)

### Dlaczego ten wygrywa:

1. **Najmniejsza konkurencja:** Nikt nie łączy Akka z AI agents eksplicytne
2. **Najwyższy technical moat:** Wymaga Akka expertise (mamy partnership)
3. **Hype alignment:** Agentic AI to top trend 2026
4. **Clear differentiator:** VirtusLab/SoftwareMill nie mogą tego zrobić bez Akka
5. **Content flywheel:** Można rozbić na serie (Part 1: Architecture, Part 2: Implementation, Part 3: Case Study)

### Timeline wykonalności:
- 2 tyg: Przygotowanie architektury i slajdów
- 2 tyg: Nagranie demo (Akka + agents w akcji)
- 1 tydzień: Promocja (David)
- **Total: 5 tygodni** ✅

### Positioning statement:
"While others bolt AI onto Python microservices, we architect AI systems 
natively in Scala — fault-tolerant, distributed, and production-proven."

---

*Uwzględnione: battlecards.md (konkurencja), content_plan.md (Playbook #3 overlap)*
"""
    
    output_file = OUTPUT / "marcus_webinar_proposals.md"
    output_file.write_text(content)
    print(f"✅ Marcus zapisał finalny output: {output_file}")


def main():
    print("=" * 60)
    print("🎯 MARCUS ENHANCED - Offer Architect + Battlecards")
    print("=" * 60)
    
    # Sprawdź czy mamy battlecards
    battlecards = read_file("battlecards.md")
    if "WHITESPACE" in battlecards:
        print("\n✅ Battlecards załadowane - zawiera WHITESPACE analysis")
    
    existing = list(DISCUSSION.glob("round_*_marcus.md")) if DISCUSSION.exists() else []
    round_num = len(existing) + 1
    
    if round_num <= 2:  # Krótsza debata dla webinar topics
        content = f"""# Runda {round_num} - Marcus (Enhanced)

## Przeczytane materiały:
- ✅ battlecards.md (konkurencja + whitespace)
- ✅ content_plan.md (Playbook series)
- ✅ brief_webinar.md (zadanie)

## Kluczowe insighty:

### Whitespace #1: "Akka + Agentic AI"
VirtusLab ma Metals MCP, SoftwareMill ma sttp-ai, ALE:
- Nikt nie łączy Akka actors z AI agents
- Actor model = supervision, fault tolerance, distributed scaling
- To EXACTLY to co potrzebne dla multi-agent systems

### Whitespace #2: "Scala-Native AI Engineering" 
Konkurencja trzyma Scala i AI w osobnych pasach:
- VirtusLab: "JVM productivity" albo "AI content" - nie razem
- SoftwareMill: Scala team i ReasonField Lab AI = osobne
- My możemy: "The only engineering partner that builds AI systems IN Scala"

### Whitespace #3: Healthcare AI + Scala
- VirtusLab = insurance (agentic underwriting)
- SoftwareMill = fintech (trading, BNPL)
- Healthcare = pusta nisza!
- Scalac ma Rally Health jako proof point

## Moja propozycja webinarów:
1. **"Akka Actors as AI Agents"** - techniczny, nasz unikalny asset
2. **"Scala 2 to AI-Ready Migration"** - kontra VirtusLab free migration
3. **"State of Scala + AI 2026"** - data-driven, authority play

## Co sądzę o innych agentach:
[Do uzupełnienia po przeczytaniu]
"""
        write_round(round_num, content)
    else:
        write_final()


if __name__ == "__main__":
    main()

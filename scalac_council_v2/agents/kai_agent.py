#!/usr/bin/env python3
"""
AGENT: Kai - Copywriter
Rola: Landing pages, email sequences, ad copy

Uruchomienie (dowolny IDE):
    Wklej zawartość prompts/kai_prompt.md do nowego chatu.
    Lub: python agents/kai_agent.py (Claude Code z bash)
"""

from pathlib import Path

# Ścieżki relatywne — działa w każdym IDE, na każdej maszynie
WORKSPACE = Path(__file__).parent.parent  # scalac_council_v2/
SHARED = WORKSPACE / "shared"
DISCUSSION = SHARED / "discussion"
OUTPUT = WORKSPACE / "output"

SYSTEM_PROMPT = """Jesteś Kai, Główny Copywriter w Scalac.

## Twoja Tożsamość
Były dziennikarz tech który został copywriterem B2B. Rozumiesz jak pisać żeby konwertować.
Twoja supermoc: zamiana technicznego żargonu w język który CTO kupuje.

## Twoje Książki
- Everybody Writes: Writing for web
- They Ask, You Answer: Big 5 content
- Content Chemistry: SEO + content
- The Copywriter's Handbook: AIDA, formulas
- Obviously Awesome: Positioning
- On Writing Well: Clarity

## Twoje Frameworki
- AIDA: Attention, Interest, Desire, Action
- Big 5: Cost, Problems, Comparisons, Reviews, Best
- 4 U's: Useful, Urgent, Unique, Ultra-specific
- PAS: Problem, Agitate, Solution
- StoryBrand: Hero/Guide narrative

## TWOJA WIEDZA RYNKOWA (Battlecards + Content Plan — Marzec 2026)

### Luka Narracyjna Konkurencji (TWOJA ZŁOTA OKAZJA):
Nikt na rynku NIE ma spójnego messagingu "Scala+AI":
- VirtusLab: blog posty o AI, ale fragmentaryczne — brak jednej jasnej propozycji
- SoftwareMill: ReasonField Lab AI ≠ Scala team — CTO dostaje dwa osobne pitch'e
- Xebia: xef.ai jest Kotlin-first, nie Scala — ich AI tools nie są Scala-native
- Endava/EPAM: zero Scala+AI messaging w ogóle

### Positioning Statement (do opracowania):
"Jedyni, gdzie Twoi Scala engineerzy SĄ Twoimi AI engineerami."
(Uderza bezpośrednio w weakness SoftwareMill i VirtusLab)

### Konkretne Messaging Claims (weryfikowalne, używaj!):
- Official Akka Tech Partner — jedyny w EU (link do potwierdzenia)
- scalac.ai — dedykowany brand Scala+AI (żaden rywal nie ma odpowiednika)
- State of Scala report — citeable authority
- 23 Clutch reviews (vs VirtusLab 8, SoftwareMill 30)
- "Integration in 14 days" vs "6+ months hiring"

### Słabości Competitors (atakuj implicite, nie nominatywnie):
- "Python-based AI teams who handoff to your Scala team" → SoftwareMill/Xebia jab
- "Compiler maintainers who haven't shipped production AI" → VirtusLab jab
- "Global consultancy where Scala is one checkbox among 50 services" → Xebia jab

### Content Plan — Struktura którą Twoje copy wspiera:
**Scala+AI Playbook Blog Series (Apr–Sep 2026, 10 postów):**
1. "Why Scala Is the Best-Kept Secret in AI Engineering" — keyword: scala ai programming
2. "Building a RAG Pipeline in Scala 3" — keyword: scala rag pipeline
3. "Akka Actors as AI Agents" — keyword: akka ai agents
4. "MCP Servers in Scala" — keyword: mcp server scala
5. "Type-Safe AI: How Scala Prevents Silent Failures" — keyword: type safe machine learning

**Flagships**:
- Czerwiec 2026: "The Scala+AI Manifesto" — 2000 słów (door-opener do Tier 1 accounts)
- Wrzesień 2026: "State of Scala+AI 2026" Survey Report

**Landing page Big 5 (They Ask, You Answer):**
- Cost: "Ile kosztuje team extension vs. hiring?"
- Problems: "Dlaczego hiring Scala devów trwa 6 miesięcy?"
- Comparisons: "Scalac vs. VirtusLab vs. SoftwareMill" (landing page /compare)
- Reviews: 23 Clutch reviews, case studies
- Best: "Kto jest najlepszym Scala+AI partnerem w Europie?"

## Twój Styl
- Prosty > Mądry (clarity > cleverness)
- "You" focused (nie "we" focused)
- Specific numbers ("2 weeks" nie "fast", "14 days" nie "quick onboarding")
- Challenger insights (question status quo)

## W Debacie
- Krytykuj techniczny żargon Marcusa ("czy CTO to rozumie w 30 sek?")
- Upraszczaj przesadne claims Eleny
- Walcz o czytelność — CTO ma 30 sekund na landing page
- Sprawdzaj czy messaging odróżnia nas od VirtusLab
- Pytaj: "Czy to brzmi jak coś co CTO by kliknął?"


def read_discussion():
    posts = []
    if DISCUSSION.exists():
        for f in sorted(DISCUSSION.glob("*.md")):
            posts.append(f"\n\n--- {f.name} ---\n{f.read_text()}")
    return "\n".join(posts) if posts else "Brak wcześniejszych postów"


def write_round(round_num, content):
    DISCUSSION.mkdir(parents=True, exist_ok=True)
    round_file = DISCUSSION / f"round_{round_num}_kai.md"
    round_file.write_text(content)
    print(f"✅ Kai napisał rundę {round_num}")


def write_final():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    
    content = """# Copy Package: Team Extension dla Fintechów Series B

## Landing Page

### Hero Section
```
Scale Your Fintech Team in 2 Weeks—Not 6 Months

Stop losing revenue to hiring delays. Get senior Scala developers 
who integrate in 14 days, not months.

[CTA: Get Architecture Review] [Secondary: See Case Studies]
```

### Problem Section (Big 5)
```
## The Hidden Cost of Slow Hiring

Every month you wait for senior developers costs you:
- €150K+ in delayed features
- Competitive disadvantage
- CTO stress and board pressure

One client calculated they lost €2M in revenue 
because their hiring took 8 months instead of 2 weeks.

[Read Bexio Case Study]
```

### Solution Section
```
## Team Extension That Actually Works

**2-Week Onboarding Guarantee**
Your developers are productive in 14 days, or we replace them free.

**Fintech Expertise Built-In**
89+ projects including Swiss banks, German healthtech, and EU fintechs.

**Zero Knowledge Silos**
Built-in knowledge transfer. Your team owns the code, always.
```

### Social Proof
```
## Trusted By Growth-Stage Fintechs

"Scalac's team integrated so fast, our CTO thought they were 
internal hires. Best outsourcing decision we made."
— CTO, Bexio (Swiss fintech, 50K+ customers)

⭐ 4.9/5 on Clutch
⭐ 89+ successful projects
⭐ 90% client retention
```

### Pricing Section
```
## Simple, Transparent Pricing

**Good** — 1-2 Developers
€85/hour • T&M • 2-week onboarding

**Better** — Team 3-5 [POPULAR]
€80/hour • Monthly retainer • Dedicated PM • SLA

**Best** — 10+ Developers  
€75/hour • Embedded Team Lead • Full KT program • 24/7 support

💡 All tiers include our 2-week guarantee
```

### FAQ (SEO + Objections)
```
## Frequently Asked Questions

**How fast can you start?**
We typically have developers ready within 5-10 business days. 
For urgent needs, we've started in 48 hours.

**What if a developer doesn't fit?**
Replacement guarantee — we swap them in 48 hours, no questions asked.

**Do they work our hours?**
Yes. Full timezone alignment with EU/US teams.

**Is our IP protected?**
Absolutely. All contracts include comprehensive IP assignment and NDAs.

**What about compliance (PCI-DSS, GDPR)?**
We have specific experience with fintech compliance. Our developers 
understand security requirements from day one.
```

---

## Email Sequence (5 emails)

### Email 1: Welcome (Day 0)
```
Subject: Your Architecture Review request + next steps

Hi [Name],

Thanks for requesting our free Architecture Review.

Here's what happens next:
1. I'll reach out within 24h to schedule
2. 5-day assessment of your system
3. Report with 3 critical bottlenecks

While you wait, here's how we helped Bexio 
scale 2x without downtime:
[Case Study Link]

Talk soon,
[Name]
Scalac
```

### Email 2: Education (Day 3)
```
Subject: The #1 mistake CTOs make when scaling teams

Hi [Name],

Most CTOs think their scaling problem is "not enough developers."

But after 89+ projects, we see the real issue:
**Architecture that doesn't support growth.**

Adding developers to a broken architecture 
is like adding horsepower to a car with flat tires.

That's why we always start with Architecture Review.

We look at:
- Event sourcing maturity
- Backpressure handling
- Circuit breakers and fallbacks
- Database bottlenecks

No sales pitch. Just technical insights.

[Schedule Your Review]

Best,
[Name]
```

### Email 3: Social Proof (Day 7)
```
Subject: "2 weeks vs 6 months" — Bexio case study

Hi [Name],

Quick story:

Bexio (Swiss fintech) needed 5 senior Scala developers.

Their options:
- Internal hiring: 6+ months, uncertain quality
- Scalac: 2 weeks, proven fintech expertise

They chose us.

Results after 12 months:
✓ 2x system performance
✓ Zero downtime migration
✓ Team expanded from 5→8 developers
✓ CTO promoted to VP Engineering

Full case study:
[Bexio Case Study]

Want similar results?
[Reply to discuss your project]

Best,
[Name]
```

### Email 4: Objection Handler (Day 14)
```
Subject: The "outsourcing risk" myth

Hi [Name],

I get it. Outsourcing feels risky.

"What if the developers don't understand our domain?"
"What if they leave mid-project?"
"What if code quality is poor?"

Fair concerns. Here's how we address them:

**Domain Knowledge**
Our developers have fintech experience. They understand 
compliance, transaction integrity, and audit requirements.

**Retention**
Average engagement: 18 months. When someone leaves, 
we do knowledge transfer to replacement. Zero lost knowledge.

**Quality**
All code goes through our internal review. 
Plus: built-in KT so your team understands everything.

Still unsure?
Start with 1 developer for 2 weeks. 
If it doesn't work, you pay nothing.

[Start Risk-Free Trial]

Best,
[Name]
```

### Email 5: CTA (Day 21)
```
Subject: Last chance: Architecture Review

Hi [Name],

This is my last email about the Architecture Review.

If you're still considering it, here's what you get:

✓ 5-day system assessment
✓ Identification of 3 critical bottlenecks  
✓ Roadmap for scaling
✓ No cost, no obligation

One client said this review saved them 
6 months of wrong turns.

Worth 30 minutes of your time?

[Book Now] or [Not interested — remove me]

Either way, thanks for your time.

[Name]
Scalac
```

---

## LinkedIn Ad Variants

### Variant A: Pain-Focused
```
Hiring senior Scala developers?

6 months average time-to-hire.
€150K+ cost of delay.

We do it in 2 weeks.

→ scalac.io/team-extension
```

### Variant B: Social Proof
```
"Scalac integrated faster than our internal hires."
— CTO, Swiss fintech (50K+ customers)

Scale your team without the hiring headache.

→ Book free Architecture Review
```

### Variant C: Challenger
```
Kubernetes won't fix your scaling problem.

80% of performance is in application layer:
• Event sourcing
• Backpressure
• Circuit breakers

We fix the real issues.

→ scalac.io/fintech-scaling
```

---

## Voice & Tone Guidelines

✅ DO:
- Specific numbers ("2 weeks", "€150K")
- "You" focused
- Challenger insights
- Proof over claims

❌ DON'T:
- Generic superlatives ("best", "leading")
- Buzzwords ("synergy", "leverage")
- Feature lists without benefits
- Passive voice

---

*Wypracowane w Radzie AI Scalac przez Kaia, z inputem Marcusa, Eleny i Davida*
"""
    
    output_file = OUTPUT / "kai_copy.md"
    output_file.write_text(content)
    print(f"✅ Kai zapisał finalny output: {output_file}")


def main():
    print("=" * 60)
    print("📝 KAI - Copywriter")
    print("=" * 60)
    
    existing = list(DISCUSSION.glob("round_*_kai.md")) if DISCUSSION.exists() else []
    round_num = len(existing) + 1
    
    if round_num <= 3:
        content = f"""# Runda {round_num} - Kai

## Moja Teza
Marcus i Elena mają solidny foundation, ale ich messaging 
jest ZA TECHNICZNY dla fintech CTOs.

CTO chce usłyszeć:
- "Scale in 2 weeks" nie "Team extension model"
- "Save €2M" nie "Gap Analysis"
- "Zero downtime" nie "Gradual migration"

## Co Sądzę o Innych

### Marcus
Twój BrandScript jest świetny, ale Challenger Pitch brzmi 
jak college lecture. Skróć do:
"Most CTOs think Kubernetes solves scaling. It doesn't. 
80% performance is in application layer. We fix that."

### Elena  
Twój lejek jest realistyczny, ale "MQL/SQL" to marketing speak.
Dla landing page użyj:
- "Free Architecture Review" (nie "Lead Magnet")
- "Talk to our team" (nie "SQL conversion")

### David
Czekam na Twój Dream 100. Bez tego moje "Get Architecture Review" 
nie ma kogo targetować.

## Moja Propozycja
- Lead with SPEED (2 weeks) i SAVINGS (€2M)
- Use "Architecture Review" jako główny CTA
- Email sequence: Education → Proof → Risk Reversal → CTA
- Challenger hook: "Kubernetes won't fix your scaling problem"

## Moje Pytania
1. David: Masz już Dream 100 listę?
2. Marcus: Czy możemy dodać konkretny ROI calculator do landing page?
3. Elena: Jaki jest realistyczny timeline od "Architecture Review" do "Closed"?
"""
        write_round(round_num, content)
    else:
        write_final()


if __name__ == "__main__":
    main()

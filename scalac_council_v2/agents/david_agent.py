#!/usr/bin/env python3
"""
AGENT: David - Lead Strategist
Rola: ABM, outbound, lead generation

Uruchomienie (dowolny IDE):
    Wklej zawartość prompts/david_prompt.md do nowego chatu.
    Lub: python agents/david_agent.py (Claude Code z bash)
"""

from pathlib import Path

# Ścieżki relatywne — działa w każdym IDE, na każdej maszynie
WORKSPACE = Path(__file__).parent.parent  # scalac_council_v2/
SHARED = WORKSPACE / "shared"
DISCUSSION = SHARED / "discussion"
OUTPUT = WORKSPACE / "output"

SYSTEM_PROMPT = """Jesteś David, Strateg Leadów w Scalac.

## Twoja Tożsamość
Były SDR który został Account Executive w SaaS. Rozumiesz cold outreach i ABM.
Twoja supermoc: zamiana strategii w konkretne konta i sekwencje.

## Twoje Książki
- Account-Based Marketing: ABM strategy
- The ABM Playbook: Tiers, execution
- No Forms, No Spam, No Cold Calls: Inbound
- LinkedIn Content Strategy: Social selling
- The Ultimate Sales Machine: Follow-up
- Fanatical Prospecting: Activity metrics
- Sales Engagement: Sequences, cadences

## Twoje Frameworki
- ABM Tiers: 1-to-1, 1-to-few, 1-to-many
- Dream 100: Focus 80% effort na 100 kont
- Signal-Based Selling: Intent data + triggers
- 12-Touch Cadence: Omni-channel sequence
- MEDDIC: Qualification (współpraca z Eleną)

## TWOJA WIEDZA RYNKOWA (Battlecards — Marzec 2026)

### Mapa Pionów Konkurencji (gdzie szukać niedosłużonych klientów):

| Konkurent | Najsilniejsze Piony | Znani Klienci | Vulnerability |
|-----------|--------------------|-----------------|----|
| VirtusLab | Retail, Insurance, Logistics, FinTech | Sourcegraph | ML team Python-centric — Scala+AI przepada |
| SoftwareMill | **FinTech** (STRONGEST), Healthcare, Retail | Paidy, SwissBorg | 2 osobne teamy, CTO jest zdezorientowany |
| Xebia | Banking/FS, Insurance, Retail, Media | ING (52K empls) | Premium pricing — mid-market nie może sobie pozwolić |
| Endava | Digital transformation | 30 agentic AI projects | ZERO Scala → każdy ich client używający Scali = warm lead |
| EPAM | Enterprise generalist | brak Scala+AI | Jak wyżej |

### Signal-Based Selling Triggers (kiedy atakować konto):
1. **Series B funding announcement** EU fintech → szybko skalują team (idealny timing)
2. **Job posting: "Scala developer"** na LinkedIn → mają problem hiring
3. **Konferencje**: Scala Days, Spark Summit, Akka meetupy → warm leads
4. **Competitor klient** publikuje case study → outreach z "what's next in AI?"
5. **Endava/EPAM engagement** z firmą używającą Scali → "Twój vendor nie ma Scala+AI"
6. **Nowe AI launch** (NVIDIA, OpenAI) → "Jak to wpłynie na Twój Scala stack?"

### Landminy do sadzenia w cold outreach:
1. "Jak Twój obecny partner łączy inwestycję w Scalę z AI roadmapem?"
2. "Czy Twój Scala team i AI team to te same osoby?"
3. "Czy masz produkcyjny system gdzie Scala i AI są zintegrowane?"
4. "Kto w Twoim dashboardzie dziś odpowiada za Scala+AI delivery?"

### Dream 100 Hunting Grounds:
- **Tier 1 (10 kont)**: EU fintechs Series B, €5-50M funding, potrzebują 5→15 devów
- **Tier 2 (15 kont)**: Companies currently using Akka → już rozumieją wartość
- **Tier 3 (25 kont)**: Companies exiting VirtusLab/SoftwareMill (watch LinkedIn posts)
- **Whitespace**: Endava/EPAM clients z Scala workloads — łatwy steal

### Wsparcie ze Strony Content (używaj jako door-openers):
- LinkedIn Scalac posts 3x/tydzień → warm intent przed cold outreach
- Blog Playbook posts → SEO inbound ("scala ai programming", "akka ai agents")
- Reddit r/scala weekly → community trust building
- Jun: "Scala+AI Manifesto" → door-opener dla Tier 1
- Sep: "State of Scala+AI 2026" survey report → excuse to reach out

### Metryki Celowe:
- Goal: 10 meetings → 3 opportunities → 1-2 closed deals w 90 dni
- Pipeline target: 500K PLN
- Average deal: ~180K PLN → potrzeba 3 dealów

## Twój Styl
- Konkrety > Ogólniki (zawsze podaj liczby)
- Data-driven (ile kont, jaka konwersja)
- Execution-focused (co kiedy kto robi)
- Account-centric (konkretne firmy, nie segmenty)

## W Debacie
- Walcz o wykonalność planu Eleny
- Pytaj o konkretne konta ("Które 50 firm w EU spełnia kryteria?")
- Weryfikuj assumptive metrics danymi z battlecards
- Przypominaj o timelines i resources
- Wnoś dane konkurencyjne kiedy dyskusja jest za ogólna


def read_discussion():
    posts = []
    if DISCUSSION.exists():
        for f in sorted(DISCUSSION.glob("*.md")):
            posts.append(f"\n\n--- {f.name} ---\n{f.read_text()}")
    return "\n".join(posts) if posts else "Brak wcześniejszych postów"


def write_round(round_num, content):
    DISCUSSION.mkdir(parents=True, exist_ok=True)
    round_file = DISCUSSION / f"round_{round_num}_david.md"
    round_file.write_text(content)
    print(f"✅ David napisał rundę {round_num}")


def write_final():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    
    content = """# ABM Strategy: Team Extension dla Fintechów Series B

## Executive Summary
- Target: 50 accounts (Tier 1: 10, Tier 2: 15, Tier 3: 25)
- Goal: 10 meetings, 3 opportunities, 1-2 closed deals
- Timeline: 90 days
- Focus: "Spears" (outbound ABM) jako główne źródło

---

## Dream 100 (Fintech Series B EU)

### Tier 1: 1-to-1 ABM (10 accounts)
Kryteria:
- Series B, 10-50M EUR funding
- Hiring 5+ developers (job postings)
- Scala/Java w stacku
- EU-based

Przykładowe konta (do research):
- Trade Republic (DE)
- N26 (mature, but try)
- Klarna (mature)
- Pleo (DK)
- Lunar (DK)
- Vivid (DE)
- Qonto (FR)
- Spendesk (FR)
- SumUp (UK/DE)
- Mollie (NL)

### Tier 2: 1-to-Few ABM (15 accounts)
Kryteria:
- Series A/B, 5-30M EUR
- Fintech/software
- Growth stage

Segmenty:
- German fintechs (5)
- Nordic fintechs (5)
- French fintechs (5)

### Tier 3: 1-to-Many ABM (25 accounts)
- Pozostałe fintech Series B w EU
- Automated sequences
- Intent-based triggering

---

## Account Research Template

Dla każdego Tier 1 account:

```
Account: [Nazwa]
Funding: [Round + Amount]
Employees: [Count]
Tech Stack: [From job postings]
Hiring: [Active roles]

Key Stakeholders:
- CTO: [Name, LinkedIn]
- VP Engineering: [Name, LinkedIn]
- Tech Lead: [Name, LinkedIn]

Trigger Events:
- Recent funding: [Date]
- Expansion news: [...]
- Hiring surge: [...]

Pain Signals:
- Job postings for 5+ devs
- "Urgent" hiring mentions
- Glassdoor reviews mentioning workload

Personalization Angle:
[Specific insight for outreach]
```

---

## Outreach Sequences

### Tier 1: 12-Touch Omni-Channel

#### Touch 1: LinkedIn Connection (Day 0)
```
Hi [Name],

Saw [Company] is scaling the engineering team post-Series B. 
We helped Bexio scale 2x without downtime.

Worth a conversation?

[Your name]
```

#### Touch 2: Email (Day 2)
```
Subject: Architecture bottleneck at [Company]?

Hi [Name],

Most fintechs we work with hit the same wall post-Series B:
- Hiring takes 6+ months
- System doesn't scale with growth
- Team burnout

We helped Bexio add 10 Scala developers in 2 weeks 
and improve performance 2x.

Worth a 15-min call to see if similar approach works for [Company]?

[CTA: Book time] or [Reply with your thoughts]

[Your name]
Scalac

P.S. Start with free Architecture Review if easier — 5 days, 
zero commitment, report with 3 critical bottlenecks.
```

#### Touch 3: LinkedIn Voice (Day 5)
```
Short voice message referencing their specific hiring challenge.
```

#### Touch 4: Email (Day 7) - Value
```
Subject: How Bexio scaled 2x (case study)

[Case study summary + lessons applicable to their company]
```

#### Touch 5: LinkedIn Comment (Day 10)
```
Engage with their recent post thoughtfully.
```

#### Touch 6: Email (Day 12) - Breakup
```
Subject: Should I close your file?

Hi [Name],

I reached out a few times about scaling [Company]'s engineering team.

Haven't heard back — which usually means:
1. Not a priority right now
2. Already solved the problem
3. Just busy :)

Either way, should I close your file or is this worth a 10-min call?

[Your name]
```

#### Touches 7-12: Mix of:
- Video message (Loom)
- Direct mail (handwritten note)
- LinkedIn article mention
- Warm intro attempt
- Event invite
- Retargeting ad

---

### Tier 2: 8-Touch Sequence

Skrócona wersja Tier 1, mniej personalization.

### Tier 3: 5-Touch Automated

Automated sequences z personalization tokens.

---

## Signal-Based Selling

### Intent Signals (monitorować)
- Job postings (5+ dev roles)
- Funding announcements
- Expansion news
- Tech stack changes
- Leadership changes (new CTO)

### Trigger-Based Plays

#### "Hiring Surge" Play
Kiedy: Account post 5+ dev jobs w 30 dni
Akcja: Priority outreach z "We can have devs ready in 2 weeks"

#### "Post-Funding" Play
Kiedy: Series B announcement
Akcja: Outreach w ciągu 48h z scaling focus

#### "Competitor Win" Play
Kiedy: Case study z podobnej firmy opublikowane
Akcja: "See how [Competitor] solved similar problem"

---

## Metrics & Targets

### Monthly Targets
| Metric | Month 1 | Month 2 | Month 3 |
|--------|---------|---------|---------|
| Accounts contacted | 20 | 20 | 10 |
| Meetings booked | 3 | 4 | 3 |
| Opportunities | 1 | 1 | 1 |
| Pipeline | 180k | 180k | 180k |

### Key Metrics
- Response rate target: 15-20%
- Meeting rate: 10%
- Show rate: 80%
- Opp conversion: 30%

---

## Tools Stack

### Research
- LinkedIn Sales Navigator (accounts)
- Apollo.io (contacts + sequences)
- Crunchbase (funding data)
- BuiltWith (tech stack)

### Engagement
- Apollo.io (email sequences)
- LinkedIn (direct outreach)
- Loom (video messages)
- Sendoso (direct mail)

### Intent
- Bombora (intent data)
- G2 (review signals)
- Job posting alerts

---

## Collaboration with Other Agents

### From Marcus (Offer)
- Use "2-week guarantee" w subject lines
- Mention Architecture Review jako low-friction entry
- Pricing transparency dla qualification

### From Elena (Funnel)
- Target 10 meetings dla 3 opportunities
- Use MEDDIC w discovery calls
- Apply JOLT na wahanie

### From Kai (Copy)
- Use landing page w email signatures
- Challenger messaging w cold outreach
- Case studies jako social proof

---

## First 30 Days Action Plan

### Week 1: Research
- [ ] Finalize Tier 1 list (10 accounts)
- [ ] Research each account (stakeholders, signals)
- [ ] Prepare personalization snippets

### Week 2: Setup
- [ ] Load contacts to Apollo
- [ ] Create sequences
- [ ] Set up LinkedIn Sales Nav

### Week 3: Launch
- [ ] Start Tier 1 outreach
- [ ] Monitor responses
- [ ] Iterate messaging

### Week 4: Optimize
- [ ] Review metrics
- [ ] Double down na działające
- [ ] Add Tier 2 accounts

---

*Wypracowane w Radzie AI Scalac przez Davida, z inputem Marcusa, Eleny i Kaia*
"""
    
    output_file = OUTPUT / "david_abm.md"
    output_file.write_text(content)
    print(f"✅ David zapisał finalny output: {output_file}")


def main():
    print("=" * 60)
    print("🎯 DAVID - Lead Strategist")
    print("=" * 60)
    
    existing = list(DISCUSSION.glob("round_*_david.md")) if DISCUSSION.exists() else []
    round_num = len(existing) + 1
    
    if round_num <= 3:
        content = f"""# Runda {round_num} - David

## Moja Teza
Marcus i Elena planują zbyt OGÓLNE podejście.
ABM wymaga konkretnych kont, nie "fintech Series B w EU".

Mam listę 10 Tier 1 accounts gotowych do outreach.

## Co Sądzę o Innych

### Marcus
Twoja oferta jest świetna, ale "Architecture Review" 
nie zadziała jeśli nie dotrzemy do CTO.

Moja korekta: Dodaj "Hiring 5+ developers? We can help in 2 weeks" 
jako pierwszy touch.

### Elena
Twój lejek zakłada 160 leads. To NIE REALISTYCZNE 
dla fintech ABM w 90 dni.

Realistycznie:
- 50 accounts contacted
- 10 meetings  
- 3 opportunities
- 1-2 closed

### Kai
Twój landing page CTA "Get Architecture Review" jest słaby.
ABM wymaga konkretnego hooka.

Lepszy CTA: "See how [Similar Company] scaled 2x"

## Moja Propozycja: Dream 100

### Tier 1 (1-to-1 ABM) - 10 accounts:
1. Trade Republic (DE) - Recent expansion, hiring
2. Pleo (DK) - Series B, scaling
3. Vivid (DE) - Growth stage, tech stack
4. Qonto (FR) - Series C but try
5. Spendesk (FR) - Expansion
6. SumUp (UK/DE) - Always hiring
7. Mollie (NL) - Growth
8. Lunar (DK) - Scaling
9. Tide (UK) - Tech team growth
10. FinCompare (DE) - Series B

Dla każdego przygotuję:
- Stakeholder map
- Personalization angle
- 12-touch sequence

## Moje Pytania
1. Marcus: Czy macie case study z każdego z tych sub-segmentów (DE, DK, FR)?
2. Elena: Czy 10 meetings wystarczy dla 3 opportunities? (30% conversion)
3. Kai: Czy możesz przygotować wariant landing page dla każdego Tier 1 account?
"""
        write_round(round_num, content)
    else:
        write_final()


if __name__ == "__main__":
    main()

# Rada AI - Scalac Marketing Council
## Kompletny System Marketingowych AI Doradców

> 🚀 **Start Here:** 
> - **Chcesz użyć od razu?** → Przewiń do ["🚀 Jak Używać - 4 Sposoby"](#-jak-używać---4-sposoby)
> - **Masz 15 minut?** → Przeczytaj [`QUICKSTART.md`](QUICKSTART.md)
> - **Używasz Kimi?** → Zobacz [`KIMI_GUIDE.md`](KIMI_GUIDE.md)
> - **Programista?** → Zobacz [`INTEGRATION.md`](INTEGRATION.md)

---

## Co To Jest?

Rada AI to zespół 5 specjalistycznych agentów AI, każdy z osobowością opartą na 5-6 książkach biznesowych, którzy współpracują aby budować i optymalizować marketing i sprzedaż Scalac.

**Kluczowa zasada:** 80% focus na CORE (team extension, distributed systems), 20% na AI (Sovereign AI, RAG).

---

## 5 Agentów

### 1. Marcus - Architekt Oferty
**Książki:** Crossing the Chasm, Monetizing Innovation, Building a StoryBrand, The Challenger Sale, Product-Led Growth, The Mom Test  
**Rola:** Projektowanie ofert, pricing, positioning  
**Output:** Offer Packages, BrandScripts, Challenger Pitches

### 2. Elena - Architektka Lejków
**Książki:** From Impossible to Inevitable, Predictable Revenue, Hacking Growth, Demand-Side Sales, The Qualified Sales Leader, Never Split the Difference  
**Rola:** Projektowanie lejków sprzedażowych, eksperymenty, kwalifikacja  
**Output:** Funnel Designs, MEDDIC Qualifications, Growth Experiments

### 3. Kai - Główny Copywriter
**Książki:** Everybody Writes, They Ask You Answer, Content Chemistry, The Copywriter's Handbook, Obviously Awesome, On Writing Well  
**Rola:** Pisanie copy które konwertuje  
**Output:** Landing pages, Case studies, Email sequences, Ad copy

### 4. Sofia - Strateg Treści
**Książki:** Content Inc., Killing Marketing, The Content Strategy Toolkit, Epic Content Marketing, Product-Led SEO, Made to Stick  
**Rola:** Planowanie contentu, SEO, editorial calendar  
**Output:** Content calendars, SEO strategy, Epic content

### 5. David - Strateg Leadów
**Książki:** Account-Based Marketing, The ABM Playbook, No Forms No Spam, LinkedIn Content Strategy, The Ultimate Sales Machine, Fanatical Prospecting, Data-Driven Marketing  
**Rola:** Generowanie leadów, outbound, ABM  
**Output:** ABM campaigns, Outbound sequences, Lead gen strategy

---

## 🚀 Jak Używać - 4 Sposoby

Wybierz jeden z poniższych sposobów korzystania z Rady AI:

---

### SPOSÓB 1: Kimi Code (Najłatwiejszy - Tutaj i Teraz)

**Użyj mnie (Kimi) jako orchestratora.** Ja zarządzam wszystkimi 5 agentami w naszej rozmowie.

#### Szybki Start:
```
Jako Marcus zaprojektuj ofertę "Team Extension dla fintechów Series B".
Przeczytaj swój system_prompt.md z AGENTS/marcus_offer_architect/
Użyj: Gap Selling, StoryBrand, Good-Better-Best.
```

#### Potem przejdź do kolejnych agentów:
```
Jako Elena zbuduj lejek dla oferty Marcusa wyżej.
Przeczytaj swój prompt z AGENTS/elena_funnel_architect/
Użyj: MEDDIC, JOLT, Three Pipelines.
```

#### Lub uruchom całą Radę naraz:
```
Uruchom Radę AI dla projektu "Sovereign AI dla banków":
1. Marcus - oferta
2. Elena - lejek  
3. Kai - landing page
4. David - ABM
5. Sofia - content strategy

Przeczytajcie swoje system_prompt.md z folderu AGENTS/.
```

**✅ Zalety:** Zero setup, działa od razu, widzę wszystkie pliki
**❌ Wady:** Trzeba ręcznie przełączać agentów komendami

**📖 Szczegóły:** `KIMI_GUIDE.md`

---

### SPOSÓB 2: ChatGPT / Claude (Osobne Chaty)

**Otwórz 5 niezależnych chatów i wklej prompt każdego agenta.**

#### Krok po kroku:
1. Otwórz ChatGPT Plus lub Claude Pro
2. Stwórz 5 nowych chatów, nazwij: "Marcus", "Elena", "Kai", "Sofia", "David"
3. W każdym wklej odpowiedni `system_prompt.md`
4. Rozmawiaj z każdym osobno
5. Ręcznie kopiuj handoff'y między chatami

#### Przykład dla Marcusa:
**Wklejasz w pierwszą wiadomość:**
```
[Cała zawartość AGENTS/marcus_offer_architect/system_prompt.md]
```

**Potem piszesz:**
```
Zaprojektuj ofertę Team Extension dla fintechów Series B.
```

**Marcus odpowiada** (pracuje zgodnie ze swoją osobowością)

**Kopiujesz odpowiedź** → wklejasz do Eleny → itd.

**✅ Zalety:** Każdy agent ma "pamięć", możesz wracać do chatów
**❌ Wady:** Ręczne handoff'y, 5 okien do śledzenia

**📖 Szczegóły:** `INTEGRATION.md` (Opcja 2)

---

### SPOSÓB 3: Python Orchestrator (Dla Developerów)

**Automatycznie uruchamia wszystkich 5 agentów przez API.**

#### Setup (5 minut):
```bash
# 1. Zainstaluj
pip install openai

# 2. Dodaj API key
export OPENAI_API_KEY="sk-..."

# 3. Uruchom projekt
python orchestrator.py --project "Team Extension" --type CORE --export
```

#### Co się dzieje:
1. Skrypt czyta prompt Marcusa → wysyła do OpenAI API → zapisuje wynik
2. Czyta prompt Eleny + wynik Marcusa → wysyła do API → zapisuje
3. Kai i David równolegle
4. Sofia na końcu
5. Wszystko w `projects/nazwa.json`

#### Koszt:
- ~$1-2 per projekt (5-10 wywołań API)
- GPT-4 = lepsze wyniki, droższe
- GPT-3.5 = szybsze, tańsze

**✅ Zalety:** Automatyczne handoff'y, eksport do JSON, skalowalne
**❌ Wady:** Wymaga API key, programowania

**📖 Szczegóły:** `INTEGRATION.md` (Opcja 1)

---

### SPOSÓB 4: Make.com / Zapier (No-Code Automation)

**Zbuduj workflow w Make.com bez kodu.**

#### Setup:
1. Wejdź na make.com (darmowe do 1000 operacji)
2. Stwórz "Scenario"
3. Trigger: Webhook lub Google Sheets
4. Moduły: OpenAI (5x - jeden per agent)
5. Output: Google Docs / Notion / Email

#### Workflow:
```
Webhook (trigger) 
  → OpenAI (Marcus) 
  → OpenAI (Elena) 
  → [Kai + David równolegle]
  → OpenAI (Sofia)
  → Google Docs (output)
```

**✅ Zalety:** Zero kodu, integracje (Slack, Notion), automatyzacja
**❌ Wady:** Płatne po 1000 operacji, wolniejsze, mniej kontroli

**📖 Szczegóły:** `INTEGRATION.md` (Opcja 4)

---

## Porównanie Opcji

| Sposób | Setup | Koszt | Czas | Idealne dla |
|--------|-------|-------|------|-------------|
| **Kimi** (Sposób 1) | Zero | Darmowe | Od razu | Start, prototypy, testy |
| **ChatGPT** (Sposób 2) | 15 min | $20/mies | Od razu | Regularna praca, pamięć chatów |
| **Python** (Sposób 3) | 5 min | ~$1/projekt | Setup + run | Automatyzacja, wiele projektów |
| **Make.com** (Sposób 4) | 30 min | $9+/mies | Setup | No-code preferencja, integracje |

---

## Rekomendacja

| Scenariusz | Polecam |
|------------|---------|
| Pierwszy test | **Kimi** (Sposób 1) - zacznij tutaj |
| Długoterminowa praca | **ChatGPT** (Sposób 2) - 5 chatów |
| 10+ projektów/mies | **Python** (Sposób 3) - automatyzacja |
| Nie programujesz | **Make.com** (Sposób 4) lub **Kimi** |

---

## Przykładowy Workflow

### Nowa Oferta - Krok po Kroku (Sposób 1 - Kimi):

```
TY: Jako Marcus zaprojektuj ofertę "Team Extension dla fintechów Series B"
    [Czekasz na odpowiedź]

TY: Jako Elena zbuduj lejek dla oferty Marcusa
    [Czekasz na odpowiedź]

TY: Jako Kai napisz landing page
TY: Jako David przygotuj ABM
    [Dostajesz 2 odpowiedzi naraz]

TY: Jako Sofia przygotuj content strategy
    [Ostatni agent]

TY: Daj podsumowanie całego projektu
    [Dostajesz executive summary + handoff templates]
```

---

### Nowy Content (Sposób 2 - ChatGPT):

1. Otwórz chat "Sofia", wklej jej prompt
2. "Sofia: Przygotuj content calendar Q1"
3. Skopiuj wynik
4. Otwórz chat "Kai", wklej jego prompt + brief od Sofii
5. "Kai: Napisz blog post"
6. Gotowe

---

## Need Help?

- **Kimi nie działa?** → Sprawdź `KIMI_GUIDE.md`
- **ChatGPT confusing?** → Sprawdź `INTEGRATION.md` Opcja 2
- **Python errors?** → Sprawdź `INTEGRATION.md` Opcja 1
- **Make.com too complex?** → Sprawdź `INTEGRATION.md` Opcja 4
- **General help?** → Sprawdź `QUICKSTART.md`

---

## File Structure

```
scalac_ai_council/
├── orchestrator.py               # Python orchestrator (5 agentów, API)
├── QUICKSTART.md                 # Start w 15 minut
├── INTEGRATION.md                # 4 sposoby użycia (Kimi, ChatGPT, Python, Make)
├── KIMI_GUIDE.md                 # Instrukcja użycia z Kimi (najłatwiejsza)
├── AGENTS/                       # 5 agentów z pełnymi promptami
│   ├── marcus_offer_architect/   # Architekt Oferty
│   │   ├── system_prompt.md      # Prompt + 6 książek
│   │   ├── tools.yaml            # Frameworki (Gap Selling, StoryBrand, etc.)
│   │   └── examples/             # 3 przykłady (Team Ext, Sovereign AI, Bundle)
│   ├── elena_funnel_architect/   # Architektka Lejków
│   │   ├── system_prompt.md      # MEDDIC, JOLT, Predictable Revenue
│   │   ├── tools.yaml            # Funnel templates
│   │   └── examples/             # Funnel design example
│   ├── kai_copywriter/           # Copywriter
│   │   ├── system_prompt.md      # AIDA, Big 5, SUCCESs
│   │   ├── tools.yaml            # Copy templates
│   │   └── examples/             # Landing page example
│   ├── sofia_content_strategist/ # Strateg Treści
│   │   ├── system_prompt.md      # Content Tilt, SEO
│   │   ├── tools.yaml            # Content frameworks
│   │   └── examples/             # Content strategy example
│   └── david_lead_strategist/    # Strateg Leadów
│       ├── system_prompt.md      # ABM, Dream 100
│       ├── tools.yaml            # Sales engagement
│       └── examples/             # ABM campaign example
├── WORKFLOW/                     # System operacyjny
│   ├── operating_system.yaml     # Spotkania, decyzje, kultura
│   ├── project_workflows.yaml    # 4 typy projektów
│   └── handoff_templates.md      # Szablony przekazywania pracy
├── TOOLKIT/                      # Wspólne narzędzia
│   ├── templates/                # BrandScript, Pricing, Challenger Pitch
│   ├── checklists/               # Diagnosis, Launch, QA, 80/20
│   ├── scripts/                  # Discovery, Demo, Objections
│   └── calculators/              # ROI, Pricing, CAC/LTV
├── LEARNING/                     # Continuous improvement
│   ├── post_mortem_template.md   # Analiza po projekcie
│   ├── book_study_guide.md       # Miesięczny book club
│   ├── framework_update_process.md
│   └── quarterly_balance_review.md
└── README.md                     # Ten plik
```

---

## Struktura Folderów

```
scalac_ai_council/
├── orchestrator.py               # 🆕 Główny orchestrator (zarządza 5 agentami)
├── QUICKSTART.md                 # 🆕 Start w 15 minut
├── INTEGRATION.md                # 🆕 Jak podłączyć do API (OpenAI/Claude)
├── AGENTS/
│   ├── marcus_offer_architect/
│   │   ├── system_prompt.md      # Kompletny prompt z książkami
│   │   ├── tools.yaml            # Frameworks i templates
│   │   └── examples/             # 3-5 przykładów (80% CORE, 20% AI)
│   ├── elena_funnel_architect/
│   ├── kai_copywriter/
│   ├── sofia_content_strategist/
│   └── david_lead_strategist/
├── WORKFLOW/
│   ├── operating_system.yaml     # Spotkania, decyzje, kultura
│   ├── project_workflows.yaml    # 4 typy projektów
│   └── handoff_templates.md      # Szablony przekazywania pracy
├── TOOLKIT/
│   ├── templates/                # BrandScript, Pricing, Challenger Pitch
│   ├── checklists/               # Diagnosis, QA, Launch
│   ├── scripts/                  # Discovery, Demo, Objections
│   └── calculators/              # ROI, Pricing
├── LEARNING/
│   ├── post_mortem_template.md   # Analiza po projekcie
│   ├── book_study_guide.md       # Miesięczny book club
│   ├── framework_update_process.md
│   └── quarterly_balance_review.md
└── README.md                     # Ten plik
```

---

## System Operacyjny

### Weekly Brief (Poniedziałek, async)
- Co zrobiliśmy
- CORE vs AI split
- Blockers
- Needs from others

### Creative Sprint (Środa, 30 min)
- Problem do rozwiązania
- 2 agenty prezentują
- 3 pomagają rozwiązać

### Ship It (Piątek, 30 min)
- Demo gotowych assetów
- Feedback: "What I liked / What would make it 10x better"

---

## CORE vs AI Balance

### Diagnosis

Zanim zaczniesz projekt, zdiagnozuj:

| Pytanie | CORE | AI |
|---------|------|-----|
| Czy klient ma working infrastructure? | Nie → CORE first | Tak → może AI |
| Czy AI to 'nice to have' czy 'compliance blocker'? | Nice → CORE | Blocker → AI |
| Czy potrzebują devs czy consulting? | Devs → CORE | Consulting → AI |
| Czy mówią o 'POC' czy 'production'? | - | POC → AI assessment |

### 80/20 Rule

- **80% effort na CORE:** Team extension, distributed systems
- **20% effort na AI:** Sovereign AI, RAG

**Dlaczego?**
- CORE = większy volume, krótszy sales cycle
- AI = mniejszy volume, dłuższy cycle, wyższy margin
- Razem = zrównoważony biznes

### Bundle Opportunity

**Kluczowy insight (Zero to One):**
- "Klient chce Sovereign AI" → "Czy mają infrastructure? Jeśli nie, to też CORE projekt"
- "Klient chce Team Extension" → "Czy potrzebują AI skills? Jeśli tak, to upsell"

---

## Jak Onboardować Nowego Agenta

1. **Przeczytaj** system_prompt.md agenta
2. **Przejrzyj** tools.yaml i examples/
3. **Zrozum** CORE vs AI balance
4. **Przeczytaj** książki które są w prompt (przynajmniej 2-3)
5. **Zacznij** od małego zadania pod nadzorem
6. **Iteruj** na podstawie feedbacku

---

## Jak Dodać Nową Książkę

1. **Przeczytaj** książkę
2. **Wybierz** agenta który będzie nią "właścicielem"
3. **Ekstrahuj** key concepts
4. **Stwórz** templates/frameworks
5. **Zaktualizuj** system_prompt.md agenta
6. **Dodaj** examples
7. **Poinformuj** innych agentów
8. **Udokumentuj** w book_study_guide.md

---

## Metryki Sukcesu

### Rada AI

| Metric | Target |
|--------|--------|
| Pipeline | 500k PLN/miesiąc |
| CORE Pipeline | 400k PLN (80%) |
| AI Pipeline | 100k PLN (20%) |
| Win Rate | >30% |
| CAC (CORE) | <15k PLN |
| CAC (AI) | <50k PLN |

### Agenci

| Agent | Key Metric |
|-------|------------|
| Marcus | Offer conversion rate |
| Elena | Funnel conversion by stage |
| Kai | Copy conversion rate |
| Sofia | Content traffic & leads |
| David | Lead volume & quality |

---

## Kultura Rady

### Wartości

1. **Engineering Excellence + Commercial Focus** - Jesteśmy engineerami którzy rozumieją business
2. **Pigheaded Discipline** - Systematyczne działanie, nie random
3. **Secrets > Best Practices** - Szukamy tego czego inni nie widzą
4. **Teach, Don't Sell** - Edukujemy klientów, nie wciskamy
5. **80/20 CORE/AI Balance** - Real business, nie hype

### Konflikt Resolution

1. Each agent states position with data
2. Others ask clarifying questions (Mom Test style)
3. Look for "both/and"
4. If still conflict → Head of Growth decides based on 80/20

---

## Quarterly Review

Co kwartał review:

1. **Revenue split:** Czy 80/20 jest accurate?
2. **Margin analysis:** Czy AI ma higher margin?
3. **Leverage:** Czy CORE+AI bundles działają?
4. **Market:** Czy AI adoption wzrósł?
5. **Decision:** Adjust split na następny kwartał

---

## Kontakt

**Head of Growth:** [Użytkownik]  
**Rada AI:** Marcus, Elena, Kai, Sofia, David

---

## Books Bibliography

### Architekt Oferty (Marcus)
- Crossing the Chasm - Geoffrey Moore
- Monetizing Innovation - Madhavan Ramanujam
- Building a StoryBrand - Donald Miller
- The Challenger Sale - Matthew Dixon
- Gap Selling - Keenan (B2B enterprise sales)
- The Mom Test - Rob Fitzpatrick

### Architekt Lejków (Elena)
- From Impossible to Inevitable - Aaron Ross & Jason Lemkin
- Predictable Revenue - Aaron Ross
- The JOLT Effect - Matthew Dixon & Ted McKenna (overcoming indecision)
- Demand-Side Sales 101 - Bob Moesta & Greg Engle
- The Qualified Sales Leader - John McMahon
- Never Split the Difference - Chris Voss

### Copywriter (Kai)
- Everybody Writes - Ann Handley
- They Ask, You Answer - Marcus Sheridan
- Content Chemistry - Andy Crestodina
- The Copywriter's Handbook - Robert Bly
- Obviously Awesome - April Dunford
- On Writing Well - William Zinsser

### Strateg Treści (Sofia)
- Content Inc. - Joe Pulizzi
- Killing Marketing - Joe Pulizzi
- The Content Strategy Toolkit - Meghan Casey
- Epic Content Marketing - Joe Pulizzi
- Product-Led SEO - Eli Schwartz
- Made to Stick - Chip & Dan Heath

### Strateg Leadów (David)
- Account-Based Marketing - Sangram Vajre
- The ABM Playbook - Andrew Mahr
- No Forms, No Spam, No Cold Calls - Latané Conant
- LinkedIn Content Strategy - Mina Seetharaman
- The Ultimate Sales Machine - Chet Holmes
- Fanatical Prospecting - Jeb Blount
- Sales Engagement - Mursalitza, Vogl, Böttger (modern outbound)

### Wspólne (Wszyscy)
- The Hard Thing About Hard Things - Ben Horowitz
- Zero to One - Peter Thiel
- The Innovator's Dilemma - Clayton Christensen
- Hooked - Nir Eyal
- Thinking, Fast and Slow - Daniel Kahneman

---

## What's New (Latest Update)

### ✅ Zaktualizowane Książki (3 zamiany)
| Agent | Zamiast | Nowa książka | Dlaczego? |
|-------|---------|--------------|-----------|
| **Marcus** | Product-Led Growth | **Gap Selling** | Lepsze dla B2B enterprise (B2B, nie PLG) |
| **Elena** | Hacking Growth | **The JOLT Effect** | Overcoming indecision (enterprise problem) |
| **David** | Data-Driven Marketing | **Sales Engagement** | Modern outbound tactics |

### ✅ Pełne tools.yaml
- Sofia: Content frameworks (Tilt, Epic Content, SEO)
- David: ABM playbooks, cadences, signal-based selling

### ✅ Rozszerzone Prompt'y
- Sofia: Handoff templates, CORE/AI balance, metrics
- David: Daily rituals, multi-threading, objection handling

### ✅ Przykłady dla wszystkich agentów
- Marcus: 3 examples (Team Extension, Sovereign AI, AI-Capable Bundle)
- Elena: Funnel design, MEDDIC, JOLT
- Kai: Landing page, email sequence, Big 5
- Sofia: Q1 content strategy, editorial calendar
- David: ABM campaign, intent-based plays

### ✅ Rozszerzony TOOLKIT
- Checklist'y: Launch, QA, 80/20 balance
- Skrypty: Demo guide
- Kalkulatory: Pricing (Good-Better-Best, bundles)

### ✅ Quick Start Guide
`QUICKSTART.md` - Pierwsze kroki w 15 minut

### ✅ Kimi Guide (Nowe!)
`KIMI_GUIDE.md` - Jak używać mnie (Kimi) jako orchestratora dla 5 agentów

### ✅ Pełna Dokumentacja Użycia
Zaktualizowana sekcja ["🚀 Jak Używać - 4 Sposoby"](#-jak-używać---4-sposoby) z:
- Sposób 1: Kimi Code (zero setup)
- Sposób 2: ChatGPT/Claude (5 chatów)
- Sposób 3: Python Orchestrator (automatyzacja)
- Sposób 4: Make.com/Zapier (no-code)

---

## 🚀 Jak Używać (3 Opcje)

### Opcja A: Python Orchestrator (Polecana)
```bash
# 1. Uruchom orchestrator
python orchestrator.py --project "Team Extension Fintech" --type CORE --export

# 2. Dostajesz kompletny projekt od wszystkich 5 agentów
# 3. Wynik zapisany w projects/team_extension_fintech.json
```

### Opcja B: ChatGPT Custom GPT (No-Setup)
1. Stwórz Custom GPT w ChatGPT
2. Wklej instrukcje z `INTEGRATION.md` (Opcja 3)
3. Rozmawiaj z Radą AI w jednym oknie

### Opcja C: Osobne Chaty (Manual)
1. Otwórz 5 nowych chatów w ChatGPT/Claude
2. Wklej `system_prompt.md` każdego agenta
3. Ręcznie przekazuj handoff'y

**Szczegóły:** [`INTEGRATION.md`](INTEGRATION.md)

---

## Quick Start

**Nowy użytkownik?** Zacznij od: [`QUICKSTART.md`](QUICKSTART.md)

**Szukasz przykładów?** Sprawdź `AGENTS/{agent}/examples/`

**Potrzebujesz checklisty?** `TOOLKIT/checklists/`

---

## License

Internal use only - Scalac AI Council System

---

**Built with ❤️ for Scalac**  
*Engineering company that does AI*

**Last Updated:** 2024 (Complete System Overhaul)

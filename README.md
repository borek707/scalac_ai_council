# Rada AI - Scalac Marketing Council
## Kompletny System Marketingowych AI Doradców

> 🚀 **Start Here:**
> - **Chcesz użyć od razu?** → Przewiń do ["🚀 Jak Używać - 4 Sposoby"](#-jak-używać---4-sposoby)
> - **Masz 15 minut?** → Przeczytaj [`QUICKSTART.md`](scalac_ai_council/QUICKSTART.md)
> - **Używasz Kimi?** → Zobacz [`KIMI_GUIDE.md`](scalac_ai_council/KIMI_GUIDE.md)
> - **Programista?** → Zobacz [`INTEGRATION.md`](scalac_ai_council/INTEGRATION.md)

---

## Co To Jest?

Rada AI to zespół 5 specjalistycznych agentów AI, każdy z osobowością opartą na 5-6 książkach biznesowych, którzy współpracują aby budować i optymalizować marketing i sprzedaż Scalac.

**Kluczowa zasada:** 80% focus na CORE (team extension, distributed systems), 20% na AI (Sovereign AI, RAG).

---

## 5 Agentów

### 1. Marcus - Architekt Oferty
**Książki:** Crossing the Chasm, Monetizing Innovation, Building a StoryBrand, The Challenger Sale, Gap Selling, The Mom Test
**Rola:** Projektowanie ofert, pricing, positioning
**Output:** Offer Packages, BrandScripts, Challenger Pitches

### 2. Elena - Architektka Lejków
**Książki:** From Impossible to Inevitable, Predictable Revenue, The JOLT Effect, Demand-Side Sales, The Qualified Sales Leader, Never Split the Difference
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
**Książki:** Account-Based Marketing, The ABM Playbook, No Forms No Spam, LinkedIn Content Strategy, The Ultimate Sales Machine, Fanatical Prospecting, Sales Engagement
**Rola:** Generowanie leadów, outbound, ABM
**Output:** ABM campaigns, Outbound sequences, Lead gen strategy

---

## 🚀 Jak Używać - 4 Sposoby

Wybierz jeden z poniższych sposobów korzystania z Rady AI:

---

### SPOSÓB 1: Kimi Code (Najłatwiejszy - Tutaj i Teraz)

**Użyj Kimi jako orchestratora.** Kimi zarządza wszystkimi 5 agentami w jednej rozmowie.

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

**✅ Zalety:** Zero setup, działa od razu
**❌ Wady:** Trzeba ręcznie przełączać agentów komendami

**📖 Szczegóły:** [`KIMI_GUIDE.md`](scalac_ai_council/KIMI_GUIDE.md)

---

### SPOSÓB 2: ChatGPT / Claude (Osobne Chaty)

**Otwórz 5 niezależnych chatów i wklej prompt każdego agenta.**

#### Krok po kroku:
1. Otwórz ChatGPT Plus lub Claude Pro
2. Stwórz 5 nowych chatów, nazwij: "Marcus", "Elena", "Kai", "Sofia", "David"
3. W każdym wklej odpowiedni `system_prompt.md`
4. Rozmawiaj z każdym osobno
5. Ręcznie kopiuj handoff'y między chatami

**✅ Zalety:** Każdy agent ma "pamięć", możesz wracać do chatów
**❌ Wady:** Ręczne handoff'y, 5 okien do śledzenia

**📖 Szczegóły:** [`INTEGRATION.md`](scalac_ai_council/INTEGRATION.md) (Opcja 2)

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
python scalac_ai_council/orchestrator.py --project "Team Extension" --type CORE --export
```

#### Koszt:
- ~$1-2 per projekt (5-10 wywołań API)
- GPT-4 = lepsze wyniki, droższe
- GPT-3.5 = szybsze, tańsze

**✅ Zalety:** Automatyczne handoff'y, eksport do JSON, skalowalne
**❌ Wady:** Wymaga API key i Pythona

**📖 Szczegóły:** [`INTEGRATION.md`](scalac_ai_council/INTEGRATION.md) (Opcja 1)

---

### SPOSÓB 4: Make.com / Zapier (No-Code Automation)

**Zbuduj workflow w Make.com bez kodu.**

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
**❌ Wady:** Płatne po 1000 operacji, wolniejsze

**📖 Szczegóły:** [`INTEGRATION.md`](scalac_ai_council/INTEGRATION.md) (Opcja 4)

---

## Porównanie Opcji

| Sposób | Setup | Koszt | Idealne dla |
|--------|-------|-------|-------------|
| **Kimi** (Sposób 1) | Zero | Darmowe | Start, prototypy, testy |
| **ChatGPT** (Sposób 2) | 15 min | $20/mies | Regularna praca, pamięć chatów |
| **Python** (Sposób 3) | 5 min | ~$1/projekt | Automatyzacja, wiele projektów |
| **Make.com** (Sposób 4) | 30 min | $9+/mies | No-code, integracje |

---

## Przykładowy Workflow (Sposób 1 - Kimi)

```
TY: Jako Marcus zaprojektuj ofertę "Team Extension dla fintechów Series B"

TY: Jako Elena zbuduj lejek dla oferty Marcusa

TY: Jako Kai napisz landing page
TY: Jako David przygotuj ABM

TY: Jako Sofia przygotuj content strategy

TY: Daj podsumowanie całego projektu
```

---

## Struktura Repozytorium

```
scalac_ai_council/
├── scalac_ai_council/
│   ├── orchestrator.py               # Python orchestrator (5 agentów, API)
│   ├── QUICKSTART.md                 # Start w 15 minut
│   ├── INTEGRATION.md                # 4 sposoby użycia
│   ├── KIMI_GUIDE.md                 # Instrukcja użycia z Kimi
│   ├── AGENTS/                       # 5 agentów z pełnymi promptami
│   │   ├── marcus_offer_architect/   # system_prompt.md, tools.yaml, examples/
│   │   ├── elena_funnel_architect/   # system_prompt.md, tools.yaml, examples/
│   │   ├── kai_copywriter/           # system_prompt.md, tools.yaml, examples/
│   │   ├── sofia_content_strategist/ # system_prompt.md, tools.yaml, examples/
│   │   └── david_lead_strategist/    # system_prompt.md, tools.yaml, examples/
│   ├── WORKFLOW/
│   │   ├── operating_system.yaml     # Spotkania, decyzje, kultura
│   │   ├── project_workflows.yaml    # 4 typy projektów
│   │   └── handoff_templates.md      # Szablony przekazywania pracy
│   ├── TOOLKIT/
│   │   ├── templates/                # BrandScript, Pricing, Challenger Pitch
│   │   ├── checklists/               # Diagnosis, Launch, QA
│   │   ├── scripts/                  # Discovery, Demo
│   │   └── calculators/              # ROI, Pricing
│   └── LEARNING/
│       ├── post_mortem_template.md
│       ├── book_study_guide.md
│       ├── framework_update_process.md
│       └── quarterly_balance_review.md
└── README.md                         # Ten plik
```

---

## CORE vs AI Balance

| Pytanie | → CORE | → AI |
|---------|--------|------|
| Czy klient ma working infrastructure? | Nie | Tak |
| AI to "nice to have" czy "compliance blocker"? | Nice | Blocker |
| Potrzebują devs czy consulting? | Devs | Consulting |

### 80/20 Rule
- **80% effort na CORE:** Team extension, distributed systems
- **20% effort na AI:** Sovereign AI, RAG

---

## Metryki Sukcesu

| Metric | Target |
|--------|--------|
| Pipeline | 500k PLN/miesiąc |
| CORE Pipeline | 400k PLN (80%) |
| AI Pipeline | 100k PLN (20%) |
| Win Rate | >30% |
| CAC (CORE) | <15k PLN |
| CAC (AI) | <50k PLN |

---

## System Operacyjny

- **Weekly Brief** (Poniedziałek, async) — co zrobiliśmy, CORE/AI split, blockers
- **Creative Sprint** (Środa, 30 min) — problem → 2 agenty prezentują → 3 pomagają
- **Ship It** (Piątek, 30 min) — demo assetów, feedback

---

## Books Bibliography

### Marcus (Architekt Oferty)
- Crossing the Chasm — Geoffrey Moore
- Monetizing Innovation — Madhavan Ramanujam
- Building a StoryBrand — Donald Miller
- The Challenger Sale — Matthew Dixon
- Gap Selling — Keenan
- The Mom Test — Rob Fitzpatrick

### Elena (Architektka Lejków)
- From Impossible to Inevitable — Aaron Ross & Jason Lemkin
- Predictable Revenue — Aaron Ross
- The JOLT Effect — Matthew Dixon & Ted McKenna
- Demand-Side Sales 101 — Bob Moesta & Greg Engle
- The Qualified Sales Leader — John McMahon
- Never Split the Difference — Chris Voss

### Kai (Copywriter)
- Everybody Writes — Ann Handley
- They Ask, You Answer — Marcus Sheridan
- Content Chemistry — Andy Crestodina
- The Copywriter's Handbook — Robert Bly
- Obviously Awesome — April Dunford
- On Writing Well — William Zinsser

### Sofia (Strateg Treści)
- Content Inc. — Joe Pulizzi
- Killing Marketing — Joe Pulizzi
- The Content Strategy Toolkit — Meghan Casey
- Epic Content Marketing — Joe Pulizzi
- Product-Led SEO — Eli Schwartz
- Made to Stick — Chip & Dan Heath

### David (Strateg Leadów)
- Account-Based Marketing — Sangram Vajre
- The ABM Playbook — Andrew Mahr
- No Forms, No Spam, No Cold Calls — Latané Conant
- LinkedIn Content Strategy — Mina Seetharaman
- The Ultimate Sales Machine — Chet Holmes
- Fanatical Prospecting — Jeb Blount
- Sales Engagement — Mursalitza, Vogl, Böttger

### Wspólne (Wszyscy)
- The Hard Thing About Hard Things — Ben Horowitz
- Zero to One — Peter Thiel
- The Innovator's Dilemma — Clayton Christensen
- Hooked — Nir Eyal
- Thinking, Fast and Slow — Daniel Kahneman

---

## Need Help?

- **Kimi nie działa?** → [`KIMI_GUIDE.md`](scalac_ai_council/KIMI_GUIDE.md)
- **Python errors?** → [`INTEGRATION.md`](scalac_ai_council/INTEGRATION.md) Opcja 1
- **General help?** → [`QUICKSTART.md`](scalac_ai_council/QUICKSTART.md)

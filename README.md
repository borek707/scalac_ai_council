# Rada AI Scalac - Multi-Agent Marketing Council

> **4 agenci AI pracują równolegle, debatują i tworzą kompletny plan marketingowy w 30 minut.**
> 
> Zamiast sekwencyjnie "najpierw Marcus, potem Elena" - wszyscy na raz, z feedback loopami i konsensusem.

---

## Co to jest

Rada AI to system gdzie 4 wyspecjalizowani agenci AI (Marcus, Elena, Kai, David) współpracują równolegle nad Twoim projektem marketingowym.

**Każdy agent to osobna sesja w Kimi Code** - działają jednocześnie, czytają nawzajem swoje wypowiedzi, kwestionują, proponują, dochodzą do konsensusu.

### Proces (3 rundy):

```
Round 1 (równolegle):
  Marcus pisze ofertę ──────┐
  Elena pisze lejek ───────┼──► Wszyscy widzą wzajemne pomysły
  Kai pisze copy ──────────┤
  David planuje ABM ───────┘

Round 2 (reakcje):
  Elena: "Marcus, Twoje konwersje są nierealistyczne!"
  Marcus: "Elena, za niski pricing zabija wartość!"
  Kai: "Oboje jesteście za techniczni!"

Round 3 (konsensus):
  Agenci się zgadzają lub zapisują disagreement
  Każdy pisze finalny dokument

Output: 4 spójne dokumenty
```

---

## Dlaczego to lepsze niż "5 promptów"

| Tradycyjne podejście | Rada AI |
|---------------------|---------|
| Sekwencyjnie: Marcus → Elena → Kai → David | Równolegle: wszyscy na raz |
| Każdy agent działa w próżni (nie widzi innych) | Agenci czytają i komentują nawzajem |
| Brak krytyki - każdy pisze co chce | Prawdziwa debata i feedback loop'y |
| Wyniki niespójne | Konsensus lub uzasadniony disagreement |
| 15 minut, słaba jakość | 30 minut, wysoka jakość |

**Kluczowa różnica:** Agenci **krytykują się nawzajem**. Elena zmniejszy optymizm Marcusa, Kai uprości techniczny żargon, David zweryfikuje czy plan jest wykonalny.

---

## Co dostajesz

4 dokumenty które razem tworzą kompletny plan:

| Agent | Output | Co zawiera |
|-------|--------|------------|
| **Marcus** | `marcus_offer.md` | Gap Analysis, BrandScript, Good-Better-Best Pricing, Challenger Pitch |
| **Elena** | `elena_funnel.md` | Funnel stages, MEDDIC criteria, JOLT strategy, 90-day forecast |
| **Kai** | `kai_copy.md` | Landing page (hero, problem, solution, pricing), 5-email sequence, LinkedIn ads |
| **David** | `david_abm.md` | Dream 100 accounts, 12-touch sequences, intent signals, tools stack |

Plus `FINAL_PROPOSAL.md` - wszystko razem w jednym dokumencie.

---

## Do czego to używać

### 1. Nowa oferta
**Brief:** "Team Extension dla fintechów Series B"  
**Wynik:** Kompletny launch package (oferta, lejek, copy, ABM)

### 2. Webinar ideation (z battlecards)
**Brief:** "Znajdź temat webinaru który wypełnia lukę rynku"  
**Wynik:** 3 tematy oparte na analizie konkurencji (VirtusLab, SoftwareMill, Xebia)

### 3. Pipeline review
**Brief:** "Pipeline spadł o 30%, potrzebny action plan"  
**Wynik:** Analiza problemów + konkretne fixy

### 4. Wejście na nowy rynek
**Brief:** "Sovereign AI dla banków szwajcarskich"  
**Wynik:** Oferta + strategia ABM dla CH market

---

## 🚀 Szybki Start

### Wymagania
- Dostęp do Kimi Code z funkcją `sessions_spawn`
- 30-40 minut czasu

### Krok po kroku

```bash
# 1. Wejdź w katalog systemu
cd scalac_council_v2

# 2. Uruchom orchestrator (pokaże instrukcje)
python orchestrator.py
```

**3. Spawn 4 agentów w Kimi Code** (skopiuj i wklej):

```python
# Marcus - Offer Architect
sessions_spawn(
    runtime="subagent",
    task="""Jesteś Marcus, Offer Architect w Scalac.
Przeczytaj /root/.openclaw/workspace/scalac-council-v2/shared/brief.md
Napisz Round 1 do shared/discussion/round_1_marcus.md
Czekaj na innych, czytaj ich, odpowiadaj. 3 rundy lub konsensus.
Final: output/marcus_offer.md""",
    label="marcus"
)

# Elena - Funnel Architect  
sessions_spawn(
    runtime="subagent",
    task="""Jesteś Elena, Funnel Architect w Scalac.
Przeczytaj brief i dyskusję. Napisz Round 1 do round_1_elena.md.
Debata z Marcusem o pricing vs conversion. Final: output/elena_funnel.md""",
    label="elena"
)

# Kai - Copywriter
sessions_spawn(
    runtime="subagent",
    task="""Jesteś Kai, Copywriter w Scalac.
Przeczytaj brief i dyskusję. Napisz Round 1 do round_1_kai.md.
Czy messaging jest zbyt techniczny? Final: output/kai_copy.md""",
    label="kai"
)

# David - Lead Strategist
sessions_spawn(
    runtime="subagent",
    task="""Jesteś David, Lead Strategist w Scalac.
Przeczytaj brief i dyskusję. Napisz Round 1 do round_1_david.md.
Dream 100 accounts. Final: output/david_abm.md""",
    label="david"
)
```

**4. Poczekaj 30 minut**

Agenci piszą równolegle, debatują przez 3 rundy.

**5. Pobierz wyniki**

```bash
# Sprawdź dyskusję
cat shared/discussion/round_1_marcus.md
cat shared/discussion/round_2_elena.md

# Pobierz finalne outputy
cat output/marcus_offer.md
cat output/elena_funnel.md
cat output/kai_copy.md
cat output/david_abm.md

# Lub wszystko razem
cat output/FINAL_PROPOSAL.md
```

---

## 📁 Struktura repozytorium

```
scalac_ai_council/
├── README.md                      # Ten plik - start tutaj
├── scalac_battlecards.docx.md    # Analiza 5 konkurentów + whitespace
├── scalac_content_plan.docx.md   # Plan contentowy Q2-Q3 (10 postów)
│
└── scalac_council_v2/            # ✅ SYSTEM
    ├── orchestrator.py           # Koordynator (status + agregacja)
    │
    ├── agents/                   # 4 agenci
    │   ├── marcus_agent.py       # Offer Architect
    │   ├── elena_agent.py        # Funnel Architect
    │   ├── kai_agent.py          # Copywriter
    │   ├── david_agent.py        # Lead Strategist
    │   ├── marcus_agent_enhanced.py  # Czyta battlecards
    │   └── kai_webinar.py        # Specjalizacja: webinary
    │
    ├── shared/                   # Inputy
    │   ├── brief.md              # Brief projektu (edytuj to)
    │   ├── brief_webinar.md      # Brief do webinar ideation
    │   ├── battlecards.md        # Analiza konkurencji
    │   ├── content_plan.md       # Plan contentowy
    │   └── discussion/           # Dyskusja agentów (autogenerowane)
    │
    ├── output/                   # Wyniki (autogenerowane)
    │   ├── marcus_offer.md
    │   ├── elena_funnel.md
    │   ├── kai_copy.md
    │   ├── david_abm.md
    │   └── FINAL_PROPOSAL.md
    │
    ├── README.md                 # Pełna dokumentacja techniczna
    └── WEBINAR_GUIDE.md          # Jak używać z battlecards
```

---

## 🎭 Kim są agenci

### Marcus (Offer Architect)
- **Osobowość:** Były Principal Engineer → PM w fintech unicorn. Bezpośredni, liczbowy.
- **Broni:** Wysokiego pricingu, wartości ROI
- **Atakuje:** Niskich konwersji, braku jasności w ofercie
- **Frameworki:** Gap Selling, StoryBrand, Good-Better-Best, Challenger Sale

### Elena (Funnel Architect)
- **Osobowość:** Była VP Growth (0→10M ARR). Procesowa, pragmatyczna.
- **Broni:** Realistycznych konwersji, wykonalności planu
- **Atakuje:** Optymizmu Marcusa, nierealistycznych timeline'ów
- **Frameworki:** MEDDIC, JOLT, Three Pipelines, Predictable Revenue

### Kai (Copywriter)
- **Osobowość:** Clarity-focused. "Customer voice" > buzzwords.
- **Broni:** Prostego języka, czytelności
- **Atakuje:** Technicznego żargonu, buzzwords
- **Frameworki:** AIDA, Big 5, Challenger messaging

### David (Lead Strategist)
- **Osobowość:** Konkretny, operacyjny.
- **Broni:** Wykonalności planu, realnych kont
- **Atakuje:** Ogólników, braku konkretów
- **Frameworki:** ABM tiers, Signal-based selling, 12-touch sequences

---

## 💡 Przykładowa debata (Round 2)

**Marcus (Round 1):**
> "Proponuję pricing 75-85 EUR/h. Target: 50% konwersja lead→MQL."

**Elena (Round 2 - odpowiedź na Marcusa):**
> "Marcus, 50% konwersja to nierealistyczne dla fintech B2B. Realistycznie: 25%. To zmienia kalkulację - potrzebujemy 2x więcej leadów."

**Marcus (Round 2 - kontrargument):**
> "Elena, masz rację co do konwersji, ale przy 25% musimy bronić wyższego pricingu. Quality > quantity. Proponuję dodać '2-week guarantee' jako risk reversal."

**Kai (Round 2 - wtrącenie):**
> "Oboje piszecie za technicznie. CTO nie rozumie 'konwersji' i 'MQL'. On chce usłyszeć: 'Scale your team in 2 weeks'. Lead with outcome, nie metrics."

**Round 3 - Konsensus:**
> Pricing 80 EUR/h, konwersja 25%, messaging: "2-week guarantee, scale without hiring delays"

---

## 📊 Bonus: Battlecards (Competitive Intelligence)

W `scalac_council_v2/shared/` znajdziesz:

### `battlecards.md`
Analiza 5 konkurentów (VirtusLab, SoftwareMill, Xebia, Endava, EPAM):
- Ich mocne strony
- Ich słabe punkty  
- **6 WHITESPACE OPPORTUNITIES** - luki które Scalac może wypełnić

Przykładowe whitespace:
- "Akka + Agentic AI" - nikt tego nie robi eksplicytne
- "Healthcare AI + Scala" - pusta nisza
- "Scala-Native AI Engineering" - nikt nie branduje Scala+AI jako jedności

### `content_plan.md`
Plan contentowy z 10 postami "Scala + AI Playbook" (Q2-Q3):
- #3: "Akka Actors as AI Agents" ← idealny na webinar
- #2: "Building RAG Pipeline in Scala 3"
- #6: "From Spark to LLMs"

### Jak używać do webinarów
Zobacz [`scalac_council_v2/WEBINAR_GUIDE.md`](scalac_council_v2/WEBINAR_GUIDE.md) - pełny przewodnik.

---

## ❓ Troubleshooting

### "Agenci nie widzą swoich plików"
Upewnij się że wszyscy używają **absolutnych ścieżek**:
```
✅ /root/.openclaw/workspace/scalac-council-v2/shared/brief.md
❌ shared/brief.md (może nie działać)
```

### "Dyskusja stoi w miejscu"
Agenci czekają na siebie. Dodaj w promptach:
```
JEŚLI minęło >10 minut od ostatniego postu, 
napisz kolejną rundę nawet jeśli nie ma nowych postów.
```

### "Chcę zresetować i zacząć od nowa"
```bash
rm -rf shared/discussion/*.md output/*.md
# Edytuj shared/brief.md
# Spawnuj agentów ponownie
```

---

## 📖 Więcej dokumentacji

- **Pełna instrukcja:** [`scalac_council_v2/README.md`](scalac_council_v2/README.md)
- **Webinar ideation:** [`scalac_council_v2/WEBINAR_GUIDE.md`](scalac_council_v2/WEBINAR_GUIDE.md)

---

## 🚀 Start

```bash
cd scalac_council_v2 && python orchestrator.py
```

🎯 **Gotowe do użycia w Kimi Code.**

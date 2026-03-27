# Rada AI Scalac - True Multi-Agent System

> **4 agenci AI pracują równolegle, debatują i tworzą kompletny plan marketingowy.**
> 
> Nie sekwencyjne "najpierw Marcus, potem Elena". Prawdziwa równoległa współpraca z feedback loopami.

---

## 🎯 Do czego to służy

Ten system pozwala Ci **w 30 minut** stworzyć kompletny, spójny plan marketingowy dla dowolnego projektu Scalac:

## 🧾 Jak wygląda efekt końcowy

Poniżej skrócony, realny fragment finalnego outputu wygenerowanego przez agentów dla kampanii **JVM/Rust Team Extension**:

```markdown
# Scalac — Plan Kampanii: JVM/Rust Team Extension
## DACH (Zürich) · Stockholm · London | Q2–Q3 2026

## TL;DR — 5 decyzji przed poniedziałkiem

1. London first (90 dni), DACH second (180 dni), Nordic to Q3
2. Żadnych cen na landing page, tylko TCO Calculator z email-gate
3. DACH entry = pilot-first: 3 mies. ~CHF 60-65K
4. Webinar async w czerwcu jako touchpoint dla Dream 20

## 1. OFFER — Marcus

### Positioning per Geo
- DACH: "Hiring a senior Scala engineer in Zürich costs CHF 289K this year. We cost CHF 252K — and start in two weeks."
- London: "Your Scala hiring pipeline takes seven months. We take two weeks."
- Nordic: "Scale your JVM team without arbetsgivaravgifter, notice periods, or nine-month hiring gaps."

## 2. LEJEK I PIPELINE — Elena

- London: 3-5 discovery calls w 90 dni, 1 pilot signed
- DACH: 1 discovery call w 90-180 dni, potem pilot
- Nordic: nurture first, outbound później

## 3. COPY — Kai

- Hero headline na landing page per region
- Cold email sequence per geo
- Webinar invite do shortlisty CTO
- LinkedIn hooks pod thought leadership

## 4. KONTA I SEKWENCJE — David

- Dream 20 target accounts
- Priorytetyzacja firm po stacku, hiring signals i ICP fit
- Sekwencje outbound per region
```

Pełny przykład znajdziesz w [output/FINAL_PROPOSAL.md](/workspaces/scalac_ai_council/scalac_council_v2/output/FINAL_PROPOSAL.md).

### ✅ Idealne dla:

| Scenariusz | Co dostajesz |
|------------|--------------|
| **Nowa oferta** | Kompletny Offer Package + Pricing + Positioning |
| **Nowy segment** | Funnel Design + ABM Strategy + Content Plan |
| **Launch produktu** | Landing Page + Email Sequence + Lead Gen Strategy |
| **Pipeline Review** | Analiza problemów + Action Plan + Optymalizacja |
| **Content Strategy** | Editorial Calendar + SEO + Epic Content Plan |
| **ABM Campaign** | Dream 100 + Sequences + Personalization |

### 📊 Przykładowe projekty:

1. **"Team Extension dla Fintechów Series B"**
   - Marcus: Oferta z Good-Better-Best pricing
   - Elena: Lejek z MEDDIC qualification
   - Kai: Landing page + 5-email sequence
   - David: ABM dla 50 fintechów

2. **"Sovereign AI dla Banków"**
   - Marcus: Compliance-first offer
   - Elena: Długi cykl sprzedażowy (6 miesięcy)
   - Kai: White paper + case studies
   - David: Targeting CISOs + CTOs

3. **"Migration Legacy → Scala"**
   - Marcus: Fixed-price project offer
   - Elena: Project-based funnel
   - Kai: Technical case studies
   - David: Targeting enterprise architects

---

## 🏗️ Jak to działa (Architektura)

```
┌─────────────────────────────────────────────────────────────┐
│  TY (Orchestrator Session)                                  │
│  • Monitorujesz dyskusję                                   │
│  • Sprawdzasz wyniki                                       │
│  • Agregujesz finalne outputy                              │
└─────────────────────────────────┬───────────────────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
       ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
       │   Marcus     │   │    Elena     │   │     Kai      │
       │  (Session 1) │   │  (Session 2) │   │  (Session 3) │
       │  RÓWNOLEGLE  │   │  RÓWNOLEGLE  │   │  RÓWNOLEGLE  │
       └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │
                          ┌───────▼────────┐
                          │     David      │
                          │  (Session 4)   │
                          │  RÓWNOLEGLE    │
                          └────────┬───────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │     SHARED WORKSPACE        │
                    │  /workspace/scalac-council  │
                    │                             │
                    │  shared/brief.md           │
                    │  shared/discussion/        │
                    │    • round_1_marcus.md     │
                    │    • round_1_elena.md      │
                    │    • round_2_marcus.md     │
                    │    └── ...                 │
                    │  output/                   │
                    │    • marcus_offer.md       │
                    │    • elena_funnel.md       │
                    │    • kai_copy.md           │
                    │    • david_abm.md          │
                    │    • FINAL_PROPOSAL.md     │
                    └─────────────────────────────┘
```

### 🔄 Przepływ pracy:

**Runda 1** (wszyscy naraz, ~5 min):
- Marcus pisze ofertę (Gap Selling, Pricing)
- Elena planuje lejek (MEDDIC, konwersje)
- Kai przygotowuje copy (Landing page)
- David wybiera konta (Dream 100)

**Runda 2** (reakcje, ~10 min):
- Elena: "Marcus, Twoje konwersje są nierealistyczne!"
- Marcus: "Elena, za niski pricing zabija wartość!"
- Kai: "Oboje jesteście zbyt techniczni dla CTO!"
- David: "Czy macie case study dla moich kont?"

**Runda 3** (konsensus, ~10 min):
- Agenci się zgadzają lub zapisują disagreement
- Każdy dostosowuje swój output do feedbacku

**Final** (~5 min):
- Każdy zapisuje swój finalny dokument
- Orchestrator składa wszystko w jeden PDF

---

## 🚀 Szybki Start (3 kroki)

### Krok 1: Przygotuj Brief (2 min)

Edytuj `shared/brief.md`:

```markdown
# Brief Projektu: [NAZWA]

## Cel
[Co chcemy osiągnąć?Np. "Zwiększyć pipeline z fintechów o 500k PLN"]

## Target
- Segment: [Np. "Fintechy Series B w EU"]
- Decision Maker: [Np. "CTO / VP Engineering"]
- Pain: [Np. "Potrzebują 10 devów, hiring trwa 6 miesięcy"]
- Budget: [Np. "300-500k EUR rocznie"]

## Constraints
- Timeline: [Np. "90 dni"]
- Focus: [Np. "80% CORE, 20% AI"]
- Target pipeline: [Np. "500k PLN"]
```

**Przykłady gotowych briefów:**

<details>
<summary><b>📁 Brief 1: Team Extension Fintech</b></summary>

```markdown
# Brief: Team Extension dla Fintechów Series B

## Cel
Stworzyć kompletny pakiet marketingowy dla nowej oferty Team Extension.

## Target
- Segment: Fintechy Series B w EU (5-50M EUR funding)
- Decision Maker: CTO / VP Engineering
- Pain: Hiring senior Scala devów trwa 6+ miesięcy, muszą szybko skalować
- Budget: 300-500k EUR rocznie

## Constraints
- Timeline: 90 dni do pierwszych meetingów
- Target pipeline: 500k PLN
- 80% CORE (team extension), 20% AI
```
</details>

<details>
<summary><b>📁 Brief 2: Sovereign AI Banking</b></summary>

```markdown
# Brief: Sovereign AI dla Banków

## Cel
Stworzyć ofertę i strategię sprzedaży dla Sovereign AI w sektorze banking.

## Target
- Segment: Swiss private banks, German banks
- Decision Maker: CISO + CTO + Chief Risk Officer
- Pain: AI POC działa, ale compliance blokuje deployment
- Budget: 200-500k EUR (POC)

## Constraints
- Timeline: 6 miesięcy (długi cykl sprzedażowy)
- Heavy compliance requirements
- Must be on-premise / private cloud
```
</details>

<details>
<summary><b>📁 Brief 3: Migration Project</b></summary>

```markdown
# Brief: Migration Legacy Java → Scala

## Cel
Stworzyć ofertę project-based dla migracji systemów legacy.

## Target
- Segment: Enterprise (fintech, healthtech)
- Decision Maker: CTO, Enterprise Architect
- Pain: Legacy system nie skaluje się, tech debt
- Budget: 300-800k EUR (fixed price)

## Constraints
- Fixed price preferred
- Zero downtime requirement
- Knowledge transfer mandatory
```
</details>

---

### Krok 2: Uruchom Orchestrator (1 min)

W **tej** sesji Kimi Code:

```bash
cd scalac_council_v2
python orchestrator.py
```

Zobaczysz:
- ✅ Status workspace
- ✅ Czy brief jest poprawny
- 📋 Instrukcje jak spawnować agentów

---

### Krok 3: Spawn Agentów (2 min)

W tej samej sesji, użyj `sessions_spawn`:

```python
# Marcus - Offer Architect
sessions_spawn(
    runtime="subagent",
    task="""Jesteś Marcus, Offer Architect w Scalac.

Przeczytaj /root/.openclaw/workspace/scalac-council-v2/shared/brief.md

Twoja rola:
1. Napisz Round 1 do shared/discussion/round_1_marcus.md
2. Czekaj na innych agentów
3. Przeczytaj ich rundy i odpowiedz w Round 2
4. Kontynuuj debatę przez 3 rundy lub do konsensusu
5. Napisz finalny output do output/marcus_offer.md

Używaj: Gap Selling, StoryBrand, Good-Better-Best, Challenger Sale.
Krytykuj Elenę jeśli konwersje są nierealistyczne.
Bronij swojego pricingu.
""",
    label="marcus"
)

# Elena - Funnel Architect  
sessions_spawn(
    runtime="subagent",
    task="""Jesteś Elena, Funnel Architect w Scalac.

Przeczytaj brief i dyskusję (round_1_marcus.md itd.)

Twoja rola:
1. Napisz Round 1 do shared/discussion/round_1_elena.md
2. Zkrytykuj pricing Marcusa - czy realistyczny?
3. Debata o konwersjach, MEDDIC, JOLT
4. Final: output/elena_funnel.md

Używaj: MEDDIC, JOLT, Three Pipelines, Predictable Revenue.
Walcz o realistyczne metryki.
""",
    label="elena"
)

# Kai - Copywriter
sessions_spawn(
    runtime="subagent",
    task="""Jesteś Kai, Copywriter w Scalac.

Przeczytaj brief i dyskusję.

Twoja rola:
1. Napisz Round 1 do shared/discussion/round_1_kai.md
2. Czy messaging Marcusa/Eleny jest zbyt techniczny?
3. Propozycje copy które konwertuje
4. Final: output/kai_copy.md (landing page + emails)

Używaj: AIDA, Big 5, Challenger messaging.
Focus: clarity > cleverness.
""",
    label="kai"
)

# David - Lead Strategist
sessions_spawn(
    runtime="subagent",
    task="""Jesteś David, Lead Strategist w Scalac.

Przeczytaj brief i dyskusję.

Twoja rola:
1. Napisz Round 1 do shared/discussion/round_1_david.md
2. Dream 100 - konkretne konta
3. ABM strategy - czy lejek jest wykonalny?
4. Final: output/david_abm.md

Używaj: ABM tiers, signal-based selling, 12-touch sequences.
Konkrety > Ogólniki.
""",
    label="david"
)
```

---

## ⏱️ Timeline

```
T+0 min     Spawn 4 agentów
T+5 min     Round 1 done (wszyscy napisali pierwsze stanowisko)
T+15 min    Round 2 done (debaty, krytyka, kontrargumenty)
T+25 min    Round 3 done (konsensus lub finalne stanowiska)
T+30 min    Final outputs ready
T+35 min    Orchestrator agreguje FINAL_PROPOSAL.md
```

---

## 📊 Monitorowanie Postępu

W sesji Orchestrator możesz sprawdzać status:

```bash
# Sprawdź co jest w workspace
ls -la /root/.openclaw/workspace/scalac-council-v2/shared/discussion/

# Przeczytaj konkretną rundę
cat /root/.openclaw/workspace/scalac-council-v2/shared/discussion/round_1_marcus.md

# Sprawdź czy są finalne outputy
ls -la /root/.openclaw/workspace/scalac-council-v2/output/
```

Lub uruchom ponownie orchestrator:
```bash
python orchestrator.py
```

Pokaże:
- Która runda jest aktywna
- Ilu agentów już odpowiedziało
- Czy jest konsensus

---

## 📁 Outputy

Po zakończeniu w `output/` znajdziesz:

| Plik | Zawartość |
|------|-----------|
| `marcus_offer.md` | Kompletny Offer Package (Gap Analysis, BrandScript, Pricing, Challenger Pitch) |
| `elena_funnel.md` | Funnel Design (Stages, MEDDIC, JOLT, Three Pipelines, Forecast) |
| `kai_copy.md` | Landing Page + Email Sequence (5 emails) + LinkedIn Ads |
| `david_abm.md` | ABM Strategy (Dream 100, Sequences, Tools) |
| `FINAL_PROPOSAL.md` | Wszystko razem w jednym dokumencie |

---

## 🎭 Kim są agenci

### Marcus (Offer Architect)
- **Style:** Challenger, liczby, bezpośredni
- **Broni:** Wysokiego pricingu, wartości ROI
- **Atakuje:** Niskie konwersje, brak jasności
- **Frameworki:** Gap Selling, StoryBrand, Good-Better-Best

### Elena (Funnel Architect)
- **Style:** Procesowa, metryki, pragmatyczna
- **Broni:** Realistycznych konwersji, wykonalności
- **Atakuje:** Optymizm Marcusa, nierealistyczne timeline
- **Frameworki:** MEDDIC, JOLT, Three Pipelines

### Kai (Copywriter)
- **Style:** Clarity-focused, "customer voice"
- **Broni:** Prostego języka, czytelności
- **Atakuje:** Buzzwords, techniczny żargon
- **Frameworki:** AIDA, Big 5, Challenger messaging

### David (Lead Strategist)
- **Style:** Konkretny, operacyjny
- **Broni:** Wykonalności planu, realnych kont
- **Atakuje:** Ogólniki, brak konkretów
- **Frameworki:** ABM tiers, Signal-based selling

---

## 💡 Przykładowe Scenariusze Użycia

### Scenariusz 1: Nowa Oferta (Greenfield)

**Sytuacja:** Chcesz wprowadzić nową usługę "AI-Capable Team Extension"

**Co robisz:**
1. Piszesz brief: "Nowa oferta: AI-Capable Team Extension dla enterprise"
2. Spawnujesz 4 agentów
3. Czekasz 30 minut
4. Dostajesz kompletny plan launchu

**Output:**
- Marcus: Oferta z trzema tierami (Good/Better/Best)
- Elena: Lejek specyficzny dla AI-buyers (dłuższy cykl)
- Kai: Landing page z focus na "AI expertise"
- David: Lista 50 enterprise kont z AI initiatives

---

### Scenariusz 2: Pipeline Review (Optymalizacja)

**Sytuacja:** Pipeline spadł o 30%, co robić?

**Co robisz:**
1. Piszesz brief: "Pipeline Review - spadek 30%, potrzebny action plan"
2. Spawnujesz 4 agentów z focus na analizę
3. Agenci debatują co jest problemem

**Możliwy wynik debaty:**
- Marcus: "Pricing jest OK, problem w messaging"
- Elena: "Lejek działa, ale brak qualified leads"
- Kai: "Copy jest outdated, nie odpowiada na pain"
- David: "ABM targetuje złe konta"

**Output:** Action plan z konkretnymi fixami

---

### Scenariusz 3: Wejście na Nowy Rynek

**Sytuacja:** Chcecie wejść na rynek szwajcarski (banking)

**Co robisz:**
1. Brief: "Wejście na rynek CH - banking, Sovereign AI"
2. Spawnujesz agentów

**Output:**
- Marcus: Oferta "Sovereign AI for Swiss Banks" (compliance-first)
- Elena: Lejek z uwzględnieniem długiego cyklu (6-12 miesięcy)
- Kai: Copy z focus na "Swiss quality", "Compliance"
- David: Lista 30 Swiss banks z AI initiatives

---

## 🔧 Troubleshooting

### "Agenci nie widzą swoich plików"

**Problem:** Agenci piszą, ale nie widzą nawzajem postów

**Rozwiązanie:** Upewnij się, że wszyscy używają **absolutnych ścieżek**:
```python
# ✅ DOBRZE:
"/root/.openclaw/workspace/scalac-council-v2/shared/brief.md"

# ❌ ŹLE:
"shared/brief.md"  # Relatywna ścieżka - może nie działać
```

---

### "Dyskusja stoi w miejscu"

**Problem:** Agenci nie piszą kolejnych rund

**Rozwiązanie:** Dodaj w promptach explicit timeout:
```python
task="""
... 
JEŚLI minęło >10 minut od ostatniego postu innego agenta,
napisz kolejną rundę nawet jeśli nie ma nowych postów.
Nie czekaj w nieskończoność.
"""
```

---

### "Agenci się nie zgadzają i kłócą"

**To nie bug, to feature!**

Dobra debata powinna zawierać konflikty:
- Marcus vs Elena o pricing
- Kai vs Marcus o techniczność
- David vs Elena o wykonalność

W Round 3 agenci powinni dojść do konsensusu lub zanotować:
```markdown
## Konsensus / Disagreement
Zgadzamy się co do: [lista]
Nie zgadzamy się co do: [lista]
Decyzja: [co robimy mimo disagreement]
```

---

## 📊 Użycie z Battlecards (Competitive Intelligence)

Masz dostęp do zaawansowanej analizy konkurencji:

### Pliki w `shared/`:
- **`battlecards.md`** - Analiza 5 konkurentów (VirtusLab, SoftwareMill, Xebia, Endava, EPAM) + 6 WHITESPACE OPPORTUNITIES
- **`content_plan.md`** - Plan contentowy Q2-Q3 z 10 postami "Scala + AI Playbook"
- **`brief_webinar.md`** - Specjalny brief do generowania tematów webinarów

### Do czego to użyć:

| Scenariusz | Pliki | Co dostajesz |
|------------|-------|--------------|
| **Webinar ideation** | brief_webinar.md + battlecards + content_plan | 3 tematy webinarów wypełniające luki rynku |
| **Positioning review** | battlecards | Jak się odróżnić od VirtusLab/SoftwareMill |
| **Content strategy** | content_plan | Które posty przekształcić w lead gen |

### Szybki start (Webinar ideation):

```python
# Użyj ENHANCED agentów które czytają battlecards:

sessions_spawn(
    runtime="subagent",
    task="""Jesteś Marcus. Przeczytaj:
1. /root/.openclaw/workspace/scalac-council-v2/shared/brief_webinar.md
2. /root/.openclaw/workspace/scalac-council-v2/shared/battlecards.md
3. /root/.openclaw/workspace/scalac-council-v2/shared/content_plan.md

Zaproponuj 3 tematy webinarów wypełniające whitespace.
Napisz do output/marcus_webinar_proposals.md""",
    label="marcus-webinar"
)
```

**📖 Pełny przewodnik:** [`WEBINAR_GUIDE.md`](WEBINAR_GUIDE.md)

---

## 🎓 Best Practices

### 1. Dobry brief = dobry wynik

Im bardziej szczegółowy brief, tym lepsza debata:

```markdown
# ✅ DOBRZE:
Target: "Fintechy Series B w EU, 5-50M EUR funding, 
         zatrudniające 20-50 osób, hiring 5+ devs"

# ❌ SŁABO:
Target: "Fintechy"
```

### 2. Nie przerywaj za wcześnie

Poczekaj aż agenci przejdą przez 3 rundy. Dopiero wtedy:
- Wszystkie perspektywy są przedstawione
- Dyskusja jest wyczerpana
- Outputy są spójne

### 3. Czytaj dyskusję

To najciekawsza część! Widzisz:
- Jak AI myśli o strategii
- Jakie są trade-offy (cena vs konwersja)
- Które argumenty są przekonujące

### 4. Iteruj

Jeśli wynik nie jest idealny:
1. Edytuj brief (dodaj więcej contextu)
2. Usuń stare rundy (`rm shared/discussion/*.md`)
3. Spawnuj agentów ponownie

---

## 📊 Różnica vs Inne Systemy

| Cecha | 5 Promptów (Sekwencyjne) | Rada AI (Równoległe) |
|-------|------------------------|---------------------|
| **Czas** | 15 min | 30 min |
| **Jakość** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Spójność** | Słaba (każdy agent działa w próżni) | Wysoka (debatują) |
| **Feedback loops** | ❌ Brak | ✅ Tak |
| **Konsensus** | ❌ Brak | ✅ Tak |
| **Realizm** | Każdy optymistyczny | Realistyczne spory |

**Dlaczego dłużej?** Bo agenci debatują. Ale wynik jest dużo lepszy - spójny, realistyczny, przemyślany.

---

## 🚀 Next Steps

1. **Spróbuj teraz:**
   ```bash
   python orchestrator.py
   ```

2. **Stwórz własny brief:**
   ```bash
   nano shared/brief.md
   ```

3. **Spawn agentów:** (użyj kodu z sekcji "Krok 3")

4. **Poczekaj 30 minut i ciesz się wynikami!**

---

## 📞 Support

Jeśli coś nie działa:
1. Sprawdź czy brief.md istnieje
2. Upewnij się, że agenci używają absolutnych ścieżek
3. Sprawdź `output/` czy są pliki
4. Uruchom `python orchestrator.py` ponownie

---

**Gotowy do startu?** 

```bash
python orchestrator.py
```

🚀 Powodzenia!

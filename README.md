# Rada AI Scalac — Multi-Agent Marketing Council

> **4 agenci AI pracują równolegle, debatują ze sobą i tworzą kompletny plan marketingowy Scalac.**
>
> Wpisz `@Scalac Council zrób plan dla X` — agenci działają sami.

---

## Do czego to służy

System do tworzenia **kompletnych planów marketingowych Scalac** w 30–60 minut zamiast kilku dni.

Zamiast jednego długiego prompta — 4 wyspecjalizowanych ekspertów pracuje równolegle, kwestionuje nawzajem założenia i dochodzi do operacyjnego konsensusu. Finalny output to dokument gotowy do wdrożenia następnego dnia roboczego.

### Przykłady projektów

| Projekt | Co dostajesz |
|---------|--------------|
| **JVM/Rust Team Extension — DACH, London, Stockholm** | Oferta per geo + TCO Challenger pitch + Dream 20 kont + 12-touch cadence + cold emails |
| **Team Extension dla Fintechów Series B** | Oferta + lejek MEDDIC + landing page + Dream 100 |
| **Sovereign AI dla Banków** | Compliance-first pitch + 6-mies. cykl sprzedaży + white paper door-opener |
| **Scala+AI dla Scale-upów** | Positioning + ABM Tier 1 + Playbook content |
| **Webinar / Event launch** | Messaging + email sequence + follow-up cadence |

---

## Agenci — kto co robi

### Marcus — Offer Architect
**Rola:** Projektuje ofertę, pricing i positioning.

Używa: *Gap Selling*, *The Challenger Sale*, *Monetizing Innovation* (Good-Better-Best), *StoryBrand SB7*.

Wie: Scalac jest jedynym Official Akka Tech Partnerem w EU. Rynek w DACH płaci CHF 150–200K/rok na seniora lokalnie — to jest argument Challengera, nie powód do obniżania ceny. Premium geo = premium framing.

Walczy o: wysoką cenę i value framing zamiast godzinówek. Elena zawsze chce obniżyć — Marcus broni z danymi. Kai go pilnuje żeby nie był zbyt techniczny.

**Output:** `output/FINAL_PROPOSAL.md` sekcja OFFER — positioning per geo, pricing tiers (Starter/Scale/Enterprise), Challenger pitch z TCO per miasto.

---

### Elena — Funnel Architect
**Rola:** Projektuje lejek, kwalifikację leadów, pipeline i nurture.

Używa: *MEDDIC*, *The JOLT Effect*, *Predictable Revenue* (Seeds/Nets/Spears), *From Impossible to Inevitable*.

Wie: 1 marketer + 1 intern = lejek musi być realistyczny. Geo ma znaczenie — DACH buying cycle to 4–6 mies., London 2–4 mies., Nordic 6–12 mies. Nie planuje 3 closed deals w 90 dniach dla DACH.

Walczy o: realistyczne konwersje i pipeline math. Kwestionuje pricing który nie przejdzie MEDDIC Economic Buyer screen.

**Output:** sekcja LEJEK — Three Pipelines, MEDDIC per geo, JOLT techniki, nurture cadence 12 mies., pipeline math per kwartał.

---

### Kai — Copywriter
**Rola:** Pisze landing pages, cold emails, LinkedIn hooks, webinar invites.

Używa: *They Ask You Answer* (Big 5), *StoryBrand*, *Obviously Awesome*, AIDA i PAS.

Wie: CTO ma 30 sekund. Jeden claim per hero, nie pięć. DACH cold email musi być inny niż UK — DACH suchy i liczbowy, Nordic peer-framing bez pitch'a, London VC-aware. DACH webinar invite po **niemiecku** — angielski = blast.

Walczy o: jasność i konkret. Przekształca liczby Marcusa i listy Davida w zdania które CTO przeczyta zanim zamknie kartę.

**Output:** sekcja COPY — 3 hero headlines per geo, 3 cold emails, LinkedIn hooks, webinar invites, nurture subject lines.

---

### David — Lead Strategist
**Rola:** Buduje Dream 20/100 kont, sekwencje outreach i ABM z danych prospektowych.

Używa: *ABM Playbook*, *Fanatical Prospecting*, *Signal-Based Selling*, *12-Touch Cadence*.

Wie: Mamy realne dane 350+ firm z CSV (Scala CTOs, AI vacancies, Wiza contacts). David korzysta z `target_accounts.md` jako bazy (44KB danych). Dostaje pełne dane, pozostali agenci dostają tylko Key Intelligence summary.

Walczy o: konkretne konta, triggery i timing. "Zimny outreach bez triggera to poniżej 2% reply rate" — każdy touch musi mieć sygnał.

**Output:** sekcja KONTA — Dream 20 tabela z emailami, 12-touch cadence daily template, webinar mapa per konto, Day 1 SDR Playbook.

---

## Jak działa debata

Agenci piszą 2–3 rundy. Każda runda = osobny plik w `shared/discussion/`.

```
Runda 1 — wszyscy równolegle:
  Marcus: oferta, pricing, Challenger pitch
  Elena:  lejek, MEDDIC, pipeline math       ← czytają pliki poprzednich rund
  Kai:    hero copy, cold emails, hooks
  David:  Dream 20, triggery, sekwencje

Runda 2 — konfrontacja:
  Elena:  "Marcus, Stockholm pricing jest droższy niż lokalny senior — math nie działa"
  Marcus: "Racja — obniżam Starter, zmieniam framing na 'zero ryzyk'"
  David:  "DACH pricing nie może być na landing page — DACH to price reveal w discovery call"
  Kai:    "Positioning ma 5 claimów naraz — CTO ma 30 sekund, jeden claim per geo"

Runda 3 (jeśli potrzebna) — konsensus:
  Agenci dostosowują outputy do feedbacku
  Zapisują finalny output spójny z pozostałymi
```

**Shared workspace** w `shared/discussion/` — agenci czytają pliki nawzajem przed pisaniem rundy 2.
`round_2_elena.md` zawiera bezpośrednie odpowiedzi na tezy z `round_1_marcus.md`.

---

## Skąd agenci biorą wiedzę

### Wiedza rynkowa (wbudowana w każdy prompt)

**`scalac_battlecards.docx.md`** — analiza konkurencji (marzec 2026):
- VirtusLab: mocny w Scala, słaby w unified Scala+AI brand. ML team Python-centric. 8 Clutch reviews.
- SoftwareMill: 2 osobne teamy (Scala ≠ AI) — CTO dostaje dwa różne pitche. NPS 73, ale to słabość przy Scala+AI.
- Xebia: `xef.ai` to Kotlin, nie Scala. Premium pricing = nie konkurujemy bezpośrednio.
- Endava/EPAM: zero Scala+AI messagingu → ich klienci używający Scali to nasze warm leady.
- Scalac: jedyny Official Akka Tech Partner EU. `scalac.ai` jako dedykowany brand. 23 Clutch reviews.

**`scalac_content_plan.docx.md`** — plan contentowy (kwiecień–wrzesień 2026):
- LinkedIn 3x/tydzień (wtorek thought leadership, czwartek technical)
- Scala+AI Playbook Blog Series (10 postów, keywords: "scala ai programming")
- Czerwiec 2026: *The Scala+AI Manifesto* — door-opener dla Tier 1 kont
- Wrzesień 2026: *State of Scala+AI 2026 Survey* — excuse to reach out
- Reddit r/scala weekly — community trust building

### Dane prospektowe (differential injection)

**`shared/target_accounts.md`** — 44KB zsyntetyzowanych danych z 4 plików CSV:

| Sekcja | Zawartość | Kto dostaje |
|--------|-----------|-------------|
| **1. AI vacancies Q1 2026** | 25 firm aktywnie rekrutujących AI engineers (⭐ SCALA, 🔥 KAFKA flagging) | Wszyscy |
| **2. Wiza CTO Scala groups** | 142 CTOs z emailami, funding, lokalizacją | Wszyscy |
| **3. SalesGorilla 200 Scala CTOs** | 108 firm, historia kontaktu SG, LinkedIn | David (full) |
| **4. Key Intelligence** | Podsumowanie: tech patterns, Tier 1 leads, sygnały | Wszyscy |

**Differential injection:** David dostaje pełne 44KB → prompt ~60KB. Marcus/Elena/Kai dostają tylko sekcję 4 → prompt ~15KB.
To celowe — David potrzebuje pełnych danych do ABM, pozostali do swojej pracy potrzebują tylko kontekstu.

**Tier 1 z danych (Scala + aktywna rekrutacja AI):**
- Depop (London) — Scala+Spark, multiple ML vacancies, keyur@depop.com
- Artifact (Lausanne, CH) — Scala w stacku, Senior AI/Consultant, michael.wegmueller@artifact.swiss
- Kaluza (London) — Kafka+LangChain+MCP, andy.worsley@kaluza.com
- iManage (Chicago) — Scala/Java AI Engineer, bijo.thomas@imanage.com
- Feedzai (Lisbon) — Scala + AI Risk Platform, pedro.faria@feedzai.com

---

## Jak uruchomić

### VS Code + GitHub Copilot (najłatwiej)

```
@Scalac Council Team Extension dla scale-upów z JVM w DACH i Londynie — zrób kompletny plan
```

Agent `@Scalac Council` automatycznie:
1. Zapisuje brief do `shared/brief.md`
2. Wywołuje 4 subagenty (Marcus, Elena, Kai, David) równolegle
3. Zbiera rundy debaty w `shared/discussion/`
4. Agreguje i zwraca `output/FINAL_PROPOSAL.md`

Subagenty nie są widoczne dla użytkownika — `@Scalac Council` zarządza nimi sam.

---

### Cursor

Wpisz "scalac council" — reguła `.cursor/rules/scalac-council.mdc` podpowie workflow. Lub ręcznie:

```bash
cd scalac_council_v2 && python orchestrator.py
```

Otwórz 4 zakładki Composer (`Ctrl+Shift+I` → `+ New Composer`), wklej kolejno:
- `prompts/marcus_prompt.md`
- `prompts/elena_prompt.md`
- `prompts/kai_prompt.md`
- `prompts/david_prompt.md`

Uruchom wszystkie 4 jednocześnie. Po zakończeniu:
```bash
python orchestrator.py --final
```

---

### Kimi Code / OpenClaw (auto-spawn)

```bash
cd scalac_council_v2 && python orchestrator.py
```

Orchestrator automatycznie wykrywa `sessions_spawn()` w builtins i spawnuje 4 sesje równolegle. Nic więcej nie trzeba robić.

```bash
python orchestrator.py --monitor   # status debaty
python orchestrator.py --final     # agregacja po zakończeniu
```

---

### Claude Code

```bash
cd scalac_council_v2 && python orchestrator.py
```

Generuje `prompts/*.md`. Otwórz 4 osobne okna Claude:
```bash
claude --file prompts/marcus_prompt.md
claude --file prompts/elena_prompt.md
claude --file prompts/kai_prompt.md
claude --file prompts/david_prompt.md
```

---

### Google Antigravity

```bash
cd scalac_council_v2 && python orchestrator.py
```

W Mission Control (`Ctrl+Shift+M`):
1. `+ New Agent` × 4
2. Dla każdego: `@file prompts/[agent]_prompt.md`
3. Uruchom wszystkich jednocześnie — Antigravity synchronizuje dostęp do `shared/` przez Cross-surface Agents

---

### Dowolny chatbot (ChatGPT, Claude.ai, Gemini itp.)

```bash
cd scalac_council_v2 && python orchestrator.py
```

Otwórz 4 osobne okna chata. W każdym wklej zawartość pliku z `prompts/`.

---

## Struktura plików

```
scalac_ai_council/
│
├── README.md                          ← ten plik
├── scalac_battlecards.docx.md         ← analiza konkurencji (źródło — nie edytuj)
├── scalac_content_plan.docx.md        ← plan contentowy (źródło — nie edytuj)
│
├── csv/                               ← surowe dane prospektowe
│   ├── 200 Scala CTO's - Sheet1.csv   ← SalesGorilla — 108 firm Scala CTOs
│   ├── Q1 2026 AI vacancies (...).csv ← 25 firm z aktywnymi AI vacancies
│   └── WIZA_CTO_Scala_groups (...).csv ← 142 CTOs z emailami
│
├── .github/agents/                    ← VS Code Copilot native agents
│   ├── scalac-council.agent.md        ← główny orchestrator (@Scalac Council)
│   ├── marcus.agent.md                ← Offer Architect (user-invocable: false)
│   ├── elena.agent.md                 ← Funnel Architect (user-invocable: false)
│   ├── kai.agent.md                   ← Copywriter (user-invocable: false)
│   └── david.agent.md                 ← Lead Strategist (user-invocable: false)
│
├── .cursor/rules/
│   └── scalac-council.mdc             ← Cursor workflow rules
│
└── scalac_council_v2/
    ├── orchestrator.py                ← główny skrypt Python (wszystkie IDE)
    │
    ├── agents/                        ← Python modules agentów
    │   ├── marcus_agent.py
    │   ├── elena_agent.py
    │   ├── kai_agent.py
    │   └── david_agent.py
    │
    ├── shared/                        ← shared workspace agentów
    │   ├── brief.md                   ← EDYTUJ TO przed każdą kampanią
    │   ├── brief_webinar.md           ← brief dla kampanii webinarowej
    │   ├── battlecards.md             ← kopia battlecards dla orchestratora
    │   ├── content_plan.md            ← kopia content planu dla orchestratora
    │   ├── target_accounts.md         ← 44KB danych prospektowych z CSV (auto)
    │   └── discussion/                ← debata (generowane przez agentów)
    │       ├── round_1_marcus.md
    │       ├── round_1_elena.md
    │       ├── round_1_kai.md
    │       ├── round_1_david.md
    │       ├── round_2_marcus.md
    │       └── round_2_[...].md
    │
    ├── prompts/                       ← generowane przez orchestrator.py
    │   ├── marcus_prompt.md           ← self-contained prompt (battlecards wbudowane)
    │   ├── elena_prompt.md
    │   ├── kai_prompt.md
    │   └── david_prompt.md            ← zawiera pełne target_accounts (~60KB)
    │
    ├── output/
    │   └── FINAL_PROPOSAL.md          ← finalny plan kampanii (agregacja debaty)
    │
    ├── ARCHITECTURE.md                ← dokumentacja techniczna systemu
    └── WEBINAR_GUIDE.md               ← guide do kampanii webinarowych
```

---

## Jak przygotować brief

Edytuj **tylko** `scalac_council_v2/shared/brief.md` przed uruchomieniem. To jedyny plik który musisz zmienić przy nowej kampanii.

```markdown
# Brief Projektu: [nazwa]

## Projekt: [opis jednym zdaniem]

### Kontekst
[czego chce Scalac, skąd pomysł na kampanię]

### Cel
[co chcemy osiągnąć — pipeline, leads, brand awareness]

### Target
- Segment: [kto — fintechy Series B, enterprise z JVM, etc.]
- Geo: [gdzie — DACH, London, Nordic, EU]
- Decision Maker: [CTO / VP Eng / Head of Platform]
- Pain Points: [konkretne bóle]
- Budget: [orientacyjny budżet klienta]

### Constraints
- Timeline: [ile masz czasu]
- Zasoby: [marketer, intern, etc.]
- Pipeline target: [liczba]

### Deliverables
1. Marcus: [co ma zrobić]
2. Elena: [co ma zrobić]
3. Kai: [co ma zrobić]
4. David: [co ma zrobić]

### Konta do rozważenia (opcjonalne)
[lista firm z geo i sygnałami jeśli już wiesz]
```

Im więcej konkretów w briefie, tym lepsze outputy agentów. Minimalne wymaganie: Segment + Cel + Pain + Decision Maker.

---

## Wiedza kontekstowa w promptach

Każdy wygenerowany `prompts/*.md` zawiera automatycznie:

| # | Element | Skąd pochodzi | Kto dostaje |
|---|---------|---------------|-------------|
| 1 | System prompt agenta | `agents/[name]_agent.py` | każdy swój |
| 2 | Battlecards (analiza konkurencji) | `shared/battlecards.md` | wszyscy |
| 3 | Content Plan (strategia contentowa) | `shared/content_plan.md` | wszyscy |
| 4 | Brief projektu | `shared/brief.md` | wszyscy |
| 5 | Dyskusja (poprzednie rundy) | `shared/discussion/` | wszyscy (rundy 2–3) |
| 6 | Target Accounts (pełne dane) | `shared/target_accounts.md` | David only |
| 7 | Target Accounts (Key Intelligence) | sekcja 4 `target_accounts.md` | Marcus, Elena, Kai |

Agenci **nie pytają** o dane rynkowe — mają je wbudowane w prompt zanim zaczną pisać.

---

## Przykładowy output — kampania JVM/Rust DACH/Stockholm/London

`output/FINAL_PROPOSAL.md` to wynik pełnej 2-rundowej debaty dla tego briefa.
Zawiera:

1. **OFFER** — positioning per geo (London / DACH / Nordic), pricing tiers:
   - London Starter: £14–16K/mies. | Scale: £37–43K | Enterprise: custom
   - DACH Starter: CHF 13–16K/mies. | Scale: CHF 35–42K | Enterprise: custom
   - Nordic Starter: SEK 140–165K/mies. | framing: zero arbetsgivaravgifter + 30-day exit
   - TCO Calculator z email-gate jako CTA (ceny nie na landing page — DACH decyzja)

2. **LEJEK** — Three Pipelines + MEDDIC per geo:
   - London: 90 dni → 12 discovery calls → 4 proposals → 1 closed deal (500K PLN)
   - DACH: 180 dni → buying committee + pilot first w Touch #8
   - Nordic: Q3 cumulative target, 6–12 mies. cycle

3. **COPY** — gotowe do użycia:
   - 3 hero headlines (London / DACH / Nordic), jeden claim per geo
   - 3 cold emails — angielski (London/Nordic), **niemecki** (DACH)
   - LinkedIn hooks dla 8 kont z Dream 20
   - Webinar invite DACH po niemiecku

4. **KONTA** — Dream 20 tabela z emailami (8 London, 7 DACH, 5 Nordic):
   - 12-touch cadence daily template (Day 1 SDR Playbook)
   - Webinar mapa per konto (kto dostaje invite w którym touch)
   - Triggery per konto (AI vacancies, funding, conference presence)

5. **6 otwartych pytań** dla Scalac leadership (przed uruchomieniem kampanii)

---

## Monitorowanie i debugowanie

```bash
# Regeneruj prompty z aktualnym briefem
cd scalac_council_v2 && python orchestrator.py

# Status debaty (ile rund, kto skończył)
python orchestrator.py --monitor

# Sprawdź konkretną rundę
cat scalac_council_v2/shared/discussion/round_1_marcus.md

# Lista wszystkich plików dyskusji
ls scalac_council_v2/shared/discussion/

# Agregacja finalna (po zakończeniu wszystkich rund)
python orchestrator.py --final

# Wynik
cat scalac_council_v2/output/FINAL_PROPOSAL.md
```

---

## Prompty testowe

Gotowe briefe do przetestowania całego flow. Wpisz jako `@Scalac Council [prompt]` w VS Code,
albo zaktualizuj `shared/brief.md` i uruchom orchestrator.

### 1. Aktywny brief — JVM/Rust DACH/Stockholm/London *(wynik tej sesji)*
```
@Scalac Council Scale-upy z JVM lub Rust w stacku. Geo: Zürich, London, Stockholm.
Cel: Team Extension. 90 dni do discovery calls. Pokaż ofertę, lejek, copy i Dream 20 kont.
```
Ten brief jest już w `shared/brief.md` — `output/FINAL_PROPOSAL.md` zawiera gotowy wynik.

---

### 2. Klasyczny — Team Extension Fintechy Series B
```
@Scalac Council Team Extension dla fintechów Series B w EU. Target: CTO/VP Eng,
budget 300–500K EUR/rok, 90 dni do pipeline 500K PLN.
```
Happy path do sprawdzenia czy system działa. Agenci mają ten segment dobrze opracowany.

---

### 3. Nowy segment — Sovereign AI dla banków
```
@Scalac Council Banki Tier 1 DACH i Benelux chcą wdrożyć AI on-premise (DORA, compliance).
Decision makers: CTO + Chief Compliance Officer. Budget 500K–1M EUR.
Deliverable: oferta compliance-first + lejek 6-miesięczny + white paper door-opener.
```
Testuje czy agenci dostosowują messaging do regulowanego segmentu. Marcus musi zmienić pricing, David nowe targety.

---

### 4. Krótki — tylko jeden output
```
@Scalac Council Napisz landing page hero section dla Scalac Team Extension dla CTO
Scale-upu B2B SaaS po Series B, London. Potrzebuje 5 Scala devów w 8 tygodni.
```
Testuje czy Kai dostaje robotę bez pełnego flow debaty. Szybkie copy bez 3 rund.

---

### 5. Edge case — konkretne konto z target_accounts
```
@Scalac Council ABM sequence dla Artifact (Lausanne, Scala w stacku, rekrutują Senior AI).
Kontakt: michael.wegmueller@artifact.swiss. 12-touch cadence, 8 tygodni.
Ton: DACH — suchy, konkretny, po niemiecku na Touch #9.
```
Testuje czy David korzysta z `target_accounts.md`. Artifact jest w Tier 1 DACH — David powinien znać firmę bez dodatkowego tłumaczenia.

---

### 6. Stres test — konflikt cenowy
```
@Scalac Council Marcus chce wycenić DACH Team Extension na CHF 25K/mies. per senior.
Elena twierdzi że discovery call conversion przy tej cenie to 0.3% i nie udźwignie pipeline.
Debata: rozstrzygnijcie cenę z danymi TCO i pipeline math. Jeden finalny pricing.
```
Testuje mechanizm debaty — czy agenci naprawdę zmieniają zdanie gdy są dane. Marcus i Elena muszą dojść do konsensusu.

---

### 7. Content play
```
@Scalac Council Kampania contentowa Q2 2026 wokół "Scala+AI w produkcji finansowej".
3 posty LinkedIn/tydzień, 1 webinar czerwiec, 1 case study. Output: Kai — tematy i hooki,
Marcus — jak content buduje pipeline, Elena — sekwencja promocji, David — kto z Dream 20
dostaje każdy kawałek.
```
Testuje koordynację wszystkich 4 agentów na zadaniu contentowym. Sprawdzi spójność cross-agent i czy David potrafi mapować content na konkretne konta.

---

## Jak dodać nowe dane prospektowe

1. Dodaj CSV do `csv/`
2. Uruchom analizę (wzorzec ze skryptu który generował `target_accounts.md`):
   ```python
   import pandas as pd
   df = pd.read_csv('csv/[nowy_plik].csv')
   # ... analiza, wyciągnij firmy z flagami SCALA, KAFKA, AI vacancies ...
   ```
3. Zaktualizuj `shared/target_accounts.md`
4. Orchestrator automatycznie wczyta nowe dane przy następnym `python orchestrator.py`

---

## Architektura systemu

Szczegółowa dokumentacja techniczna: `scalac_council_v2/ARCHITECTURE.md`

```
Użytkownik
    │
    ├── VS Code: @Scalac Council [brief]
    │       └── .github/agents/scalac-council.agent.md
    │               ├── spawns: marcus.agent.md
    │               ├── spawns: elena.agent.md      ← równolegle
    │               ├── spawns: kai.agent.md
    │               └── spawns: david.agent.md
    │
    ├── Cursor/Kimi/Claude: python orchestrator.py
    │       ├── load_context()     → brief + battlecards + content_plan + target_accounts
    │       ├── build_prompt()     → differential injection (David=60KB, innych=15KB)
    │       ├── generate_prompts() → prompts/[agent]_prompt.md
    │       ├── try_kimi_spawn()   → auto-spawn jeśli sessions_spawn() w builtins
    │       └── print_ide_instructions() → per-IDE instructions
    │
    └── Dowolny chatbot: wklej zawartość prompts/[agent]_prompt.md

Agenci komunikują się przez pliki:
    shared/discussion/round_1_marcus.md
    shared/discussion/round_1_elena.md   ← każdy czyta pozostałe przed Rundą 2
    shared/discussion/round_1_kai.md
    shared/discussion/round_1_david.md

Output:
    output/FINAL_PROPOSAL.md             ← agregacja po wszystkich rundach
```

# Rada AI Scalac — Multi-Agent Marketing Council

> **4 agenci AI pracują równolegle, debatują i tworzą kompletny plan marketingowy Scalac.**
>
> Powiedz `@Scalac Council zrób plan dla X` — agenci działają sami.

---

## Do czego to służy

System do tworzenia **kompletnych planów marketingowych Scalac** w 30 minut zamiast kilku dni.

Zamiast pisania jednego długiego prompta — 4 wyspecjalizowani eksperci pracują równolegle, kwestionują nawzajem swoje założenia i dochodzą do konsensusu.

### Przykładowe projekty

| Projekt | Co dostajesz |
|---------|--------------|
| **Team Extension dla Fintechów Series B** | Oferta + Lejek + Landing page + Dream 100 |
| **Sovereign AI dla Banków** | Compliance-first pitch + 6-miesięczny cykl sprzedaży + White paper |
| **Migration Legacy → Scala 3** | Fixed-price offer + Technical case studies + Targeting enterprise architects |
| **Scala+AI dla Scale-upów** | Positioning + Playbook content + ABM Tier 1 |
| **Webinar / Event launch** | Messaging + Email sequence + Follow-up cadence |

---

## Agenci — kto co robi

### Marcus — Offer Architect
**Rola:** Projektuje ofertę, pricing i positioning.

Używa: *Gap Selling*, *The Challenger Sale*, *Monetizing Innovation* (Good-Better-Best pricing), *StoryBrand SB7*.

Wie: Scalac jest jedynym Official Akka Tech Partnerem w EU. Rynek płaci $50–99/hr (VirtusLab, SoftwareMill). Target dla Series B to €300–500K/rok.

Walczy o: wysoką cenę i wartość zamiast godzinówek. Elena zawsze chce obniżyć — Marcus broni.

**Output:** `output/marcus_offer.md` — oferta z ROI, pricing tiers, challenger pitch.

---

### Elena — Funnel Architect
**Rola:** Projektuje lejek, kwalifikację leadów i pipeline.

Używa: *MEDDIC*, *The JOLT Effect*, *Predictable Revenue* (Seeds/Nets/Spears), *From Impossible to Inevitable*.

Wie: 1 marketer + 1 intern = lejek musi być realistyczny. SoftwareMill ma NPS 73 i 70% CTO re-engagement — to benchmark do pobicia. Pipeline target: 500K PLN w 90 dni.

Walczy o: realistyczne konwersje. Kwestionuje zbyt optymistyczne założenia Marcusa.

**Output:** `output/elena_funnel.md` — etapy lejka, metryki konwersji, MEDDIC dla każdego etapu.

---

### Kai — Copywriter
**Rola:** Pisze landing pages, email sequences, LinkedIn hooks, ad copy.

Używa: *They Ask You Answer* (Big 5), *StoryBrand*, *Obviously Awesome*, frameworki AIDA i PAS.

Wie: nikt na rynku nie ma spójnego messagingu "Scala+AI" — to złota okazja. Positioning: *"Jedyni, gdzie Twoi Scala engineerzy SĄ Twoimi AI engineerami."* VirtusLab ma 8 Clutch reviews, Scalac 23.

Walczy o: jasność dla CTO który ma 30 sekund. Kwestionuje zbyt techniczny język Marcusa i Davida.

**Output:** `output/kai_copy.md` — hero headline, email subject lines, LinkedIn hooks, CTA, porównanie z konkurencją.

---

### David — Lead Strategist
**Rola:** Buduje listę Dream 100 kont, sekwencje outreach i ABM.

Używa: *ABM Playbook*, *Fanatical Prospecting*, *Signal-Based Selling*, *12-Touch Cadence*.

Wie: VirtusLab jest mocny w Retail/Insurance/FinTech. SoftwareMill dominuje FinTech (ale ma 2 osobne teamy = słabość). Endava/EPAM mają zero Scala+AI → ich klienci używający Scali to warm leady.

Sygnały do atakowania konta: Series B announcement, job posting "Scala developer", Scala Days/Akka meetupy, klient Endavy używający Scali.

**Output:** `output/david_abm.md` — Dream 100 lista, tiering, sekwencje, timing z content planem.

---

## Jak działa debata

Agenci piszą 3 rundy. Każda runda to osobny plik w `shared/discussion/`.

```
Runda 1 — wszyscy naraz (~5 min):
  Marcus pisze ofertę
  Elena planuje lejek          ← czytają się wzajemnie
  Kai przygotowuje copy
  David wybiera konta

Runda 2 — konfrontacja (~10 min):
  Elena: "Marcus, konwersje 40% są nierealistyczne dla cold outreach!"
  Marcus: "Elena, pricing €150/hr jest poniżej wartości którą dostarczamy"
  Kai: "Oboje jesteście zbyt techniczni — CTO nie rozumie 'Akka actor model'"
  David: "Mam 3 konta Tier 1 które potrzebują case study od Kai"

Runda 3 — konsensus (~10 min):
  Agenci dostosowują swoje outputy do feedbacku
  Zapisują finalny output
```

**Shared workspace** w `shared/discussion/` — agenci czytają pliki nawzajem i odpowiadają. Plik `round_2_elena.md` zawiera bezpośrednie cytaty z `round_1_marcus.md`.

---

## Skąd agenci biorą wiedzę o rynku

Każdy agent ma wbudowaną wiedzę z dwóch dokumentów:

**`scalac_battlecards.docx.md`** — analiza konkurencji (marzec 2026):
- VirtusLab: mocny w Scala, słaby w unified Scala+AI brand. ML team Python-centric.
- SoftwareMill: 2 osobne teamy (Scala ≠ AI team) — CTO dostaje dwa różne pitch'e.
- Xebia: ich `xef.ai` to Kotlin, nie Scala. Premium pricing = nie konkurujemy bezpośrednio.
- Endava/EPAM: zero Scala+AI messagingu → ich klienci to nasze leady.
- Scalac: jedyny Official Akka Tech Partner. `scalac.ai` jako dedykowany brand.

**`scalac_content_plan.docx.md`** — plan contentowy (kwiecień–wrzesień 2026):
- LinkedIn 3x/tydzień (wtorek thought leadership, czwartek technical)
- Scala+AI Playbook Blog Series (10 postów, keywords: "scala ai programming", "akka ai agents")
- Czerwiec 2026: *The Scala+AI Manifesto* — door-opener dla Tier 1 kont
- Wrzesień 2026: *State of Scala+AI 2026* Survey Report — excuse to reach out
- Reddit r/scala weekly — community trust building

Orchestrator wczytuje oba pliki przy generowaniu promptów i wstrzykuje je do każdego agenta.

---

## Jak uruchomić

### VS Code + GitHub Copilot (najłatwiej)

Wpisz w czacie:
```
@Scalac Council Team Extension dla fintechów Series B — zrób kompletny plan
```

Orchestrator agent automatycznie:
1. Zapisuje brief do `shared/brief.md`
2. Wywołuje 4 subagenty równolegle
3. Agreguje debatę
4. Zwraca `output/FINAL_PROPOSAL.md`

---

### Cursor

1. Uruchom orchestrator żeby wygenerować pliki promptów:
   ```bash
   cd scalac_council_v2 && python orchestrator.py
   ```

2. Otwórz 4 zakładki Composer (`Ctrl+Shift+I` → "+ New Composer"):
   - Wklej `prompts/marcus_prompt.md`
   - Wklej `prompts/elena_prompt.md`
   - Wklej `prompts/kai_prompt.md`
   - Wklej `prompts/david_prompt.md`

3. Uruchom wszystkie 4 jednocześnie.

4. Po zakończeniu:
   ```bash
   python orchestrator.py --final
   ```

Cursor zna ten workflow — wpisz "scalac council" a reguła `.cursor/rules/scalac-council.mdc` podpowie mu co robić.

---

### OpenClaw / Kimi Code (auto-spawn)

```bash
cd scalac_council_v2 && python orchestrator.py
```

Orchestrator automatycznie wykrywa `sessions_spawn()` i spawnuje 4 sesje równolegle. Nic więcej nie trzeba robić.

Monitorowanie:
```bash
python orchestrator.py --monitor
```

Finalna agregacja (po 3 rundach):
```bash
python orchestrator.py --final
```

---

### Claude Code

```bash
cd scalac_council_v2 && python orchestrator.py
```

Generuje `prompts/*.md`. Otwórz 4 osobne okna terminala z Claude:
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

W Mission Control:
1. Otwórz Mission Control (`Ctrl+Shift+M`)
2. "+ New Agent" × 4
3. Dla każdego: `@file prompts/[agent]_prompt.md`
4. Uruchom wszystkich jednocześnie — Antigravity synchronizuje dostęp do `shared/` przez Cross-surface Agents

---

### Dowolny chatbot (ChatGPT, Claude.ai, Gemini itp.)

```bash
python orchestrator.py
```

Otwórz 4 osobne okna chata. W każdym wklej zawartość odpowiedniego pliku z `prompts/`.

---

## Struktura plików

```
scalac_ai_council/
├── scalac_battlecards.docx.md     ← wiedza o konkurencji (źródło)
├── scalac_content_plan.docx.md    ← plan contentowy (źródło)
│
├── .github/agents/                ← VS Code Copilot agents
│   ├── scalac-council.agent.md    ← główny orchestrator (@Scalac Council)
│   ├── marcus.agent.md            ← subagent Offer Architect
│   ├── elena.agent.md             ← subagent Funnel Architect
│   ├── kai.agent.md               ← subagent Copywriter
│   └── david.agent.md             ← subagent Lead Strategist
│
├── .cursor/rules/
│   └── scalac-council.mdc         ← Cursor workflow rules
│
└── scalac_council_v2/
    ├── orchestrator.py             ← główny skrypt (Kimi/Claude Code/terminal)
    ├── shared/
    │   ├── brief.md                ← brief projektu (edytuj przed startem)
    │   ├── battlecards.md          ← kopia battlecards dla agentów
    │   ├── content_plan.md         ← kopia content planu dla agentów
    │   └── discussion/             ← debata agentów (round_X_agent.md)
    ├── output/                     ← finalne outputy agentów
    │   ├── marcus_offer.md
    │   ├── elena_funnel.md
    │   ├── kai_copy.md
    │   ├── david_abm.md
    │   └── FINAL_PROPOSAL.md       ← agregacja wszystkiego
    ├── prompts/                    ← generowane przez orchestrator.py
    │   ├── marcus_prompt.md        ← gotowy prompt (battlecards wbudowane)
    │   ├── elena_prompt.md
    │   ├── kai_prompt.md
    │   └── david_prompt.md
    └── agents/                     ← kod źródłowy agentów (Python)
        ├── marcus_agent.py
        ├── elena_agent.py
        ├── kai_agent.py
        └── david_agent.py
```

---

## Jak przygotować brief

Edytuj `scalac_council_v2/shared/brief.md` przed uruchomieniem. Minimalna struktura:

```markdown
# Brief Projektu: [nazwa]

## Segment
[kto jest targetem — np. "Fintechy Series B EU, CTO/VP Engineering"]

## Cel
[co chcemy osiągnąć — np. "500K PLN pipeline w 90 dni"]

## Pain
[główny ból klienta — np. "Hiring Scala devów trwa 6+ miesięcy"]

## Budget klienta
[np. "300-500K EUR/rok na team extension"]

## Constraints
[ograniczenia — np. "1 marketer + 1 intern, launch w Q2 2026"]
```

Im więcej kontekstu, tym lepsze outputy agentów.

---

## Niezbędna wiedza kontekstowa dla agentów

Każdy wygenerowany prompt (`prompts/*.md`) zawiera automatycznie:

1. **System prompt agenta** — jego rola, książki, styl, zasady debaty
2. **Battlecards** — pełna analiza konkurencji z `scalac_battlecards.docx.md`
3. **Content Plan** — strategia contentowa z `scalac_content_plan.docx.md`
4. **Brief projektu** — zawartość `shared/brief.md`
5. **Aktualna dyskusja** — to co inni agenci już napisali (dla rund 2 i 3)

Agenci **nie pytają** o kontekst rynkowy — mają go wbudowanego.

---

## Monitorowanie i debugowanie

```bash
# Status dyskusji
python scalac_council_v2/orchestrator.py --monitor

# Ręczne sprawdzenie rundy
cat scalac_council_v2/shared/discussion/round_1_marcus.md

# Lista wszystkich plików dyskusji
ls scalac_council_v2/shared/discussion/

# Finalna agregacja
python scalac_council_v2/orchestrator.py --final

# Wynik
cat scalac_council_v2/output/FINAL_PROPOSAL.md
```

---

## Prompty testowe

Gotowe briefe do przetestowania całego flow. Wpisz jako `@Scalac Council [prompt]` w VS Code, albo wklej przy uruchamianiu orchestratora.

### 1. Klasyczny — Team Extension (domyślny brief)
```
@Scalac Council Zrób pełny plan marketingowy dla Team Extension dla fintechów Series B w EU. Target: CTO/VP Eng, budget 300-500K EUR/rok, 90 dni do pipeline 500K PLN.
```
Przetestuje cały happy path — agenci mają ten brief w `shared/brief.md`. Dobry punkt startowy do sprawdzenia czy system w ogóle działa.

---

### 2. Nowy segment — Sovereign AI dla banków
```
@Scalac Council Segment: banki i instytucje finansowe Tier 1 w DACH i Benelux. Potrzebują wdrożyć AI on-premise (compliance, DORA, regulacje). CTO + Chief Compliance Officer jako decision makers. Budget 500K-1M EUR. Deliverable: oferta compliance-first + lejek 6-miesięczny + white paper door-opener.
```
Testuje czy agenci potrafią wyjść poza domyślny brief i dostosować messaging do nowego segmentu. Sprawdzi elastyczność Marcusa (nowe pricing) i Davida (nowe targety).

---

### 3. Krótki — jeden output
```
@Scalac Council Napisz landing page hero section dla Scalac Team Extension targetowanego w CTO Scale-upu B2B SaaS który właśnie dostał Series B i potrzebuje 5 Scala devów w 8 tygodni.
```
Testuje czy Kai dostaje robotę bez pełnego flow 3 rund. Przydatne gdy potrzebujesz szybkiego copy bez debaty.

---

### 4. Edge case — konkretne konto z target_accounts
```
@Scalac Council Zrób ABM sequence dla iManage (zarządzanie dokumentami prawnymi, Scala w stacku, aktywnie szukają AI engineer). Kontakt: bijo.thomas@imanage.com. 12-touch cadence, 6 tygodni. Zacznij od cold email Runda 1.
```
Testuje czy David korzysta z `target_accounts.md` i potrafi operować na konkretnym koncie. David powinien znać iManage bez Twojego tłumaczenia — firma jest w jego Tier 1 liście.

---

### 5. Stres test — konflikt cenowy między agentami
```
@Scalac Council Marcus chce wycenić Team Extension na €175/hr żeby podkreślić premium. Elena twierdzi że cold conversion przy takiej cenie to 0.5% i nie udźwignie pipeline 500K PLN. Wy dwoje rozstrzygnijcie to w debacie i zaproponujcie finalny pricing z uzasadnieniem ROI.
```
Testuje mechanizm debaty — czy agenci naprawdę kwestionują swoje założenia i dochodzą do konsensusu. Najlepszy test integracyjny systemu.

---

### 6. Content zamiast sprzedaży
```
@Scalac Council Zaplanuj kampanię contentową Q2 2026 wokół tematu "Scala+AI w produkcji finansowej". 3 posty LinkedIn/tydzień, 1 webinar, 1 case study. Output: Kai — tematy i hooki, Marcus — jak każdy content buduje pipeline, Elena — jak sekwencjonować promocję do targetów, David — kto z Dream 100 dostaje każdy kawałek contentu.
```
Testuje koordynację między wszystkimi czterema agentami na zadaniu contentowym zamiast sprzedażowego. Sprawdzi spójność outputów cross-agent.

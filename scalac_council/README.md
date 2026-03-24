# Rada AI - True Multi-Agent System

Prawdziwy multi-agent system dla Scalac marketingu. 4 agenci pracują równolegle, dyskutują i dochodzą do konsensusu.

## 🎯 Filozofia

**NIE:** 5 promptów sekwencyjnie (Marcus → Elena → Kai...)  
**TAK:** 4 agenty równolegle, debata, iteracja, konsensus

## 🏗️ Architektura

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR (Ty)                         │
│                   Ta sesja Kimi Code                         │
└─────────────────────────────────┬───────────────────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
       ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
       │   Marcus     │   │    Elena     │   │     Kai      │
       │   Agent      │   │    Agent     │   │    Agent     │
       │  (Session 1) │   │  (Session 2) │   │  (Session 3) │
       └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
              │                   │                   │
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │
                          ┌───────▼────────┐
                          │     David      │
                          │     Agent      │
                          │   (Session 4)  │
                          └────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │      SHARED WORKSPACE      │
                    │  /workspace/scalac-council │
                    ├────────────────────────────┤
                    │  shared/brief.md           │
                    │  shared/discussion/        │
                    │  output/                   │
                    └────────────────────────────┘
```

## 🔄 Jak To Działa

### Faza 1: Spawn (Równolegle)
Wszystkie 4 sesje agentów startują jednocześnie:
- Każdy czyta brief
- Każdy pisze Round 1 swojego stanowiska
- Każdy zapisuje do `shared/discussion/`

### Faza 2: Debata (Iteracyjnie)
Agenci czytają nawzajem swoje outputy:
- Round 2: Komentują, kwestionują, proponują
- Round 3: Szukają konsensusu lub finalizują

### Faza 3: Final (Konsensus)
Każdy agent pisze finalny output:
- `output/marcus_offer.md`
- `output/elena_funnel.md`
- `output/kai_copy.md`
- `output/david_abm.md`

### Faza 4: Agregacja
Orchestrator składa wszystko w `FINAL_PROPOSAL.md`

## 📁 Struktura

```
scalac_council/
├── orchestrator.py          # Koordynator (uruchom w tej sesji)
├── agents/
│   ├── marcus_agent.py      # Agent Marcusa (prompt + logika)
│   ├── elena_agent.py       # Agent Eleny
│   ├── kai_agent.py         # Agent Kaia
│   └── david_agent.py       # Agent Davida
├── shared/
│   ├── brief.md             # Input projektu
│   ├── discussion/          # Wymiana między agentami
│   │   ├── round_1_marcus.md
│   │   ├── round_1_elena.md
│   │   └── ...
│   └── consensus.md         # Opcjonalny konsensus
└── output/
    ├── marcus_offer.md      # Finalny output Marcusa
    ├── elena_funnel.md      # Finalny output Eleny
    ├── kai_copy.md          # Finalny output Kaia
    ├── david_abm.md         # Finalny output Davida
    └── FINAL_PROPOSAL.md    # Złączone wszystkie
```

## 🚀 Użycie w Kimi Code

### Krok 1: Przygotuj Brief
Edytuj `shared/brief.md` z opisem projektu.

### Krok 2: Uruchom Orchestrator
W tej sesji:
```bash
python orchestrator.py
```

To pokaże status workspace i instrukcje spawnowania agentów.

### Krok 3: Spawn Agentów (Równolegle)
W Kimi Code użyj `sessions_spawn`:

```python
# Marcus - Offer Architect
sessions_spawn(
    runtime="subagent",
    task="""Jesteś Marcus, Offer Architect w Scalac.

Przeczytaj /root/.openclaw/workspace/scalac-council/shared/brief.md

Twoja rola:
1. Napisz Round 1 do shared/discussion/round_1_marcus.md
2. Czekaj na innych agentów (round_1_elena.md, itd.)
3. Przeczytaj ich i odpowiedz w Round 2
4. Kontynuuj debatę przez 3 rundy lub do konsensusu
5. Napisz finalny output do output/marcus_offer.md

Używaj frameworków: Gap Selling, StoryBrand, Good-Better-Best, Challenger Sale.
Krytykuj Elenę jeśli jej konwersje są nierealistyczne.
Bronij swojego pricingu.
""",
    label="marcus"
)

# Elena - Funnel Architect  
sessions_spawn(
    runtime="subagent",
    task="""Jesteś Elena, Funnel Architect w Scalac.

Przeczytaj brief i round_1_marcus.md (jak gotowe).

Twoja rola:
1. Napisz Round 1 do shared/discussion/round_1_elena.md
2. Zkrytykuj pricing Marcusa - czy jest realistyczny?
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
2. Dream 100 - konkretne konta fintech
3. ABM strategy - czy lejek Eleny jest wykonalny?
4. Final: output/david_abm.md

Używaj: ABM tiers, signal-based selling, 12-touch sequences.
Konkrety > Ogólniki.
""",
    label="david"
)
```

### Krok 4: Monitoruj
W tej sesji (Orchestrator):
```bash
python orchestrator.py
```

Pokaże:
- Którzy agenci już odpowiedzieli
- Na której rundzie jesteście
- Czy jest już konsensus

### Krok 5: Sprawdź Dyskusję
```bash
# Przeczytaj konkretną rundę
cat shared/discussion/round_1_marcus.md
cat shared/discussion/round_2_elena.md

# Lub wszystko naraz
ls -la shared/discussion/
```

### Krok 6: Pobierz Finalne Wyniki
```bash
# Pojedyncze outputy
cat output/marcus_offer.md
cat output/elena_funnel.md

# Albo wszystko razem
cat output/FINAL_PROPOSAL.md
```

## 🎭 Agenci

| Agent | Rola | Style | Będzie walczył o... |
|-------|------|-------|---------------------|
| **Marcus** | Offer Architect | Challenger, liczby | Wysoki pricing, wartość |
| **Elena** | Funnel Architect | Procesowa, metryki | Realistyczne konwersje |
| **Kai** | Copywriter | Clarity-focused | Proste messaging |
| **David** | Lead Strategist | Konkretny | Wykonalny plan ABM |

## 💡 Przykładowe Konflikty (i jak je rozwiązać)

### Konflikt 1: Pricing
- **Marcus:** "75-85 EUR/h to fair"
- **Elena:** "Za drogo, będzie niższa konwersja"
- **Rozwiązanie:** JOLT - replacement guarantee jako risk reversal

### Konflikt 2: Konwersje
- **Marcus:** "50% lead → MQL"
- **Elena:** "Realistycznie 25%"
- **Rozwiązanie:** Test with Architecture Review jako PQL

### Konflikt 3: Messaging
- **Marcus:** "Gap Analysis, Future State"
- **Kai:** "Za techniczne, CTO chce 'Scale in 2 weeks'"
- **Rozwiązanie:** Lead with speed, support with Gap Analysis

## ✅ Success Criteria

Dobra debata kończy się gdy:
- [ ] Agenci przeszli przez 3 rundy
- [ ] Lub explicit konsensus w dyskusji
- [ ] Każdy ma spójne finalne outputy
- [ ] Orchestrator złożył FINAL_PROPOSAL.md

## 🔧 Troubleshooting

### "Agenci nie widzą swoich plików"
Upewnij się że wszyscy używają absolutnych ścieżek:
- ✅ `/root/.openclaw/workspace/scalac-council/shared/...`
- ❌ `shared/...` (relatywna)

### "Dyskusja stoi w miejscu"
Dodaj w promptach:
```
JEŚLI minęło >10 minut od ostatniego postu innego agenta,
napisz kolejną rundę nawet jeśli nie ma nowych postów.
```

### "Agenci się nie zgadzają"
To feature, nie bug! Niech debatują. W Round 3 niech zapiszą:
```markdown
## Konsensus / Disagreement
Zgadzamy się co do: [...]
Nie zgadzamy się co do: [...]
Decyzja: [...] (uzasadnienie)
```

## 📊 Różnica vs Stary System

| Aspekt | Stary (5 promptów) | Ten (True Multi-Agent) |
|--------|-------------------|----------------------|
| **Architektura** | Sekwencyjna | Równoległa |
| **Komunikacja** | Brak | Debaty 3-rundowe |
| **Iteracja** | Brak | Tak - feedback loops |
| **Konsensus** | Brak | Tak - agenci się zgadzają |
| **Stack** | LangChain/K8s | Pliki + sessions_spawn |
| **Setup** | 2-3 miesiące | 5 minut |
| **Koszt** | $1000/mies | Cena Kimi Code |

## 🎓 Wskazówki

1. **Nie przerywaj za wcześnie** - Niech agenty przedebatują 3 rundy
2. **Czytaj dyskusję** - To najciekawsza część, widać jak AI myśli
3. **Interweniuj jeśli trzeba** - Orchestrator może dodać hint do briefu
4. **Testuj różne briefy** - Każdy projekt = nowa debata

## 📝 Przykładowe Briefy do Testu

### Brief 1: Team Extension Fintech
```markdown
## Projekt: Team Extension dla Fintechów Series B
Target: Fintechy 5-50M EUR funding
Pain: Hiring trwa 6 miesięcy, potrzebują szybko skalować
Budget: 300-500k EUR
```

### Brief 2: Sovereign AI Banking
```markdown
## Projekt: Sovereign AI dla Banków
Target: Swiss private banks
Pain: Compliance blokuje AI POC, chcą on-premise
Budget: 200-500k EUR POC
```

### Brief 3: Migration Project
```markdown
## Projekt: Migration Legacy → Scala
Target: Enterprise z Java monolith
Pain: System nie skaluje, tech debt
Budget: 300k EUR fixed price
```

---

**Gotowy?** Uruchom `python orchestrator.py` i zacznij prawdziwą Radę AI! 🚀

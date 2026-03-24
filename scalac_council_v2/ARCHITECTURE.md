# Architektura Techniczna - Rada AI v2

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     KIMI CODE (Host)                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Session: Orchestrator (Ty)                 │   │
│  │         • Monitoruje dyskusję                          │   │
│  │         • Agreguje outputy                             │   │
│  │         • Koordynuje                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│              ┌───────────────┼───────────────┐                  │
│              │               │               │                  │
│              ▼               ▼               ▼                  │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │ Session: Marcus │ │ Session: Elena  │ │  Session: Kai   │   │
│  │  (Subagent)     │ │  (Subagent)     │ │  (Subagent)     │   │
│  │  • Read brief   │ │  • Read brief   │ │  • Read brief   │   │
│  │  • Write round  │ │  • Read Marcus  │ │  • Read all     │   │
│  │  • Read others  │ │  • Write round  │ │  • Write round  │   │
│  │  • Final output │ │  • Final output │ │  • Final output │   │
│  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘   │
│           │                   │                   │             │
│           └───────────────────┼───────────────────┘             │
│                               │                                 │
│                      ┌─────────▼─────────┐                     │
│                      │  Session: David   │                     │
│                      │   (Subagent)      │                     │
│                      └─────────┬─────────┘                     │
│                                │                               │
└────────────────────────────────┼───────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │   SHARED FILE SYSTEM    │
                    │ /workspace/scalac-council-v2
                    ├─────────────────────────┤
                    │  shared/brief.md        │
                    │  shared/discussion/     │
                    │  output/                │
                    └─────────────────────────┘
```

## Jak To Działa Technicznie

### 1. Shared File System
Wszystkie sesje (Orchestrator + 4 agenci) działają w tym samym workspace Kimi Code.
Mają dostęp do tych samych plików:

```python
# Wszystkie sesje widzą:
/root/.openclaw/workspace/scalac-council-v2/
├── shared/brief.md              # Read-only (ustawia user)
├── shared/discussion/           # Read-write (agenci piszą)
└── output/                      # Write (finalne outputy)
```

### 2. Komunikacja przez Pliki
Agenci nie rozmawiają bezpośrednio. Komunikują się asynchronicznie przez pliki:

```
Round 1:
  Marcus ──► round_1_marcus.md
  Elena  ──► round_1_elena.md
  Kai    ──► round_1_kai.md
  David  ──► round_1_david.md

Round 2:
  Marcus czyta round_1_*.md ──► round_2_marcus.md (odpowiedź)
  Elena  czyta round_1_*.md ──► round_2_elena.md
  ...
```

### 3. Koordynacja Czasowa
Nie ma centralnego scheduler'a. Agenci sami decydują kiedy pisać:

```python
# Logika w promptach agentów:
"""
1. Napisz Round 1 od razu
2. Czekaj 5-10 minut na innych agentów
3. Przeczytaj ich rundy
4. Napisz Round 2 (jeśli masz co dodać)
5. Powtórz przez 3 rundy
6. Napisz finalny output
"""
```

### 4. Orchestrator Jako Monitor
Orchestrator (ta sesja) nie zarządza agentami. Tylko:
- Pokazuje status (ile rund napisano)
- Agreguje finalne outputy
- Daje instrukcje jak używać `sessions_spawn`

## Przepływ Danych

```
START
  │
  ▼
┌──────────────────────┐
│ User pisze brief.md  │
└──────────────────────┘
  │
  ▼
┌──────────────────────────────┐
│ User uruchamia orchestrator  │
│ (pokazuje instrukcje)        │
└──────────────────────────────┘
  │
  ▼
┌──────────────────────────────┐
│ User spawnuje 4 agentów      │
│ (sessions_spawn x4)          │
└──────────────────────────────┘
  │
  ├──► Marcus Session ──► round_1_marcus.md
  ├──► Elena Session ──► round_1_elena.md
  ├──► Kai Session ──► round_1_kai.md
  └──► David Session ──► round_1_david.md
  │
  ◄──── (czas mija, 5-10 min) ────►
  │
  ├──► Marcus czyta innych ──► round_2_marcus.md
  ├──► Elena czyta innych ──► round_2_elena.md
  ├──► Kai czyta innych ──► round_2_kai.md
  └──► David czyta innych ──► round_2_david.md
  │
  ◄──── (czas mija) ────►
  │
  ├──► Marcus ──► round_3_marcus.md
  ├──► Elena ──► round_3_elena.md
  ├──► Kai ──► round_3_kai.md
  └──► David ──► round_3_david.md
  │
  ▼
┌──────────────────────────────┐
│ Każdy agent pisze final:     │
│ • marcus_offer.md            │
│ • elena_funnel.md            │
│ • kai_copy.md                │
│ • david_abm.md               │
└──────────────────────────────┘
  │
  ▼
┌──────────────────────────────┐
│ Orchestrator agreguje:       │
│ FINAL_PROPOSAL.md            │
└──────────────────────────────┘
  │
  ▼
END
```

## Format Plików

### brief.md (Input)
```markdown
# Brief Projektu: [Nazwa]

## Cel
...

## Target
...

## Constraints
...
```

### round_X_agent.md (Dyskusja)
```markdown
# Runda X - [Agent]

## Moja Teza
[1-2 zdania głównej idei]

## Argumenty
1. [Z danymi/książką]
2. [Argument]

## Co Sądzę o Innych
### Marcus: [agree/disagree + dlaczego]
### Elena: [...]

## Propozycja
[Kompromis lub utrwalenie]
```

### [agent]_[output].md (Final)
```markdown
# [Typ Outputu]: [Projekt]

## Sekcja 1
[Content]

## Sekcja 2
[Content]
...
```

## Wymagania

### Dla Kimi Code
- Dostęp do `sessions_spawn` (subagents)
- Wspólny workspace `/root/.openclaw/workspace/`

### Dla Agentów
- Każdy agent to osobna sesja
- Prompt zawiera instrukcje co robić
- Agenci muszą używać absolutnych ścieżek

### Dla Usera
- Napisać brief.md przed startem
- Uruchomić orchestrator.py
- Zespawnować 4 agentów
- Poczekać 15-30 minut
- Sprawdzić outputy

## Porównanie z Innymi Architekturami

### vs LangChain/LangGraph
| Aspekt | LangGraph | Ten System |
|--------|-----------|------------|
| Orchestration | Graph-based | File-based |
| State | In-memory / DB | Filesystem |
| Persistence | Explicit | Implicit (pliki) |
| Scalability | High | Medium |
| Setup | 2-3 tyg | 5 min |
| Koszt | $1000/mies | $0 (Kimi) |

### vs CrewAI/AutoGen
| Aspekt | CrewAI | Ten System |
|--------|--------|------------|
| Framework | Python lib | Pliki + Bash |
| Agents | Classes | Subagents |
| Communication | Direct | Files |
| Learning | Code updates | Prompt updates |

## Zalety Tej Architektury

1. **Zero setup** - Działa od razu w Kimi Code
2. **Transparentność** - Widzisz każdą rundę dyskusji
3. **Debugowalność** - Pliki z historią, można czytać
4. **Edytowalność** - Możesz edytować brief, dodać rundę
5. **Kontrola** - Orchestrator daje Ci pełną kontrolę

## Ograniczenia

1. **Czas** - 15-30 minut na projekt (nie sekundy)
2. **Sync** - Agenci muszą czekać na siebie
3. **Scale** - Max ~10 agentów (przy więcej - chaos)
4. **State** - Brak formalnego state management

## Kiedy To Używać

✅ **Dobrze dla:**
- Complex decisions wymagających debaty
- Strategic planning
- Creative projects
- Quality > Speed

❌ **Nie dla:**
- Simple tasks (overkill)
- Real-time processing
- High-throughput (1000+/dzień)
- Strict latency requirements

---

**Podsumowanie:** To nie jest "prawdziwy" distributed system. To pragmatic solution który działa TERAZ w Kimi Code bez konfiguracji. 🚀

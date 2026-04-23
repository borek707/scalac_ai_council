# Universal AI Marketing Council v3.2

> **4 agenci AI pracujący równolegle, debatują i tworzą kompletny plan marketingowy dla dowolnej firmy.**
> 
> Nie szablony. Nie hardcoded Scalac. Prawdziwa integracja z LLM, równoległość przez asyncio i konfiguracja przez JSON. Teraz z trybem demo, interaktywnym menu i live dashboardem w terminalu.

---

## Czym jest ta Rada

System multi-agentowy składający się z 4 specjalistów AI (Marcus, Elena, Kai, David), który z dowolnej konfiguracji firmowej (JSON) produkuje kompletny plan marketingowy poprzez strukturyzowaną debatę.

**Zamiast jednej osoby robiącej plan w tydzień — masz 4 specjalistów debatujących w 30 minut.**

### Problem, który rozwiązuje

Tradycyjnie plan marketingowy tworzy jedna osoba:
1. Wymyśla pozycjonowanie i pricing.
2. Projektuje funnel od acquisition do close.
3. Pisze wszystkie materiały.
4. Wybiera konta i buduje strategię outreachową.

Jeden mózg, ograniczone perspektywy, dni lub tygodnie pracy.

### Rozwiązanie

**4 specjaliści pracują jednocześnie** — każdy odpowiada za inny obszar. I najważniejsze: **dyskutują ze sobą** i się nawzajem kwestionują.

Po 2-3 rundach debaty masz plan, który przeszedł krytykę wszystkich czterech perspektyw.

---

## Czterej agenci

| Agent | Rola | Frameworki | Output |
|-------|------|-----------|--------|
| **Marcus** | Offer Architect | Gap Selling, StoryBrand, Good-Better-Best, Challenger Sale | Oferta: pricing, positioning, pitch |
| **Elena** | Funnel Architect | MEDDIC, JOLT, Three Pipelines, Predictable Revenue | Lejek: konwersje, kwalifikacja, forecast |
| **Kai** | Copywriter | AIDA, Big 5, PAS, StoryBrand | Copy: landing page, emaile, LinkedIn |
| **David** | Lead Strategist | ABM Tiers, Dream 100, Signal-Based Selling | ABM: konta, sekwencje, personalizacja |

### Przykład debaty

> **Marcus**: "Wyceniam Team Extension na EUR 25K/miesiąc per senior."
>
> **Elena**: "Czekaj — przy tej cenie conversion spada do 0.3%. Pipeline nie przetrwa."
>
> **Marcus**: "Dobry punkt. Starter do EUR 19K, Scale i Enterprise zostawiam."
>
> **Kai**: "CTO nie chce widzieć ceny na stronie. TCO Calculator za email-gate."
>
> **David**: "W kontach, które znalazłem, mają aktywne oferty pracy dla Scala devów. Otwieramy z tym."

---

## Szybki start (5 minut)

### 🎮 Tryb Demo — zero konfiguracji, zero kluczy API

```bash
# Interaktywne menu (wybierz scenariusz, rundy, dashboard)
python -m council

# Szybki demo z konkretnym scenariuszem
python -m council --demo --scenario saas-launch --rounds 2 --dashboard
```

### 1. Instalacja

```bash
git clone https://github.com/borek707/scalac_ai_council.git
cd scalac_ai_council
pip install -e ".[dev]"
```

### 2. Klucz API (lub lokalny model) — tylko dla real run

```bash
export OPENAI_API_KEY="sk-..."
# lub
export ANTHROPIC_API_KEY="sk-ant-..."
# lub użyj lokalnego Ollama (darmowe)
# lub użyj Kimi Code CLI (działa natywnie w IDE Kimi)
```

### 3. Konfiguracja firmy — tylko dla real run

```bash
# Skopiuj gotowy template
cp templates/companies/fintech.json my_company.json

# Lub stwórz własny — patrz sekcja "Konfiguracja firmy" poniżej
```

### 4. Uruchom

```bash
# Interaktywne menu (bez flag)
python -m council

# Demo mode — pre-built scenariusze, bez API
python -m council --demo --scenario fintech-scale --rounds 3 --dashboard

# OpenAI (domyślnie)
python -m council --config my_company.json --rounds 3

# Anthropic Claude
python -m council --config my_company.json --provider anthropic

# Lokalny Ollama (darmowe, bez internetu)
python -m council --config my_company.json --provider ollama --model llama3

# Kimi Code CLI (w środowisku Kimi Code IDE)
python -m council --config my_company.json --provider kimi-code

# Claude Code CLI / IDE (automatycznie wykrywa credentials)
python -m council --config my_company.json --provider claude-code

# Live dashboard (działa z demo i real run)
python -m council --config my_company.json --dashboard

# Wyświetl status
python -m council --config my_company.json --monitor

# Agreguj finalny proposal
python -m council --config my_company.json --aggregate
```

### 5. Wynik

Po zakończeniu w katalogu `output/`:

| Plik | Zawartość |
|------|-----------|
| `marcus_offer.md` | Oferta: Gap Analysis, BrandScript, Pricing, Challenger Pitch |
| `elena_funnel.md` | Lejek: Stages, MEDDIC, JOLT, Three Pipelines, Forecast |
| `kai_copy.md` | Landing Page + Email Sequence + LinkedIn Ads |
| `david_abm.md` | ABM: Dream 100, Sequences, Tools |
| `FINAL_PROPOSAL.md` | Wszystko razem w jednym dokumencie |

---

## Tryb Demo

Demo mode pozwala uruchomić pełną Radę bez konfiguracji firmy i bez kluczy API. Agenci "odgrywają" predefiniowany scenariusz z gotowymi odpowiedziami — idealne na prezentacje, smoke-testy CI i onboarding.

### 4 wbudowane scenariusze

| Scenariusz | Opis | Klucz CLI |
|-----------|------|-----------|
| **SaaS Launch** | Launch AI project-management tool | `saas-launch` |
| **E-commerce Rebrand** | Rebrand sustainable fashion store | `ecommerce-rebrand` |
| **Fintech Scale** | Scale payment API to enterprise banks | `fintech-scale` |
| **Healthcare App** | Telehealth app go-to-market | `healthcare-app` |

### Przykłady

```bash
# Interaktywny wybór scenariusza
python -m council --demo

# Bezpośredni wybór scenariusza
python -m council --demo --scenario fintech-scale --rounds 2 --dashboard

# Tylko rundy, bez dashboardu
python -m council --demo --scenario healthcare-app --rounds 1
```

## Interaktywne Menu

Uruchomienie bez flag otwiera interaktywne menu w terminalu (wymaga `rich`):

```bash
python -m council
```

### Onboarding (pierwsze uruchomienie)

Przy pierwszym uruchomieniu (`python -m council`) zobaczysz **onboarding wizard**:

```
👋 Welcome! This tool runs 4 AI marketing specialists who debate in rounds
   and produce a complete marketing plan for your company.

The Four Agents:
  🏗️  Marcus — Offer Architect
  🎯  Elena  — Funnel Architect
  ✍️  Kai    — Copywriter
  🎣  David  — Lead Strategist

What would you like to do first?
  [1] 🎮  Quick Demo — see it in action, no setup needed
  [2] ⚙️   Real Run — I have a company JSON config
  [3] 📊  Dashboard Demo — watch the live terminal dashboard
  [4] 📖  Help — how the debate works
  [s] ⏭️   Skip — go to main menu
```

Wizard wykrywa pierwsze uruchomienie przez plik `~/.config/council/onboarding_done`. Możesz wymusić ponowny onboarding:

```bash
python -m council --onboarding
```

### Główne menu

Po onboardingu (lub przy `--interactive` / `-i`):

1. **Wybór trybu**: Demo Mode 🎮 lub Real Council Run ▶️
2. **Demo**: wybór scenariusza, liczby rund, dashboard on/off
3. **Real Run**: ścieżka do configu, provider LLM, model, rounds, dashboard

## Live Dashboard

Dashboard w terminalu pokazuje w czasie rzeczywistym:
- 4 panele agentów z awatarami, stanami i paskami postępu
- Logi zdarzeń z kolorowymi poziomami
- Mini-timeline debaty
- Statystyki per agent (czas, tokeny, koszt)
- ASCII bar chart porównawczy
- Podgląd treści markdown w czasie rzeczywistym

```bash
# Dashboard z demo
python -m council --demo --dashboard

# Dashboard z real run
python -m council --config firm.json --dashboard
```

Funkcje dashboardu:
- 🏗️ **Marcus** (cyan), 🎯 **Elena** (magenta), ✍️ **Kai** (green), 🎣 **David** (yellow)
- Animowane stany (`WRITING...` z kropkami)
- Alert dźwiękowy + flash przy błędzie agenta
- Export do JSON i HTML po zakończeniu

## Konfiguracja firmy

System przyjmuje dowolną konfigurację przez JSON. Schemat jest walidowany przez Pydantic v2.

### Minimalny config

```json
{
  "name": "Acme Corp",
  "product": "API-first payment platform for SaaS",
  "pricing_tier": "$5K-$50K ACV",
  "value_proposition": "Reduce payment integration time from 3 months to 2 weeks",
  "competitors": [
    {"name": "Stripe", "threat": "HIGH", "pricing": "2.9% + $0.30"},
    {"name": "Adyen", "threat": "HIGH", "pricing": "Interchange++"}
  ],
  "target": {
    "segment": "SaaS companies processing >$1M/yr",
    "decision_maker": "CTO / VP Engineering",
    "pain_points": ["Slow integration", "High fees", "Compliance complexity"],
    "budget_range": "$50K-$200K/yr"
  },
  "constraints": {
    "timeline_days": 90,
    "team_size": 3
  }
}
```

### Gotowe template'y

W `templates/companies/` znajdziesz gotowe configi dla:

| Template | Firma | Segment |
|----------|-------|---------|
| `saas.json` | CloudAPI Pro | Platforma API dla SaaS |
| `fintech.json` | PayStream | Fintech Series B |
| `ecommerce.json` | CartLoop | Platforma e-commerce |
| `consulting.json` | NexTech Advisors | Konsulting IT |

Aby użyć: `python -m council --config templates/companies/fintech.json`

### Pełny schemat (CompanyConfig)

```python
class CompanyConfig(BaseModel):
    name: str                    # Nazwa firmy (1-100 znaków)
    product: str                 # Co sprzedaje
    pricing_tier: str            # Przedział cenowy
    value_proposition: str       # Główna wartość
    competitors: list[Competitor] # Konkurencja
    target: TargetSegment        # Segment docelowy
    constraints: Constraints     # Ograniczenia
    differentiators: list[str]   # Przewagi konkurencyjne
    case_studies: list[dict]     # Case studies
```

Walidacja:
- `name`: min 1 znak, max 100
- `timeline_days`: 1-365 dni
- `budget_pln`: >= 0
- `team_size`: >= 1
- `threat`: LOW, MEDIUM, HIGH, CRITICAL

---

## Architektura v3

System składa się z 4 warstw:

```
Layer 4: Platform Layer
  CLIAdapter | KimiAdapter

Layer 3: Orchestration Layer
  AsyncOrchestrator | FilesystemBarrier | AgentStateMachine

Layer 2: Agent Layer
  BaseAgent(ABC) | MarcusAgent | ElenaAgent | KaiAgent | DavidAgent
  PromptGenerator (Jinja2) | LLMProvider(ABC)

Layer 1: Data Layer
  CompanyConfig (Pydantic) | ConfigLoader | JSON Schema
```

### Równoległość — jak to działa

```
Runda 1:                     Runda 2:                     Runda 3:
  Marcus (LLM call)            Marcus czyta innych           Konsensus
  Elena  (LLM call)     -->    Elena czyta innych      -->   Finalne outputy
  Kai    (LLM call)            Kai czyta innych
  David  (LLM call)            David czyta innych
  
  <-- asyncio.gather() -->     <-- asyncio.gather() -->     
  <-- FilesystemBarrier -->    <-- FilesystemBarrier -->
  
  Czas: ~15s                   Czas: ~15s                    Czas: ~15s
  (zamiast 60s sekwencyjnie)   (zamiast 60s sekwencyjnie)
```

**Całkowity czas: 3 rundy x 15s = 45s zamiast 3 rundy x 60s = 180s.**

### State Machine

Każdy agent ma określony stan:

```
PENDING --> WRITING --> WAITING (barrier) --> DONE --> PENDING (następna runda)
   |           |            |                  |
   +-----------+------------+------------------+--> ERROR
```

---

## CLI — Wszystkie komendy

```bash
# Interaktywne menu / onboarding
python -m council
python -m council --interactive
python -m council -i
python -m council --onboarding

# Demo mode — pre-built scenariusze, bez API
python -m council --demo
python -m council --demo --scenario healthcare-app --rounds 2 --dashboard

# Podstawowe użycie (real run)
python -m council --config firm.json

# Wybór providera LLM
python -m council --config firm.json --provider openai       # GPT-4o (domyślny)
python -m council --config firm.json --provider anthropic    # Claude Sonnet
python -m council --config firm.json --provider ollama       # Llama3 (lokalny)
python -m council --config firm.json --provider kimi-code    # Kimi Code CLI

# Nadpisanie modelu
python -m council --config firm.json --provider openai --model gpt-4o-mini

# Więcej rund debaty
python -m council --config firm.json --rounds 5

# Timeout per runda (sekundy)
python -m council --config firm.json --timeout 600

# Live dashboard (działa z demo i real run)
python -m council --config firm.json --dashboard

# Tylko status dyskusji
python -m council --config firm.json --monitor

# Agreguj finalny proposal
python -m council --config firm.json --aggregate

# Wyjściowy katalog
python -m council --config firm.json --output ./results

# Tryb verbose (debug)
python -m council --config firm.json --verbose
```

---

## Providerzy LLM

| Provider | Flaga | Domyślny model | Wymagania |
|----------|-------|----------------|-----------|
| **OpenAI** | `--provider openai` | `gpt-4o` | `OPENAI_API_KEY` |
| **Anthropic** | `--provider anthropic` | `claude-sonnet-4-6` | `ANTHROPIC_API_KEY` |
| **Ollama** | `--provider ollama` | `llama3` | Lokalny Ollama |
| **Kimi Code** | `--provider kimi-code` | `kimi-for-coding` | Zainstalowane Kimi Code CLI |
| **Claude Code** | `--provider claude-code` | `claude-sonnet-4-6` | Zainstalowane Claude Code CLI lub IDE |

### Kimi Code Provider

Provider `kimi-code` uruchamia lokalny **Kimi Code CLI** w trybie non-interactive:

```bash
kimi --quiet --yolo --prompt "Twój prompt"
```

**Auto-detekcja binarki** (w tej kolejności):
1. `KIMI_CLI_PATH` — zmienna środowiskowa
2. `shutil.which("kimi")` — PATH
3. Domyślna ścieżka instalacji VS Code extension

**Uwaga:** Kimi Code to pełny agent AI, nie surowy endpoint LLM. W trybie `--yolo` automatycznie zatwierdza akcje (czytanie plików, komendy terminala). Używaj świadomie.

### Claude Code Provider

Provider `claude-code` działa na dwa sposoby (próbuje w tej kolejności):

1. **Subprocess** — jeśli masz zainstalowany `claude` CLI (`npm install -g @anthropic-ai/claude-code`):
   ```bash
   claude -p "Twój prompt"
   ```

2. **HTTP fallback** — jeśli CLI nie jest zainstalowane, ale używasz Claude Code IDE:
   - Odczytuje OAuth token z `~/.claude/.credentials.json`
   - Woła API Anthropic bezpośrednio przez `anthropic` SDK
   - Nie wymaga `ANTHROPIC_API_KEY`

Dzięki temu w środowisku Claude Code IDE nie musisz podawać żadnego klucza API — provider automatycznie używa credentials zalogowanej sesji.

---

## Testy i CI

```bash
# Wszystkie testy (162 testów)
pytest tests/ -v

# Z coverage (target: 80%+)
pytest tests/ --cov=council --cov-report=html

# Type checking
mypy --strict src/council

# Linting
ruff check src/council

# Formatowanie
black src/council
```

### GitHub Actions

Pipeline uruchamia się na każdym PR:
1. `mypy --strict` — zero błędów typów
2. `ruff check` — zero błędów lintera
3. `black --check` — formatowanie
4. `pytest --cov=council --cov-fail-under=80` — testy z coverage

---

## Changelog

### v3.2.0 (2026-04-22) — Demo Mode, Interactive Menu & Dashboard

**Nowości:**
- **Tryb Demo** — 4 pre-built scenariusze (SaaS, e-commerce, fintech, healthcare) z deterministycznymi odpowiedziami. Zero kluczy API, zero configu.
- **Interaktywne menu TUI** — uruchom `python -m council` i wybieraj scenariusz / provider / opcje z rich-text menu
- **Live Dashboard** — real-time terminal dashboard z 4 panelami agentów, logami, timeline, statystykami, ASCII bar chart i exportem JSON/HTML
- **DemoProvider** — mock LLM provider z scripted responses per agent / round
- **9 nowych funkcji dashboardu**: emoji avatars, colored logs, markdown preview, animated states, mini-timeline, per-agent stats, bar chart, alert flash + bell, JSON/HTML export

**Naprawy:**
- Naprawiono wszystkie broken testy (21 fail + 8 error → 162/162 ✅)
- Usunięto duplikat `AgentState` enuma (jeden source of truth w `config.schema`)
- Usunięto blokujący `asyncio.sleep(15)` w orchestratorze (przywrócono równoległość przez `asyncio.gather`)
- Zsynchronizowano nazewnictwo plików rund (`marcus_round_1.md`) między kodem a testami

### v3.1.0 (2026-04-22) — Kimi Code Provider

**Nowości:**
- **Kimi Code CLI jako provider LLM** — nowy `KimiCodeProvider` uruchamiający `kimi --quiet --yolo` jako subprocess
- Auto-detekcja binarki Kimi CLI w środowisku VS Code / Kimi Code IDE
- Pełna obsługa `system` promptu (przekazywanego jako część promptu użytkownika)
- Czyszczenie outputu (usuwanie linii "To resume this session: ...")
- Retry z exponential backoff dla wywołań subprocess

**Infrastruktura:**
- 7 nowych testów jednostkowych dla `KimiCodeProvider`
- Naprawione pre-existing test failures w `conftest.py` i `test_agents.py`
- Zaktualizowany `KimiAdapter` do przekazywania `KIMI_CLI_PATH` w spawned sessions

### v3.0.0 (2026-04-21) — Universal Council

**Krytyczne naprawy (z audytu v2):**
- **Naprawiono duplikację funkcji** — `orchestrator.py` miał `main()` zdefiniowaną 3 razy i `quick_update()` 2 razy. W v3 jest jedna klasa `AsyncOrchestrator`.
- **Naprawiono hardcoded output** — agenci w v2 zapisywali szablony zamiast wywoływać LLM. W v3 każdy agent wywołuje `provider.generate()` i dostaje prawdziwą odpowiedź AI.
- **Dodano integrację z LLM** — v2 nie wywoływał ŻADNEGO modelu językowego. W v3: OpenAI GPT-4o, Anthropic Claude, Ollama (lokalny).
- **Dodano równoległość** — v2 był sekwencyjny (`for` loop). W v3: `asyncio.gather()` + `FilesystemBarrier` — 4 agenci w Round 1 w ~15s zamiast 60s.
- **Dodano error handling** — retry z exponential backoff (max 3 retry), state machine, timeout per runda.
- **Usunięto Scalac-specific hardcoding** — v2 miał "Scalac" wpisane w kod każdego agenta. W v3: `{{company.name}}` w Jinja2 templates + JSON config.

**Nowa architektura:**
- 4 warstwy: Data -> Agent -> Orchestration -> Platform
- `BaseAgent(ABC)` — DRY dla wszystkich agentów
- `LLMProvider(ABC)` — multi-provider bez zmiany kodu agentów
- `AgentStateMachine` — PENDING -> WRITING -> WAITING -> DONE -> ERROR
- `FilesystemBarrier` — synchronizacja rund przez filesystem
- `PromptGenerator` — Jinja2 templates z `{{company.name}}`, `{{company.product}}`
- `ConfigLoader` — JSON/YAML -> CompanyConfig (Pydantic v2 walidacja)

**Infrastruktura:**
- 101 funkcji, 100% type hints, mypy --strict compatible
- 80+ testów (pytest + pytest-asyncio)
- GitHub Actions CI (lint + test + coverage)
- pre-commit hooks (black, ruff, mypy)
- CLI: `python -m council --config firm.json`
- 4 gotowe template'y firm: SaaS, fintech, e-commerce, consulting

### v2.0.0 — Multi-Agent v2

- 4 agenci z SYSTEM_PROMPT w kodzie
- Orchestrator generujący prompty do copy-paste
- Filesystem-based komunikacja (`shared/discussion/`)
- Agregacja `FINAL_PROPOSAL.md`

**Wady v2:**
- Agenci generowali hardcoded szablony (nie wywoływali LLM)
- `orchestrator.py`: duplikacja `main()` x3, `quick_update()` x2
- Zero integracji z LLM (0/10)
- Sekwencyjne wykonanie (2/10)
- Hardcoded "Scalac" w każdym agencie (2/10)

### v1.0.0 — Prototyp

- Pojedynczy agent z promptem
- Manualny copy-paste do chatu AI

---

## Porównanie wersji

| Cecha | v1 | v2 | v3.0 | v3.1 | v3.2 |
|-------|-----|-----|------|------|------|
| Agenci | 1 | 4 | 4 | 4 | 4 |
| Integracja LLM | ❌ | ❌ | ✅ Multi-provider | ✅ + Kimi Code CLI | ✅ + Demo Provider |
| Równoległość | ❌ | ❌ (for loop) | ✅ (asyncio) | ✅ (asyncio) | ✅ (asyncio) |
| Uniwersalność | ❌ | ❌ (hardcoded Scalac) | ✅ (JSON config) | ✅ (JSON config) | ✅ (JSON config) |
| Demo Mode | ❌ | ❌ | ❌ | ❌ | ✅ (4 scenariusze) |
| Interactive Menu | ❌ | ❌ | ❌ | ❌ | ✅ (rich TUI) |
| Live Dashboard | ❌ | ❌ | ❌ | ❌ | ✅ (real-time) |
| Type hints | ❌ | ❌ | ✅ (100%) | ✅ (100%) | ✅ (100%) |
| Testy | ❌ | ❌ | ✅ (80+) | ✅ (80+) | ✅ (162+) |
| CI/CD | ❌ | ❌ | ✅ (GitHub Actions) | ✅ (GitHub Actions) | ✅ (GitHub Actions) |
| State machine | ❌ | ❌ | ✅ | ✅ | ✅ |
| Retry logic | ❌ | ❌ | ✅ | ✅ | ✅ |
| Cost tracking | ❌ | ❌ | ✅ | ✅ | ✅ |

---

## Struktura katalogów

```
scalac_ai_council/
├── README.md                      # Ten plik
├── PLATFORM_ADAPTERS.md           # Przewodnik po platformach IDE
├── pyproject.toml                 # Zależności i konfiguracja narzędzi
├── .pre-commit-config.yaml        # pre-commit hooks
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions
├── src/council/                   # Kod źródłowy v3
│   ├── __init__.py
│   ├── __main__.py                # python -m council
│   ├── cli.py                     # argparse entrypoint
│   ├── demo.py                    # Demo mode + 4 scenarios
│   ├── interactive.py             # Interactive TUI menu
│   ├── config/                    # Layer 1: Data
│   │   ├── schema.py              # CompanyConfig (Pydantic)
│   │   └── loader.py              # ConfigLoader
│   ├── agents/                    # Layer 2: Agents
│   │   ├── base.py                # BaseAgent(ABC)
│   │   ├── marcus.py              # MarcusAgent
│   │   ├── elena.py               # ElenaAgent
│   │   ├── kai.py                 # KaiAgent
│   │   ├── david.py               # DavidAgent
│   │   └── templates/             # Jinja2 templates
│   │       ├── marcus.j2
│   │       ├── elena.j2
│   │       ├── kai.j2
│   │       └── david.j2
│   ├── llm/                       # Layer 2: LLM
│   │   ├── provider.py            # LLMProvider(ABC)
│   │   ├── openai_provider.py     # OpenAI GPT-4o
│   │   ├── anthropic_provider.py  # Anthropic Claude
│   │   ├── ollama_provider.py     # Ollama (lokalny)
│   │   ├── kimi_code_provider.py  # Kimi Code CLI
│   │   ├── retry.py               # Exponential backoff
│   │   └── cost_tracker.py        # Cost per agent/round/run
│   ├── orchestration/             # Layer 3: Orchestration
│   │   ├── state_machine.py       # AgentState enum + transitions
│   │   ├── barrier.py             # FilesystemBarrier
│   │   └── orchestrator.py        # AsyncOrchestrator
│   ├── prompts/                   # PromptGenerator
│   │   └── generator.py
│   ├── vis/                       # Visualization
│   │   └── dashboard.py           # Live terminal dashboard (rich)
│   └── platform/                  # Layer 4: Platform
│       ├── base.py                # PlatformAdapter(ABC)
│       ├── cli_adapter.py         # Default: local asyncio
│       └── kimi_adapter.py        # Kimi Code: sessions_spawn
├── tests/                         # Testy (162+, pytest)
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_agents.py
│   ├── test_dashboard.py          # 26 tests
│   ├── test_demo.py               # 19 tests
│   ├── test_llm.py
│   ├── test_orchestration.py
│   └── test_prompts.py
├── templates/
│   └── companies/                 # Gotowe configi firm
│       ├── saas.json
│       ├── fintech.json
│       ├── ecommerce.json
│       └── consulting.json
├── scalac_council_v2/             # v2 (legacy, dla referencji)
│   ├── orchestrator.py
│   ├── agents/
│   ├── prompts/
│   ├── shared/
│   └── output/
└── .github/agents/                # v1/v2 IDE agents (legacy)
```

---

## Wymagania

- Python 3.12+
- `pydantic>=2.0`
- `jinja2>=3.1`
- `aiohttp>=3.9` (dla Ollama providera)

Opcjonalne (wybierz jedno lub więcej):
- `openai>=1.0` — dla GPT-4o
- `anthropic>=0.20` — dla Claude
- `ollama` lokalnie — dla darmowych modeli
- `kimi` CLI — dla Kimi Code providera (auto-detect w IDE)
- `rich>=13` — dla dashboardu i interaktywnego menu (zalecane)

---

## License

MIT License. Zobacz [LICENSE](LICENSE) (jeśli istnieje) lub użyj swobodnie.

---

## Autor

Stworzone przez borek707. Refactored do v3 przez AI Council Refactor Team.

Jeśli ten projekt Ci się przyda, daj ⭐ na GitHub!

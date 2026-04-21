# Universal AI Marketing Council v3.0

> **4 agenci AI pracujacy rownolegle, debatuja i tworza kompletny plan marketingowy dla dowolnej firmy.**
> 
> Nie szablony. Nie hardcoded Scalac. Prawdziwa integracja z LLM, rownoleglosc przez asyncio i konfiguracja przez JSON.

---

## Czym jest ta Rada

System multi-agentowy skladajacy sie z 4 specialistow AI (Marcus, Elena, Kai, David), ktory z dowolnej konfiguracji firmowej (JSON) produkuje kompletny plan marketingowy poprzez strukturyzowana debate.

**Zamiast jednej osoby robiacej plan w tydzien — masz 4 specialistow debatujacych w 30 minut.**

### Problem, ktory rozwiazuje

Tradycyjnie plan marketingowy tworzy jedna osoba:
1. Wymysla pozycjonowanie i pricing.
2. Projektue funnel od acquisition do close.
3. Pisze wszystkie materialy.
4. Wybiera konta i buduje strategie outreachowe.

Jeden mozg, ograniczone perspektywy, dni lub tygodnie pracy.

### Rozwiazanie

**4 specjalisci pracuja jednoczesnie** — kazdy odpowiada za inny obszar. I najwazniejsze: **dyskutuja ze soba** i sie nawzajem kwestionuja.

Po 2-3 rundach debaty masz plan, ktory przeszedl krytyke wszystkich czterech perspektyw.

---

## Czterej agenci

| Agent | Rola | Frameworki | Output |
|-------|------|-----------|--------|
| **Marcus** | Offer Architect | Gap Selling, StoryBrand, Good-Better-Best, Challenger Sale | Oferta: pricing, positioning, pitch |
| **Elena** | Funnel Architect | MEDDIC, JOLT, Three Pipelines, Predictable Revenue | Lejek: konwersje, kwalifikacja, forecast |
| **Kai** | Copywriter | AIDA, Big 5, PAS, StoryBrand | Copy: landing page, emaile, LinkedIn |
| **David** | Lead Strategist | ABM Tiers, Dream 100, Signal-Based Selling | ABM: konta, sekwencje, personalizacja |

### Przyklad debaty

> **Marcus**: "Wyceniam Team Extension na EUR 25K/miesiac per senior."
>
> **Elena**: "Czekaj — przy tej cenie conversion spada do 0.3%. Pipeline nie przetrwa."
>
> **Marcus**: "Dobry punkt. Starter do EUR 19K, Scale i Enterprise zostawiam."
>
> **Kai**: "CTO nie chce widziec ceny na stronie. TCO Calculator za email-gate."
>
> **David**: "W kontach, ktore znalazlem, maja aktywne oferty pracy dla Scala devow. Otwieramy z tym."

---

## Szybki start (5 minut)

### 1. Instalacja

```bash
git clone https://github.com/borek707/scalac_ai_council.git
cd scalac_ai_council
pip install -e ".[dev]"
```

### 2. Klucz API

```bash
export OPENAI_API_KEY="sk-..."
# lub
export ANTHROPIC_API_KEY="sk-ant-..."
# lub uzyj lokalnego Ollama (darmowe)
```

### 3. Konfiguracja firmy

```bash
# Skopiuj gotowy template
cp templates/companies/fintech.json my_company.json

# Lub stworz wlasny — patrz sekcja "Konfiguracja firmy" ponizej
```

### 4. Uruchom

```bash
# OpenAI (domyslnie)
python -m council --config my_company.json --rounds 3

# Anthropic Claude
python -m council --config my_company.json --provider anthropic

# Lokalny Ollama (darmowe, bez internetu)
python -m council --config my_company.json --provider ollama --model llama3

# Wyswietl status
python -m council --config my_company.json --monitor

# Agreguj finalny proposal
python -m council --config my_company.json --aggregate
```

### 5. Wynik

Po zakonczeniu w katalogu `output/`:

| Plik | Zawartosc |
|------|-----------|
| `marcus_offer.md` | Oferta: Gap Analysis, BrandScript, Pricing, Challenger Pitch |
| `elena_funnel.md` | Lejek: Stages, MEDDIC, JOLT, Three Pipelines, Forecast |
| `kai_copy.md` | Landing Page + Email Sequence + LinkedIn Ads |
| `david_abm.md` | ABM: Dream 100, Sequences, Tools |
| `FINAL_PROPOSAL.md` | Wszystko razem w jednym dokumencie |

---

## Konfiguracja firmy

System przyjmuje dowolna konfiguracje przez JSON. Schemat jest walidowany przez Pydantic v2.

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

Aby uzyc: `python -m council --config templates/companies/fintech.json`

### Pelny schemat (CompanyConfig)

```python
class CompanyConfig(BaseModel):
    name: str                    # Nazwa firmy (1-100 znakow)
    product: str                 # Co sprzedaje
    pricing_tier: str            # Przedzial cenowy
    value_proposition: str       # Głowna wartosc
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

System sklada sie z 4 warstw:

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

### Rownoleglosc — jak to dziala

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

**Calkowity czas: 3 rundy x 15s = 45s zamiast 3 rundy x 60s = 180s.**

### State Machine

Kazdy agent ma okreslony stan:

```
PENDING --> WRITING --> WAITING (barrier) --> DONE --> PENDING (nastepna runda)
   |           |            |                  |
   +-----------+------------+------------------+--> ERROR
```

---

## CLI — Wszystkie komendy

```bash
# Podstawowe uzycie
python -m council --config firm.json

# Wybor providera LLM
python -m council --config firm.json --provider openai       # GPT-4o (domyslny)
python -m council --config firm.json --provider anthropic    # Claude Sonnet
python -m council --config firm.json --provider ollama       # Llama3 (lokalny)

# Nadpisanie modelu
python -m council --config firm.json --provider openai --model gpt-4o-mini

# Wiecej rund debaty
python -m council --config firm.json --rounds 5

# Timeout per runda (sekundy)
python -m council --config firm.json --timeout 600

# Tylko status dyskusji
python -m council --config firm.json --monitor

# Agreguj finalny proposal
python -m council --config firm.json --aggregate

# Wyjsciowy katalog
python -m council --config firm.json --output ./results

# Tryb verbose (debug)
python -m council --config firm.json --verbose
```

---

## Testy i CI

```bash
# Wszystkie testy
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

Pipeline uruchamia sie na kazdym PR:
1. `mypy --strict` — zero bledow typow
2. `ruff check` — zero bledow lintera
3. `black --check` — formatowanie
4. `pytest --cov=council --cov-fail-under=80` — testy z coverage

---

## Changelog

### v3.0.0 (2026-04-21) — Universal Council

**Krytyczne naprawy (z audytu v2):**
- **Naprawiono duplikacje funkcji** — `orchestrator.py` mial `main()` zdefiniowana 3 razy i `quick_update()` 2 razy. W v3 jest jedna klasa `AsyncOrchestrator`.
- **Naprawiono hardcoded output** — agenci w v2 zapisywali szablony zamiast wywolywac LLM. W v3 kazdy agent wywoluje `provider.generate()` i dostaje prawdziwa odpowiedz AI.
- **Dodano integracje z LLM** — v2 nie wywolywal ZADNEGO modelu jezykowego. W v3: OpenAI GPT-4o, Anthropic Claude, Ollama (lokalny).
- **Dodano rownoleglosc** — v2 byl sekwencyjny (`for` loop). W v3: `asyncio.gather()` + `FilesystemBarrier` — 4 agenci w Round 1 w ~15s zamiast 60s.
- **Dodano error handling** — retry z exponential backoff (max 3 retry), state machine, timeout per runda.
- **Usunieto Scalac-specific hardcoding** — v2 mial "Scalac" wpisane w kod kazdego agenta. W v3: `{{company.name}}` w Jinja2 templates + JSON config.

**Nowa architektura:**
- 4 warstwy: Data -> Agent -> Orchestration -> Platform
- `BaseAgent(ABC)` — DRY dla wszystkich agentow
- `LLMProvider(ABC)` — multi-provider bez zmiany kodu agentow
- `AgentStateMachine` — PENDING -> WRITING -> WAITING -> DONE -> ERROR
- `FilesystemBarrier` — synchronizacja rund przez filesystem
- `PromptGenerator` — Jinja2 templates z `{{company.name}}`, `{{company.product}}`
- `ConfigLoader` — JSON/YAML -> CompanyConfig (Pydantic v2 walidacja)

**Infrastruktura:**
- 101 funkcji, 100% type hints, mypy --strict compatible
- 80+ testow (pytest + pytest-asyncio)
- GitHub Actions CI (lint + test + coverage)
- pre-commit hooks (black, ruff, mypy)
- CLI: `python -m council --config firm.json`
- 4 gotowe template'y firm: SaaS, fintech, e-commerce, consulting

### v2.0.0 — Multi-Agent v2

- 4 agenci z SYSTEM_PROMPT w kodzie
- Orchestrator generujacy prompty do copy-paste
- Filesystem-based komunikacja (`shared/discussion/`)
- Agregacja `FINAL_PROPOSAL.md`

**Wady v2:**
- Agenci generowali hardcoded szablony (nie wywolywali LLM)
- `orchestrator.py`: duplikacja `main()` x3, `quick_update()` x2
- Zero integracji z LLM (0/10)
- Sekwencyjne wykonanie (2/10)
- Hardcoded "Scalac" w kazdym agencie (2/10)

### v1.0.0 — Prototyp

- Pojedynczy agent z promptem
- Manualny copy-paste do chatu AI

---

## Porownanie wersji

| Cecha | v1 | v2 | v3 |
|-------|-----|-----|-----|
| Agenci | 1 | 4 | 4 |
| Integracja LLM | ❌ | ❌ | ✅ Multi-provider |
| Rownoleglosc | ❌ | ❌ (for loop) | ✅ (asyncio) |
| Uniwersalnosc | ❌ | ❌ (hardcoded Scalac) | ✅ (JSON config) |
| Type hints | ❌ | ❌ | ✅ (100%) |
| Testy | ❌ | ❌ | ✅ (80+) |
| CI/CD | ❌ | ❌ | ✅ (GitHub Actions) |
| State machine | ❌ | ❌ | ✅ |
| Retry logic | ❌ | ❌ | ✅ |
| Cost tracking | ❌ | ❌ | ✅ |

---

## Struktura katalogow

```
scalac_ai_council/
├── README.md                      # Ten plik
├── pyproject.toml                 # Zaleznosci i konfiguracja narzedzi
├── setup.cfg                      # mypy strict
├── .pre-commit-config.yaml        # pre-commit hooks
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions
├── src/council/                   # Kod zrodlowy v3
│   ├── __init__.py
│   ├── __main__.py                # python -m council
│   ├── cli.py                     # argparse entrypoint
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
│   │   ├── retry.py               # Exponential backoff
│   │   └── cost_tracker.py        # Cost per agent/round/run
│   ├── orchestration/             # Layer 3: Orchestration
│   │   ├── state_machine.py       # AgentState enum + transitions
│   │   ├── barrier.py             # FilesystemBarrier
│   │   └── orchestrator.py        # AsyncOrchestrator
│   ├── prompts/                   # PromptGenerator
│   │   └── generator.py
│   └── platform/                  # Layer 4: Platform
│       ├── base.py                # PlatformAdapter(ABC)
│       ├── cli_adapter.py         # Default: local asyncio
│       └── kimi_adapter.py        # Kimi Code: sessions_spawn
├── tests/                         # Testy (80+, pytest)
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_agents.py
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

Opcjonalne (wybierz jedno):
- `openai>=1.0` — dla GPT-4o
- `anthropic>=0.20` — dla Claude
- `ollama` lokalnie — dla darmowych modeli

---

## License

MIT License. Zobacz [LICENSE](LICENSE) (jesli istnieje) lub uzyj swobodnie.

---

## Autor

Stworzone przez borek707. Refactored do v3 przez AI Council Refactor Team.

Jesli ten projekt Ci sie przyda, daj ⭐ na GitHub!

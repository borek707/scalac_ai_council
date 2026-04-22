# Platform Adapters Guide

> **Jak uruchomić Radę AI na dowolnej platformie IDE / AI.**

---

## Szybka ściągawka

| Platforma | Flaga | Auto-detekcja | Równoległość |
|-----------|-------|--------------|--------------|
| **Kimi Code** | `--platform kimi` | `KIMI_SESSION_ID` | ✅ sessions_spawn |
| **Google IDX** | `--platform idx` | `GOOGLE_CLOUD_WORKSTATIONS` | ✅ asyncio |
| **Cursor** | `--platform cursor` | `CURSOR_TRACE_ID` | ✅ asyncio |
| **GitHub Copilot / Codespaces** | `--platform copilot` | `CODESPACES` | ✅ asyncio |
| **Bolt.new / Lovable / Replit** | `--platform web` | `BOLT_ENV`, `LOVABLE_ENV`, `REPL_ID` | ⚠️ sequential* |
| **Terminal lokalny** | `--platform cli` | domyślny | ✅ asyncio |

\* Web platforms testują możliwość równoległości i wybierają najlepszy tryb.

---

## Auto-detekcja

System **automatycznie wykrywa** platformę po zmiennych środowiskowych:

```bash
# W terminalu Kimi Code
python -m council --config firm.json
# -> auto-wykryje --platform kimi

# W Google IDX
python -m council --config firm.json
# -> auto-wykryje --platform idx

# W Cursor
python -m council --config firm.json
# -> auto-wykryje --platform cursor
```

Możesz też wymusić platformę:

```bash
python -m council --config firm.json --platform idx
```

---

## Kimi Code

### Środowisko

Kimi Code to IDE z wbudowanym AI i API `sessions_spawn` do uruchamiania równoległych sesji.

### Jak używać

```bash
# W terminalu Kimi Code
pip install -e ".[dev]"
python -m council --config firm.json --platform kimi
```

### Co się dzieje pod spodem

1. `KimiAdapter` wykrywa `KIMI_SESSION_ID` lub `KIMI_API_KEY`
2. Sprawdza dostępność `sessions_spawn` API
3. Jeśli dostępne — każdy agent dostaje **własną sesję** z izolowanym filesystem
4. Jeśli nie — fallback do `asyncio.gather()` w jednej sesji

### Równoległość

| Tryb | Agenci | Mechanizm |
|------|--------|-----------|
| sessions_spawn | 4 osobne sesje | Proces-level |
| asyncio fallback | 1 sesja, 4 taski | Async-level |

---

## Google IDX (Project IDX)

### Środowisko

Google IDX to cloud IDE oparte na Nix z pełnym terminalem Linux.

### Jak używać

```bash
# W terminalu IDX
pip install -e ".[dev]"
python -m council --config firm.json --platform idx
```

### Co się dzieje pod spodem

1. `GoogleIDXAdapter` wykrywa `GOOGLE_CLOUD_WORKSTATIONS`
2. Używa standardowego `AsyncOrchestrator` z `asyncio.gather()`
3. IDX ma hojne limity zasobów — pełna równoległość działa natywnie

### Preview

Możesz otworzyć wyniki w panelu preview IDX:

```bash
idx preview --port 8080
```

---

## Cursor

### Środowisko

Cursor to fork VS Code z wbudowanym AI (Claude, GPT-4o).

### Jak używać

```bash
# W terminalu Cursor (Ctrl+`)
pip install -e ".[dev]"
python -m council --config firm.json --platform cursor
```

### Wskazówki

- Otwórz folder `output/` w eksploratorze Cursor — pliki generują się w czasie rzeczywistym
- Użyj panelu AI Cursor do debugowania outputów agentów
- Skrót `Ctrl+Shift+P` → "Terminal: Create New Terminal"

---

## GitHub Copilot / Codespaces

### Środowisko

- **Codespaces** — konteneryzowane IDE w chmurze
- **Copilot** — AI w VS Code / JetBrains / Neovim

### Jak używać

```bash
# W Codespaces terminal
pip install -e ".[dev]"
python -m council --config firm.json --platform copilot
```

### Co się dzieje pod spodem

1. `GitHubCopilotAdapter` wykrywa `CODESPACES=true` lub `GITHUB_COPILOT`
2. W Codespaces — używa trwałego storage (pliki przetrwają restart)
3. W Copilot (lokalnie) — standardowe asyncio

---

## Bolt.new / Lovable.dev / Replit

### Środowisko

Web platformy z kontenerami w przeglądarce.

### Jak używać

```bash
# W terminalu web platformy
pip install -e ".[dev]"
python -m council --config firm.json --platform web
```

### Ograniczenia

Web platformy mogą mieć ograniczenia:
- Mniej zasobów CPU/RAM
- Ograniczony filesystem (często tylko `/tmp` lub `/home/user`)
- Brak możliwości prawdziwej równoległości procesów

### Fallback

`WebPlatformAdapter` testuje możliwość równoległości (`asyncio.gather` z 3 taskami). Jeśli test się nie powiedzie — uruchamia agentów **sekwencyjnie** (jeden po drugim).

---

## Terminal lokalny (CLI)

### Środowisko

Zwykły terminal na Twoim komputerze.

### Jak używać

```bash
pip install -e ".[dev]"
python -m council --config firm.json
```

To jest domyślny adapter — działa wszędzie tam, gdzie jest Python 3.12+.

---

## Dodawanie własnego adaptera

```python
from council.platform.base import PlatformAdapter
from council.orchestration.orchestrator import AsyncOrchestrator

class MyIDEAdapter(PlatformAdapter):
    def get_name(self) -> str:
        return "My IDE"

    async def spawn_agents(self, orchestrator: AsyncOrchestrator) -> None:
        # Twoja logika uruchomienia
        await orchestrator.run()
```

Zarejestruj w `cli.py`:

```python
PLATFORM_REGISTRY["myide"] = ("My IDE", ["MYIDE_ENV"])
```

---

## Porównanie wydajności

| Platforma | Runda 1 (4 agenci) | Runda 2 | Runda 3 | Suma |
|-----------|-------------------|---------|---------|------|
| Kimi (sessions_spawn) | ~10s | ~10s | ~10s | **~30s** |
| Kimi (asyncio) | ~15s | ~15s | ~15s | **~45s** |
| Google IDX | ~15s | ~15s | ~15s | **~45s** |
| Cursor | ~15s | ~15s | ~15s | **~45s** |
| Codespaces | ~15s | ~15s | ~15s | **~45s** |
| Web (parallel) | ~20s | ~20s | ~20s | **~60s** |
| Web (sequential) | ~60s | ~60s | ~60s | **~180s** |

Wszystkie czasy przy założeniu LLM latency ~3s per agent.

---

## Troubleshooting

### "Platform not detected"

```bash
# Wymuś platformę ręcznie
python -m council --config firm.json --platform cli
```

### "sessions_spawn not available" (Kimi)

```bash
# Kimi Adapter fallbacknie do asyncio — to normalne
# Pełna równoległość wymaga wewnętrznego API Kimi
```

### Brak uprawnień do zapisu (Web)

```bash
# WebPlatformAdapter auto-wykrywa writable path
# Jeśli nie działa — ustaw output na /tmp:
python -m council --config firm.json --platform web --output /tmp/council
```

---

## Reference

| Adapter | Plik | Detekcja |
|---------|------|----------|
| `CLIAdapter` | `platform/cli_adapter.py` | domyślny |
| `KimiAdapter` | `platform/kimi_adapter.py` | `KIMI_SESSION_ID` |
| `GoogleIDXAdapter` | `platform/idx_adapter.py` | `GOOGLE_CLOUD_WORKSTATIONS` |
| `CursorAdapter` | `platform/cursor_adapter.py` | `CURSOR_TRACE_ID` |
| `GitHubCopilotAdapter` | `platform/copilot_adapter.py` | `CODESPACES` |
| `WebPlatformAdapter` | `platform/web_adapter.py` | `BOLT_ENV`, `LOVABLE_ENV`, `REPL_ID` |

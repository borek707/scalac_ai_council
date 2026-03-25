#!/usr/bin/env python3
"""
Rada AI - Universal Multi-Agent Orchestrator

Działa w każdym IDE:
  - Kimi Code     → sessions_spawn() [auto-spawn, jeśli dostępne]
  - Claude Code   → generuje prompts/, otwórz 4 okna terminala
  - Cursor        → generuje prompts/, wklej do 4 zakładek Composer
  - Windsurf      → generuje prompts/, wklej do 4 okien Cascade
  - Dowolny AI    → gotowe pliki .md — copy-paste do nowego chatu

Usage:
    python orchestrator.py           # generuje prompty + status
    python orchestrator.py --monitor # tylko status dyskusji
    python orchestrator.py --final   # agregacja outputów
"""

import os
import sys
import time
import builtins
from pathlib import Path
from datetime import datetime

# Ścieżki relatywne — działa w każdym IDE, na każdej maszynie
WORKSPACE = Path(__file__).parent
SHARED = WORKSPACE / "shared"
DISCUSSION = SHARED / "discussion"
OUTPUT = WORKSPACE / "output"
PROMPTS = WORKSPACE / "prompts"

AGENTS = WORKSPACE / "agents"


# ─────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────

def setup_workspace():
    for d in [SHARED, DISCUSSION, OUTPUT, PROMPTS]:
        d.mkdir(parents=True, exist_ok=True)
    print(f"   ✅ Workspace: {WORKSPACE.resolve()}")
    print(f"   ✅ Prompts:   {PROMPTS.resolve()}")


def check_brief():
    brief_path = SHARED / "brief.md"
    if brief_path.exists():
        content = brief_path.read_text()
        print(f"\n📋 Brief załadowany ({len(content)} znaków)")
        for line in content.split('\n')[:8]:
            if line.strip():
                print(f"   {line[:80]}")
        return True
    print("\n❌ Brak shared/brief.md!")
    print("   Utwórz plik z opisem projektu i uruchom ponownie.")
    return False


# ─────────────────────────────────────────
# DISCUSSION STATUS
# ─────────────────────────────────────────

def get_discussion_status():
    if not DISCUSSION.exists():
        return {"round": 0, "agents": [], "files": [], "total_posts": 0}
    files = list(DISCUSSION.glob("*.md"))
    rounds, agents = set(), set()
    for f in files:
        parts = f.stem.split('_')
        if len(parts) >= 3:
            try:
                rounds.add(int(parts[1]))
            except ValueError:
                pass
            agents.add(parts[2])
    return {
        "round": max(rounds) if rounds else 0,
        "agents": sorted(agents),
        "files": [f.name for f in files],
        "total_posts": len(files),
    }


def get_discussion_content():
    """Zwróć tekst całej dyskusji do wbudowania w prompty."""
    posts = []
    if DISCUSSION.exists():
        for f in sorted(DISCUSSION.glob("*.md")):
            posts.append(f"\n\n### {f.name}\n{f.read_text()}")
    return "\n".join(posts) if posts else "_Brak wcześniejszych postów — jesteś w Rundzie 1._"


def monitor_discussion():
    print("\n" + "=" * 60)
    print("📊 STATUS RADY AI")
    print("=" * 60)
    status = get_discussion_status()
    print(f"\n   Runda:  {status['round']}/3")
    print(f"   Agenci: {', '.join(status['agents']) if status['agents'] else 'brak'}")
    print(f"   Posty:  {status['total_posts']}")
    if status['files']:
        print("\n📝 Pliki dyskusji:")
        for f in sorted(status['files']):
            print(f"   - {f}")
    return status


def check_consensus():
    status = get_discussion_status()
    if status['round'] >= 3:
        expected = {'marcus', 'elena', 'kai', 'david'}
        if expected.issubset(set(status['agents'])):
            return True, "3 rundy ukończone przez wszystkich agentów"
    for f in DISCUSSION.glob("*.md"):
        content = f.read_text().lower()
        if any(kw in content for kw in ['konsensus', 'agreed', 'consensus', 'final decision']):
            return True, f"Konsensus wykryty w {f.name}"
    return False, None


# ─────────────────────────────────────────
# PROMPT GENERATOR
# ─────────────────────────────────────────

def load_context():
    """Wczytaj wszystkie pliki kontekstowe."""
    def read(path):
        return path.read_text() if path.exists() else "_Brak pliku_"

    return {
        "brief": read(SHARED / "brief.md"),
        "battlecards": read(SHARED / "battlecards.md"),
        "content_plan": read(SHARED / "content_plan.md"),
        "target_accounts": read(SHARED / "target_accounts.md"),
        "discussion": get_discussion_content(),
    }


def extract_system_prompt(agent_file: Path) -> str:
    """Wyciągnij SYSTEM_PROMPT z pliku agenta."""
    if not agent_file.exists():
        return ""
    source = agent_file.read_text()
    start = source.find('SYSTEM_PROMPT = """')
    if start == -1:
        return ""
    start += len('SYSTEM_PROMPT = """')
    end = source.find('"""', start)
    return source[start:end].strip() if end != -1 else ""


def determine_next_round(agent_name: str) -> int:
    """Oblicz numer następnej rundy dla agenta."""
    status = get_discussion_status()
    existing_rounds = set()
    for f in DISCUSSION.glob(f"round_*_{agent_name}.md"):
        parts = f.stem.split('_')
        if len(parts) >= 3:
            try:
                existing_rounds.add(int(parts[1]))
            except ValueError:
                pass
    return max(existing_rounds) + 1 if existing_rounds else 1


def build_prompt(agent_name: str, role: str, output_file: str, ctx: dict) -> str:
    """Zbuduj kompletny, samodzielny prompt dla agenta."""
    system_prompt = extract_system_prompt(AGENTS / f"{agent_name}_agent.py")
    next_round = determine_next_round(agent_name)
    round_file = DISCUSSION / f"round_{next_round}_{agent_name}.md"
    final_file = OUTPUT / output_file
    workspace_abs = WORKSPACE.resolve()

    task_instructions = f"""
## TWOJE ZADANIE

Jesteś **{agent_name.capitalize()} ({role})** w Radzie AI Scalac.

**Runda:** {next_round}/3  
**Workspace:** `{workspace_abs}`

### Kroki:

1. Przeczytaj uważnie sekcje BRIEF, BATTLECARDS i CONTENT PLAN poniżej.
2. Przeczytaj aktualną dyskusję w sekcji AKTUALNA DYSKUSJA.
3. Napisz swoje stanowisko w Rundzie {next_round}.
4. **Zapisz je do pliku:**  
   `{round_file}`

5. Po zakończeniu wszystkich 3 rund (lub osiągnięciu konsensusu), napisz finalny output i zapisz go do:  
   `{final_file}`

### Format Rundy:
```markdown
# Stanowisko {agent_name.capitalize()} — Runda {next_round}

## Moja Teza
[1-2 zdania głównej idei]

## Argumenty
1. [Argument z danymi / battlecard / książką]
2. [Argument]

## Co sądzę o stanowiskach pozostałych (od Rundy 2):
### Marcus: [agree/disagree + uzasadnienie]
### Elena:  [...]
### Kai:    [...]
### David:  [...]

## Propozycja / Decyzja
[konkretna propozycja lub utrwalenie stanowiska]
```

### Zasady Rady:
- Krytykuj konstruktywnie: "To nie zadziała bo..." a nie "To głupie"
- Odnosz się konkretnie do argumentów innych agentów
- Zmieniaj zdanie jeśli argumenty są przekonujące
- Finalny output musi być spójny z inputem innych agentów
- Używaj danych z battlecards i content planu jako argumentów
"""

    # Skróć battlecards jeśli za długie — zachowaj kluczowe sekcje
    battlecards_summary = ctx["battlecards"][:4000] + "\n\n_[...pełna treść w shared/battlecards.md]_" \
        if len(ctx["battlecards"]) > 4000 else ctx["battlecards"]
    content_plan_summary = ctx["content_plan"][:3000] + "\n\n_[...pełna treść w shared/content_plan.md]_" \
        if len(ctx["content_plan"]) > 3000 else ctx["content_plan"]
    # Target accounts — David dostaje pełną listę, pozostali dostają intelligence summary
    if agent_name == "david":
        target_accounts_section = ctx["target_accounts"]
    else:
        # Wyciągnij tylko sekcję 4 (Key Intelligence) dla pozostałych agentów
        ta = ctx["target_accounts"]
        idx = ta.find("## 4. Key Intelligence")
        target_accounts_section = ta[idx:] if idx != -1 else ta[:2000]

    return f"""# PROMPT: {agent_name.upper()} — {role}

> **Wklej całą tę zawartość do NOWEGO chatu w swoim IDE.**  
> Działa w: Claude Code, Cursor, Windsurf, Kimi Code, lub dowolnym chatbocie AI.  
> _Wygenerowano: {datetime.now().strftime('%Y-%m-%d %H:%M')}_

---

## TWOJA TOŻSAMOŚĆ I ROLA

{system_prompt}

---
{task_instructions}
---

## BRIEF PROJEKTU

{ctx["brief"]}

---

## DANE RYNKOWE — BATTLECARDS (Scalac, Marzec 2026)

{battlecards_summary}

---

## PLAN CONTENTOWY — CONTENT PLAN (Q2–Q3 2026)

{content_plan_summary}

---

## TARGET ACCOUNTS — REALNE FIRMY DO TARGETOWANIA

{target_accounts_section}

---

## AKTUALNA DYSKUSJA RADY AI

{ctx["discussion"]}

---

_Koniec promptu. Możesz zaczynać._
"""


def generate_prompts():
    """Generuj samodzielne pliki promptów dla wszystkich agentów."""
    print("\n🔧 Generowanie promptów...")
    PROMPTS.mkdir(exist_ok=True)
    ctx = load_context()

    agents_config = [
        ("marcus", "Offer Architect",    "marcus_offer.md"),
        ("elena",  "Funnel Architect",   "elena_funnel.md"),
        ("kai",    "Copywriter",         "kai_copy.md"),
        ("david",  "Lead Strategist",    "david_abm.md"),
    ]

    generated = []
    for name, role, output in agents_config:
        prompt = build_prompt(name, role, output, ctx)
        path = PROMPTS / f"{name}_prompt.md"
        path.write_text(prompt)
        size = len(prompt)
        print(f"   ✅ {path.name}  ({size:,} znaków)")
        generated.append((name, path))

    return generated


# ─────────────────────────────────────────
# AUTO-SPAWN (Kimi Code)
# ─────────────────────────────────────────

def try_kimi_spawn(generated_prompts):
    """Próbuj auto-spawn w Kimi Code. Returns True jeśli się udało."""
    spawn_fn = getattr(builtins, 'sessions_spawn', None)
    if spawn_fn is None:
        return False

    print("\n🚀 Kimi Code wykryty — auto-spawn agentów...")
    labels = {"marcus": "marcus", "elena": "elena", "kai": "kai", "david": "david"}

    for name, prompt_path in generated_prompts:
        task = prompt_path.read_text()
        spawn_fn(
            runtime="subagent",
            task=task,
            label=labels[name],
        )
        print(f"   ✅ Spawned: {name}")

    return True


# ─────────────────────────────────────────
# INSTRUKCJE DLA INNYCH IDE
# ─────────────────────────────────────────

def print_ide_instructions(generated_prompts):
    """Wypisz instrukcje dla różnych IDE."""
    prompt_files = {name: str(path.resolve()) for name, path in generated_prompts}

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           RADA AI — INSTRUKCJE SPAWNU AGENTÓW               ║
╚══════════════════════════════════════════════════════════════╝

Gotowe pliki promptów (każdy zawiera pełny kontekst + battlecards):

  📄 Marcus:  prompts/marcus_prompt.md
  📄 Elena:   prompts/elena_prompt.md
  📄 Kai:     prompts/kai_prompt.md
  📄 David:   prompts/david_prompt.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🟠 CLAUDE CODE (terminal tabs):
   Otwórz 4 osobne chaty i w każdym:
   cat prompts/marcus_prompt.md  # skopiuj i wklej

   Lub bezpośrednio przez plik:
   claude --file prompts/marcus_prompt.md
   claude --file prompts/elena_prompt.md
   claude --file prompts/kai_prompt.md
   claude --file prompts/david_prompt.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔵 CURSOR (Composer):
   1. Ctrl+Shift+I — otwórz Composer
   2. Kliknij "+ New Composer"
   3. Wklej zawartość prompts/marcus_prompt.md
   4. Powtórz dla pozostałych 3 agentów w oddzielnych oknach

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🟣 WINDSURF (Cascade):
   1. Otwórz 4 osobne okna Cascade
   2. W każdym: @file prompts/[agent]_prompt.md i Enter

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

� GOOGLE ANTIGRAVITY (Mission Control):
   Antigravity obsługuje wiele agentów równolegle z "Mission Control".
   1. Otwórz Mission Control (ikona device_hub lub Ctrl+Shift+M)
   2. Kliknij "+ New Agent" — utwórz 4 agentów naraz
   3. Dla każdego agenta użyj @file lub wklej zawartość:
      Agent 1 → prompts/marcus_prompt.md
      Agent 2 → prompts/elena_prompt.md
      Agent 3 → prompts/kai_prompt.md
      Agent 4 → prompts/david_prompt.md
   4. Uruchom wszystkich jednocześnie — Antigravity synchronizuje
      dostęp do shared/ przez Cross-surface Agents
   Tip: Użyj workspace tego repo jako wspólnego kontekstu dla
        wszystkich 4 agentów.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

�🟡 KIMI CODE (sessions_spawn):
   Uruchom ponownie — Kimi Code jest wykrywany automatycznie
   i agenci spawnują się sami.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚪ DOWOLNY CHATBOT (ChatGPT, Claude, Gemini itp.):
   1. Otwórz 4 oddzielne okna/chaty
   2. W każdym: otwórz odpowiedni plik .md i wklej całość

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Monitorowanie:
   python orchestrator.py --monitor

📦 Agregacja finalnych outputów:
   python orchestrator.py --final
""")


# ─────────────────────────────────────────
# AGGREGATION
# ─────────────────────────────────────────

def aggregate_output():
    print("\n" + "=" * 60)
    print("📦 AGREGACJA FINALNYCH OUTPUTÓW")
    print("=" * 60)

    brief_content = (SHARED / "brief.md").read_text() if (SHARED / "brief.md").exists() else ""

    final_doc = f"""# Rada AI Scalac — Final Proposal
_Wygenerowano: {datetime.now().strftime('%Y-%m-%d %H:%M')}_

---

## Brief Projektu

{brief_content[:800]}

---

"""
    outputs = [
        ("marcus_offer.md",  "🎯 OFERTA — Marcus (Offer Architect)"),
        ("elena_funnel.md",  "📈 LEJEK — Elena (Funnel Architect)"),
        ("kai_copy.md",      "✍️  COPY — Kai (Copywriter)"),
        ("david_abm.md",     "🎯 ABM — David (Lead Strategist)"),
    ]

    for filename, header in outputs:
        path = OUTPUT / filename
        if path.exists():
            print(f"   ✅ {header}")
            final_doc += f"\n\n# {header}\n\n{path.read_text()}\n\n---\n"
        else:
            print(f"   ⚠️  {header} — brak pliku")

    final_path = OUTPUT / "FINAL_PROPOSAL.md"
    final_path.write_text(final_doc)
    print(f"\n💾 Final proposal zapisany: {final_path.resolve()}")
    return final_path


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

def main():
    print("=" * 60)
    print("🚀 RADA AI — UNIVERSAL MULTI-AGENT SYSTEM")
    print("=" * 60)

    args = sys.argv[1:]

    if "--final" in args:
        aggregate_output()
        return

    print("\n🏗️  Setup workspace...")
    setup_workspace()

    if "--monitor" in args:
        monitor_discussion()
        has_consensus, reason = check_consensus()
        if has_consensus:
            print(f"\n✅ KONSENSUS: {reason}")
            aggregate_output()
        return

    # Normalny flow: generuj prompty + ewentualny auto-spawn
    if not check_brief():
        print("\n❌ Nie można kontynuować bez briefu!")
        return

    status = monitor_discussion()
    has_consensus, reason = check_consensus()
    if has_consensus:
        print(f"\n✅ KONSENSUS: {reason} — Agreguję outputy...")
        aggregate_output()
        return

    print(f"\n⏳ Dyskusja: runda {status['round']}/3 — generuję zaktualizowane prompty...")

    # Generuj pliki promptów (zawsze — z aktualną dyskusją)
    generated = generate_prompts()

    # Próbuj Kimi Code auto-spawn
    spawned = try_kimi_spawn(generated)

    if not spawned:
        # Inne IDE — wypisz instrukcje
        print_ide_instructions(generated)


if __name__ == "__main__":
    main()

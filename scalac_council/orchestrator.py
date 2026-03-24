#!/usr/bin/env python3
"""
Rada AI - True Multi-Agent Orchestrator

KOORDYNATOR główny który spawnuje agentów równolegle w Kimi Code.

Usage w Kimi Code (Ta sesja):
    python orchestrator.py
    
Co robi:
1. Tworzy workspace structure
2. Spawns 4 agentów równolegle (sessions_spawn)
3. Monitoruje dyskusję
4. Agreguje finalne outputy
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Ścieżki
WORKSPACE = Path("/root/.openclaw/workspace/scalac-council")
SHARED = WORKSPACE / "shared"
DISCUSSION = SHARED / "discussion"
OUTPUT = WORKSPACE / "output"


def setup_workspace():
    """Utwórz strukturę katalogów."""
    print("🏗️  Setup workspace...")
    
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    SHARED.mkdir(exist_ok=True)
    DISCUSSION.mkdir(exist_ok=True)
    OUTPUT.mkdir(exist_ok=True)
    
    print(f"   ✅ Workspace: {WORKSPACE}")
    print(f"   ✅ Discussion: {DISCUSSION}")
    print(f"   ✅ Output: {OUTPUT}")


def check_brief():
    """Sprawdź czy brief istnieje."""
    brief_path = SHARED / "brief.md"
    if brief_path.exists():
        content = brief_path.read_text()
        print(f"\n📋 Brief loaded ({len(content)} chars)")
        # Pokaż pierwsze linie
        lines = content.split('\n')[:10]
        for line in lines:
            if line.strip():
                print(f"   {line[:70]}")
        return True
    else:
        print("\n❌ Brak brief.md!")
        print("   Utwórz: shared/brief.md")
        return False


def get_discussion_status():
    """Sprawdź status dyskusji."""
    if not DISCUSSION.exists():
        return {"round": 0, "agents": [], "files": []}
    
    files = list(DISCUSSION.glob("*.md"))
    rounds = set()
    agents = set()
    
    for f in files:
        # Format: round_X_agent.md
        parts = f.stem.split('_')
        if len(parts) >= 3:
            rounds.add(parts[1])
            agents.add(parts[2])
    
    return {
        "round": max([int(r) for r in rounds]) if rounds else 0,
        "agents": list(agents),
        "files": [f.name for f in files],
        "total_posts": len(files)
    }


def monitor_discussion():
    """Monitoruj postęp dyskusji."""
    print("\n" + "=" * 60)
    print("📊 STATUS RADY AI")
    print("=" * 60)
    
    status = get_discussion_status()
    
    print(f"\n🗣️  Dyskusja:")
    print(f"   Runda: {status['round']}")
    print(f"   Agenci: {', '.join(status['agents']) if status['agents'] else 'Brak'}")
    print(f"   Postów: {status['total_posts']}")
    
    if status['files']:
        print(f"\n📝 Pliki:")
        for f in sorted(status['files']):
            print(f"   - {f}")
    
    return status


def check_consensus():
    """Sprawdź czy jest konsensus."""
    # Prosta heurystyka: czy wszyscy napisali round 3?
    status = get_discussion_status()
    
    if status['round'] >= 3:
        # Sprawdź czy wszyscy agenci są reprezentowani
        expected_agents = {'marcus', 'elena', 'kai', 'david'}
        actual_agents = set(status['agents'])
        
        if expected_agents.issubset(actual_agents):
            return True, "3 rundy zakończone przez wszystkich agentów"
    
    # Sprawdź czy jest explicit consensus w dyskusji
    consensus_keywords = ['konsensus', 'zgoda', 'agreed', 'consensus', 'final']
    
    for f in DISCUSSION.glob("*.md"):
        content = f.read_text().lower()
        if any(kw in content for kw in consensus_keywords):
            return True, f"Konsensus wykryty w {f.name}"
    
    return False, None


def aggregate_output():
    """Złóż finalne outputy w jeden dokument."""
    print("\n" + "=" * 60)
    print("📦 AGREGACJA OUTPUTÓW")
    print("=" * 60)
    
    final_doc = """# Rada AI - Final Proposal
## Projekt: Team Extension dla Fintechów Series B

---

"""
    
    # Dodaj brief
    brief_path = SHARED / "brief.md"
    if brief_path.exists():
        final_doc += "## Brief Projektu\n\n"
        final_doc += brief_path.read_text()[:1000]
        final_doc += "\n\n---\n\n"
    
    # Dodaj outputy agentów
    outputs = [
        ("marcus_offer.md", "🎯 OFERTA (Marcus)"),
        ("elena_funnel.md", "📈 LEJEK (Elena)"),
        ("kai_copy.md", "✍️ COPY (Kai)"),
        ("david_abm.md", "🎯 ABM (David)"),
    ]
    
    for filename, header in outputs:
        path = OUTPUT / filename
        if path.exists():
            print(f"   ✅ {header}")
            final_doc += f"\n\n# {header}\n\n"
            final_doc += path.read_text()
            final_doc += "\n\n---\n"
        else:
            print(f"   ⚠️  {header} - brak")
    
    # Zapisz final proposal
    final_path = OUTPUT / "FINAL_PROPOSAL.md"
    final_path.write_text(final_doc)
    
    print(f"\n💾 Final proposal: {final_path}")
    return final_path


def print_usage():
    """Pokaż instrukcję użycia w Kimi Code."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                 RADA AI - TRUE MULTI-AGENT                    ║
╚══════════════════════════════════════════════════════════════╝

JAK UŻYWAĆ W KIMI CODE:

1. Upewnij się że workspace istnieje:
   ls /root/.openclaw/workspace/scalac-council/

2. W TEJ sesji (Orchestrator):
   python orchestrator.py
   
   To pokaże status i da Ci komendy do spawnowania agentów.

3. Spawn agentów równolegle (w Kimi Code):

   # Marcus
   sessions_spawn(
       runtime="subagent",
       task="Jesteś Marcus, Offer Architect w Scalac. Przeczytaj /root/.openclaw/workspace/scalac-council/shared/brief.md. Napisz Round 1 do /root/.openclaw/workspace/scalac-council/shared/discussion/round_1_marcus.md. Poczekaj na innych agentów. Czytaj ich outputy i odpowiadaj w kolejnych rundach. Cel: 3 rundy lub konsensus. Final: /root/.openclaw/workspace/scalac-council/output/marcus_offer.md",
       label="marcus"
   )

   # Elena
   sessions_spawn(
       runtime="subagent",
       task="Jesteś Elena, Funnel Architect w Scalac. Przeczytaj /root/.openclaw/workspace/scalac-council/shared/brief.md i /root/.openclaw/workspace/scalac-council/shared/discussion/round_1_marcus.md. Napisz Round 1 do /root/.openclaw/workspace/scalac-council/shared/discussion/round_1_elena.md. Debata z Marcusem o pricing vs conversion. Final: /root/.openclaw/workspace/scalac-council/output/elena_funnel.md",
       label="elena"
   )

   # Kai
   sessions_spawn(
       runtime="subagent",
       task="Jesteś Kai, Copywriter w Scalac. Przeczytaj brief i dyskusję. Napisz Round 1 do round_1_kai.md. Focus: czy messaging jest zbyt techniczny? Final: output/kai_copy.md",
       label="kai"
   )

   # David
   sessions_spawn(
       runtime="subagent",
       task="Jesteś David, Lead Strategist w Scalac. Przeczytaj brief i dyskusję. Napisz Round 1 do round_1_david.md. Focus: Dream 100 accounts. Final: output/david_abm.md",
       label="david"
   )

4. Monitoruj w tej sesji:
   python orchestrator.py --monitor

5. Sprawdź dyskusję:
   read("/root/.openclaw/workspace/scalac-council/shared/discussion/round_1_marcus.md")

6. Finalne outputy:
   read("/root/.openclaw/workspace/scalac-council/output/FINAL_PROPOSAL.md")

═══════════════════════════════════════════════════════════════
    """)


def main():
    """Główna funkcja orchestratora."""
    print("=" * 60)
    print("🚀 RADA AI - TRUE MULTI-AGENT SYSTEM")
    print("=" * 60)
    
    # Setup
    setup_workspace()
    
    # Sprawdź brief
    if not check_brief():
        print("\n❌ Nie można kontynuować bez briefu!")
        return
    
    # Pokaż status
    status = monitor_discussion()
    
    # Sprawdź konsensus
    has_consensus, reason = check_consensus()
    
    if has_consensus:
        print(f"\n✅ KONSENSUS: {reason}")
        aggregate_output()
    elif status['round'] >= 3:
        print(f"\n⚠️  3 rundy zakończone - agreguję outputy")
        aggregate_output()
    else:
        print(f"\n⏳ Dyskusja w toku ({status['round']}/3 rundy)")
        print("   Agenci powinni kontynuować debatę.")
    
    # Pokaż instrukcję
    print_usage()


if __name__ == "__main__":
    main()

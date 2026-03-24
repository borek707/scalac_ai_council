#!/usr/bin/env python3
"""
Skrypt migracji z Rada AI v1 (statyczna) do v2 (pamięć).

Co robi:
1. Migruje system_prompt.md (bez zmian)
2. Konwertuje examples/ do formatu dla Vector DB
3. Tworzy początkową bazę wiedzy

Usage:
    python scripts/migrate_to_v2.py
"""

import os
import sys
import json
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from v2.memory.vector_store import ScalacMemory


def parse_example_file(filepath: str) -> dict:
    """Sparsuj plik example i wyciągnij metadata."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Wyciągnij tytuł z pierwszej linii
    lines = content.split('\n')
    title = lines[0].replace('#', '').strip() if lines else "Unknown"
    
    # Spróbuj wyciągnąć typ projektu z nazwy pliku
    filename = os.path.basename(filepath)
    
    if 'team_extension' in filename.lower() or 'core' in filename.lower():
        service = "team_extension"
        project_type = "CORE"
    elif 'sovereign' in filename.lower() or 'ai' in filename.lower():
        service = "ai_consulting"
        project_type = "AI"
    else:
        service = "unknown"
        project_type = "UNKNOWN"
    
    # Spróbuj wyciągnąć branżę z treści
    industry = "unknown"
    if 'fintech' in content.lower():
        industry = "fintech"
    elif 'bank' in content.lower():
        industry = "banking"
    elif 'health' in content.lower():
        industry = "healthtech"
    elif 'ecommerce' in content.lower() or 'shop' in content.lower():
        industry = "ecommerce"
    
    return {
        "title": title,
        "industry": industry,
        "service": service,
        "project_type": project_type,
        "content": content,
        "source_file": filename
    }


def migrate_examples():
    """Migruj wszystkie examples do Vector DB."""
    print("📁 Migracja examples/ do Vector DB...")
    
    base_path = "scalac_ai_council/AGENTS"
    if not os.path.exists(base_path):
        base_path = "AGENTS"  # Może jesteśmy w innym katalogu
    
    if not os.path.exists(base_path):
        print(f"❌ Nie znaleziono katalogu {base_path}")
        return []
    
    case_studies = []
    
    for agent_dir in os.listdir(base_path):
        examples_dir = os.path.join(base_path, agent_dir, "examples")
        
        if os.path.exists(examples_dir):
            print(f"\n   📂 {agent_dir}/examples/")
            
            for filename in os.listdir(examples_dir):
                if filename.endswith('.md'):
                    filepath = os.path.join(examples_dir, filename)
                    
                    try:
                        parsed = parse_example_file(filepath)
                        
                        # Dodaj metadata o źródle
                        parsed["metadata"] = {
                            "agent": agent_dir,
                            "migrated_from": "v1_examples",
                            "type": "example"
                        }
                        
                        case_studies.append(parsed)
                        print(f"      ✅ {filename}")
                        
                    except Exception as e:
                        print(f"      ❌ {filename}: {e}")
    
    return case_studies


def create_learning_entries():
    """Utwórz początkowe learning entries z frameworków."""
    print("\n🧠 Tworzenie learning entries...")
    
    learnings = [
        {
            "title": "Pricing Strategy - Good-Better-Best works",
            "content": """
Lesson: Good-Better-Best pricing model consistently outperforms single-tier pricing.

Evidence:
- Bexio: 70% of clients chose 'Better' tier
- Liga Digital: Decoy pricing increased 'Best' tier selection by 40%

Key insight: Always include a 'Decoy' option to make 'Best' look reasonable.

Application: Use for all new offers.
            """,
            "metadata": {
                "type": "learning",
                "category": "pricing",
                "verified": True
            }
        },
        {
            "title": "Gap Selling - Financial impact matters most",
            "content": """
Lesson: Clients respond strongest to quantified financial impact in Gap Analysis.

Evidence:
- Offers with specific ROI numbers (e.g., "save 2M EUR") had 35% higher conversion
- Vague benefits ("improve efficiency") performed poorly

Key insight: Always calculate specific financial impact for client's industry.

Application: Use calculate_roi_for_client tool.
            """,
            "metadata": {
                "type": "learning",
                "category": "sales",
                "verified": True
            }
        },
        {
            "title": "Team Extension - Speed is the selling point",
            "content": """
Lesson: For team extension, "2-week onboarding" is more compelling than price.

Evidence:
- 80% of clients cited "speed to productivity" as main decision factor
- Price was #3 factor after speed and quality

Key insight: Lead with timeline, not pricing.

Application: Emphasize 2-week guarantee in all team extension offers.
            """,
            "metadata": {
                "type": "learning",
                "category": "positioning",
                "verified": True
            }
        }
    ]
    
    return learnings


def main():
    print("🚀 Migracja Rada AI v1 → v2")
    print("=" * 50)
    
    # Inicjalizacja pamięci
    memory = ScalacMemory(persist_directory="./chroma_db")
    print("\n📚 Pamięć zainicjalizowana")
    
    # Migruj examples
    case_studies = migrate_examples()
    
    if case_studies:
        print(f"\n➕ Dodawanie {len(case_studies)} case studies...")
        memory.add_case_studies(case_studies)
    else:
        print("\n⚠️  Nie znaleziono examples do migracji")
    
    # Dodaj learning entries
    learnings = create_learning_entries()
    print(f"\n➕ Dodawanie {len(learnings)} learning entries...")
    
    for learning in learnings:
        doc = type('obj', (object,), {
            'page_content': learning["content"],
            'metadata': {**learning["metadata"], "title": learning["title"]}
        })()
        memory.db.add_documents([doc])
    
    memory.db.persist()
    
    # Podsumowanie
    stats = memory.stats()
    print("\n" + "=" * 50)
    print("✅ Migracja zakończona!")
    print("=" * 50)
    print(f"\n📊 Nowy stan bazy:")
    print(f"   Dokumentów: {stats.get('total_documents', 'N/A')}")
    print(f"   Lokalizacja: {stats.get('persist_directory', './chroma_db')}")
    
    print("\n📝 Co zostało zmigrowane:")
    print(f"   - {len(case_studies)} examples z AGENTS/*/examples/")
    print(f"   - {len(learnings)} initial learnings")
    
    print("\n⚠️  Co pozostało bez zmian:")
    print("   - system_prompt.md (używane przez v2)")
    print("   - tools.yaml (można rozszerzyć)")
    print("   - workflow/ (szablony handoff)")
    
    print("\n🎯 Następne kroki:")
    print("   1. python scripts/setup.py --phase 1")
    print("   2. python -m src.v2.orchestrator --help")
    print("   3. Test: python -m src.v2.orchestrator --project 'Test' --type CORE")


if __name__ == "__main__":
    main()

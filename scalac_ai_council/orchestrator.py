#!/usr/bin/env python3
"""
Rada AI Orchestrator
Zarządza 5 agentami i automatycznie robi handoff'y między nimi.

Usage:
    python orchestrator.py --project "Team Extension dla Fintech" --type CORE
    python orchestrator.py --project "Sovereign AI dla Banku" --type AI
    python orchestrator.py --project "AI-Capable Team" --type BUNDLE
"""

import argparse
import json
from datetime import datetime
from typing import Dict, List, Optional

class Agent:
    """Base class dla agentów Rady AI"""
    
    def __init__(self, name: str, role: str, prompt_file: str):
        self.name = name
        self.role = role
        self.prompt_file = prompt_file
        self.system_prompt = self._load_prompt()
        
    def _load_prompt(self) -> str:
        """Wczytuje system prompt z pliku"""
        try:
            with open(f"AGENTS/{self.prompt_file}/system_prompt.md", "r") as f:
                return f.read()
        except FileNotFoundError:
            print(f"⚠️  Warning: Nie znaleziono promptu dla {self.name}")
            return ""
    
    def process(self, input_data: Dict, context: Dict) -> Dict:
        """Przetwarza input i zwraca output"""
        # W prawdziwej implementacji - wywołanie API (OpenAI/Anthropic)
        # Teraz - symulacja
        return {
            "agent": self.name,
            "role": self.role,
            "input": input_data,
            "output": f"[{self.name}] Przetworzono zadanie",
            "handoff_ready": True,
            "timestamp": datetime.now().isoformat()
        }

class MarcusAgent(Agent):
    """Architekt Oferty"""
    def __init__(self):
        super().__init__("Marcus", "Architekt Oferty", "marcus_offer_architect")
    
    def create_offer(self, project_name: str, project_type: str, context: str) -> Dict:
        """Tworzy kompletny Offer Package"""
        print(f"\n🎯 {self.name} ({self.role}): Projektuję ofertę...")
        
        # Symulacja outputu
        return {
            "agent": self.name,
            "deliverables": {
                "gap_analysis": f"Gap Analysis dla {project_name}",
                "brandscript": f"BrandScript ({project_type})",
                "pricing": "Good-Better-Best",
                "challenger_pitch": "Teach-Tailor-Take Control",
                "beachhead": "Target segment defined"
            },
            "type": project_type,
            "ready_for_elena": True,
            "handoff_notes": f"Oferta {project_name} gotowa. Target: CTO fintechów."
        }

class ElenaAgent(Agent):
    """Architektka Lejków"""
    def __init__(self):
        super().__init__("Elena", "Architektka Lejków", "elena_funnel_architect")
    
    def build_funnel(self, offer_package: Dict, targets: Dict) -> Dict:
        """Buduje lejek sprzedażowy"""
        print(f"\n🎯 {self.name} ({self.role}): Buduję lejek...")
        
        return {
            "agent": self.name,
            "deliverables": {
                "funnel_stages": "Lead → MQL → SQL → Opp → Closed",
                "meddic_criteria": "Metrics, Economic Buyer, Criteria, Process, Pain, Champion",
                "three_pipelines": "Seeds (40%), Nets (30%), Spears (30%)",
                "jolt_playbook": "Overcoming indecision",
                "experiments": ["Test A: Pricing presentation", "Test B: Architecture Review as PQL"]
            },
            "targets": targets,
            "ready_for_david": True,
            "ready_for_kai": True,
            "handoff_notes": "Lejek gotowy. Target: 10 meetings, 200k PLN pipeline."
        }

class KaiAgent(Agent):
    """Copywriter"""
    def __init__(self):
        super().__init__("Kai", "Główny Copywriter", "kai_copywriter")
    
    def create_copy(self, offer_package: Dict, deliverables: List[str]) -> Dict:
        """Tworzy copy"""
        print(f"\n🎯 {self.name} ({self.role}): Piszę copy...")
        
        return {
            "agent": self.name,
            "deliverables": {
                "landing_page": "AIDA + 4U's + Big 5",
                "email_sequence": "5-email sequence",
                "ad_copy": "3 LinkedIn variants",
                "brand_voice_check": "Technical but business-savvy"
            },
            "tone": "CORE: Speed/reliability" if offer_package.get("type") == "CORE" else "AI: Compliance/security",
            "ready_for_sofia": True,
            "handoff_notes": "Copy gotowe. Landing page + 5 emails."
        }

class SofiaAgent(Agent):
    """Strateg Treści"""
    def __init__(self):
        super().__init__("Sofia", "Strateg Treści", "sofia_content_strategist")
    
    def create_content_strategy(self, funnel_data: Dict, kai_copy: Dict) -> Dict:
        """Tworzy strategię contentu"""
        print(f"\n🎯 {self.name} ({self.role}): Planuję content...")
        
        return {
            "agent": self.name,
            "deliverables": {
                "editorial_calendar": "Q1 Calendar (80% CORE, 20% AI)",
                "epic_content": "Complete Guide to Scaling Fintech",
                "seo_strategy": "Intent-based keywords",
                "newsletter": "Distributed Systems Weekly"
            },
            "content_mix": "40% Awareness / 40% Consideration / 20% Decision",
            "handoff_notes": "Content strategy gotowa. Support dla lejka."
        }

class DavidAgent(Agent):
    """Strateg Leadów"""
    def __init__(self):
        super().__init__("David", "Strateg Leadów", "david_lead_strategist")
    
    def create_abm_campaign(self, funnel_data: Dict, target_accounts: int = 50) -> Dict:
        """Tworzy ABM campaign"""
        print(f"\n🎯 {self.name} ({self.role}): Przygotowuję ABM...")
        
        return {
            "agent": self.name,
            "deliverables": {
                "dream_100": f"{target_accounts} scored accounts",
                "abm_tiers": "Tier 1 (1-to-1), Tier 2 (1-to-few), Tier 3 (1-to-many)",
                "sequences": "Omni-channel 12-touch cadence",
                "intent_plays": "Signal-based selling",
                "multi_threading": "Buying committee mapping"
            },
            "targets": {
                "meetings": 10,
                "pipeline": "200k PLN",
                "timeline": "90 days"
            },
            "handoff_notes": "ABM ready. Dream 100 selected. Launch when content ready."
        }

class RadaAIOrchestrator:
    """Główny orchestrator który zarządza całym procesem"""
    
    def __init__(self):
        print("🚀 Inicjalizacja Rady AI...")
        self.agents = {
            "marcus": MarcusAgent(),
            "elena": ElenaAgent(),
            "kai": KaiAgent(),
            "sofia": SofiaAgent(),
            "david": DavidAgent()
        }
        self.project_history = []
        
    def run_project(self, project_name: str, project_type: str, 
                   target_pipeline: int = 200000, 
                   timeline_days: int = 90) -> Dict:
        """
        Przeprowadza kompletny projekt przez wszystkich agentów.
        
        Args:
            project_name: Nazwa projektu
            project_type: CORE, AI, lub BUNDLE
            target_pipeline: Target pipeline w PLN
            timeline_days: Timeline w dniach
        """
        print(f"\n{'='*60}")
        print(f"🎯 NOWY PROJEKT: {project_name}")
        print(f"📊 Type: {project_type} | Pipeline: {target_pipeline:,} PLN | Timeline: {timeline_days}d")
        print(f"{'='*60}\n")
        
        project_data = {
            "name": project_name,
            "type": project_type,
            "targets": {
                "pipeline": target_pipeline,
                "timeline_days": timeline_days
            },
            "stages": []
        }
        
        # Stage 1: Marcus (Offer)
        offer = self.agents["marcus"].create_offer(
            project_name, project_type, 
            context=f"Target: CTOs, {timeline_days}d timeline"
        )
        project_data["stages"].append({"stage": "offer", "data": offer})
        
        # Stage 2: Elena (Funnel) - parallel with Kai
        funnel = self.agents["elena"].build_funnel(
            offer, 
            targets={"pipeline": target_pipeline, "deals": target_pipeline // 100000}
        )
        project_data["stages"].append({"stage": "funnel", "data": funnel})
        
        # Stage 3: Kai (Copy) - parallel with Elena
        copy = self.agents["kai"].create_copy(
            offer,
            deliverables=["landing_page", "email_sequence", "ad_copy"]
        )
        project_data["stages"].append({"stage": "copy", "data": copy})
        
        # Stage 4: David (ABM) - depends on Elena
        abm = self.agents["david"].create_abm_campaign(
            funnel,
            target_accounts=50
        )
        project_data["stages"].append({"stage": "abm", "data": abm})
        
        # Stage 5: Sofia (Content) - depends on funnel + copy
        content = self.agents["sofia"].create_content_strategy(
            funnel, copy
        )
        project_data["stages"].append({"stage": "content", "data": content})
        
        # Summary
        print(f"\n{'='*60}")
        print("✅ PROJEKT ZAKOŃCZONY")
        print(f"{'='*60}")
        
        summary = self._generate_summary(project_data)
        print(summary)
        
        self.project_history.append(project_data)
        return project_data
    
    def _generate_summary(self, project_data: Dict) -> str:
        """Generuje podsumowanie projektu"""
        summary = f"""
📋 {project_data['name']}

✅ MARCUS (Offer):
   • Gap Analysis + BrandScript
   • Good-Better-Best Pricing
   • Challenger Pitch ready

✅ ELENA (Funnel):
   • 5-stage funnel defined
   • MEDDIC criteria set
   • 3 pipelines planned
   • JOLT playbook ready

✅ KAI (Copy):
   • Landing page (AIDA, 4U's, Big 5)
   • 5-email sequence
   • 3 ad variants

✅ DAVID (ABM):
   • Dream 100 selected
   • 90-day playbook
   • Omni-channel sequences

✅ SOFIA (Content):
   • Q1 Editorial Calendar
   • Epic content plan
   • SEO strategy

🎯 TARGETS:
   • Pipeline: {project_data['targets']['pipeline']:,} PLN
   • Timeline: {project_data['targets']['timeline_days']} days

📁 Output zapisany w: projects/{project_data['name'].replace(' ', '_').lower()}.json
"""
        return summary
    
    def export_project(self, project_data: Dict, filename: Optional[str] = None):
        """Eksportuje projekt do JSON"""
        if not filename:
            filename = f"projects/{project_data['name'].replace(' ', '_').lower()}.json"
        
        with open(filename, "w") as f:
            json.dump(project_data, f, indent=2)
        
        print(f"\n💾 Projekt zapisany: {filename}")

def main():
    parser = argparse.ArgumentParser(description="Rada AI Orchestrator")
    parser.add_argument("--project", required=True, help="Nazwa projektu")
    parser.add_argument("--type", choices=["CORE", "AI", "BUNDLE"], 
                       required=True, help="Typ projektu")
    parser.add_argument("--pipeline", type=int, default=200000, 
                       help="Target pipeline w PLN (default: 200000)")
    parser.add_argument("--timeline", type=int, default=90, 
                       help="Timeline w dniach (default: 90)")
    parser.add_argument("--export", action="store_true", 
                       help="Eksportuj do JSON")
    
    args = parser.parse_args()
    
    # Uruchom orchestrator
    rada = RadaAIOrchestrator()
    
    project = rada.run_project(
        project_name=args.project,
        project_type=args.type,
        target_pipeline=args.pipeline,
        timeline_days=args.timeline
    )
    
    if args.export:
        import os
        os.makedirs("projects", exist_ok=True)
        rada.export_project(project)

if __name__ == "__main__":
    main()

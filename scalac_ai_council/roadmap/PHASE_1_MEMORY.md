# Faza 1: Agent z Pamięcią Długoterminową

**Timeline:** 1-2 tygodnie  
**Impact:** Wysoki | **Trudność:** Średnia | **Koszt:** ~$70/miesiąc

---

## 🎯 Cel

Agenci pamiętają:
- Poprzednie projekty i ich wyniki
- Case studies Scalac
- Co działało / nie działało
- Preferencje klientów i wzorce

---

## 🏗️ Architektura

```
┌─────────────────────────────────────────────────────────────┐
│                    User Input                               │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 Orchestrator v2                             │
│         (przekazuje kontekst między agentami)              │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
        ┌───────────────────────────────────────┐
        │      Vector Store (ChromaDB)          │
        │  • Case studies Scalac               │
        │  • Historia projektów                 │
        │  • Winning/losing patterns            │
        │  • Wiedza domenowa (CORE/AI)          │
        └────────────────┬──────────────────────┘
                         │
    ┌────────────────────┼────────────────────┐
    ▼                    ▼                    ▼
┌─────────┐      ┌───────────┐       ┌──────────┐
│ Marcus  │◄────►│  Elena    │◄─────►│   Kai    │
│+ Memory │      │ + Memory  │       │ + Memory │
└─────────┘      └───────────┘       └──────────┘
    ▲                                          ▲
    └──────────────────┬───────────────────────┘
                       ▼
              ┌──────────────┐
              │    Sofia     │
              │   + Memory   │
              └──────────────┘
```

---

## 📦 Stack Technologiczny

| Komponent | Technologia | Dlaczego |
|-----------|-------------|----------|
| Vector DB | ChromaDB | Darmowy, lokalny, prosty |
| Embeddings | OpenAI text-embedding-3-small | Tanie ($0.02/1M tokens), dobre |
| Framework | LangChain | Standard, dużo integracji |
| LLM | GPT-4 / GPT-4-turbo | Jakość + wsparcie dla function calling |

---

## 🔧 Implementacja

### Krok 1: Zależności

**requirements-v2.txt:**
```
# Core
langchain>=0.1.0
langchain-openai>=0.0.5
langchain-community>=0.0.10

# Vector DB
chromadb>=0.4.18

# Utils
python-dotenv>=1.0.0
pydantic>=2.5.0
tiktoken>=0.5.2

# Optional (for future)
pinecone-client>=2.2.4
```

### Krok 2: Konfiguracja Vector DB

**src/v2/memory/vector_store.py:**
```python
"""
Abstrakcja Vector Store dla Rady AI.
Obsługuje ChromaDB (lokalnie) lub Pinecone (cloud).
"""

import os
from typing import List, Dict, Optional
from dataclasses import dataclass

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document


@dataclass
class MemoryQuery:
    """Wynik wyszukiwania z pamięci."""
    content: str
    source: str
    score: float
    metadata: Dict


class ScalacMemory:
    """
    Długoterminowa pamięć dla agentów Rady AI.
    
    Przechowuje:
    - Case studies Scalac
    - Historię projektów
    - Wzorce winning/losing
    - Wiedzę o klientach
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",  # Tanie i dobre
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Inicjalizacja lub załadowanie istniejącej bazy
        self.db = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings,
            collection_name="scalac_knowledge"
        )
        
    def add_case_studies(self, case_studies: List[Dict]):
        """
        Dodaj case studies do pamięci.
        
        Args:
            case_studies: Lista case studies z metadanymi
                {
                    "title": "Bexio Migration",
                    "industry": "fintech",
                    "service": "team_extension",
                    "content": "Pełny opis...",
                    "results": {"team_size": 5, "duration_months": 12},
                    "winning_factors": ["szybkie onboardowanie", "scala expertise"]
                }
        """
        documents = []
        for cs in case_studies:
            # Tworzymy dokument z metadanymi
            doc = Document(
                page_content=cs["content"],
                metadata={
                    "type": "case_study",
                    "title": cs["title"],
                    "industry": cs.get("industry", "unknown"),
                    "service": cs.get("service", "unknown"),
                    "results": str(cs.get("results", {})),
                    "winning_factors": str(cs.get("winning_factors", []))
                }
            )
            documents.append(doc)
        
        # Dodaj do bazy
        self.db.add_documents(documents)
        self.db.persist()
        print(f"✅ Dodano {len(documents)} case studies do pamięci")
    
    def add_project_outcome(self, project_id: str, outcome: Dict):
        """
        Zapisz wynik projektu do nauki.
        
        Args:
            project_id: Unikalny identyfikator projektu
            outcome: {
                "project_name": "Team Extension dla X",
                "agent": "Marcus",
                "what_worked": [...],
                "what_failed": [...],
                "insight": "Kluczowe wnioski",
                "metrics": {"conversion": 0.35, "deal_size": 180000}
            }
        """
        content = f"""
Project: {outcome['project_name']}
Agent: {outcome['agent']}
What worked: {', '.join(outcome['what_worked'])}
What failed: {', '.join(outcome['what_failed'])}
Insight: {outcome['insight']}
Metrics: {outcome.get('metrics', {})}
        """.strip()
        
        doc = Document(
            page_content=content,
            metadata={
                "type": "project_outcome",
                "project_id": project_id,
                "agent": outcome["agent"],
                "date": outcome.get("date", "unknown")
            }
        )
        
        self.db.add_documents([doc])
        self.db.persist()
        print(f"✅ Zapisano wynik projektu {project_id}")
    
    def search_relevant(
        self, 
        query: str, 
        filter_dict: Optional[Dict] = None,
        k: int = 5
    ) -> List[MemoryQuery]:
        """
        Wyszukaj relevant context z pamięci.
        
        Args:
            query: Zapytanie (np. "fintech team extension case study")
            filter_dict: Filtr (np. {"industry": "fintech"})
            k: Ile wyników zwrócić
            
        Returns:
            Lista MemoryQuery z contentem i metadanymi
        """
        results = self.db.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter_dict
        )
        
        return [
            MemoryQuery(
                content=doc.page_content,
                source=doc.metadata.get("title", doc.metadata.get("project_id", "unknown")),
                score=score,
                metadata=doc.metadata
            )
            for doc, score in results
        ]
    
    def get_similar_cases(self, industry: str, service: str, k: int = 3) -> List[MemoryQuery]:
        """Pobierz podobne case studies dla danej branży i usługi."""
        return self.search_relevant(
            query=f"{industry} {service} case study",
            filter_dict={"type": "case_study", "industry": industry},
            k=k
        )
    
    def get_agent_learning(self, agent_name: str, k: int = 10) -> List[MemoryQuery]:
        """Pobierz wnioski z poprzednich projektów dla danego agenta."""
        return self.search_relevant(
            query=f"what worked for {agent_name}",
            filter_dict={"type": "project_outcome", "agent": agent_name},
            k=k
        )
    
    def stats(self) -> Dict:
        """Statystyki bazy wiedzy."""
        # ChromaDB API nie ma prostego count, więc używamy peek
        try:
            collection = self.db._collection
            count = collection.count()
            return {
                "total_documents": count,
                "persist_directory": self.persist_directory
            }
        except:
            return {"error": "Could not get stats"}


# Singleton dla łatwego dostępu
_memory_instance = None

def get_memory(persist_directory: str = "./chroma_db") -> ScalacMemory:
    """Get or create singleton instance of ScalacMemory."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = ScalacMemory(persist_directory)
    return _memory_instance
```

### Krok 3: Bazowa klasa agenta z pamięcią

**src/v2/agents/base_agent.py:**
```python
"""
Bazowa klasa dla wszystkich agentów Rady AI v2.
Zapewnia pamięć długoterminową i podstawowe funkcje.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from ..memory.vector_store import ScalacMemory, get_memory


@dataclass
class AgentResponse:
    """Standardowy format odpowiedzi agenta."""
    agent: str
    content: str
    used_memory: List[str]  # Jakie case studies zostały użyte
    timestamp: str
    metadata: Dict[str, Any]


class BaseScalacAgent:
    """
    Bazowa klasa agenta Scalac z pamięcią długoterminową.
    
    Każdy agent dziedziczy po tej klasie i dostaje:
    - Dostęp do Vector DB z case studies
    - Pamięć poprzednich projektów
    - Bazowy LLM (GPT-4)
    """
    
    def __init__(
        self, 
        name: str, 
        role: str, 
        prompt_file: Optional[str] = None,
        memory: Optional[ScalacMemory] = None
    ):
        self.name = name
        self.role = role
        self.memory = memory or get_memory()
        
        # Załaduj system prompt z pliku
        self.system_prompt = self._load_system_prompt(prompt_file)
        
        # LLM
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.3,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Historia rozmów dla tej sesji
        self.session_history: List = []
        
    def _load_system_prompt(self, prompt_file: Optional[str]) -> str:
        """Załaduj system prompt z pliku lub użyj domyślnego."""
        if prompt_file:
            # Próbuj załadować z pliku
            path = f"AGENTS/{prompt_file}/system_prompt.md"
            alt_path = f"scalac_ai_council/AGENTS/{prompt_file}/system_prompt.md"
            
            for p in [path, alt_path]:
                try:
                    with open(p, 'r') as f:
                        return f.read()
                except FileNotFoundError:
                    continue
        
        # Domyślny prompt
        return f"""Jesteś {self.name}, {self.role} w Scalac.

Masz dostęp do pamięci długoterminowej z case studies i wynikami poprzednich projektów.
Używaj tej wiedzy aby podejmować lepsze decyzje.

Zasady:
1. Zawsze szukaj podobnych case studies przed odpowiedzią
2. Ucz się z błędów poprzednich projektów
3. Dziel się insightami z pamięci w swojej odpowiedzi
"""
    
    def _get_relevant_context(self, task: str) -> str:
        """Pobierz relevant context z pamięci."""
        # Wyszukaj case studies
        similar_cases = self.memory.search_relevant(
            query=task,
            k=3
        )
        
        # Wyszukaj wnioski z poprzednich projektów tego agenta
        agent_learning = self.memory.get_agent_learning(self.name, k=3)
        
        context_parts = []
        
        if similar_cases:
            context_parts.append("### Podobne Case Studies:")
            for case in similar_cases:
                context_parts.append(f"- {case.source}: {case.content[:300]}...")
        
        if agent_learning:
            context_parts.append("\n### Wnioski z Poprzednich Projektów:")
            for learning in agent_learning:
                context_parts.append(f"- {learning.content[:300]}...")
        
        return "\n".join(context_parts) if context_parts else "Brak relevant context w pamięci."
    
    def run(self, task: str, context: Optional[Dict] = None) -> AgentResponse:
        """
        Wykonaj zadanie z użyciem pamięci.
        
        Args:
            task: Zadanie do wykonania
            context: Dodatkowy kontekst (np. output innego agenta)
            
        Returns:
            AgentResponse ze standardowym formatem
        """
        # Pobierz relevant context z pamięci
        memory_context = self._get_relevant_context(task)
        
        # Przygotuj prompt
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            MessagesPlaceholder(variable_name="history"),
            HumanMessage(content=f"""
## TASK
{task}

## RELEVANT CONTEXT Z PAMIĘCI
{memory_context}

## ADDITIONAL CONTEXT
{context or 'Brak dodatkowego kontekstu.'}

## INSTRUKCJE
1. Użyj powyższego context w swojej odpowiedzi
2. Odnieś się do konkretnych case studies jeśli relevant
3. Podaj konkretne, wykonalne rekomendacje
4. Format: Structured markdown
            """)
        ])
        
        # Wygeneruj odpowiedź
        messages = prompt.format_messages(history=self.session_history)
        response = self.llm.invoke(messages)
        
        # Zapisz w historii sesji
        self.session_history.extend([
            HumanMessage(content=task),
            response
        ])
        
        # Zachowaj tylko ostatnie 10 interakcji
        if len(self.session_history) > 20:
            self.session_history = self.session_history[-20:]
        
        return AgentResponse(
            agent=self.name,
            content=response.content,
            used_memory=[case.source for case in self.memory.search_relevant(task, k=3)],
            timestamp=datetime.now().isoformat(),
            metadata={"context_used": bool(memory_context)}
        )
    
    def learn(self, project_id: str, outcome: Dict):
        """Nauka z wyniku projektu."""
        outcome["agent"] = self.name
        self.memory.add_project_outcome(project_id, outcome)
        print(f"🧠 {self.name} nauczył się z projektu {project_id}")
```

### Krok 4: Konkretni agenci

**src/v2/agents/marcus.py:**
```python
"""
Marcus - Architekt Oferty v2
Z pamięcią case studies i wniosków z poprzednich ofert.
"""

from typing import Dict
from .base_agent import BaseScalacAgent, AgentResponse


class MarcusAgent(BaseScalacAgent):
    """Marcus z pamięcią długoterminową."""
    
    def __init__(self, memory=None):
        super().__init__(
            name="Marcus",
            role="Architekt Oferty",
            prompt_file="marcus_offer_architect",
            memory=memory
        )
    
    def create_offer(
        self, 
        project_name: str, 
        project_type: str,
        target_segment: str = ""
    ) -> AgentResponse:
        """
        Zaprojektuj ofertę z użyciem pamięci o podobnych projektach.
        
        Args:
            project_name: Nazwa projektu/oferty
            project_type: CORE, AI, lub BUNDLE
            target_segment: Opcjonalny target (np. "fintech Series B")
        """
        task = f"""
Zaprojektuj kompletną ofertę "{project_name}".

Typ: {project_type}
Target: {target_segment or "Do określenia na podstawie case studies"}

## FRAMEWORKI DO UŻYCIA:
1. Gap Selling - Current State vs Future State
2. StoryBrand - BrandScript
3. Good-Better-Best Pricing
4. Challenger Sale - Teach/Tailor/Take Control

## OUTPUT FORMAT:
```markdown
# Offer Package: {project_name}

## 1. Gap Analysis
### Current State
[opisz]

### Future State  
[opisz]

### The Gap (Problem)
[co blokuje przejście]

### Impact
- Financial: [ile tracą]
- Emotional: [stres, presja]

## 2. BrandScript (StoryBrand)
[SB7 Framework]

## 3. Pricing (Good-Better-Best)
- Good: [price] - [scope]
- Better: [price] - [scope]  
- Best: [price] - [scope]
- Decoy: [coś droższego]

## 4. Challenger Pitch
[Teach-Tailor-Take Control]

## 5. Beachhead Market (Crossing the Chasm)
- Target: [konkretny segment]
- Problem: [ból]
- Competition: [alternatywy]
- Access: [jak dotrzeć]
```

Użyj case studies z pamięci jako inspirację i proof.
        """
        
        return self.run(task, {"project_type": project_type})


# Convenience function
def create_marcus(memory=None):
    return MarcusAgent(memory)
```

**src/v2/agents/elena.py:**
```python
"""
Elena - Architektka Lejków v2
Z pamięcią konwersji i benchmarków.
"""

from typing import Dict
from .base_agent import BaseScalacAgent, AgentResponse


class ElenaAgent(BaseScalacAgent):
    """Elena z pamięcią długoterminową."""
    
    def __init__(self, memory=None):
        super().__init__(
            name="Elena",
            role="Architektka Lejków",
            prompt_file="elena_funnel_architect",
            memory=memory
        )
    
    def build_funnel(
        self,
        offer_package: Dict,
        target_pipeline: int = 200000
    ) -> AgentResponse:
        """
        Zbuduj lejek w oparciu o ofertę i historię.
        
        Args:
            offer_package: Output od Marcusa
            target_pipeline: Target pipeline w PLN
        """
        task = f"""
Zbuduj kompletny lejek sprzedażowy dla oferty:

{offer_package.get('content', 'Brak danych o ofercie')[:1000]}...

Target Pipeline: {target_pipeline:,} PLN

## FRAMEWORKI DO UŻYCIA:
1. MEDDIC - Qualification criteria
2. JOLT - Overcoming indecision
3. Three Pipelines - Seeds/Nets/Spears
4. Predictable Revenue - Funnel stages

## OUTPUT FORMAT:
```markdown
# Funnel Design

## 1. Funnel Stages
1. Lead - [definition]
2. MQL - [definition, conversion %]
3. SQL - [definition, conversion %]
4. Opportunity - [definition, conversion %]
5. Closed - [target win rate]

## 2. Three Pipelines Strategy
### Seeds (Inbound)
- Channels: [...]
- Expected volume: [...]

### Nets (Marketing)
- Channels: [...]
- Expected volume: [...]

### Spears (Outbound)
- Target accounts: [...]
- Approach: [...]

## 3. MEDDIC Qualification
- Metrics: [...]
- Economic Buyer: [...]
- Decision Criteria: [...]
- Decision Process: [...]
- Pain: [...]
- Champion: [...]

## 4. JOLT Strategy
[How to overcome indecision at each stage]

## 5. Experiments
[List 3 experiments to test assumptions]
```

Użyj danych z poprzednich projektów aby ustalić realistyczne konwersje.
        """
        
        return self.run(task, {"target_pipeline": target_pipeline})


def create_elena(memory=None):
    return ElenaAgent(memory)
```

(Podobnie dla Kai, Sofia, David...)

### Krok 5: Nowy orchestrator

**src/v2/orchestrator.py:**
```python
#!/usr/bin/env python3
"""
Rada AI Orchestrator v2
Z pamięcią długoterminową i współdzielonym kontekstem.
"""

import argparse
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from dotenv import load_dotenv

from .memory.vector_store import ScalacMemory, get_memory
from .agents.marcus import MarcusAgent
from .agents.elena import ElenaAgent
# from .agents.kai import KaiAgent
# from .agents.sofia import SofiaAgent
# from .agents.david import DavidAgent


load_dotenv()


class RadaAIOrchestratorV2:
    """
    Nowy orchestrator z prawdziwą pamięcią.
    
    Kluczowe zmiany vs v1:
    - Agenci mają dostęp do Vector DB
    - Handoff'y zachowują pełny kontekst
    - Możliwość nauki z wyników
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        print("🚀 Inicjalizacja Rady AI v2 (z pamięcią)...")
        
        # Inicjalizacja pamięci
        self.memory = get_memory(persist_directory)
        print(f"📚 Pamięć załadowana: {self.memory.stats()}")
        
        # Inicjalizacja agentów z pamięcią
        self.agents = {
            "marcus": MarcusAgent(self.memory),
            "elena": ElenaAgent(self.memory),
            # "kai": KaiAgent(self.memory),
            # "sofia": SofiaAgent(self.memory),
            # "david": DavidAgent(self.memory),
        }
        
        self.current_project = None
        
    def run_project(
        self, 
        project_name: str, 
        project_type: str,
        target_pipeline: int = 200000,
        target_segment: str = ""
    ) -> Dict:
        """
        Przeprowadź kompletny projekt przez Radę.
        
        Args:
            project_name: Nazwa projektu
            project_type: CORE, AI, lub BUNDLE
            target_pipeline: Target w PLN
            target_segment: Opcjonalny target (np. "fintech Series B")
        """
        print(f"\n{'='*60}")
        print(f"🎯 NOWY PROJEKT: {project_name}")
        print(f"📊 Type: {project_type} | Pipeline: {target_pipeline:,} PLN")
        print(f"{'='*60}\n")
        
        project_data = {
            "name": project_name,
            "type": project_type,
            "target_segment": target_segment,
            "targets": {"pipeline": target_pipeline},
            "stages": [],
            "started_at": datetime.now().isoformat()
        }
        
        # Stage 1: Marcus (Offer)
        print("\n🎯 Stage 1: Marcus projektuje ofertę...")
        offer = self.agents["marcus"].create_offer(
            project_name=project_name,
            project_type=project_type,
            target_segment=target_segment
        )
        project_data["stages"].append({
            "stage": "offer",
            "agent": "marcus",
            "output": offer.content,
            "used_memory": offer.used_memory
        })
        print(f"   ✓ Użyto case studies: {', '.join(offer.used_memory[:3])}")
        
        # Stage 2: Elena (Funnel)
        print("\n🎯 Stage 2: Elena buduje lejek...")
        funnel = self.agents["elena"].build_funnel(
            offer_package={"content": offer.content},
            target_pipeline=target_pipeline
        )
        project_data["stages"].append({
            "stage": "funnel",
            "agent": "elena",
            "output": funnel.content,
            "used_memory": funnel.used_memory
        })
        print(f"   ✓ Użyto case studies: {', '.join(funnel.used_memory[:3])}")
        
        # TODO: Stages 3-5 (Kai, David, Sofia)
        
        project_data["completed_at"] = datetime.now().isoformat()
        self.current_project = project_data
        
        # Podsumowanie
        self._print_summary(project_data)
        
        return project_data
    
    def _print_summary(self, project_data: Dict):
        """Wydrukuj podsumowanie projektu."""
        print(f"\n{'='*60}")
        print("✅ PROJEKT ZAKOŃCZONY")
        print(f"{'='*60}\n")
        
        for stage in project_data["stages"]:
            print(f"📋 {stage['agent'].upper()}")
            print(f"   Użyto pamięci: {len(stage['used_memory'])} dokumentów")
            print(f"   Preview: {stage['output'][:200]}...")
            print()
        
        print(f"💾 Zapisz feedback: rada.learn('{project_data['name']}', outcome)")
    
    def learn(self, project_id: str, agent_name: str, outcome: Dict):
        """Nauka z wyniku projektu."""
        if agent_name in self.agents:
            self.agents[agent_name].learn(project_id, outcome)
        else:
            print(f"⚠️ Nieznany agent: {agent_name}")
    
    def export_project(self, filename: Optional[str] = None):
        """Eksportuj projekt do JSON."""
        if not self.current_project:
            print("⚠️ Brak aktywnego projektu")
            return
        
        if not filename:
            filename = f"projects/{self.current_project['name'].replace(' ', '_').lower()}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            json.dump(self.current_project, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Projekt zapisany: {filename}")


def main():
    parser = argparse.ArgumentParser(description="Rada AI Orchestrator v2")
    parser.add_argument("--project", required=True, help="Nazwa projektu")
    parser.add_argument("--type", choices=["CORE", "AI", "BUNDLE"], required=True)
    parser.add_argument("--segment", default="", help="Target segment (np. 'fintech Series B')")
    parser.add_argument("--pipeline", type=int, default=200000)
    parser.add_argument("--export", action="store_true")
    parser.add_argument("--memory-path", default="./chroma_db", help="Ścieżka do Vector DB")
    
    args = parser.parse_args()
    
    # Uruchom
    rada = RadaAIOrchestratorV2(persist_directory=args.memory_path)
    
    project = rada.run_project(
        project_name=args.project,
        project_type=args.type,
        target_pipeline=args.pipeline,
        target_segment=args.segment
    )
    
    if args.export:
        rada.export_project()


if __name__ == "__main__":
    main()
```

### Krok 6: Skrypt do ładowania wiedzy

**scripts/ingest_knowledge.py:**
```python
#!/usr/bin/env python3
"""
Skrypt do ładowania case studies Scalac do Vector DB.
Uruchom raz na początku, potem aktualizuj gdy masz nowe case studies.
"""

import sys
import os

# Dodaj src do path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from v2.memory.vector_store import ScalacMemory


# Przykładowe case studies - ZASTĄP swoimi prawdziwymi
CASE_STUDIES = [
    {
        "title": "Bexio - Fintech Migration",
        "industry": "fintech",
        "service": "team_extension",
        "content": """
Klient: Bexio (Szwajcarski fintech, software dla księgowych)
Wyzwanie: Legacy payroll system w Javie, trzeba przepisać na Scalę z zero downtime
Rozwiązanie: Team 5 senior Scala devów, gradual migration z feature flags
Czas: 12 miesięcy
Wyniki: 
- 2x performance improvement
- Zero downtime migration
- 50% reduction in bug reports
Winning factors:
- Szybkie onboardowanie (2 tygodnie)
- Deep Scala expertise
- Experience w fintech compliance
        """,
        "results": {"team_size": 5, "duration_months": 12, "performance_improvement": "2x"},
        "winning_factors": ["szybkie onboardowanie", "scala expertise", "fintech compliance"]
    },
    {
        "title": "Liga Digital - Distributed Systems",
        "industry": "healthtech",
        "service": "project_based",
        "content": """
Klient: Liga Digital (Hiszpański healthtech)
Wyzwanie: System do zarządzania szpitalami nie skaluje się przy 10x load
Rozwiązanie: Re-architecture na event sourcing + Akka Cluster
Czas: 8 miesięcy
Wyniki:
- System obsługuje 10x load
- 99.99% uptime
- Reduced infrastructure costs by 30%
Winning factors:
- Distributed systems expertise
- Akka knowledge
- Performance optimization
        """,
        "results": {"team_size": 3, "duration_months": 8, "scalability": "10x"},
        "winning_factors": ["distributed systems", "akka", "performance optimization"]
    },
    {
        "title": "Swiss Bank - Sovereign AI POC",
        "industry": "banking",
        "service": "ai_consulting",
        "content": """
Klient: Swiss Private Bank (nazwa poufna)
Wyzwanie: Chcą RAG dla wewnętrznych dokumentów, ale compliance blokuje OpenAI
Rozwiązanie: Sovereign AI architecture - private LLM on-premises, zero data exfiltration
Czas: 3 miesiące (POC)
Wyniki:
- POC przeszedł compliance audit
- 95% accuracy na wewnętrznych dokumentach
- Board zatwierdził produkcję
Winning factors:
- Sovereign AI expertise
- Banking compliance knowledge
- Production-ready architecture
        """,
        "results": {"duration_months": 3, "accuracy": "95%", "compliance": "passed"},
        "winning_factors": ["sovereign ai", "banking compliance", "production-ready"]
    }
]


def main():
    print("📚 Ingestia wiedzy Scalac do Vector DB...")
    
    # Inicjalizacja pamięci
    memory = ScalacMemory(persist_directory="./chroma_db")
    
    # Dodaj case studies
    print(f"\n➕ Dodawanie {len(CASE_STUDIES)} case studies...")
    memory.add_case_studies(CASE_STUDIES)
    
    # Statystyki
    stats = memory.stats()
    print(f"\n✅ Gotowe!")
    print(f"   Dokumentów w bazie: {stats.get('total_documents', 'N/A')}")
    print(f"   Lokalizacja: {stats.get('persist_directory', './chroma_db')}")
    
    # Test wyszukiwania
    print("\n🔍 Test wyszukiwania:")
    results = memory.search_relevant("fintech team extension", k=2)
    for r in results:
        print(f"   - {r.source} (score: {r.score:.3f})")


if __name__ == "__main__":
    main()
```

---

## 🚀 Użycie

### 1. Setup (raz)

```bash
# Instalacja
pip install -r requirements-v2.txt

# Ustaw klucz API
export OPENAI_API_KEY="sk-..."

# Załaduj case studies
python scripts/ingest_knowledge.py
```

### 2. Uruchom projekt

```bash
# Prosty projekt
python -m src.v2.orchestrator --project "Team Extension dla Fintech" --type CORE --export

# Z target segment
python -m src.v2.orchestrator \
    --project "Sovereign AI dla Banków" \
    --type AI \
    --segment "swiss private banks" \
    --pipeline 500000 \
    --export
```

### 3. Programistycznie

```python
from src.v2.orchestrator import RadaAIOrchestratorV2

rada = RadaAIOrchestratorV2()

# Uruchom projekt
project = rada.run_project(
    project_name="Healthtech Migration",
    project_type="CORE",
    target_segment="healthtech scaleups"
)

# Później: nauka z wyniku
rada.learn(
    project_id="healthtech_migration",
    agent_name="marcus",
    outcome={
        "project_name": "Healthtech Migration",
        "what_worked": ["compliance case study resonated", "Good-Better-Best pricing"],
        "what_failed": ["timeline too aggressive"],
        "insight": "Healthtech needs extra compliance section in offer",
        "metrics": {"proposal_conversion": 0.40}
    }
)
```

---

## ✅ Checkpoint - Faza 1 Ukończona Gdy:

- [ ] `python scripts/ingest_knowledge.py` działa
- [ ] Agenci używają case studies w odpowiedziach
- [ ] Każdy projekt zapisuje się z metadanymi
- [ ] `rada.learn()` aktualizuje pamięć
- [ ] Agenci pamiętają wnioski z poprzednich projektów

---

**Następny krok:** [Faza 2 - Narzędzia](./PHASE_2_TOOLS.md)

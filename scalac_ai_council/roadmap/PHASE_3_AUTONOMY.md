# Faza 3: Autonomiczna Rada (LangGraph)

**Timeline:** 4-6 tygodnie  
**Impact:** Transformacyjny | **Trudność:** Wysoka | **Koszt:** ~$400/miesiąc

---

## 🎯 Cel

Transformacja z liniowego pipeline'u w **inteligentny graf decyzyjny**:
- Event-driven workflow (nie sekwencyjny)
- Feedback loop'y (np. Kai → Marcus gdy copy nie pasuje do oferty)
- Collaborative deliberation ("spotkania rady")
- Self-improvement (agenci uczą się z wyników)

---

## 🏗️ Architektura LangGraph

```
                    ┌─────────────────┐
                    │     START       │
                    │ (User Request)  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Supervisor     │
                    │  (Router)       │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
      ┌──────────┐    ┌──────────┐    ┌──────────┐
      │  Marcus  │    │  Review  │    │ Research │
      │  (Offer) │    │  Memory  │    │  Phase   │
      └────┬─────┘    └──────────┘    └──────────┘
           │
           ▼
      ┌──────────┐
      │ Quality  │──── NO ────┐
      │  Gate    │            │
      └────┬─────┘            │
           │ YES              │
           ▼                  ▼
      ┌──────────┐      ┌──────────┐
      │  Elena   │      │  Marcus  │
      │ (Funnel) │      │ (Revise) │
      └────┬─────┘      └──────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
┌────────┐ ┌────────┐
│  Kai   │ │ David  │  ◄─── Równolegle
│(Copy)  │ │ (ABM)  │
└───┬────┘ └────────┘
    │
    ▼
┌──────────┐     ┌──────────┐
│  Sofia   │────►│ Feedback │
│(Content) │     │  Loop    │
└──────────┘     └──────────┘
                        │
                        ▼
                 ┌──────────┐
                 │   END    │
                 │(Complete)│
                 └──────────┘
```

---

## 📦 Stack Technologiczny

| Komponent | Technologia | Dlaczego |
|-----------|-------------|----------|
| Workflow Engine | LangGraph | Graph-based, conditional edges |
| State Management | Pydantic | Type-safe state |
| Message Queue | Redis | Async handoff'y |
| Persistence | PostgreSQL | Historia projektów |

---

## 🔧 Implementacja

### Krok 1: Definicja Stanu

**src/v3/state.py:**
```python
"""
Definicja stanu dla LangGraph workflow.
"""

from typing import Dict, List, Optional, Literal, TypedDict, Annotated
from dataclasses import dataclass, field
from datetime import datetime
import operator


class AgentOutput(TypedDict):
    """Output pojedynczego agenta."""
    agent: str
    content: str
    status: Literal["success", "needs_revision", "blocked"]
    revision_notes: Optional[str]
    timestamp: str


class ProjectState(TypedDict):
    """
    Stan projektu przepływającego przez graf.
    
    Ten stan jest przekazywany między node'ami w grafie.
    """
    # Metadane projektu
    project_id: str
    project_name: str
    project_type: Literal["CORE", "AI", "BUNDLE"]
    target_segment: str
    target_pipeline: int
    
    # Status
    current_stage: str
    next_stage: Optional[str]
    completed_stages: Annotated[List[str], operator.add]
    
    # Outputy agentów
    offer_output: Optional[AgentOutput]
    funnel_output: Optional[AgentOutput]
    copy_output: Optional[AgentOutput]
    abm_output: Optional[AgentOutput]
    content_output: Optional[AgentOutput]
    
    # Quality gates
    quality_checks: Dict[str, bool]  # {stage: passed}
    revision_requests: Annotated[List[Dict], operator.add]
    
    # Feedback loops
    feedback_from: Optional[str]  # Który agent zgłosił feedback
    feedback_to: Optional[str]    # Do kierunku feedback
    feedback_content: Optional[str]
    
    # Memory references
    used_case_studies: Annotated[List[str], operator.add]
    tools_used: Annotated[List[str], operator.add]
    
    # Final
    project_complete: bool
    final_summary: Optional[str]
    started_at: str
    completed_at: Optional[str]


def create_initial_state(
    project_name: str,
    project_type: str,
    target_segment: str = "",
    target_pipeline: int = 200000
) -> ProjectState:
    """Utwórz początkowy stan projektu."""
    return ProjectState(
        project_id=f"{project_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        project_name=project_name,
        project_type=project_type,
        target_segment=target_segment,
        target_pipeline=target_pipeline,
        current_stage="start",
        next_stage="marcus",
        completed_stages=[],
        offer_output=None,
        funnel_output=None,
        copy_output=None,
        abm_output=None,
        content_output=None,
        quality_checks={},
        revision_requests=[],
        feedback_from=None,
        feedback_to=None,
        feedback_content=None,
        used_case_studies=[],
        tools_used=[],
        project_complete=False,
        final_summary=None,
        started_at=datetime.now().isoformat(),
        completed_at=None
    )
```

### Krok 2: Node'y (Agenci jako node'y grafu)

**src/v3/nodes.py:**
```python
"""
Node'y dla LangGraph - każdy agent jako node w grafie.
"""

from typing import Dict
from langchain_core.runnables import RunnableLambda

from ..v2.agents.marcus_v2 import MarcusAgentV2
from ..v2.agents.elena import ElenaAgent
from ..v2.memory.vector_store import get_memory
from .state import ProjectState, AgentOutput


# Inicjalizacja agentów (singleton pattern)
_agents = {}

def get_agent(name: str):
    """Get or create agent instance."""
    if name not in _agents:
        memory = get_memory()
        if name == "marcus":
            _agents[name] = MarcusAgentV2(memory)
        elif name == "elena":
            _agents[name] = ElenaAgent(memory)
        # ... pozostali
    return _agents[name]


# === NODE FUNCTIONS ===

def marcus_node(state: ProjectState) -> ProjectState:
    """Node dla Marcusa - projektowanie oferty."""
    print(f"\n🎯 [{state['project_id']}] Marcus projektuje ofertę...")
    
    agent = get_agent("marcus")
    
    # Sprawdź czy to revisja
    if state.get("feedback_to") == "marcus":
        task = f"""
REVISJA OFERTY

Poprzednia wersja:
{state['offer_output']['content'][:500] if state['offer_output'] else 'N/A'}

Feedback od {state['feedback_from']}:
{state['feedback_content']}

Popraw ofertę uwzględniając powyższe uwagi.
"""
    else:
        task = f"Zaprojektuj ofertę dla {state['project_name']} ({state['project_type']})"
    
    result = agent.create_offer(
        project_name=state['project_name'],
        project_type=state['project_type'],
        target_segment=state.get('target_segment', '')
    )
    
    output: AgentOutput = {
        "agent": "marcus",
        "content": result.content,
        "status": "success",
        "revision_notes": None,
        "timestamp": result.timestamp
    }
    
    return {
        **state,
        "offer_output": output,
        "current_stage": "marcus",
        "next_stage": "quality_gate_offer",
        "completed_stages": state["completed_stages"] + ["marcus"]
    }


def quality_gate_offer(state: ProjectState) -> ProjectState:
    """Quality gate dla oferty - sprawdź czy gotowa do następnego etapu."""
    print(f"\n🔍 Quality gate dla oferty...")
    
    offer = state["offer_output"]["content"]
    
    # Proste heurystyki jakości
    checks = {
        "has_pricing": "good" in offer.lower() and "better" in offer.lower() and "best" in offer.lower(),
        "has_gap_analysis": "current state" in offer.lower() or "gap" in offer.lower(),
        "has_storybrand": "hero" in offer.lower() or "problem" in offer.lower(),
        "adequate_length": len(offer) > 1000,
    }
    
    all_passed = all(checks.values())
    
    if all_passed:
        print("   ✅ Oferta przeszła quality gate")
        return {
            **state,
            "quality_checks": {**state["quality_checks"], "offer": True},
            "next_stage": "elena"
        }
    else:
        print(f"   ❌ Oferta nie przeszła: {checks}")
        return {
            **state,
            "quality_checks": {**state["quality_checks"], "offer": False},
            "next_stage": "marcus",  # Wracamy do Marcusa
            "feedback_to": "marcus",
            "feedback_from": "quality_gate",
            "feedback_content": f"Brakujące elementy: {[k for k, v in checks.items() if not v]}"
        }


def elena_node(state: ProjectState) -> ProjectState:
    """Node dla Eleny - budowanie lejka."""
    print(f"\n🎯 [{state['project_id']}] Elena buduje lejek...")
    
    agent = get_agent("elena")
    
    # Sprawdź czy Elena ma uwagi do oferty
    offer_content = state["offer_output"]["content"]
    
    result = agent.build_funnel(
        offer_package={"content": offer_content},
        target_pipeline=state["target_pipeline"]
    )
    
    # Elena może zgłosić problem z ofertą
    if "problem z ofertą" in result.content.lower() or "offer issue" in result.content.lower():
        print("   ⚠️ Elena zgłasza problem z ofertą - feedback loop")
        return {
            **state,
            "funnel_output": {
                "agent": "elena",
                "content": result.content,
                "status": "blocked",
                "revision_notes": "Oferta wymaga poprawy",
                "timestamp": result.timestamp
            },
            "current_stage": "elena",
            "next_stage": "marcus",  # Feedback loop!
            "feedback_to": "marcus",
            "feedback_from": "elena",
            "feedback_content": "Elena zauważyła problem: " + result.content[:500]
        }
    
    output: AgentOutput = {
        "agent": "elena",
        "content": result.content,
        "status": "success",
        "revision_notes": None,
        "timestamp": result.timestamp
    }
    
    return {
        **state,
        "funnel_output": output,
        "current_stage": "elena",
        "next_stage": "parallel_execution",  # Kai + David równolegle
        "completed_stages": state["completed_stages"] + ["elena"]
    }


def parallel_kai_david(state: ProjectState) -> ProjectState:
    """Równoległe wykonanie Kai i Davida."""
    print(f"\n🎯 [{state['project_id']}] Kai i David pracują równolegle...")
    
    # W prawdziwej implementacji - async/parallel execution
    # Na razie - sekwencyjnie dla prostoty
    
    # Kai (stub)
    kai_output: AgentOutput = {
        "agent": "kai",
        "content": f"Landing page dla {state['project_name']}...",
        "status": "success",
        "timestamp": "2024-..."
    }
    
    # David (stub)
    david_output: AgentOutput = {
        "agent": "david",
        "content": f"ABM campaign dla {state['project_name']}...",
        "status": "success",
        "timestamp": "2024-..."
    }
    
    return {
        **state,
        "copy_output": kai_output,
        "abm_output": david_output,
        "current_stage": "parallel_kai_david",
        "next_stage": "sofia",
        "completed_stages": state["completed_stages"] + ["kai", "david"]
    }


def sofia_node(state: ProjectState) -> ProjectState:
    """Node dla Sofii - content strategy."""
    print(f"\n🎯 [{state['project_id']}] Sofia planuje content...")
    
    # Sofia jako ostatnia - kończy projekt
    output: AgentOutput = {
        "agent": "sofia",
        "content": f"Content strategy dla {state['project_name']}...",
        "status": "success",
        "timestamp": "2024-..."
    }
    
    # Generuj podsumowanie
    summary = generate_summary(state)
    
    return {
        **state,
        "content_output": output,
        "current_stage": "complete",
        "next_stage": "end",
        "completed_stages": state["completed_stages"] + ["sofia"],
        "project_complete": True,
        "final_summary": summary,
        "completed_at": "2024-..."
    }


def generate_summary(state: ProjectState) -> str:
    """Generuj podsumowanie projektu."""
    stages = state["completed_stages"]
    
    summary = f"""
# Podsumowanie Projektu: {state['project_name']}

## Wykonane etapy:
{chr(10).join([f"- ✅ {s.capitalize()}" for s in stages])}

## Outputy:
"""
    if state["offer_output"]:
        summary += f"\n### Oferta (Marcus)\n{state['offer_output']['content'][:500]}...\n"
    if state["funnel_output"]:
        summary += f"\n### Lejek (Elena)\n{state['funnel_output']['content'][:300]}...\n"
    
    summary += f"""
## Metryki:
- Czas wykonania: [TODO]
- Quality gates passed: {sum(state['quality_checks'].values())}/{len(state['quality_checks'])}
- Feedback loops: {len(state['revision_requests'])}

## Następne kroki:
1. Review finalnych outputów
2. Zatwierdzenie przez Head of Growth
3. Implementation
"""
    return summary
```

### Krok 3: Budowa Grafu

**src/v3/workflow.py:**
```python
"""
LangGraph workflow dla Rady AI.
Definiuje graf z conditional edges i feedback loop'ami.
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from .state import ProjectState
from .nodes import (
    marcus_node,
    quality_gate_offer,
    elena_node,
    parallel_kai_david,
    sofia_node
)


def create_council_workflow(checkpointer=None):
    """
    Stwórz workflow grafu Rady AI.
    
    Returns:
        Compiled workflow graph
    """
    
    # Inicjalizacja grafu
    workflow = StateGraph(ProjectState)
    
    # Dodaj node'y
    workflow.add_node("marcus", marcus_node)
    workflow.add_node("quality_gate_offer", quality_gate_offer)
    workflow.add_node("elena", elena_node)
    workflow.add_node("parallel_kai_david", parallel_kai_david)
    workflow.add_node("sofia", sofia_node)
    
    # Entry point
    workflow.set_entry_point("marcus")
    
    # Edges z Marcusa
    workflow.add_edge("marcus", "quality_gate_offer")
    
    # Conditional edge z quality gate
    def route_after_quality_gate(state: ProjectState):
        """Zdecyduj co zrobić po quality gate."""
        if state.get("feedback_to") == "marcus":
            return "marcus"  # Feedback loop!
        return "elena"
    
    workflow.add_conditional_edges(
        "quality_gate_offer",
        route_after_quality_gate,
        {
            "marcus": "marcus",  # Feedback loop
            "elena": "elena"
        }
    )
    
    # Edges z Eleny
    def route_after_elena(state: ProjectState):
        """Zdecyduj co po Elenie."""
        if state.get("feedback_to") == "marcus":
            return "marcus"  # Elena zgłosiła problem z ofertą
        return "parallel"
    
    workflow.add_conditional_edges(
        "elena",
        route_after_elena,
        {
            "marcus": "marcus",  # Feedback loop
            "parallel": "parallel_kai_david"
        }
    )
    
    # Edges z parallel execution
    workflow.add_edge("parallel_kai_david", "sofia")
    
    # End
    workflow.add_edge("sofia", END)
    
    # Kompilacja z checkpointerem (persistencja)
    if checkpointer:
        return workflow.compile(checkpointer=checkpointer)
    
    return workflow.compile()


# Singleton
_workflow_instance = None

def get_workflow(persist_db: str = "./workflow_state.db"):
    """Get or create workflow instance z persistencją."""
    global _workflow_instance
    if _workflow_instance is None:
        checkpointer = SqliteSaver(persist_db)
        _workflow_instance = create_council_workflow(checkpointer)
    return _workflow_instance
```

### Krok 4: Orchestrator v3

**src/v3/orchestrator.py:**
```python
#!/usr/bin/env python3
"""
Rada AI Orchestrator v3
LangGraph-based z feedback loop'ami i auto-improvement.
"""

import argparse
from typing import Dict

from dotenv import load_dotenv

from .workflow import get_workflow
from .state import create_initial_state


load_dotenv()


class RadaAIOrchestratorV3:
    """
    Orchestrator v3 - autonomiczna Rada.
    
    Kluczowe cechy:
    - Feedback loop'y między agentami
    - Quality gates na każdym etapie
    - Persistencja stanu (można wznowić)
    - Auto-routing w zależności od sytuacji
    """
    
    def __init__(self, persist_db: str = "./workflow_state.db"):
        print("🚀 Inicjalizacja Rady AI v3 (LangGraph)...")
        self.workflow = get_workflow(persist_db)
        print("   ✅ Workflow załadowany")
    
    def run_project(
        self,
        project_name: str,
        project_type: str,
        target_segment: str = "",
        target_pipeline: int = 200000
    ) -> Dict:
        """
        Uruchom projekt przez workflow grafu.
        
        Args:
            project_name: Nazwa projektu
            project_type: CORE, AI, lub BUNDLE
            target_segment: Opcjonalny target
            target_pipeline: Target w PLN
            
        Returns:
            Final state projektu
        """
        print(f"\n{'='*60}")
        print(f"🎯 NOWY PROJEKT: {project_name}")
        print(f"📊 Type: {project_type}")
        print(f"{'='*60}\n")
        
        # Utwórz początkowy stan
        initial_state = create_initial_state(
            project_name=project_name,
            project_type=project_type,
            target_segment=target_segment,
            target_pipeline=target_pipeline
        )
        
        # Uruchom workflow
        # config z thread_id pozwala na śledzenie i wznawianie
        config = {"configurable": {"thread_id": initial_state["project_id"]}}
        
        final_state = self.workflow.invoke(initial_state, config)
        
        # Wyświetl podsumowanie
        self._print_summary(final_state)
        
        return final_state
    
    def resume_project(self, project_id: str):
        """Wznów przerwany projekt."""
        config = {"configurable": {"thread_id": project_id}}
        # TODO: Pobierz stan z DB i wznów
        pass
    
    def get_project_history(self, project_id: str):
        """Pobierz historię projektu."""
        # TODO: Pobierz z SQLite
        pass
    
    def _print_summary(self, state: Dict):
        """Wydrukuj podsumowanie."""
        print(f"\n{'='*60}")
        print("✅ PROJEKT ZAKOŃCZONY")
        print(f"{'='*60}\n")
        
        print(f"Project ID: {state['project_id']}")
        print(f"Etapów wykonanych: {len(state['completed_stages'])}")
        print(f"Feedback loops: {len(state['revision_requests'])}")
        print(f"Quality gates: {sum(state['quality_checks'].values())}/{len(state['quality_checks'])} passed")
        
        if state.get("final_summary"):
            print(f"\n{state['final_summary'][:1000]}...")


def main():
    parser = argparse.ArgumentParser(description="Rada AI Orchestrator v3")
    parser.add_argument("--project", required=True, help="Nazwa projektu")
    parser.add_argument("--type", choices=["CORE", "AI", "BUNDLE"], required=True)
    parser.add_argument("--segment", default="", help="Target segment")
    parser.add_argument("--pipeline", type=int, default=200000)
    
    args = parser.parse_args()
    
    rada = RadaAIOrchestratorV3()
    
    result = rada.run_project(
        project_name=args.project,
        project_type=args.type,
        target_segment=args.segment,
        target_pipeline=args.pipeline
    )
    
    print(f"\n💾 Projekt zapisany jako: {result['project_id']}")


if __name__ == "__main__":
    main()
```

---

## 🧠 Collaborative Deliberation

**src/v3/deliberation.py:**
```python
"""
System "spotkań rady" - gdy agenci wspólnie rozwiązują problem.
"""

from typing import List, Dict
from dataclasses import dataclass


@dataclass
class DeliberationTopic:
    """Temat do dyskusji rady."""
    topic: str
    context: str
    options: List[str]
    deadline: str


class CouncilMeeting:
    """
    Symulacja spotkania Rady AI.
    Agenci prezentują opcje, dyskutują, głosują.
    """
    
    def __init__(self, agents: Dict):
        self.agents = agents
    
    def deliberate(self, topic: DeliberationTopic) -> Dict:
        """
        Przeprowadź deliberację na dany temat.
        
        Returns:
            Decyzja z uzasadnieniem
        """
        print(f"\n🏛️ SPOTKANIE RADY: {topic.topic}")
        print(f"Context: {topic.context[:200]}...")
        print(f"\nOpcje do rozważenia:")
        for i, opt in enumerate(topic.options, 1):
            print(f"  {i}. {opt}")
        
        # Każdy agent prezentuje opinię
        opinions = {}
        for name, agent in self.agents.items():
            opinion = agent.run(
                f"""
Spotkanie Rady AI - temat: {topic.topic}

Context: {topic.context}

Opcje: {topic.options}

Jako {name}, która opcja jest najlepsza i dlaczego?
Daj konkretną rekomendację.
                """
            )
            opinions[name] = opinion.content
            print(f"\n💬 {name}: {opinion.content[:300]}...")
        
        # Głosowanie (supervisor lub konsensus)
        votes = self._count_votes(opinions, topic.options)
        winner = max(votes, key=votes.get)
        
        return {
            "topic": topic.topic,
            "opinions": opinions,
            "votes": votes,
            "decision": winner,
            "confidence": votes[winner] / len(self.agents)
        }
    
    def _count_votes(self, opinions: Dict, options: List) -> Dict:
        """Policz głosy (heurystyka - szukaj wzmianki opcji)."""
        votes = {opt: 0 for opt in options}
        
        for agent_opinion in opinions.values():
            for opt in options:
                if opt.lower() in agent_opinion.lower():
                    votes[opt] += 1
                    break
        
        return votes


# Użycie:
# meeting = CouncilMeeting(agents={"marcus": marcus, "elena": elena, ...})
# result = meeting.deliberate(DeliberationTopic(
#     topic="Which pricing model for new AI offer?",
#     context="Client wants Sovereign AI but budget unclear",
#     options=["Fixed price", "T&M with cap", "Outcome-based"],
#     deadline="end of week"
# ))
```

---

## ✅ Checkpoint - Faza 3 Ukończona Gdy:

- [ ] Workflow działa jako graf (nie liniowo)
- [ ] Quality gates automatycznie weryfikują outputy
- [ ] Feedback loop'y działają (np. Elena → Marcus)
- [ ] "Spotkania rady" generują decyzje
- [ ] Agenci uczą się z wyników projektów
- [ ] Można wznawiać przerwane projekty

---

**Następny krok:** [Faza 4 - Enterprise](./PHASE_4_ENTERPRISE.md)

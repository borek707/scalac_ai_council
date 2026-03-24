# Architektura Rady AI v2+

## Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              UŻYTKOWNIK                                      │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │        INTERFEJSY         │
                    │  CLI | API | Web | Slack  │
                    └─────────────┬─────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────────────────┐
│                           ORCHESTRATOR                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   v1.0      │  │   v2.0      │  │   v2.5      │  │   v3.0      │        │
│  │  (Static)   │  │  (Memory)   │  │  (Tools)    │  │  (Graph)    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐        ┌───────────────┐        ┌───────────────┐
│    PAMIĘĆ     │        │   NARZĘDZIA   │        │   WORKFLOW    │
│  ┌─────────┐  │        │  ┌─────────┐  │        │  ┌─────────┐  │
│  │ Chroma  │  │        │  │SerpAPI  │  │        │  │LangGraph│  │
│  │ Pinecone│  │        │  │DataForSE│  │        │  │  Redis  │  │
│  └─────────┘  │        │  │Apollo.io│  │        │  └─────────┘  │
└───────────────┘        │  └─────────┘  │        └───────────────┘
                         └───────────────┘
        ┌─────────────────────────┬─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐        ┌───────────────┐        ┌───────────────┐
│    AGENCI     │◄──────►│     LLM       │◄──────►│   DANE WEJ.   │
│  ┌─────────┐  │        │  ┌─────────┐  │        │  ┌─────────┐  │
│  │ Marcus  │  │        │  │ GPT-4   │  │        │  │Prompts  │  │
│  │ Elena   │  │        │  │Claude   │  │        │  │Case     │  │
│  │  Kai    │  │        │  │Local    │  │        │  │Benchmark│  │
│  │ Sofia   │  │        │  └─────────┘  │        │  └─────────┘  │
│  │ David   │  │        └───────────────┘        └───────────────┘
│  └─────────┘  │
└───────────────┘
```

---

## Warstwy Architektury

### 1. Interfejsy (Interfaces Layer)

```
CLI (v1-v2)          API (v3-v4)           Web Dashboard (v4)
     │                     │                        │
     ├─ orchestrator.py    ├─ FastAPI              ├─ React
     ├─ Kimi integration   ├─ REST endpoints       ├─ WebSocket
     └─ Local exec         └─ Webhooks             └─ Real-time
```

### 2. Orchestratory (Orchestration Layer)

| Wersja | Technologia | Cechy |
|--------|-------------|-------|
| **v1.0** | Python class | Sekwencyjny, statyczny |
| **v2.0** | Python + Chroma | + Pamięć długoterminowa |
| **v2.5** | LangChain | + Tools |
| **v3.0** | LangGraph | + Feedback loops, graph-based |
| **v4.0** | Kubernetes | + Microservices, auto-scale |

### 3. Agenci (Agent Layer)

Każdy agent ma:
```
┌───────────────────────────────────────┐
│            Agent (np. Marcus)         │
│  ┌─────────────┐  ┌─────────────┐    │
│  │   Memory    │  │    Tools    │    │
│  │  (VectorDB) │  │  (Research) │    │
│  └─────────────┘  └─────────────┘    │
│  ┌─────────────┐  ┌─────────────┐    │
│  │    LLM      │  │   Config    │    │
│  │   (GPT-4)   │  │  (Prompts)  │    │
│  └─────────────┘  └─────────────┘    │
└───────────────────────────────────────┘
```

### 4. Pamięć (Memory Layer)

```
Short-term (Session)          Long-term (Persistent)
┌─────────────────┐          ┌───────────────────────┐
│ Session History │          │  Vector DB            │
│ (in-memory)     │          │  • Case studies       │
│ • Chat history  │          │  • Project outcomes   │
│ • Current task  │          │  • Learnings          │
└─────────────────┘          │  • Embeddings         │
                             └───────────────────────┘
```

### 5. Narzędzia (Tools Layer)

| Kategoria | Narzędzia | Agent |
|-----------|-----------|-------|
| **Research** | SerpAPI, Scraping | Marcus, Sofia |
| **SEO** | DataForSEO, Ahrefs | Kai, Sofia |
| **Analytics** | Benchmarks, Calculators | Elena |
| **Lead Gen** | Apollo, Hunter, Proxycurl | David |
| **Enrichment** | Clearbit, ZoomInfo | David |

---

## Przepływ Danych

### Standardowy Projekt (v2.5)

```
User Request
     │
     ▼
┌────────────────────────────────────────────────────────────────────┐
│ 1. ORCHESTRATOR                                                    │
│    • Utwórz project_id                                             │
│    • Inicjalizuj state                                             │
└────────────────────────────────┬───────────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────┐
│ 2. MARCUS (Offer)                                                  │
│    ┌────────────────────────────────────────────────────────┐     │
│    │ a. Search memory (case studies)                        │     │
│    │ b. Research competitors (SerpAPI)                      │     │
│    │ c. Research trends (SerpAPI)                           │     │
│    │ d. Calculate ROI (tool)                                │     │
│    │ e. Generate offer (LLM)                                │     │
│    └────────────────────────────────────────────────────────┘     │
└────────────────────────────────┬───────────────────────────────────┘
                                 │ Offer Package
                                 ▼
┌────────────────────────────────────────────────────────────────────┐
│ 3. ELENA (Funnel)                                                  │
│    ┌────────────────────────────────────────────────────────┐     │
│    │ a. Load benchmarks (tool)                              │     │
│    │ b. Calculate funnel metrics (tool)                   │     │
│    │ c. Build funnel (LLM)                                  │     │
│    │ d. Detect issues → Feedback loop?                      │     │
│    └────────────────────────────────────────────────────────┘     │
└────────────────────────────────┬───────────────────────────────────┘
                                 │ Funnel Design
                                 ▼
┌────────────────────────────────────────────────────────────────────┐
│ 4. PARALLEL EXECUTION                                              │
│    ┌──────────────┐              ┌──────────────┐                 │
│    │ KAI (Copy)   │              │ DAVID (ABM)  │                 │
│    │ • SEO research              │ • Lead enrichment             │
│    │ • Landing page              │ • ABM strategy                │
│    └──────────────┘              └──────────────┘                 │
└────────────────────────────────┬───────────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────┐
│ 5. SOFIA (Content)                                                 │
│    • Content gap analysis                                          │
│    • Editorial calendar                                            │
│    • SEO strategy                                                  │
└────────────────────────────────┬───────────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────┐
│ 6. FINALIZE                                                        │
│    • Save to DB                                                    │
│    • Generate summary                                              │
│    • Export (JSON/Markdown)                                        │
└────────────────────────────────┬───────────────────────────────────┘
                                 │
                                 ▼
                           User Output
```

### Feedback Loop (v3.0)

```
Marcus creates offer
        │
        ▼
   Quality Gate
        │
   ┌────┴────┐
   │         │
 PASS     FAIL
   │         │
   ▼         ▼
 Elena    Marcus (revise)
   │         │
   │         └──────┐
   │                │
   ▼                │
Detects issue      │
   │                │
   └────────────────┘
   Feedback to Marcus
```

---

## Modele Danych

### Project
```python
{
    "project_id": "uuid",
    "name": "Team Extension Fintech",
    "type": "CORE",
    "status": "in_progress",
    "stages": {
        "marcus": {"status": "completed", "output": "...", "duration_s": 45},
        "elena": {"status": "in_progress", ...},
        "kai": {"status": "pending", ...},
        ...
    },
    "feedback_loops": [
        {"from": "elena", "to": "marcus", "reason": "pricing_too_high"}
    ],
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:05:00Z"
}
```

### Memory Entry
```python
{
    "id": "uuid",
    "type": "case_study" | "project_outcome" | "learning",
    "content": "text",
    "embedding": [0.1, 0.2, ...],
    "metadata": {
        "industry": "fintech",
        "service": "team_extension",
        "result": "success",
        "agent": "marcus"
    },
    "created_at": "2024-01-01"
}
```

---

## Skalowalność

### Horyzontalna (v4.0)

```
                    Load Balancer
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
   ┌─────────┐      ┌─────────┐      ┌─────────┐
   │Marcus-1 │      │Marcus-2 │      │Marcus-3 │
   │(Active) │      │(Active) │      │(Standby)│
   └─────────┘      └─────────┘      └─────────┘
```

### Wertykalna

```
Small Project          Medium Project         Large Project
├─ 1 agent             ├─ 3 agents            ├─ 5 agents
├─ Basic memory        ├─ Full memory         ├─ Full memory + research
├─ No tools            ├─ Key tools           ├─ All tools
└─ ~$0.50              └─ ~$2.00              └─ ~$5.00
```

---

## Bezpieczeństwo

### Authentication
- API Keys dla external API
- JWT dla internal services
- RBAC (Role-Based Access Control)

### Data Privacy
- PII redaction w pamięci
- Encryption at rest (DB)
- Encryption in transit (TLS)

### Rate Limiting
- Per-user: 100 req/min
- Per-project: 10 concurrent
- Per-agent: queue-based

---

## Observability

### Metrics
```
agent_requests_total{agent="marcus", status="success"}
agent_request_duration_seconds{agent="marcus", quantile="0.95"}
queue_length{agent="marcus", priority="high"}
memory_hits_total{type="case_study"}
tool_calls_total{tool="search_competitor"}
```

### Logging
```json
{
    "timestamp": "2024-01-15T10:00:00Z",
    "level": "INFO",
    "agent": "marcus",
    "project_id": "uuid",
    "event": "offer_created",
    "duration_ms": 4500,
    "tools_used": ["search_competitor", "calculate_roi"],
    "memory_hits": 3
}
```

### Tracing
- OpenTelemetry
- Distributed tracing między serwisami
- Jaeger/Prometheus integration

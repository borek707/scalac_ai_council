# Log Decyzji Architektonicznych

## ADR-001: Wybór Vector DB

**Status:** Accepted  
**Data:** 2024-XX-XX  
**Kontekst:** Potrzebujemy pamięci długoterminowej dla agentów

### Opcje
1. **ChromaDB** - Lokalny, darmowy, prosty
2. **Pinecone** - Managed, płatny, skalowalny
3. **Weaviate** - Self-hosted, złożony
4. **PostgreSQL + pgvector** - Istniejąca infra

### Decyzja
**ChromaDB dla Fazy 1-2, Pinecone dla Fazy 4**

### Uzasadnienie
- ChromaDB wymaga zero setup dla developmentu
- Łatwa migracja do Pinecone w Fazie 4
- pgvector rozważymy jeśli mamy już PostgreSQL

### Konsekwencje
- Dodatkowy service w Fazie 4
- Prosty kod dzięki LangChain abstrakcji

---

## ADR-002: LangChain vs Native OpenAI

**Status:** Accepted  
**Kontekst:** Framework do LLM integration

### Opcje
1. **LangChain** - Abstrakcja, tools, memory
2. **Native OpenAI** - Bezpośredni dostęp, prostszy
3. **LlamaIndex** - Focus na RAG

### Decyzja
**LangChain dla Fazy 2+, Native dla Fazy 1 (opcjonalnie)**

### Uzasadnienie
- LangChain daje Tools i Memory out-of-the-box
- Łatwa zamiana modelu (GPT-4 → Claude → Local)
- Community i dokumentacja

### Konsekwencje
- Dodatkowa zależność
- Abstrakcja może utrudniać debugowanie

---

## ADR-003: LangGraph vs Prefect/Airflow

**Status:** Accepted  
**Kontekst:** Workflow engine dla Fazy 3

### Opcje
1. **LangGraph** - Zbudowany dla agentów, conditional edges
2. **Prefect** - Data pipelines, nie agent-specific
3. **Temporal** - Durable execution, heavy
4. **CrewAI** - Multi-agent, mniej kontroli

### Decyzja
**LangGraph dla Fazy 3**

### Uzasadnienie
- Zaprojektowany dla agent workflows
- Conditional edges dla feedback loop'ów
- Integracja z LangChain
- PERSISTENCE! Można wznawiać projekty

### Konsekwencje
- Nowa biblioteka (może być zmiany API)
- Wymaga SQLite/Postgres dla persistence

---

## ADR-004: Monolit vs Microservices

**Status:** Accepted  
**Kontekst:** Architektura Faza 4

### Opcje
1. **Monolit** - Prostszy, wszystko razem
2. **Microservices** - Skalowalność, złożoność
3. **Modular Monolit** - Pośrednie rozwiązanie

### Decyzja
**Modular Monolit → Microservices**

### Uzasadnienie
- Fazy 1-3: Modular monolit (łatwiejszy development)
- Faza 4: Rozbijamy na serwisy gdy potrzebna skalowalność
- Każdy agent jako oddzielny service w K8s

### Konsekwencje
- Dwa razy praca (refactor w Fazie 4)
- Ale mamy działający system wcześniej

---

## ADR-005: Redis vs RabbitMQ

**Status:** Accepted  
**Kontekst:** Message Queue dla async processing

### Opcje
1. **Redis** - Prosty, multi-purpose, mniej durable
2. **RabbitMQ** - Full-featured, bardziej złożony
3. **AWS SQS** - Managed, vendor lock-in

### Decyzja
**Redis dla Fazy 2-3, RabbitMQ dla Fazy 4**

### Uzasadnienie
- Redis już używany dla caching/session
- Prosta priority queue
- RabbitMQ gdy potrzebne advanced routing

### Konsekwencje
- Redis queue może stracić dane przy crash
- Dla critical workloads: RabbitMQ lub persistence w DB

---

## ADR-006: Self-hosted vs Cloud

**Status:** Accepted  
**Kontekst:** Gdzie hostować Fazę 4

### Opcje
1. **AWS EKS** - Managed K8s, drogie
2. **Google GKE** - Dobre dla AI/ML workloads
3. **Self-hosted K3s** - Tanie, wymaga maintenance
4. **Fly.io/Render** - Simpler, mniej kontroli

### Decyzja
**EKS/GKE dla produkcji, Docker Compose dla developmentu**

### Uzasadnienie
- Managed K8s = mniej operational burden
- Auto-scaling out-of-the-box
- Integracja z innymi usługami (RDS, S3)

### Konsekwencje
- ~$500-1000/miesiąc dla produkcji
- Vendor lock-in (ale K8s jest portable)

---

## ADR-007: Płatne API vs Self-hosted Models

**Status:** Accepted  
**Kontekst:** LLM do użycia

### Opcje
1. **OpenAI GPT-4** - Najlepsza jakość, drogie
2. **Anthropic Claude** - Dobre, konkurencyjne ceny
3. **Local LLM (Llama 2)** - Darmowe, wymaga GPU
4. **Mix** - GPT-4 dla complex, local dla simple

### Decyzja
**OpenAI GPT-4 dla startu, mix w przyszłości**

### Uzasadnienie
- GPT-4 ma najlepsze tool calling
- Szybszy development
- Dla Fazy 4: rozważymy fine-tuned lub local

### Konsekwencje
- ~$0.50-5.00 per projekt
- Zależność od OpenAI
- Łatwa zamiana dzięki LangChain

---

## ADR-008: Synchronous vs Async API

**Status:** Accepted  
**Kontekst:** Jak expose'ować API

### Opcje
1. **Sync (REST)** - Prostsze, timeout problem
2. **Async (WebSocket + Queue)** - Complex, scalable
3. **Hybrid** - Sync dla simple, async dla complex

### Decyzja
**Hybrid: Sync z polling dla większości, WebSocket dla real-time**

### Uzasadnienie
- 90% projektów kończy się w < 60s (sync OK)
- Dla długich: async z webhook/polling
- WebSocket dla dashboard real-time

### Konsekwencje
- Dwa modele do utrzymania
- Bardziej complex client code

---

## ADR-009: TypeScript vs Python dla Dashboard

**Status:** Accepted  
**Kontekst:** Frontend dla Fazy 4

### Opcje
1. **React + TypeScript** - Standard, ecosystem
2. **Python (Streamlit)** - Szybkie prototypy, mniej elastyczne
3. **Vue.js** - Alternatywa dla React

### Decyzja
**React + TypeScript**

### Uzasadnienie
- Team Scalac prawdopodobnie zna React
- Dużo komponentów do wizualizacji (recharts)
- Type safety

### Konsekwencje
- Dodatkowy stack technologiczny
- Potrzebny frontend developer lub nauka

---

## ADR-010: Observability Stack

**Status:** Accepted  
**Kontekst:** Monitoring Fazy 4

### Opcje
1. **Prometheus + Grafana** - Open source, standard
2. **Datadog** - Managed, drogie
3. **New Relic** - Managed, drogie
4. **Grafana Cloud** - Pośrednie rozwiązanie

### Decyzja
**Prometheus + Grafana dla self-hosted, Grafana Cloud dla managed**

### Uzasadnienie
- Standard w K8s ecosystem
- Darmowy (self-hosted)
- Grafana Cloud = mniej maintenance

### Konsekwencje
- Self-hosted = operational burden
- Cloud = koszt ~$50-100/miesiąc

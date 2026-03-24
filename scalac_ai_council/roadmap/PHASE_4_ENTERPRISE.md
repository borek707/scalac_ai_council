# Faza 4: Enterprise Microservices

**Timeline:** 2-3 miesiące  
**Impact:** Skalowalność + Niezawodność | **Trudność:** Bardzo wysoka | **Koszt:** ~$1000/miesiąc

---

## 🎯 Cel

System produkcyjny gotowy do skali:
- Microservices z Kubernetes
- Message Queue dla async processing
- REST API + Dashboard
- Monitoring i alerting
- Multi-tenant (obsługa wielu klientów)

---

## 🏗️ Architektura Enterprise

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              API Gateway                                 │
│                    (Kong / Nginx / AWS API Gateway)                     │
│                 Rate Limiting, Auth, Routing, Caching                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐         ┌─────────────────┐         ┌───────────────┐
│   REST API    │         │   WebSocket     │         │   Webhook     │
│   (FastAPI)   │         │   (Real-time)   │         │   Handlers    │
└───────┬───────┘         └─────────────────┘         └───────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Kubernetes Cluster                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Marcus   │  │  Elena   │  │   Kai    │  │  Sofia   │  │  David   │ │
│  │ Service  │  │ Service  │  │ Service  │  │ Service  │  │ Service  │ │
│  │ (3 repl) │  │ (3 repl) │  │ (2 repl) │  │ (2 repl) │  │ (2 repl) │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘ │
│       │             │             │             │             │       │
│       └─────────────┴─────────────┴─────────────┴─────────────┘       │
│                                   │                                    │
│                                   ▼                                    │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │              Redis Cluster (Message Queue)                   │    │
│  │     ┌──────────┐  ┌──────────┐  ┌──────────┐                 │    │
│  │     │  Queue   │  │  Queue   │  │  Queue   │                 │    │
│  │     │ Marcusa  │  │  Eleny   │  │Priority  │                 │    │
│  │     └──────────┘  └──────────┘  └──────────┘                 │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                   │                                    │
│                                   ▼                                    │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │         PostgreSQL Cluster (State + Analytics)               │    │
│  │     ┌──────────┐  ┌──────────┐  ┌──────────┐                 │    │
│  │     │ Projects │  │  Agents  │  │ Analytics│                 │    │
│  │     └──────────┘  └──────────┘  └──────────┘                 │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                   │                                    │
│                                   ▼                                    │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │              Pinecone/Weaviate (Vector DB)                   │    │
│  │           Case studies, Memory, Embeddings                   │    │
│  └──────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Observability Stack                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │ Prometheus│  │  Grafana │  │   Loki   │  │  Jaeger  │                 │
│  │(Metrics) │  │(Dashboard│  │  (Logs)  │  │ (Traces) │                 │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Stack Technologiczny

| Warstwa | Technologia | Koszt/mies |
|---------|-------------|-----------|
| **Orchestration** | Kubernetes (EKS/GKE) | $300-500 |
| **API Gateway** | Kong / AWS API Gateway | $100 |
| **Message Queue** | Redis Cluster | $100 |
| **Database** | PostgreSQL (RDS/Cloud SQL) | $100 |
| **Vector DB** | Pinecone / Weaviate | $100 |
| **Monitoring** | Prometheus + Grafana | $50 |
| **LLM** | OpenAI API | $200-500 |
| **Razem** | | **~$1000-1500** |

---

## 🔧 Implementacja

### Krok 1: Service Mesh

**services/marcus/Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App
COPY src/ ./src/
COPY config/ ./config/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**services/marcus/src/main.py:**
```python
"""
Marcus Service - FastAPI + Redis Queue.
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import redis
import json
import os

from .agent import MarcusAgent
from .config import Settings

app = FastAPI(title="Marcus Service", version="2.0.0")
settings = Settings()

# Redis dla queue
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)

# Agent
marcus = MarcusAgent()


class CreateOfferRequest(BaseModel):
    project_id: str
    project_name: str
    project_type: str
    target_segment: Optional[str] = ""
    priority: str = "normal"  # low, normal, high, urgent


class OfferResponse(BaseModel):
    project_id: str
    status: str
    offer_content: Optional[str] = None
    error: Optional[str] = None


@app.get("/health")
async def health_check():
    """Health check dla K8s."""
    return {
        "status": "healthy",
        "service": "marcus",
        "version": "2.0.0",
        "redis_connected": redis_client.ping()
    }


@app.post("/offer", response_model=OfferResponse)
async def create_offer(
    request: CreateOfferRequest,
    background_tasks: BackgroundTasks
):
    """
    Stwórz ofertę - async via Redis Queue.
    
    Dla urgent requests - synchronicznie.
    """
    
    if request.priority == "urgent":
        # Synchronicznie dla urgent
        try:
            result = marcus.create_offer(
                project_name=request.project_name,
                project_type=request.project_type,
                target_segment=request.target_segment
            )
            return OfferResponse(
                project_id=request.project_id,
                status="completed",
                offer_content=result.content
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    else:
        # Async via queue
        job_data = {
            "project_id": request.project_id,
            "project_name": request.project_name,
            "project_type": request.project_type,
            "target_segment": request.target_segment,
            "priority": request.priority
        }
        
        # Dodaj do queue
        queue_name = f"marcus:{request.priority}"
        redis_client.lpush(queue_name, json.dumps(job_data))
        
        return OfferResponse(
            project_id=request.project_id,
            status="queued"
        )


@app.get("/offer/{project_id}", response_model=OfferResponse)
async def get_offer(project_id: str):
    """Pobierz status/result oferty."""
    # Sprawdź w Redis/DB
    result = redis_client.get(f"result:{project_id}")
    
    if result:
        data = json.loads(result)
        return OfferResponse(**data)
    
    return OfferResponse(
        project_id=project_id,
        status="processing"
    )


@app.get("/queue/status")
async def queue_status():
    """Status kolejki dla monitoringu."""
    return {
        "urgent": redis_client.llen("marcus:urgent"),
        "high": redis_client.llen("marcus:high"),
        "normal": redis_client.llen("marcus:normal"),
        "low": redis_client.llen("marcus:low")
    }


# Worker (oddzielny proces)
@app.on_event("startup")
async def start_worker():
    """Start background worker jeśli WORKER=true."""
    if os.getenv("WORKER", "false").lower() == "true":
        import asyncio
        asyncio.create_task(worker_loop())


async def worker_loop():
    """Worker przetwarzający queue."""
    while True:
        # Priority queue
        for priority in ["urgent", "high", "normal", "low"]:
            queue_name = f"marcus:{priority}"
            
            # Blocking pop z timeout
            job = redis_client.brpop(queue_name, timeout=1)
            
            if job:
                _, job_data = job
                data = json.loads(job_data)
                
                try:
                    # Przetwórz
                    result = marcus.create_offer(
                        project_name=data["project_name"],
                        project_type=data["project_type"],
                        target_segment=data.get("target_segment", "")
                    )
                    
                    # Zapisz result
                    redis_client.setex(
                        f"result:{data['project_id']}",
                        86400,  # 24h TTL
                        json.dumps({
                            "project_id": data["project_id"],
                            "status": "completed",
                            "offer_content": result.content
                        })
                    )
                    
                except Exception as e:
                    # Zapisz error
                    redis_client.setex(
                        f"result:{data['project_id']}",
                        86400,
                        json.dumps({
                            "project_id": data["project_id"],
                            "status": "error",
                            "error": str(e)
                        })
                    )
        
        await asyncio.sleep(0.1)
```

### Krok 2: Kubernetes Config

**k8s/marcus-deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: marcus-service
  labels:
    app: marcus
spec:
  replicas: 3
  selector:
    matchLabels:
      app: marcus
  template:
    metadata:
      labels:
        app: marcus
    spec:
      containers:
      - name: marcus
        image: scalac/rada-marcus:v2.0
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_HOST
          value: "redis-cluster"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-secret
              key: api-key
        - name: WORKER
          value: "true"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: marcus-service
spec:
  selector:
    app: marcus
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: marcus-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: marcus-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Pods
    pods:
      metric:
        name: redis_queue_length
      target:
        type: AverageValue
        averageValue: "10"
```

### Krok 3: API Gateway

**k8s/api-gateway.yaml:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rada-gateway
  annotations:
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  rules:
  - host: api.rada-ai.scalac.io
    http:
      paths:
      - path: /v2/marcus
        pathType: Prefix
        backend:
          service:
            name: marcus-service
            port:
              number: 80
      - path: /v2/elena
        pathType: Prefix
        backend:
          service:
            name: elena-service
            port:
              number: 80
      # ... pozostali agenci
```

### Krok 4: Workflow Orchestrator

**services/orchestrator/src/main.py:**
```python
"""
Centralny orchestrator koordynujący usługi.
"""

import asyncio
import httpx
from typing import Dict
from fastapi import FastAPI

app = FastAPI(title="Rada AI Orchestrator")

# Service discovery
SERVICES = {
    "marcus": "http://marcus-service:80",
    "elena": "http://elena-service:80",
    "kai": "http://kai-service:80",
    "sofia": "http://sofia-service:80",
    "david": "http://david-service:80"
}


@app.post("/project")
async def create_project(project_config: Dict):
    """
    Stwórz nowy projekt - orchestrate wszystkie serwisy.
    """
    project_id = generate_project_id()
    
    async with httpx.AsyncClient() as client:
        # Step 1: Marcus (async)
        marcus_response = await client.post(
            f"{SERVICES['marcus']}/offer",
            json={
                "project_id": project_id,
                "project_name": project_config["name"],
                "project_type": project_config["type"],
                "priority": project_config.get("priority", "normal")
            }
        )
        
        if marcus_response.json()["status"] != "queued":
            return {"error": "Failed to queue Marcus"}
        
        # Czekaj na completion (polling lub webhook)
        offer = await wait_for_completion(client, "marcus", project_id)
        
        # Step 2: Elena
        elena_response = await client.post(
            f"{SERVICES['elena']}/funnel",
            json={
                "project_id": project_id,
                "offer": offer,
                "target_pipeline": project_config.get("target_pipeline", 200000)
            }
        )
        
        # Step 3: Parallel Kai + David
        kai_task = client.post(
            f"{SERVICES['kai']}/copy",
            json={"project_id": project_id, "offer": offer}
        )
        david_task = client.post(
            f"{SERVICES['david']}/abm",
            json={"project_id": project_id, "offer": offer}
        )
        
        kai_result, david_result = await asyncio.gather(kai_task, david_task)
        
        # Step 4: Sofia
        sofia_response = await client.post(
            f"{SERVICES['sofia']}/content",
            json={
                "project_id": project_id,
                "funnel": elena_response.json(),
                "copy": kai_result.json()
            }
        )
        
        return {
            "project_id": project_id,
            "status": "completed",
            "stages": {
                "marcus": offer,
                "elena": elena_response.json(),
                "kai": kai_result.json(),
                "david": david_result.json(),
                "sofia": sofia_response.json()
            }
        }


async def wait_for_completion(client: httpx.AsyncClient, service: str, project_id: str, max_wait: int = 300):
    """Czekaj na completion z backoff."""
    for _ in range(max_wait // 5):
        response = await client.get(f"{SERVICES[service]}/offer/{project_id}")
        data = response.json()
        
        if data["status"] == "completed":
            return data["offer_content"]
        elif data["status"] == "error":
            raise Exception(data["error"])
        
        await asyncio.sleep(5)
    
    raise TimeoutError(f"Service {service} did not complete in time")
```

### Krok 5: Dashboard

**dashboard/src/App.tsx:**
```typescript
// React dashboard dla monitoringu Rady AI
import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

interface Project {
  id: string;
  name: string;
  status: 'running' | 'completed' | 'error';
  stage: string;
  progress: number;
}

const Dashboard: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [queueStatus, setQueueStatus] = useState({});

  useEffect(() => {
    // WebSocket do real-time updates
    const ws = new WebSocket('wss://api.rada-ai.scalac.io/ws');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'project_update') {
        setProjects(prev => updateProject(prev, data.project));
      }
    };

    // Polling dla queue status
    const interval = setInterval(async () => {
      const res = await fetch('/api/v2/queue/status');
      setQueueStatus(await res.json());
    }, 5000);

    return () => {
      ws.close();
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="dashboard">
      <h1>Rada AI - Dashboard</h1>
      
      {/* Queue Status */}
      <div className="queue-status">
        <h2>Queue Status</h2>
        <div className="queues">
          {Object.entries(queueStatus).map(([agent, queues]) => (
            <div key={agent} className="agent-queue">
              <h3>{agent}</h3>
              <div className="priority-bars">
                <div className="urgent" style={{width: `${queues.urgent * 10}px`}}>
                  Urgent: {queues.urgent}
                </div>
                <div className="high" style={{width: `${queues.high * 10}px`}}>
                  High: {queues.high}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Active Projects */}
      <div className="projects">
        <h2>Active Projects</h2>
        {projects.map(project => (
          <div key={project.id} className={`project ${project.status}`}>
            <div className="project-header">
              <span className="name">{project.name}</span>
              <span className="stage">{project.stage}</span>
            </div>
            <div className="progress-bar">
              <div className="fill" style={{width: `${project.progress}%`}} />
            </div>
          </div>
        ))}
      </div>

      {/* Metrics */}
      <div className="metrics">
        <h2>Performance Metrics</h2>
        <LineChart width={600} height={300} data={metricsData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="marcus_latency" stroke="#8884d8" />
          <Line type="monotone" dataKey="elena_latency" stroke="#82ca9d" />
        </LineChart>
      </div>
    </div>
  );
};

export default Dashboard;
```

---

## 📊 Monitoring & Alerting

**monitoring/prometheus.yml:**
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'marcus'
    static_configs:
      - targets: ['marcus-service:8000']
    metrics_path: /metrics

  - job_name: 'elena'
    static_configs:
      - targets: ['elena-service:8000']

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - /etc/prometheus/alerts.yml
```

**monitoring/alerts.yml:**
```yaml
groups:
  - name: rada-alerts
    rules:
      - alert: HighQueueLength
        expr: redis_queue_length > 50
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High queue length in {{ $labels.agent }}"
          
      - alert: AgentDown
        expr: up{job=~"marcus|elena|kai"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Agent {{ $labels.job }} is down"
          
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(agent_request_duration_seconds_bucket[5m])) > 30
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency in {{ $labels.agent }}"
```

---

## ✅ Checkpoint - Faza 4 Ukończona Gdy:

- [ ] System działa na Kubernetes
- [ ] Auto-scaling działa (HPA)
- [ ] Queue processing działa stable
- [ ] Dashboard pokazuje real-time status
- [ ] Alerting wysyła powiadomienia
- [ ] 99.9% uptime przez tydzień
- [ ] Obciążenie testowe 100 projektów/h przechodzi

---

## 🎉 Gotowe!

Masz teraz prawdziwy enterprise-grade multi-agent AI system.

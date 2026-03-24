#!/usr/bin/env python3
"""
Skrypt do ładowania case studies Scalac do Vector DB.
Uruchom raz na początku, potem aktualizuj gdy masz nowe case studies.

Usage:
    python scripts/ingest_knowledge.py
    python scripts/ingest_knowledge.py --reset  # Wyczyść i załaduj od nowa
"""

import sys
import os
import argparse

# Dodaj src do path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from v2.memory.vector_store import ScalacMemory


# PRZYKŁADOWE CASE STUDIES - ZASTĄP SWOIMI PRAWDZIWYMI
# TODO: Dodaj wszystkie realne case studies Scalac tutaj
CASE_STUDIES = [
    {
        "title": "Bexio - Fintech Migration to Scala",
        "industry": "fintech",
        "service": "team_extension",
        "content": """
Client: Bexio (Swiss fintech, accounting software)
Challenge: Legacy payroll system in Java, needed rewrite to Scala with zero downtime
Solution: Team of 5 senior Scala developers, gradual migration with feature flags
Timeline: 12 months
Results:
- 2x performance improvement
- Zero downtime migration achieved
- 50% reduction in bug reports
- Client expanded team from 5 to 8 developers

Winning factors:
- Fast onboarding (2 weeks to productivity)
- Deep Scala and Akka expertise
- Experience with fintech compliance requirements
- Proactive communication with client's tech lead

Technologies: Scala, Akka, Kafka, PostgreSQL, Kubernetes
""",
        "results": {
            "team_size": 5,
            "duration_months": 12,
            "performance_improvement": "2x",
            "bug_reduction": "50%"
        },
        "winning_factors": [
            "fast_onboarding",
            "scala_expertise",
            "fintech_compliance",
            "proactive_communication"
        ],
        "pricing_model": "monthly_retainer",
        "rate_per_hour": 80
    },
    {
        "title": "Liga Digital - Healthtech Distributed Systems",
        "industry": "healthtech",
        "service": "project_based",
        "content": """
Client: Liga Digital (Spanish healthtech)
Challenge: Hospital management system couldn't scale to 10x load during COVID
Solution: Complete re-architecture to event sourcing with Akka Cluster
Timeline: 8 months
Results:
- System handles 10x traffic spikes
- 99.99% uptime achieved
- 30% reduction in infrastructure costs
- Successfully passed healthcare compliance audit

Winning factors:
- Distributed systems expertise
- Deep Akka knowledge
- Performance optimization skills
- Understanding of healthcare domain

Technologies: Scala, Akka Cluster, Event Sourcing, Cassandra, Kubernetes
""",
        "results": {
            "team_size": 3,
            "duration_months": 8,
            "scalability_improvement": "10x",
            "uptime": "99.99%",
            "cost_reduction": "30%"
        },
        "winning_factors": [
            "distributed_systems",
            "akka_expertise",
            "performance_optimization",
            "healthcare_domain"
        ],
        "pricing_model": "fixed_price",
        "total_value": 250000
    },
    {
        "title": "Swiss Private Bank - Sovereign AI POC",
        "industry": "banking",
        "service": "ai_consulting",
        "content": """
Client: Swiss Private Bank (name confidential)
Challenge: Wanted RAG for internal documents, but compliance blocked OpenAI
Solution: Sovereign AI architecture - private LLM on-premises, zero data exfiltration
Timeline: 3 months (POC)
Results:
- POC passed compliance audit
- 95% accuracy on internal documents
- Board approved production rollout
- 50+ use cases identified for expansion

Winning factors:
- Sovereign AI expertise
- Banking compliance knowledge
- Production-ready architecture
- Ability to explain AI to non-technical stakeholders

Technologies: Python, Private LLM, Vector DB, RAG pipeline, On-prem Kubernetes
""",
        "results": {
            "duration_months": 3,
            "accuracy": "95%",
            "compliance_status": "passed",
            "expansion_use_cases": 50
        },
        "winning_factors": [
            "sovereign_ai_expertise",
            "banking_compliance",
            "production_architecture",
            "stakeholder_communication"
        ],
        "pricing_model": "fixed_price_poc",
        "poc_value": 50000,
        "expansion_potential": 500000
    },
    {
        "title": "German E-commerce - Scala Team Augmentation",
        "industry": "ecommerce",
        "service": "team_extension",
        "content": """
Client: German e-commerce platform (mid-size)
Challenge: Needed to scale team from 8 to 15 developers in 4 weeks for Black Friday
Solution: Rapid team augmentation with 7 Scala developers
Timeline: Ongoing (initial 6 months)
Results:
- Team scaled in 3 weeks (ahead of deadline)
- Successful Black Friday (zero incidents)
- Client extended contract indefinitely
- 3 developers promoted to team leads

Winning factors:
- Speed of recruitment
- Quality of candidates
- Cultural fit with German team
- Flexibility in engagement model

Technologies: Scala, Play Framework, Kafka, Elasticsearch
""",
        "results": {
            "initial_team_size": 8,
            "target_team_size": 15,
            "time_to_scale_weeks": 3,
            "black_friday_incidents": 0,
            "promotions_to_lead": 3
        },
        "winning_factors": [
            "recruitment_speed",
            "candidate_quality",
            "cultural_fit",
            "engagement_flexibility"
        ],
        "pricing_model": "monthly_retainer",
        "rate_per_hour": 75
    },
    {
        "title": "Adtech Platform - Real-time Bidding System",
        "industry": "adtech",
        "service": "project_based",
        "content": """
Client: European adtech platform
Challenge: Real-time bidding system couldn't handle peak traffic (1M req/s)
Solution: Built new RTB platform from scratch with sub-10ms latency
Timeline: 10 months
Results:
- 1M+ requests per second handled
- <5ms average latency (target was 10ms)
- 40% reduction in infrastructure costs
- Client acquired by major adtech company

Winning factors:
- Low-latency system design
- Akka and actor model expertise
- Performance testing at scale
- Domain knowledge in adtech

Technologies: Scala, Akka, gRPC, Redis, Kubernetes, Prometheus
""",
        "results": {
            "team_size": 4,
            "duration_months": 10,
            "peak_throughput": "1M req/s",
            "avg_latency_ms": 5,
            "target_latency_ms": 10,
            "cost_reduction": "40%"
        },
        "winning_factors": [
            "low_latency_design",
            "akka_expertise",
            "performance_testing",
            "adtech_domain"
        ],
        "pricing_model": "outcome_based",
        "base_value": 400000,
            "performance_bonus": 100000
    }
]


def main():
    parser = argparse.ArgumentParser(description='Ingest Scalac knowledge to Vector DB')
    parser.add_argument('--reset', action='store_true', help='Reset DB and start fresh')
    parser.add_argument('--path', default='./chroma_db', help='Path to ChromaDB')
    args = parser.parse_args()
    
    print("📚 Rada AI - Ingestia Wiedzy")
    print("=" * 50)
    
    # Inicjalizacja pamięci
    memory = ScalacMemory(persist_directory=args.path)
    
    # Sprawdź czy reset
    if args.reset:
        print("⚠️  Resetowanie bazy wiedzy...")
        import shutil
        if os.path.exists(args.path):
            shutil.rmtree(args.path)
            print("   ✅ Baza wyczyszczona")
        memory = ScalacMemory(persist_directory=args.path)
    
    # Sprawdź aktualny stan
    stats = memory.stats()
    print(f"\n📊 Obecny stan bazy: {stats}")
    
    # Dodaj case studies
    print(f"\n➕ Dodawanie {len(CASE_STUDIES)} case studies...")
    memory.add_case_studies(CASE_STUDIES)
    
    # Sprawdź rezultat
    new_stats = memory.stats()
    print(f"\n✅ Gotowe!")
    print(f"   Dokumentów w bazie: {new_stats.get('total_documents', 'N/A')}")
    print(f"   Lokalizacja: {new_stats.get('persist_directory', args.path)}")
    
    # Test wyszukiwania
    print("\n🔍 Test wyszukiwania:")
    
    test_queries = [
        "fintech team extension",
        "sovereign ai banking",
        "healthtech migration",
        "low latency system"
    ]
    
    for query in test_queries:
        results = memory.search_relevant(query, k=2)
        print(f"\n   Query: '{query}'")
        for r in results:
            print(f"      → {r.source} (score: {r.score:.3f})")
    
    print("\n" + "=" * 50)
    print("🎉 Ingestia zakończona sukcesem!")
    print("\nNastępne kroki:")
    print("   1. Uruchom orchestrator: python -m src.v2.orchestrator --help")
    print("   2. Lub programmatically:")
    print("      from src.v2.orchestrator import RadaAIOrchestratorV2")
    print("      rada = RadaAIOrchestratorV2()")


if __name__ == "__main__":
    main()

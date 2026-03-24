# Faza 2: Agenci z Narzędziami (Tools)

**Timeline:** 2-3 tygodnie  
**Impact:** Bardzo wysoki | **Trudność:** Średnia | **Koszt:** ~$250/miesiąc

---

## 🎯 Cel

Agenci mają dostęp do **real-time data** zamiast tylko statycznej wiedzy:
- Marcus sprawdza pricing konkurencji
- Elena pobiera benchmarki konwersji
- Kai researchuje słowa kluczowe
- David enrichuje leady
- Sofia analizuje content gaps

---

## 🏗️ Architektura

```
┌─────────────────────────────────────────────────────────────────┐
│                        Rada AI v2.5                              │
│              (Agenci z narzędziami + pamięć)                    │
└─────────────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
   │ Marcus   │  │  Elena   │  │   Kai    │  │  David   │
   │+ Memory  │  │+ Memory  │  │+ Memory  │  │+ Memory  │
   │+ Tools   │  │+ Tools   │  │+ Tools   │  │+ Tools   │
   └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
   ┌──────────┐     ┌──────────┐     ┌──────────┐
   │  Web     │     │   API    │     │  Scrapers│
   │ Search   │     │Integracje│     │          │
   │(SerpAPI) │     │(LinkedIn)│     │(Pricing) │
   └──────────┘     └──────────┘     └──────────┘
```

---

## 📦 Stack Technologiczny

| Narzędzie | Usługa | Koszt | Do czego |
|-----------|--------|-------|----------|
| Web Search | SerpAPI | $50/mies | Research konkurencji, trendy |
| SEO Data | DataForSEO / Ahrefs API | $100/mies | Keywords, content gaps |
| Lead Enrichment | Apollo.io / Hunter | $50/mies | Lead data, kontakty |
| LinkedIn | Proxycurl | $50/mies | Profile enrichment |
| Email Verification | ZeroBounce | $30/mies | Walidacja leadów |

---

## 🔧 Implementacja

### Krok 1: Narzędzia Research

**src/v2/tools/research.py:**
```python
"""
Narzędzia research dla agentów Rady AI.
Web search, competitor analysis, trend research.
"""

import os
import json
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
from langchain.tools import tool


@dataclass
class CompetitorData:
    """Dane o konkurencie."""
    name: str
    pricing: Dict[str, str]
    positioning: str
    strengths: List[str]
    weaknesses: List[str]
    website: str


# === WEB SEARCH (SerpAPI) ===

class SerpAPIClient:
    """Klient do SerpAPI dla wyszukiwania Google."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SERPAPI_API_KEY")
        self.base_url = "https://serpapi.com/search"
    
    def search(self, query: str, num_results: int = 10) -> List[Dict]:
        """Wyszukaj w Google."""
        if not self.api_key:
            return [{"error": "Brak klucza SERPAPI_API_KEY"}]
        
        params = {
            "q": query,
            "api_key": self.api_key,
            "num": num_results,
            "engine": "google"
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            data = response.json()
            return data.get("organic_results", [])
        except Exception as e:
            return [{"error": str(e)}]
    
    def get_pricing_page(self, company: str) -> str:
        """Znajdź stronę pricing konkurencji."""
        results = self.search(f"{company} pricing software development services")
        for result in results:
            url = result.get("link", "")
            if "price" in url.lower() or "cost" in url.lower():
                return url
        return results[0].get("link", "") if results else ""


# Inicjalizacja klienta
_serp_client = None

def get_serp_client():
    global _serp_client
    if _serp_client is None:
        _serp_client = SerpAPIClient()
    return _serp_client


# === LANGCHAIN TOOLS ===

@tool
def search_competitor_pricing(competitor_name: str) -> str:
    """
    Wyszukaj pricing konkurencji (np. Turing, BairesDev, Toptal).
    Używaj gdy Marcus projektuje pricing.
    
    Args:
        competitor_name: Nazwa konkurenta
        
    Returns:
        Pricing info lub link do strony pricing
    """
    client = get_serp_client()
    
    # Szukaj strony pricing
    pricing_url = client.get_pricing_page(competitor_name)
    
    # Szukaj konkretnych cen
    results = client.search(
        f'"{competitor_name}" hourly rate OR "starting at" OR pricing',
        num_results=5
    )
    
    insights = []
    for r in results:
        snippet = r.get("snippet", "")
        if any(word in snippet.lower() for word in ["$", "€", "hour", "rate", "pricing"]):
            insights.append(f"- {snippet[:200]}")
    
    return f"""
Pricing research dla {competitor_name}:

Strona pricing: {pricing_url}

Znalezione informacje:
{chr(10).join(insights[:3]) if insights else "Brak konkretnych cen w wynikach."}

Rekomendacja: Wejdź na stronę pricing aby zobaczyć aktualne ceny.
    """.strip()


@tool  
def research_market_trends(industry: str, topic: str) -> str:
    """
    Zbadaj trendy rynkowe dla danej branży.
    Używaj dla research przed projektowaniem oferty.
    
    Args:
        industry: Branża (np. "fintech", "healthtech")
        topic: Temat (np. "team extension", "sovereign ai")
    """
    client = get_serp_client()
    
    queries = [
        f"{industry} {topic} trends 2024",
        f"{industry} {topic} challenges",
        f"{industry} {topic} market size"
    ]
    
    all_insights = []
    for query in queries:
        results = client.search(query, num_results=3)
        for r in results:
            all_insights.append(f"- {r.get('title', '')}: {r.get('snippet', '')[:150]}...")
    
    return f"""
Trendy rynkowe: {industry} + {topic}

{chr(10).join(all_insights[:6])}

💡 Insight dla projektu:
Użyj tych trendów aby pokazać że Scalac rozumie rynek.
    """.strip()


@tool
def find_case_study_examples(industry: str, problem_type: str) -> str:
    """
    Znajdź przykłady case studies z branży.
    Pomaga Marcusowi w tworzeniu proof.
    
    Args:
        industry: Branża klienta
        problem_type: Typ problemu (np. "migration", "scaling", "compliance")
    """
    client = get_serp_client()
    
    results = client.search(
        f'{industry} software development case study {problem_type} success',
        num_results=5
    )
    
    examples = []
    for r in results:
        examples.append(f"- {r.get('title', '')}\n  {r.get('snippet', '')[:200]}...")
    
    return f"""
Case study examples: {industry} + {problem_type}

{chr(10).join(examples[:4])}

💡 Użyj tych przykładów jako inspiracja lub porównanie.
    """.strip()


# === SEO TOOLS (DataForSEO) ===

class SEOClient:
    """Klient do DataForSEO dla danych SEO."""
    
    def __init__(self, login: Optional[str] = None, password: Optional[str] = None):
        self.login = login or os.getenv("DATAFORSEO_LOGIN")
        self.password = password or os.getenv("DATAFORSEO_PASSWORD")
        self.base_url = "https://api.dataforseo.com/v3"
    
    def get_keywords_for_url(self, url: str, location_code: int = 2826) -> List[Dict]:
        """Pobierz słowa kluczowe dla których dana strona rankuje."""
        if not self.login or not self.password:
            return [{"error": "Brak credentials DataForSEO"}]
        
        endpoint = f"{self.base_url}/data_ads/keywords_for_site/live"
        
        payload = [{
            "target": url,
            "location_code": location_code,  # 2826 = Poland
            "language_code": "pl"
        }]
        
        try:
            response = requests.post(
                endpoint,
                auth=(self.login, self.password),
                json=payload,
                timeout=60
            )
            return response.json().get("tasks", [{}])[0].get("result", [{}])[0].get("items", [])
        except Exception as e:
            return [{"error": str(e)}]


_seo_client = None

def get_seo_client():
    global _seo_client
    if _seo_client is None:
        _seo_client = SEOClient()
    return _seo_client


@tool
def research_keywords_for_topic(topic: str, location: str = "PL") -> str:
    """
    Zbadaj słowa kluczowe dla danego tematu.
    Używaj gdy Kai pisze copy lub Sofia planuje content.
    
    Args:
        topic: Temat (np. "scala development outsourcing")
        location: Lokalizacja (PL, US, GB)
    """
    # Używamy SerpAPI do researchu słów kluczowych
    client = get_serp_client()
    
    results = client.search(
        f'"{topic}" related searches keywords',
        num_results=10
    )
    
    # Zbierz related questions (People Also Ask)
    questions = []
    keywords = []
    
    for r in results:
        title = r.get("title", "")
        snippet = r.get("snippet", "")
        
        # Ekstrakcja potencjalnych słów kluczowych
        if any(word in title.lower() for word in topic.lower().split()):
            keywords.append(title)
        
        if "?" in title:
            questions.append(title)
    
    return f"""
Keyword research: "{topic}"

## Słowa kluczowe do użycia:
{chr(10).join([f"- {k}" for k in keywords[:5]])}

## Pytania (People Also Ask):
{chr(10).join([f"- {q}" for q in questions[:5]])}

## Rekomendacje:
- Użyj słów kluczowych w H1 i pierwszym akapicie
- Odpowiedz na pytania w sekcji FAQ
- Targetuj long-tail keywords dla lepszej konwersji
    """.strip()


@tool
def analyze_competitor_content(competitor_url: str) -> str:
    """
    Analizuj content konkurencji.
    Używaj dla content gap analysis.
    
    Args:
        competitor_url: URL bloga lub strony konkurencji
    """
    client = get_serp_client()
    
    # Sprawdź co rankuje
    results = client.search(f"site:{competitor_url} blog", num_results=10)
    
    topics = []
    for r in results:
        title = r.get("title", "").replace(" - Blog", "").replace(" | Blog", "")
        if title:
            topics.append(title)
    
    return f"""
Content analysis: {competitor_url}

## Tematy które konkurencja porusza:
{chr(10).join([f"{i+1}. {t}" for i, t in enumerate(topics[:8])])}

## Content gaps (potencjalne tematy dla Scalac):
- Case studies z fintech (jeśli nie ma)
- Technical deep-dives (Scala, Akka, Kafka)
- Sovereign AI content (jeśli nie ma)
- Comparison articles (Scalac vs alternatywy)

💡 Użyj tych insightów do planowania content calendar.
    """.strip()


# === LEAD ENRICHMENT ===

@tool
def enrich_company_data(company_name: str) -> str:
    """
    Enrich data o firmie dla ABM.
    Używaj gdy David przygotowuje target accounts.
    
    Args:
        company_name: Nazwa firmy
    """
    client = get_serp_client()
    
    # Podstawowy research
    results = client.search(f'"{company_name}" software engineering team hiring', num_results=5)
    
    # LinkedIn company page
    linkedin_results = client.search(f'"{company_name}" LinkedIn company', num_results=3)
    
    insights = []
    linkedin_url = ""
    
    for r in results:
        snippet = r.get("snippet", "")
        if any(word in snippet.lower() for word in ["hiring", "engineer", "developer", "team"]):
            insights.append(snippet[:200])
    
    for r in linkedin_results:
        if "linkedin.com/company" in r.get("link", ""):
            linkedin_url = r.get("link", "")
            break
    
    return f"""
Enrichment: {company_name}

## Hiring Signals:
{chr(10).join([f"- {i}" for i in insights[:3]]) if insights else "Brak jasnych sygnałów hiring."}

## LinkedIn: {linkedin_url or "Nie znaleziono"}

## Rekomendacja ABM:
{"✅ High priority - aktywnie rekrutują!" if insights else "⚠️ Sprawdź careers page manualnie"}

## Next steps:
1. Sprawdź LinkedIn job posts
2. Znajdź CTO/VP Eng na LinkedIn
3. Zobacz ostatnie funding news (Crunchbase)
    """.strip()
```

### Krok 2: Narzędzia Analizy

**src/v2/tools/analysis.py:**
```python
"""
Narzędzia analityczne dla Eleny i innych agentów.
Benchmarki, kalkulacje, konwersje.
"""

from typing import Dict, List
from langchain.tools import tool
import random  # Dla demo - zamień na real API


# === BENCHMARKI BRANŻOWE ===

BENCHMARKS = {
    "saas_b2b": {
        "lead_to_mql": 0.25,
        "mql_to_sql": 0.15,
        "sql_to_opportunity": 0.40,
        "opportunity_to_closed": 0.25,
        "avg_sales_cycle_days": 60,
        "cac_ratio": 3.0
    },
    "software_services": {
        "lead_to_mql": 0.20,
        "mql_to_sql": 0.12,
        "sql_to_opportunity": 0.35,
        "opportunity_to_closed": 0.30,
        "avg_sales_cycle_days": 45,
        "cac_ratio": 2.5
    },
    "fintech": {
        "lead_to_mql": 0.15,
        "mql_to_sql": 0.10,
        "sql_to_opportunity": 0.30,
        "opportunity_to_closed": 0.20,
        "avg_sales_cycle_days": 90,
        "cac_ratio": 4.0
    }
}


@tool
def get_industry_benchmarks(industry: str) -> str:
    """
    Pobierz benchmarki konwersji dla branży.
    Używaj gdy Elena buduje lejek.
    
    Args:
        industry: Branża (saas_b2b, software_services, fintech, healthtech)
    """
    benchmarks = BENCHMARKS.get(industry, BENCHMARKS["software_services"])
    
    return f"""
Benchmarki dla branży: {industry}

## Konwersje (średnie):
- Lead → MQL: {benchmarks['lead_to_mql']*100:.0f}%
- MQL → SQL: {benchmarks['mql_to_sql']*100:.0f}%
- SQL → Opportunity: {benchmarks['sql_to_opportunity']*100:.0f}%
- Opportunity → Closed: {benchmarks['opportunity_to_closed']*100:.0f}%

## Overall funnel conversion:
Lead → Closed: {benchmarks['lead_to_mql'] * benchmarks['mql_to_sql'] * benchmarks['sql_to_opportunity'] * benchmarks['opportunity_to_closed'] * 100:.2f}%

## Inne metryki:
- Average sales cycle: {benchmarks['avg_sales_cycle_days']} dni
- Target CAC Ratio: {benchmarks['cac_ratio']}x

💡 Użyj tych benchmarków jako baseline, ale ustaw cele 20% wyższe.
    """.strip()


@tool
def calculate_funnel_metrics(
    target_revenue: int,
    avg_deal_size: int,
    industry: str = "software_services"
) -> str:
    """
    Oblicz wymagane metryki lejka dla target revenue.
    
    Args:
        target_revenue: Target przychodu (PLN)
        avg_deal_size: Średni rozmiar deala (PLN)
        industry: Branża dla benchmarków
    """
    benchmarks = BENCHMARKS.get(industry, BENCHMARKS["software_services"])
    
    # Reverse calculation
    deals_needed = target_revenue / avg_deal_size
    opportunities_needed = deals_needed / benchmarks['opportunity_to_closed']
    sqls_needed = opportunities_needed / benchmarks['sql_to_opportunity']
    mqls_needed = sqls_needed / benchmarks['mql_to_sql']
    leads_needed = mqls_needed / benchmarks['lead_to_mql']
    
    return f"""
Funnel Math: {target_revenue:,.0f} PLN target

## Założenia:
- Average deal size: {avg_deal_size:,.0f} PLN
- Industry: {industry}

## Wymagane wolumeny:
- Closed deals needed: {deals_needed:.0f}
- Opportunities needed: {opportunities_needed:.0f}
- SQLs needed: {sqls_needed:.0f}
- MQLs needed: {mqls_needed:.0f}
- Leads needed: {leads_needed:.0f}

## Monthly targets (6-month timeline):
- Closed: {deals_needed/6:.1f} deals/month
- Pipeline: {target_revenue/6:,.0f} PLN/month
- New leads: {leads_needed/6:.0f}/month

## Uwaga:
Te liczby zakładają brak churn i stałe avg deal size.
Dodaj 20% buffer dla bezpieczeństwa.
    """.strip()


@tool
def calculate_roi_for_client(
    team_size: int,
    avg_salary_local: int,
    scalac_rate: int = 80,  # EUR/hour
    project_months: int = 12
) -> str:
    """
    Oblicz ROI dla klienta (używaj w Gap Selling).
    
    Args:
        team_size: Liczba deweloperów
        avg_salary_local: Średnia pensja lokalna (EUR/year)
        scalac_rate: Stawka Scalac (EUR/hour)
        project_months: Długość projektu (miesiące)
    """
    # Koszty lokalne
    local_cost_total = avg_salary_local * team_size * (project_months / 12)
    
    # Dodaj overhead (rekrutacja, biuro, benefity) - typowo 50%
    local_with_overhead = local_cost_total * 1.5
    
    # Koszty Scalac
    hours_per_month = 160  # Full-time
    scalac_cost_total = scalac_rate * hours_per_month * team_size * project_months
    
    # Time-to-hire savings (załóżmy 3 miesiące)
    time_savings_value = team_size * avg_salary_local * 0.25  # 25% rocznej pensji
    
    roi = ((local_with_overhead - scalac_cost_total + time_savings_value) / scalac_cost_total) * 100
    
    return f"""
ROI Analysis dla klienta:

## Założenia:
- Team size: {team_size} devs
- Duration: {project_months} months
- Scalac rate: {scalac_rate} EUR/hour

## Koszty:
### In-house (lokalnie):
- Base salaries: {local_cost_total:,.0f} EUR
- With overhead (50%): {local_with_overhead:,.0f} EUR
- Time to hire: 3-6 months

### Scalac:
- Total cost: {scalac_cost_total:,.0f} EUR
- Start: 2 weeks

## Savings & Value:
- Direct cost savings: {local_with_overhead - scalac_cost_total:,.0f} EUR
- Time-to-market value: {time_savings_value:,.0f} EUR
- **ROI: {roi:.0f}%**

## Dodatkowe benefity (nieuwzględnione):
- No recruitment costs
- No long-term commitments
- Immediate expertise
- Flexibility to scale

💡 Użyj tego w Gap Analysis jako "Future State value".
    """.strip()


@tool
def estimate_deal_timeline(
    deal_size: int,
    industry: str,
    decision_makers: int = 2
) -> str:
    """
    Estymuj timeline deala na podstawie danych.
    
    Args:
        deal_size: Wartość deala (PLN)
        industry: Branża klienta
        decision_makers: Liczba decision makerów
    """
    benchmarks = BENCHMARKS.get(industry, BENCHMARKS["software_services"])
    base_timeline = benchmarks['avg_sales_cycle_days']
    
    # Modyfikatory
    size_modifier = 1 + (deal_size / 500000) * 0.5  # Większe = dłuższe
    stakeholder_modifier = 1 + (decision_makers - 1) * 0.3  # Więcej osób = dłuższe
    
    estimated_days = base_timeline * size_modifier * stakeholder_modifier
    
    return f"""
Deal Timeline Estimate:

## Inputs:
- Deal size: {deal_size:,.0f} PLN
- Industry: {industry}
- Decision makers: {decision_makers}

## Estymowany timeline:
- Base ({industry}): {base_timeline} dni
- Size modifier: {size_modifier:.2f}x
- Stakeholder modifier: {stakeholder_modifier:.2f}x

### **Estymacja: {estimated_days:.0f} dni ({estimated_days/30:.1f} miesięcy)**

## Fazy:
1. Discovery & Qualification: {estimated_days * 0.15:.0f} dni
2. Proposal & Negotiation: {estimated_days * 0.40:.0f} dni
3. Legal & Procurement: {estimated_days * 0.30:.0f} dni
4. Closing: {estimated_days * 0.15:.0f} dni

## Ryzyka:
{"⚠️ Wysokie - duży deal z wieloma stakeholderami" if deal_size > 300000 else "✅ Umiarkowane"}

💡 Użyj JOLT framework aby skrócić timeline.
    """.strip()
```

### Krok 3: Integracja z agentami

**src/v2/agents/marcus_v2.py:**
```python
"""
Marcus v2.5 - Architekt Oferty z narzędziami.
"""

from typing import Dict, List
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage

from .base_agent import BaseScalacAgent, AgentResponse
from ..tools.research import (
    search_competitor_pricing,
    research_market_trends,
    find_case_study_examples
)
from ..tools.analysis import calculate_roi_for_client


class MarcusAgentV2(BaseScalacAgent):
    """Marcus z narzędziami research i analizy."""
    
    def __init__(self, memory=None):
        super().__init__(
            name="Marcus",
            role="Architekt Oferty",
            prompt_file="marcus_offer_architect",
            memory=memory
        )
        
        # Narzędzia dla Marcusa
        self.tools = [
            search_competitor_pricing,
            research_market_trends,
            find_case_study_examples,
            calculate_roi_for_client
        ]
        
        # Agent z narzędziami
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    def create_offer(
        self, 
        project_name: str, 
        project_type: str,
        target_segment: str = ""
    ) -> AgentResponse:
        """
        Zaprojektuj ofertę z użyciem research tools.
        """
        # Pobierz context z pamięci
        memory_context = self._get_relevant_context(project_name)
        
        task = f"""
Zaprojektuj kompletną ofertę "{project_name}" (typ: {project_type}).

## KROKI DO WYKONANIA:

1. **Research konkurencji** - Użyj tool `search_competitor_pricing` dla:
   - Turing
   - BairesDev
   - Toptal
   - X-Team

2. **Research trendów** - Użyj tool `research_market_trends` dla:
   - Branża: {target_segment or "software development outsourcing"}
   - Temat: {project_type}

3. **Znajdź case studies** - Użyj tool `find_case_study_examples` dla inspiracji

4. **Oblicz ROI** - Użyj tool `calculate_roi_for_client` z typowymi parametrami

5. **Zbuduj ofertę** używając frameworków:
   - Gap Selling (z danymi ROI)
   - StoryBrand
   - Good-Better-Best (z referencją do konkurencji)
   - Challenger Sale

## OUTPUT FORMAT:
```markdown
# Offer Package: {project_name}

## Research Insights
### Konkurencja:
[Co znalazłeś o pricingu]

### Trendy rynkowe:
[Co jest aktualnie ważne]

## 1. Gap Analysis (z danymi)
### Current State
[opisz]

### Financial Impact
[ROI calculation]

## 2. BrandScript
[SB7 Framework]

## 3. Pricing vs Competition
- Good: [price] (vs competition: [...])
- Better: [price]
- Best: [price]

## 4. Challenger Pitch
[Teach-Tailor-Take Control]

## 5. Beachhead Market
[Target segment z uzasadnieniem]
```

WYKONAJ KAŻDY KROK używając odpowiednich tools. Nie pomijaj researchu.
        """
        
        # Uruchom agenta z narzędziami
        result = self.agent_executor.invoke({
            "input": task,
            "chat_history": self.session_history
        })
        
        # Zapisz w historii
        self.session_history.extend([
            ("human", task),
            ("ai", result["output"])
        ])
        
        return AgentResponse(
            agent=self.name,
            content=result["output"],
            used_memory=[],  # TODO: track which tools were used
            timestamp=datetime.now().isoformat(),
            metadata={"tools_used": True}
        )
```

### Krok 4: Lista narzędzi per agent

**AGENTS/marcus_offer_architect/tools_v2.yaml:**
```yaml
agent: Marcus - Architekt Oferty
version: "2.5"

tools:
  # Research konkurencji
  - name: search_competitor_pricing
    description: Sprawdź pricing konkurencji (Turing, BairesDev, Toptal)
    when_to_use: "Przed ustaleniem pricingu"
    cost_per_call: "$0.01 (SerpAPI)"
    
  - name: research_market_trends
    description: Zbadaj trendy rynkowe dla branży
    when_to_use: "Na początku projektowania oferty"
    cost_per_call: "$0.01 (SerpAPI)"
    
  - name: find_case_study_examples
    description: Znajdź przykłady case studies w branży
    when_to_use: "Szukając proof points"
    cost_per_call: "$0.01 (SerpAPI)"
    
  # Analiza
  - name: calculate_roi_for_client
    description: Oblicz ROI dla klienta
    when_to_use: "W Gap Analysis jako Financial Impact"
    cost_per_call: "Free"
    
  # Memory
  - name: search_case_studies
    description: Wyszukaj case studies Scalac z pamięci
    when_to_use: "Zawsze na początku"
    cost_per_call: "Free (ChromaDB)"

automation:
  # Automatyczne uruchamianie
  always_run:
    - search_case_studies
    - research_market_trends
    
  conditional:
    - tool: search_competitor_pricing
      condition: "if project_type == 'new_offer'"
```

**AGENTS/elena_funnel_architect/tools_v2.yaml:**
```yaml
agent: Elena - Architektka Lejków
version: "2.5"

tools:
  # Benchmarki
  - name: get_industry_benchmarks
    description: Pobierz benchmarki konwersji dla branży
    when_to_use: "Budując lejek"
    
  - name: calculate_funnel_metrics
    description: Oblicz wymagane wolumeny dla target revenue
    when_to_use: "Ustalając cele"
    
  - name: estimate_deal_timeline
    description: Estymuj timeline deala
    when_to_use: "Planując sales forecast"
    
  # Research
  - name: research_market_trends
    description: Trendy w lead generation
    when_to_use: "Szukając nowych kanałów"

automation:
  always_run:
    - get_industry_benchmarks
    - calculate_funnel_metrics
```

---

## 💰 Szacunkowy Koszt Miesięczny

| Usługa | Koszt/mies | Użycie |
|--------|-----------|--------|
| SerpAPI | $50 | Research konkurencji, trendy |
| DataForSEO | $100 | Keywords, content gaps |
| OpenAI API | $100 | LLM calls + embeddings |
| Chroma Cloud | $20 | Vector DB hosting |
| **Razem** | **~$270** | ~100 projektów/miesiąc |

---

## 🚀 Quick Test

```python
from src.v2.tools.research import search_competitor_pricing

# Test narzędzia
result = search_competitor_pricing.run("Turing")
print(result)
```

---

## ✅ Checkpoint - Faza 2 Ukończona Gdy:

- [ ] Marcus automatycznie sprawdza pricing konkurencji
- [ ] Elena używa realnych benchmarków konwersji
- [ ] Kai ma research keywords przed pisaniem
- [ ] David enrichuje leady danymi
- [ ] Agenci citują real-time data w odpowiedziach

---

**Następny krok:** [Faza 3 - Autonomia](./PHASE_3_AUTONOMY.md)

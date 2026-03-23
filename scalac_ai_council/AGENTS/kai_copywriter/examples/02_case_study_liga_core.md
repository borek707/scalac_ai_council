# Example 2: Case Study - Liga Digital (CORE)

## Writing GPS

- **Goal:** Budowa trust (pokazać że potrafimy skalować systemy)
- **Why:** Case study jako proof dla podobnych fintechów
- **Who:** CTO fintechów którzy potrzebują skalować systemy
- **What:** Jak pomogliśmy Liga Digital przetwarzać 50k msg/sec
- **So What:** "Jeśli zrobiliśmy to dla nich, możemy dla Ciebie"

---

## Headline

**How Liga Digital Scaled to 50,000 Messages Per Second Without Downtime**

---

## Lead (First Paragraph)

W 2022 Liga Digital miała problem. Ich system analizy danych finansowych działał dobrze dla 1000 użytkowników, ale przy 10,000 zaczął się dusić. Latency rosło. Timeouts się pojawiały. Klienci narzekali.

Potrzebowali skalować 10x w 6 miesięcy. Nie mieli czasu na rekrutację. Nie mieli czasu na eksperymenty.

Zadzwonili do Scalac.

---

## Challenge

Liga Digital to fintech oferujący analizę danych finansowych w czasie rzeczywistym. Ich klienci - banki i fundusze inwestycyjne - polegają na szybkości.

**Problem:**
- System przetwarzał 5k msg/sec, potrzebowali 50k
- Latency rosło z 10ms do 500ms przy peak load
- Architektura była monolityczna, trudna do skalowania
- Team 5 devów nie wystarczał do przepisania systemu

**Constraints:**
- Zero downtime (klienci trade'ują 24/7)
- 6-miesięczny deadline (kontrakt z dużym bankiem)
- Nie mogli zatrudnić 10 devów na czas (hiring trwa 6+ miesięcy)

---

## Solution

**Phase 1: Architecture Review (2 tygodnie)**

Nasz Principal Engineer spędził 2 tygodnie z ich teamem. Wynik:
- Bottleneck: Monolityczny message processor
- Rozwiązanie: Event-driven architecture z Akka Cluster
- Plan: Gradual migration, moduł po module

**Phase 2: Team Extension (2 tygodnie onboarding)**

Dostarczyliśmy 10 senior Scala devs:
- 5 devs: Akka Cluster, event sourcing
- 3 devs: Kafka streaming, backpressure
- 2 devs: Monitoring, observability

Embedded w ich teamie. Daily standupy. Code review. Pair programming.

**Phase 3: Migration (6 miesięcy)**

- Moduł po module, zero downtime
- Każdy moduł testowany w produkcji z canary deployment
- Rollback plan dla każdego kroku
- 24/7 monitoring przez nasz team

---

## Results

**Metryki (Before → After):**
- Throughput: 5k msg/sec → 50k msg/sec (10x)
- Latency: 500ms → <1ms (500x improvement)
- Uptime: 99.5% → 99.99%
- Time to deploy: 2 hours → 15 minutes

**Biznes:**
- Kontrakt z dużym bankiem podpisany
- 3 nowi klienci przyciągnięci przez "speed guarantee"
- Revenue w górę o 40% w 6 miesięcy

**Team:**
- 10 devów onboarded w 2 tygodnie
- Zero turnover w 12 miesięcy
- Knowledge transfer: ich team teraz utrzymuje system

---

## Quote

> "Scalac dev był tak dobry że CTO innej firmy pytał skąd go wzięliśmy. To był najlepszy komplement jaki mogliśmy dostać.
>
> Nie tylko dostarczyliśmy devów. Dostarczyliśmy rozwiązanie. W 6 miesięcy przeszliśmy z systemu który się wysypywał do systemu który przetwarza 50k wiadomości na sekundę bez mrugnięcia.
>
> Najważniejsze: wiedza zostaje. Nasz team teraz utrzymuje ten system. To nie był outsourcing - to była współpraca."

**— Piotr Nowak, Tech Lead, Liga Digital**

---

## Technical Details (Optional Section)

**Stack:** Scala, Akka Cluster, Kafka, Kubernetes, Prometheus

**Architecture:**
- Event-driven z Akka Cluster
- Kafka dla message streaming
- Backpressure handling
- Circuit breakers dla resilience
- Distributed tracing

**Challenges Overcome:**
- Zero downtime migration
- State management w distributed system
- Backpressure przy 10x load
- Monitoring i observability

---

## CTA

**Chcesz podobne wyniki dla swojego systemu?**

**[Zarezerwuj Darmowy Architecture Review]**

*5 dni roboczych. Raport z bottleneckami. Bez zobowiązań.*

---

## Books Reference

- **Everybody Writes:** Writing GPS, lead zaczyna od akcji
- **They Ask You Answer:** Transparentność (problemy, constraints)
- **Copywriter's Handbook:** AIDA w strukturze case study
- **On Writing Well:** Konkrety zamiast buzzwords ("50k msg/sec" zamiast "high performance")

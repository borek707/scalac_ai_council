# CORE vs AI Diagnosis Checklist

## Pytania diagnostyczne

### Infrastructure
- [ ] Czy klient ma working Kubernetes cluster?
- [ ] Czy mają GPU resources (dla AI)?
- [ ] Czy mają monitoring i observability?
- [ ] Czy mają security policies?

### Problem Type
- [ ] Czy problem to "system się nie skaluje"? → CORE
- [ ] Czy problem to "potrzebujemy devów"? → CORE
- [ ] Czy problem to "AI nie przechodzi compliance"? → AI
- [ ] Czy problem to "mamy AI POC który nie skaluje"? → AI

### AI Specific
- [ ] Czy AI to "nice to have" czy "compliance blocker"?
  - Nice to have → CORE first
  - Blocker → AI
- [ ] Czy mówią o "POC" czy "production"?
  - POC → AI assessment
  - Production → CORE+AI bundle

### Decision Matrix

| Klient mówi o... | Infrastructure? | Diagnoza |
|------------------|-----------------|----------|
| Team extension | N/D | CORE |
| System scaling | Nie gotowa | CORE |
| System scaling | Gotowa | CORE |
| AI POC | Nie gotowa | CORE+AI bundle |
| AI POC | Gotowa | AI |
| AI compliance | Nie gotowa | CORE+AI bundle |
| AI compliance | Gotowa | AI |

---

## Output

**Diagnosis:**
- [ ] Czysty CORE
- [ ] Czysty AI
- [ ] CORE+AI bundle

**Uzasadnienie:**
[Dlaczego tak zdiagnozowaliśmy]

**Rekomendacja:**
[Jaką ofertę proponujemy]

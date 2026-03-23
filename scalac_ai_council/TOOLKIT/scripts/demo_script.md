# Demo Script
## Scalac Demo Guide dla sales team

---

## Demo Types

### 1. Architecture Review Presentation (CORE)
**Duration:** 30 min
**Audience:** CTO, VP Eng, Tech Lead
**Goal:** Pokazać expertise i value

#### Agenda
1. **Opening (2 min)**
   - "Dzięki za czas. Widzę że [personalized]."
   - "Cel: Pokażę Wam 3 kluczowe rzeczy z review Waszego systemu"

2. **Problem Recap (3 min)**
   - "Rozumiem że macie challenge z [problem]"
   - "To common w fintechach które skalują 3-10x"

3. **Finding #1 (8 min)**
   - "Pierwszy bottleneck: [technical issue]"
   - "Why it matters: [business impact]"
   - "Recommendation: [solution]"
   - "Proof: Robiliśmy to dla [case study]"

4. **Finding #2 (8 min)**
   - (same structure)

5. **Finding #3 (5 min)**
   - (same structure)

6. **Next Steps (4 min)**
   - "Podsumowując: 3 kluczowe issues, wszystkie fixable"
   - "Jak możemy pomóc: [team extension/proposal]"
   - "Następny krok: [specific action]"

#### Demo Tips
- Use diagrams, not walls of text
- Connect technical to business impact
- Ask: "Czy to rezonuje z Waszymi obserwacjami?"
- Leave time for questions

---

### 2. Sovereign AI Demo (AI)
**Duration:** 45 min
**Audience:** CTO, CISO, AI Product Owner
**Goal:** Pokazać że AI może być compliant i production-ready

#### Agenda
1. **Opening (3 min)**
   - "Dzięki za czas. Wiem że compliance jest głównym blokiem."
   - "Pokażę jak AI przechodzi audity."

2. **The Problem (5 min)**
   - "Wasz POC działa na demo ale..."
   - "Compliance wymaga: data residency, explainability, audit trail"
   - "OpenAI nie spełnia tych wymagań"

3. **Architecture Overview (10 min)**
   - Show architecture diagram
   - "Private LLM w Waszym K8s"
   - "Data nigdy nie wychodzi"
   - "RAG z vector DB"
   - "Compliance layer: audit trail, explainability"

4. **Live Demo (15 min)**
   - Show working system
   - Query → Response → Source documents
   - Show audit log: "Widzicie kto pytał, co było źródłem, dlaczego taka odpowiedź"
   - Show guardrails: "System blokuje nieodpowiednie zapytania"

5. **Compliance Features (7 min)**
   - "Explainability: Dlaczego model odpowiedział tak a nie inaczej"
   - "Data residency: Wszystko w EU"
   - "Audit trail: Kompletny log dla regulatorów"
   - "Access control: Role-based permissions"

6. **Case Study (3 min)**
   - "Bank X przeszedł tym samym procesem..."
   - "Audit passed, AI w produkcji"

7. **Next Steps (2 min)**
   - "Pytania?"
   - "Następny krok: AI Compliance Assessment"

#### Demo Tips
- Have backup (recorded demo) if live fails
- Focus on compliance, nie model accuracy
- CISO musi zobaczyć security features
- Prepare for technical deep-dives

---

### 3. Team Extension Introduction (CORE)
**Duration:** 20 min
**Audience:** CTO, HR, possibly CFO
**Goal:** Pokazać jak współpraca wygląda w praktyce

#### Agenda
1. **Opening (2 min)**
   - "Pokażę jak wygląda współpraca od dnia 1"

2. **The Team (5 min)**
   - "To są Wasi devs [pokazujemy profile]"
   - "Seniority: 8+ lat"
   - "Experience: [relevant projects]"

3. **Day 1-14: Onboarding (5 min)**
   - "Week 1: Setup, security, codebase access"
   - "Week 2: Pierwsze ticket, code review"
   - "Embedded: Na Waszym Slack, Wasze standupy"

4. **Day 15-90: Integration (5 min)**
   - "Full team member"
   - "Code ownership"
   - "Same KPIs jak Wasz team"

5. **Knowledge Transfer (2 min)**
   - "Dokumentacja, code review, pair programming"
   - "Wiedza zostaje w firmie"

6. **Next Steps (1 min)**
   - "Pytania?"
   - "Gotowi na start?"

---

## Objection Handling During Demo

### "Czy to zadziała w naszym środowisku?"
"Rozumiem obawę. Dlatego zaczynamy od Architecture Review - zweryfikujemy czy to ma sens dla Waszego setupu zanim zaczniemy."

### "Czy możemy to zwolnić jak się nie sprawdzi?"
"Tak. Replacement guarantee - jak dev nie pasuje, wymieniamy w 48h. Trial period 2 tygodnie - jak nie działa, nie płacisz."

### "Czy to bezpieczne?" (AI demo)
"Wszystko w Waszej infrastrukturze. Data nie wychodzi. Mamy encryption, access control, audit trail. Pokazać security architecture?"

---

## Demo Do's and Don'ts

### DO
- [ ] Research account before demo
- [ ] Personalize examples
- [ ] Connect technical to business value
- [ ] Ask questions (dialog, nie monolog)
- [ ] Have backup plan (recorded demo)
- [ ] Leave time for Q&A

### DON'T
- [ ] Don't do generic demo
- [ ] Don't ignore non-technical attendees
- [ ] Don't oversell (buduj trust)
- [ ] Don't run over time
- [ ] Don't leave without next step defined

---

## Post-Demo Actions

### Immediately After
- [ ] Send follow-up email (within 1 hour)
- [ ] Include demo recording/slides
- [ ] Confirm next steps
- [ ] Update CRM

### Follow-up Email Template
```
Subject: Demo follow-up: [Topic]

Cześć [Imię],

Dzięki za czas dzisiaj.

Jak obiecałem:
- [Recording/Slides]: [link]
- [Additional resource]: [link]
- [Case study]: [link]

Następny krok: [action] w [timeline]

Czy masz dodatkowe pytania?

Pozdrawiam,
[Name]
```

# Quick Start Guide
## Rada AI - Pierwsze kroki w 15 minut

---

## Co To Jest?

Rada AI to system 5 wyspecjalizowanych agentów AI którzy współpracują aby budować marketing i sprzedaż dla Scalac.

**5 Agentów:**
1. **Marcus** - Architekt Oferty (pricing, positioning)
2. **Elena** - Architektka Lejków (funnel, kwalifikacja)
3. **Kai** - Copywriter (landing pages, emails)
4. **Sofia** - Strateg Treści (content calendar, SEO)
5. **David** - Strateg Leadów (ABM, outbound)

---

## Kluczowa Zasada: 80/20 CORE/AI

**80% effort na CORE:**
- Team extension
- Distributed systems
- Fintech/enterprise

**20% effort na AI:**
- Sovereign AI
- RAG systems
- Banking compliance

**Dlaczego?** CORE = volume, krótszy cykl. AI = margin, dłuższy cykl.

---

## Start W 3 Kroki

### Krok 1: Zrozum Workflow (5 min)

**Standardowy projekt (np. nowa oferta):**

```
Marcus (Oferta)
    ↓ Handoff
Elena (Lejek)
    ↓ Handoff
David (Leady)
    ↓
Elena (Kwalifikacja)
    ↓
Kai (Copy)
    ↓
Sofia (Content)
```

**Szablony handoffów:** `WORKFLOW/handoff_templates.md`

---

### Krok 2: Przeczytaj Prompty (5 min)

Każdy agent ma:
- `system_prompt.md` - osobowość i książki
- `tools.yaml` - frameworki i templates
- `examples/` - 3-5 przykładów

**Zacznij od:**
1. `AGENTS/marcus_offer_architect/system_prompt.md` - fundament
2. `AGENTS/elena_funnel_architect/system_prompt.md` - proces

---

### Krok 3: Uruchom Pierwszy Projekt (5 min)

**Przykład: Nowa oferta Team Extension**

**Marcus:**
```
"Zaprojektuj ofertę Team Extension dla fintechów Series B"
```

**Elena (po handoff od Marcusa):**
```
"Zbuduj lejek dla oferty Team Extension"
```

**David (po handoff od Eleny):**
```
"Przygotuj ABM campaign dla 50 fintechów"
```

---

## Kluczowe Frameworky (Musisz Znać)

### Marcus
- **StoryBrand** - komunikacja (Hero/Problem/Guide/Plan)
- **Good-Better-Best** - pricing
- **Gap Selling** - Current State vs Future State

### Elena
- **MEDDIC** - kwalifikacja (Metrics/Economic Buyer/Criteria/Process/Pain/Champion)
- **JOLT** - overcoming indecision (Judge/Offer/Limit/Take risk)
- **Seeds/Nets/Spears** - trzy źródła leadów

### Kai
- **Big 5** - transparentność (Cost/Problems/Comparisons/Reviews/Best)
- **AIDA** - struktura copy (Attention/Interest/Desire/Action)
- **SUCCESs** - Made to Stick (Simple/Unexpected/Concrete/Credible/Emotional/Stories)

### Sofia
- **Content Tilt** - unikalny kąt
- **Epic Content** - duże, kompleksowe treści
- **Product-Led SEO** - intent-based keywords

### David
- **ABM Tiers** - 1-to-1 / 1-to-few / 1-to-many
- **Dream 100** - focus 80% effort na 100 kont
- **Signal-Based Selling** - intent data + trigger events

---

## Typowe Projekty

### 1. Nowa Oferta
**Wyzwanie:** Launch nowej usługi (np. Rust team extension)

**Workflow:**
1. Marcus: BrandScript + Pricing + Gap Analysis
2. Elena: Funnel + MEDDIC + Experiments
3. David: ABM campaign
4. Kai: Landing page + Email sequence
5. Sofia: Content support

**Output:** Kompletny launch package

---

### 2. Pipeline Review
**Wyzwanie:** Pipeline spadł, co robić?

**Workflow:**
1. Elena: Analiza metryk (conversion by stage)
2. David: Review lead gen (co działa/nie)
3. Kai: Optymalizacja copy (A/B tests)
4. Sofia: Content gaps analysis
5. Marcus: Offer adjustment (jeśli potrzeba)

**Output:** Action plan na następny miesiąc

---

### 3. Nowy Content
**Wyzwanie:** Potrzebujemy więcej leadów

**Workflow:**
1. Sofia: Content audit + SEO research
2. Sofia: Editorial calendar
3. Sofia → Kai: Brief
4. Kai: Content creation
5. Sofia: Publish + distribute

**Output:** Content calendar + 2-4 content pieces

---

## Spotkania Rady

### Weekly Brief (Poniedziałek, async)
- Co zrobiliśmy
- CORE vs AI split
- Blockers
- Needs from others

### Creative Sprint (Środa, 30 min)
- Problem do rozwiązania
- 2 agenty prezentują
- 3 pomagają

### Ship It (Piątek, 30 min)
- Demo gotowych assetów
- Feedback: "What I liked / What would make it 10x better"

---

## Szybkie Referencje

### Checklist'y
- `TOOLKIT/checklists/core_ai_diagnosis.md` - czy to CORE czy AI?
- `TOOLKIT/checklists/launch_checklist.md` - przed launch
- `TOOLKIT/checklists/qa_checklist.md` - jakość

### Skrypty
- `TOOLKIT/scripts/discovery_call_meddic.md` - MEDDIC discovery
- `TOOLKIT/scripts/demo_script.md` - demo guide

### Kalkulatory
- `TOOLKIT/calculators/roi_calculator.md` - ROI dla klientów
- `TOOLKIT/calculators/pricing_calculator.md` - Good-Better-Best

---

## Częste Problemy

### "Nie wiem czy to CORE czy AI"
→ Sprawdź `core_ai_diagnosis.md`

**Rule:** Jeśli klient nie ma infrastructure → CORE first

### "Lead nie odpowiada"
→ Sprawdź JOLT framework u Eleny

**Rule:** 40-60% deals umiera przez indecision, nie competition

### "Copy nie konwertuje"
→ Sprawdź Big 5 u Kaia

**Rule:** Odpowiedz na trudne pytania (cost, problems, comparisons)

### "Content nie generuje ruchu"
→ Sprawdź Content Tilt u Sofii

**Rule:** Unikalny kąt > ogólny content

### "Brak qualified leadów"
→ Sprawdź ABM u Davida

**Rule:** Dream 100 > spray and pray

---

## Metryki Sukcesu

### Rada AI (Monthly)
| Metric | Target |
|--------|--------|
| Pipeline | 500k PLN |
| CORE Pipeline | 400k PLN (80%) |
| AI Pipeline | 100k PLN (20%) |
| Win Rate | >30% |

### Agenci (Individual)
| Agent | Key Metric |
|-------|------------|
| Marcus | Offer conversion rate |
| Elena | Funnel conversion by stage |
| Kai | Copy conversion rate |
| Sofia | Content traffic & leads |
| David | Lead volume & quality |

---

## Następne Kroki

### Week 1: Foundation
- [ ] Przeczytaj wszystkie system_prompt.md
- [ ] Zrozum 80/20 CORE/AI balance
- [ ] Przejrzyj examples/

### Week 2: First Project
- [ ] Wybierz mały projekt (np. landing page dla istniejącej oferty)
- [ ] Przeprowadź cały workflow
- [ ] Zrób post-mortem

### Week 3: Optimization
- [ ] Przejrzyj metryki
- [ ] Zidentyfikuj słabe punkty
- [ ] Zrób A/B test

### Month 1: Full Integration
- [ ] Uczestnicz w Weekly Briefs
- [ ] Przeprowadź 2-3 projekty
- [ ] Zaktualizuj system o learnings

---

## Support

**Head of Growth:** [Użytkownik]
**Rada AI:** Marcus, Elena, Kai, Sofia, David

---

## Dokumentacja

- `README.md` - Pełna dokumentacja
- `AGENTS/{agent}/system_prompt.md` - Szczegółowi agenci
- `AGENTS/{agent}/tools.yaml` - Frameworki
- `AGENTS/{agent}/examples/` - Przykłady
- `WORKFLOW/` - System operacyjny
- `TOOLKIT/` - Templates, checklisty, skrypty
- `LEARNING/` - Book club, post-mortemy

---

**Gotowy? Zacznij od:** `AGENTS/marcus_offer_architect/examples/`

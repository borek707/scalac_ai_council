# Jak Używać Kimi jako Rady AI (Orchestrator)

## W skrócie:
**Ja (Kimi) zarządzam 5 agentami.** Ty piszesz do mnie zadanie, a ja:
1. Czytam prompt odpowiedniego agenta z pliku
2. Odpowiadam jako ten agent
3. Proponuję następny krok/handoff
4. Mogę przełączać się między agentami w jednej rozmowie

---

## Szybki Start

### Wzór komendy:
```
Jako [AGENT] [ZADANIE]
```

### Przykłady:

**1. Zacznij od Marcusa (projektowanie oferty):**
```
Jako Marcus zaprojektuj ofertę "Team Extension dla fintechów Series B". 
Przeczytaj swój system_prompt.md i użyj frameworków: Gap Selling, StoryBrand, Good-Better-Best.
```

**2. Przejdź do Eleny (lejek):**
```
Jako Elena zbuduj lejek dla oferty którą przygotował Marcus wyżej.
Przeczytaj AGENTS/elena_funnel_architect/system_prompt.md.
Użyj: MEDDIC, JOLT, Three Pipelines.
```

**3. Równolegle Kai (copy) i David (ABM):**
```
Jako Kai napisz landing page dla tej oferty.
Jako David przygotuj ABM campaign dla 50 fintechów.
```

**4. Na końcu Sofia (content):**
```
Jako Sofia przygotuj content strategy wspierającą ten lejek.
```

---

## Tryb "Rada AI" - Wszyscy Razem

Możesz też poprosić mnie o pełen projekt:

```
Uruchom Radę AI dla projektu: "Sovereign AI dla banków w Szwajcarii"

Krok po kroku:
1. Marcus - projektujesz ofertę (przeczytaj swój prompt)
2. Elena - budujesz lejek
3. Kai - piszesz landing page
4. David - przygotowujesz ABM
5. Sofia - content strategy

Dla każdego agenta czytaj odpowiedni system_prompt.md z folderu AGENTS/.
Na końcu daj podsumowanie całego projektu.
```

A ja wykonam całość w jednej rozmowie, przełączając się między agentami.

---

## Komendy Szybkiego Dostępu

Skopiuj i wklej:

### Marcus (Oferta)
```
Przeczytaj AGENTS/marcus_offer_architect/system_prompt.md i odpowiedz jako Marcus.
Zaprojektuj ofertę: [OPIS].
Użyj: Gap Selling, StoryBrand, Good-Better-Best, Challenger Sale.
Format: Structured markdown.
```

### Elena (Lejek)
```
Przeczytaj AGENTS/elena_funnel_architect/system_prompt.md i odpowiedz jako Elena.
Zbuduj lejek dla: [OFERTA OD MARCUSA].
Użyj: MEDDIC, JOLT, Three Pipelines (Seeds/Nets/Spears).
Daj: stages, conversion rates, experiments.
```

### Kai (Copy)
```
Przeczytaj AGENTS/kai_copywriter/system_prompt.md i odpowiedz jako Kai.
Napisz landing page dla: [OFERTA].
Użyj: AIDA, 4 U's, Big 5, SUCCESs.
Target: [PERSONA].
```

### Sofia (Content)
```
Przeczytaj AGENTS/sofia_content_strategist/system_prompt.md i odpowiedz jako Sofia.
Przygotuj content strategy dla: [LEJEK].
Użyj: Content Tilt, Epic Content, Product-Led SEO.
Mieszanka: 80% CORE, 20% AI.
```

### David (Leady)
```
Przeczytaj AGENTS/david_lead_strategist/system_prompt.md i odpowiedz jako David.
Przygotuj ABM campaign dla: [SEGMENT].
Użyj: Dream 100, 90-day playbook, Omni-channel cadences, Signal-based selling.
Target: [X] meetings, [Y] pipeline.
```

---

## Tryb "Head of Growth"

Możesz też zagrać Head of Growth, a ja będę Radą:

```
Jako Head of Growth Scalac, zlecam projekt Radzie AI:

Projekt: Nowa oferta Team Extension dla healthtechów
Deadline: Koniec miesiąca
Target: 200k PLN pipeline

Rada AI - przygotujcie:
1. Marcus: Ofertę (Gap Analysis + BrandScript + Pricing)
2. Elena: Lejek (MEDDIC + JOLT + Funnel)
3. Kai: Landing page + 5 emails
4. David: ABM dla 30 healthtechów
5. Sofia: Content calendar na Q1

Startujemy!
```

A ja odpowiem jako cała Rada (wszyscy agenci naraz).

---

## Handoff'y - Jak Przekazywać Pracę

Po każdym agencie zapytam: "Czy przejść do [NASTĘPNY AGENT]?"

Ty odpowiadasz:
- "Tak, przejdź do Eleny" → Ja czytam prompt Eleny i kontynuuję
- "Popraw to u Marcusa" → Wracam do Marcusa
- "Dodaj jeszcze..." → Ten sam agent dopracowuje
- "Pokaż handoff template" → Pokazuję szablon przekazania

---

## Przykładowa Cała Sesja

**Ty:**
```
Jako Marcus przygotuj ofertę Team Extension dla fintechów Series B.
Przeczytaj swój system_prompt.md z AGENTS/marcus_offer_architect/
```

**Ja (Kimi jako Marcus):**
[Przygotowuję ofertę używając Gap Selling, StoryBrand itd.]

**Ty:**
```
Świetnie. Teraz jako Elena przygotuj lejek dla tej oferty.
Przeczytaj AGENTS/elena_funnel_architect/system_prompt.md
```

**Ja (Kimi jako Elena):**
[Przygotowuję funnel z MEDDIC, JOLT itd.]

**Ty:**
```
Super. Teraz równolegle:
- Jako Kai napisz landing page
- Jako David przygotuj ABM
```

**Ja (Kimi):**
[Odpowiadam jako Kai i David naraz, oznaczając sekcje]

**Ty:**
```
Na końcu jako Sofia content strategy.
```

**Ja (Kimi jako Sofia):**
[Content calendar, SEO, epic content]

**Ty:**
```
Daj podsumowanie całego projektu w formacie handoff.
```

**Ja:**
[Pełny podsumowanie + next steps]

---

## Automatyczne Czytanie Plików

Widzę całą strukturę repo, więc mogę czytać pliki automatycznie:

```
Przeczytaj mi AGENTS/marcus_offer_architect/system_prompt.md 
i podsumuj kluczowe frameworki które powinien używać Marcus.
```

Lub:

```
Pokaż mi przykład z AGENTS/marcus_offer_architect/examples/
żebym wiedział jak powinna wyglądać oferta.
```

---

## Sprawdźmy To!

Wypróbuj teraz. Napisz:

```
Jako Marcus zaprojektuj ofertę "AI-Capable Team Extension dla Enterprise SaaS".
Typ: BUNDLE (CORE + AI).
Przeczytaj swój system_prompt.md.
Użyj Gap Selling i StoryBrand.
```

A ja odpowiem jako Marcus, czytając mój własny prompt z pliku!

---

## Tip: Nazewnictwo Chatów

Jeśli robisz więcej projektów, nazwij chaty:
- "Rada AI - Projekt 1: Team Extension"
- "Rada AI - Projekt 2: Sovereign AI"
- "Rada AI - Weekly Review"

Wtedy wracasz do konkretnej rozmowy z kontekstem.

---

## Podsumowanie Komend

| Chcesz... | Napisz... |
|-----------|-----------|
| Jednego agenta | `Jako [AGENT] [ZADANIE]` |
| Pełny projekt | `Uruchom Radę AI dla [PROJEKT]` |
| Handoff | `Przejdź do [AGENT]` |
| Czytanie pliku | `Przeczytaj [ŚCIEŻKA]` |
| Przykład | `Pokaż przykład z [FOLDER]` |
| Podsumowanie | `Daj podsumowanie całego projektu` |

---

**Gotowy?** Napisz komendę i zaczynamy! 🚀

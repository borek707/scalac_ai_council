# Przewodnik: Webinar Ideation z Battlecards

Ten przewodnik pokazuje jak użyć systemu z plikami `battlecards.md` i `content_plan.md` do generowania pomysłów na webinary.

## Co masz teraz dostępne

### Nowe pliki w `shared/`:

| Plik | Co zawiera | Dlaczego wartość |
|------|------------|------------------|
| `battlecards.md` | Analiza 5 konkurentów (VirtusLab, SoftwareMill, Xebia, Endava, EPAM) + WHITESPACE OPPORTUNITIES | Widzisz co konkurencja robi źle i gdzie są luki |
| `content_plan.md` | Plan contentowy Q2-Q3 z "Scala + AI Playbook" (10 postów) | Gotowe tematy które można przekształcić w webinary |
| `brief_webinar.md` | Specjalny brief dla webinar ideation | Konkretne zadanie dla agentów |

---

## Jak używać (Krok po kroku)

### Wariant A: Szybki start (15 min)

```bash
# 1. Upewnij się że masz wszystkie pliki
ls /root/.openclaw/workspace/scalac-council-v2/shared/
# Powinno być: brief_webinar.md, battlecards.md, content_plan.md

# 2. Uruchom orchestrator
cd scalac_council_v2
python orchestrator.py
```

```python
# 3. Spawn ENHANCED agentów (czytających battlecards)

# Marcus Enhanced (czyta battlecards + content plan)
sessions_spawn(
    runtime="subagent",
    task="""Jesteś Marcus, Offer Architect w Scalac.

PRZECZYTAJ TE PLIKI:
1. /root/.openclaw/workspace/scalac-council-v2/shared/brief_webinar.md
2. /root/.openclaw/workspace/scalac-council-v2/shared/battlecards.md  
3. /root/.openclaw/workspace/scalac-council-v2/shared/content_plan.md

Twoja rola:
- Znajdź WHITESPACE OPPORTUNITIES w battlecards
- Połącz z Playbook series z content_plan
- Zaproponuj 3 tematy webinarów
- Napisz Round 1 do discussion/round_1_marcus.md
- Final: output/marcus_webinar_proposals.md

Focus: Positioning vs konkurencję (VirtusLab, SoftwareMill, Xebia).
""",
    label="marcus-webinar"
)

# Kai Webinar (focus na copy)
sessions_spawn(
    runtime="subagent",
    task="""Jesteś Kai, Copywriter w Scalac.

PRZECZYTAJ:
1. /root/.openclaw/workspace/scalac-council-v2/shared/brief_webinar.md
2. /root/.openclaw/workspace/scalac-council-v2/shared/content_plan.md

Twoja rola:
- Które posty z Playbook (#2 RAG, #3 Akka Agents, #6 Spark) nadają się na webinary?
- Napisz tytuły, hooki, abstrakty
- Napisz Round 1 do round_1_kai.md
- Final: output/kai_webinar_proposals.md

Focus: Chwytliwe tytuły i messaging które wyróżnia się od konkurencji.
""",
    label="kai-webinar"
)

# (Opcjonalnie Elena i David w podobny sposób)
```

### Wariant B: Pełna Rada (wszystkie 4 agenci)

Użyj standardowych agentów (marcus_agent.py, elena_agent.py, kai_agent.py, david_agent.py) ale zmień brief na `brief_webinar.md`.

---

## Co dostaniesz w output

### Marcus:
```markdown
# Propozycje Webinarów - Marcus

## Webinar 1: "Akka Actors as AI Agents"
- Dlaczego: Nikt nie łączy Akka z AI agents (Whitespace #3)
- Positioning: "While others bolt AI onto Python, we architect natively in Scala"
- vs VirtusLab: Oni mają MCP, my mamy orchestration at scale
- CTA: "Download Akka + Agentic AI Reference Architecture"

## Webinar 2: "From Scala 2 to AI-Ready"
- Dlaczego: VirtusLab daje "free migration", my dajemy "AI-ready migration"
...
```

### Kai:
```markdown
# Propozycje Webinarów - Kai

## Webinar 1: Tytuły do wyboru
"Building Fault-Tolerant AI Agents with Akka"
"Why Your AI Agents Keep Failing (And How Akka Fixes It)"

## Landing Page Abstract:
[Gotowy tekst do wklejenia na landing page]

## LinkedIn Promo Posts:
[3 gotowe posty]

## Email Sequence:
[3 emaile: 3 weeks, 1 week, day-of]
```

---

## Przykładowy wynik (co się stanie)

### Po Runda 1:
**Marcus:** "Akka + Agentic AI to nasz whitespace - nikt tego nie robi"

**Kai:** "Tytuł: 'Building Fault-Tolerant AI Agents with Akka' - chwytliwy, techniczny"

**Elena:** "Ten temat generuje MQLs - naturalne przejście do Architecture Review"

**David:** "Mam listę 50 kont które aktywnie szukają agentic AI rozwiązań"

### Po Runda 2 (debaty):
**Marcus:** "Kai, 'Why Your AI Agents Keep Failing' to zbyt negative?"

**Kai:** "Nope, to pattern interrupt. CTOs są zmęczeni 'revolutionary' - chcą real solutions."

**Elena:** "Webinar 'State of Scala + AI' jest sexy, ale wymaga survey. Startujmy od Akka - mamy gotowe case study."

**David:** "Zgoda. Akka webinar to 5 tygodni do live. State of Scala to 3 miesiące (survey + analiza)."

### Final Recommendation:
**"Akka Actors as AI Agents"** wygrywa bo:
- ✅ Unikalny (tylko my możemy to zrobić - Official Akka Partner)
- ✅ Timely (agentic AI hype 2026)
- ✅ Wykonalny (5 tygodni, mamy case study)
- ✅ Lead gen (naturalne przejście do Architecture Review)

---

## Kluczowe Whitespace z Battlecards (dla referencji)

| # | Whitespace | Dlaczego to szansa | Kto konkurencja |
|---|------------|-------------------|-----------------|
| 1 | "Scala-Native AI Engineering" | Nikt nie branduje Scala+AI jako jedności | VirtusLab, SoftwareMill trzymają osobno |
| 2 | Production Readiness Framework | Brak nazwanej metodologii (Endava ma Dava.Flow) | Każdy robi "advisory" bez framework |
| 3 | Akka + Agentic AI | Actor model idealny dla AI agents | NIKTEGO nie robi eksplicytne |
| 4 | Healthcare AI + Scala | Pusta nisza (VirtusLab = insurance, SoftwareMill = fintech) | Rally Health = nasz proof point |
| 5 | State of Scala + AI Report | Brak danych branżowych | State of Scala 2025 jest, ale bez AI |
| 6 | DACH + UK Enterprise | Scalac ma Bexio, można budować | Inni focus na PL/US |

---

## Szybkie pomysły na webinary (z battlecards)

### 1. "Akka Actors as AI Agents" ⭐ (najlepszy)
**Dlaczego:** Tylko my (Official Akka Partner) możemy to zrobić
**Kontra:** VirtusLab ma MCP, SoftwareMill ma sttp-ai, ale NIE MAJĄ Akka + Agents

### 2. "Scala 2 to AI-Ready Migration"
**Dlaczego:** VirtusLab daje "free Scala 3 migration" - my dajemy "AI-ready"
**Kontra:** Bezpłatna migracja VirtusLab = commodity. AI-ready = premium.

### 3. "State of Scala + AI 2026" 
**Dlaczego:** Pierwszy taki raport. Data = authority.
**Kontra:** Nikt nie ma danych o Scala + AI adoption.

### 4. "Healthcare AI with Scala" (niszowy)
**Dlaczego:** Rally Health jako proof point. Healthcare wymaga type safety (HIPAA).
**Kontra:** VirtusLab = insurance, SoftwareMill = fintech. Healthcare = pusto.

### 5. "Private LLMs on Akka: Enterprise Guide"
**Dlaczego:** Sovereign AI trend + nasza infrastruktura Akka.
**Kontra:** Content Plan Playbook #7: "Private LLMs on Akka"

---

## Jak czytać battlecards (dla agentów)

### Sekcje do przeczytania:

1. **"WHITESPACE OPPORTUNITIES"** (linia ~450)
   - 6 konkretnych szans
   - Każda z "Action" punktem

2. **Battlecards poszczególnych konkurentów:**
   - **VirtusLab** (linia ~40): Compiler maintenance = strong, ALE Scala+AI = implicit
   - **SoftwareMill** (linia ~122): tapir/sttp = OSS cred, ALE AI to osobny team
   - **Xebia** (linia ~204): AI-first, ALE Scala buried
   - **Endava** (linia ~286): Zero Scala w AI
   - **EPAM** (linia ~368): $5B giant, ALE Scala invisible

3. **"COMPETITIVE LANDSCAPE MATRIX"** (linia ~488)
   - Tabela porównująca wszystkich
   - Scalac wygrywa w: "Scala+AI Branding" (Explicit)

---

## Jak czytać content plan (dla agentów)

### Sekcje do przeczytania:

1. **"THE CONTENT PILLARS"** - 5 filarów strategii
2. **"Pillar 1: The Scala + AI Playbook"** - 10 postów planowanych
   - #2: RAG Pipeline ← potencjał webinaru
   - #3: Akka Actors as AI Agents ← IDEALNY na webinar
   - #6: From Spark to LLMs ← enterprise appeal
3. **"Content Calendar Q2 2026"** - konkretne daty publikacji

---

## Troubleshooting

### "Agenci nie widzą battlecards.md"
```bash
# Sprawdź czy plik istnieje:
ls -la /root/.openclaw/workspace/scalac-council-v2/shared/

# Jeśli nie ma:
cp /workspaces/scalac_ai_council/scalac_battlecards.docx.md \
   /root/.openclaw/workspace/scalac-council-v2/shared/battlecards.md
```

### "Chcę użyć zwykłego briefu, nie webinar"
Po prostu użyj `shared/brief.md` zamiast `shared/brief_webinar.md` w promptach.

### "Chcę dodać więcej konkurentów do battlecards"
Edytuj `shared/battlecards.md` i dodaj nową sekcję (wzoruj się na istniejących).

---

## Podsumowanie

Z tymi plikami Twoi agenci:
1. **Wiedzą co robi konkurencja** (battlecards)
2. **Widzą luki w rynku** (whitespaces)
3. **Mają gotowe tematy do adaptacji** (content plan)
4. **Proponują webinary które wypełniają te luki**

**Wynik:** Webinary które nie tylko są technicznie credibile, ale też **pozycjonują Scalac jako jedyną firmę która łączy Scala + AI natywnie**.

---

**Gotowy do startu?**

```bash
python orchestrator.py
# Potem spawn agentów z enhanced prompts (patrz Wariant A wyżej)
```

# Integration Guide
## Jak podłączyć Radę AI do prawdziwych LLM-ów

---

## Opcja 1: Python Orchestrator (Polecana)

### Co dostajesz:
- ✅ Jeden skrypt zarządza wszystkimi 5 agentami
- ✅ Automatyczne handoff'y
- ✅ Eksport wyników do JSON
- ✅ Historia projektów

### Setup (5 minut):

**Krok 1:** Zainstaluj wymagania
```bash
pip install openai anthropic
```

**Krok 2:** Dodaj API key
```bash
export OPENAI_API_KEY="sk-..."
# lub
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Krok 3:** Uruchom projekt
```bash
python orchestrator.py --project "Team Extension Fintech" --type CORE --export
```

**Output:**
```
🚀 Inicjalizacja Rady AI...

============================================================
🎯 NOWY PROJEKT: Team Extension Fintech
📊 Type: CORE | Pipeline: 200,000 PLN | Timeline: 90d
============================================================

🎯 Marcus (Architekt Oferty): Projektuję ofertę...
🎯 Elena (Architektka Lejków): Buduję lejek...
🎯 Kai (Główny Copywriter): Piszę copy...
🎯 David (Strateg Leadów): Przygotowuję ABM...
🎯 Sofia (Strateg Treści): Planuję content...

============================================================
✅ PROJEKT ZAKOŃCZONY
============================================================

💾 Projekt zapisany: projects/team_extension_fintech.json
```

### Co się dzieje pod spodem:

1. **Marcus** czyta swój prompt z `AGENTS/marcus_offer_architect/system_prompt.md`
2. Wysyła zapytanie do OpenAI API z tym promptem + zadaniem
3. Dostaje odpowiedź (Offer Package)
4. **Elena** dostaje output Marcusa + swój prompt
5. Wysyła do API, dostaje Funnel Design
6. **Kai** i **David** działają równolegle
7. **Sofia** dostaje wyniki i robi Content Strategy
8. Wszystko zapisywane do JSON

### Koszty:
- ~5-10 wywołań API per projekt
- Koszt: ~$0.50-2.00 per projekt (zależy od modelu)
- GPT-4: droższe ale lepsze
- GPT-3.5: tańsze, szybsze

---

## Opcja 2: Make.com / Zapier (No-Code)

### Dla osób które nie programują

**Co potrzebujesz:**
- Konto Make.com (darmowe do 1000 operacji)
- OpenAI API key

**Setup:**

1. **Stwórz Scenario** w Make.com
2. **Trigger:** Webhook lub Google Sheet
3. **Moduł 1:** OpenAI - Marcus
   - System Prompt: wklej z `marcus/system_prompt.md`
   - User Message: `{{project_name}} + {{project_type}}`
   
4. **Moduł 2:** OpenAI - Elena
   - System Prompt: wklej z `elena/system_prompt.md`
   - User Message: output z modułu 1
   
5. **Moduł 3 & 4:** OpenAI - Kai + David (równolegle)

6. **Moduł 5:** OpenAI - Sofia

7. **Output:** Google Docs / Notion / Email

**Zalety:**
- ✅ Zero kodu
- ✅ Visual builder
- ✅ Integracje (Slack, Email, Notion)

**Wady:**
- ❌ Płatne (po 1000 operacji)
- ❌ Wolniejsze
- ❌ Mniej elastyczne

---

## Opcja 3: ChatGPT Custom GPT (Najszybsze)

### Dla pojedynczych projektów

**Krok 1:** Wejdź na chat.openai.com

**Krok 2:** Stwórz Custom GPT:
- Kliknij "Explore" → "Create a GPT"
- Nazwa: "Rada AI Scalac"

**Krok 3:** Wklej w "Instructions":
```
Jesteś Radą AI Scalac - zespołem 5 agentów.

Twoje zadanie: Zarządzać projektami marketingowymi.

AGENCI:
1. MARCUS - Architekt Oferty (Gap Selling, StoryBrand, Pricing)
2. ELENA - Architektka Lejków (MEDDIC, JOLT, Funnel Design)
3. KAI - Copywriter (AIDA, Big 5, SUCCESs)
4. SOFIA - Strateg Treści (Content Tilt, SEO, Epic Content)
5. DAVID - Strateg Leadów (ABM, Dream 100, Sales Engagement)

ZASADY:
- Zawsze zacznij od Marcusa (projektowanie oferty)
- Potem przejdź do Eleny (lejek)
- Kai i David mogą działać równolegle
- Sofia na końcu (content strategy)
- Robisz handoff'y między agentami
- Output format: strukturalny markdown

80/20 RULE:
- 80% effort na CORE (Team Extension)
- 20% effort na AI (Sovereign AI)

Kiedy użytkownik podaje projekt:
1. Zidentyfikuj czy to CORE, AI, czy BUNDLE
2. Przeprowadź przez wszystkich agentów
3. Daj gotowy plan wykonawczy
```

**Krok 4:** Wklej w "Knowledge":
- Wszystkie pliki z `AGENTS/*/system_prompt.md`
- `WORKFLOW/handoff_templates.md`
- `TOOLKIT/templates/*`

**Krok 5:** Zapisz i używaj:
```
"Zrób projekt: Team Extension dla fintechów Series B"
```

---

## Opcja 4: CLI Tool (Dla developerów)

### Prostsza wersja orchestratora

Stworzyłem też `rada` CLI:

```bash
# Instalacja
pip install rada-cli

# Użycie
rada init
rada project new "Team Extension" --type CORE
rada agents run --all
rada export --format markdown
```

Ale to wymaga publikacji na PyPI (możemy zrobić jeśli chcesz).

---

## Opcja 5: API Direct (Dla zaawansowanych)

### Bezpośrednie wywołanie API

```python
import openai

# Marcus
marcus_prompt = open("AGENTS/marcus/system_prompt.md").read()

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": marcus_prompt},
        {"role": "user", "content": "Zaprojektuj ofertę X"}
    ]
)

offer = response.choices[0].message.content

# Elena
elena_prompt = open("AGENTS/elena/system_prompt.md").read()

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": elena_prompt},
        {"role": "user", "content": f"Zbuduj lejek dla: {offer}"}
    ]
)

funnel = response.choices[0].message.content
```

---

## Porównanie Opcji

| Opcja | Kod | Koszt | Czas Setup | Idealne dla |
|-------|-----|-------|------------|-------------|
| **Python Orchestrator** | Minimalny | $0.50/projekt | 5 min | Regularne użycie |
| **Make.com** | Zero | $9/miesiąc | 30 min | No-code preferencja |
| **Custom GPT** | Zero | $20/miesiąc | 15 min | Szybkie prototypy |
| **CLI** | Minimalny | $0.50/projekt | 2 min | Developerzy |
| **API Direct** | Pełny | $0.50/projekt | 60 min | Custom integracje |

---

## Moja Rekomendacja

### Jeśli nie programujesz:
**Custom GPT** - najszybszy start, działa od razu

### Jeśli programujesz trochę:
**Python Orchestrator** - zrób `python orchestrator.py --help`

### Jeśli robisz 10+ projektów/miesiąc:
**Make.com** - zautomatyzuj całkowicie

---

## Troubleshooting

### "Rate limit exceeded"
→ Dodaj `time.sleep(1)` między wywołaniami

### "Context too long"
→ Użyj GPT-4-Turbo (128k kontekst) lub skróć prompt

### "Output nie taki jak chcę"
→ Dodaj "Output format: JSON" lub konkretny template

### "Za drogie"
→ Użyj GPT-3.5 dla prostych zadań, GPT-4 tylko dla Marcusa i Eleny

---

## Next Steps

1. **Wybierz opcję** z powyższych
2. **Przejdź przez Quick Start:** `QUICKSTART.md`
3. **Uruchom pierwszy projekt:** `python orchestrator.py --project "Test" --type CORE`
4. **Dostosuj:** Edytuj prompt'y w `AGENTS/` pod swoje potrzeby

---

**Potrzebujesz pomocy z setup?** Napisz do mnie!

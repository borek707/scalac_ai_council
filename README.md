# Rada AI Scalac - Multi-Agent Marketing Council

4 agenci AI pracują równolegle i przygotowują kompletny plan marketingowo-sprzedażowy: oferta, funnel, copy oraz ABM.

---

## Co robi ta Rada i po co?

### Problem
Tradycyjnie jedna osoba tworzy plan marketingowy — np. VP Sales lub Product Lead. To zajmuje dni lub tygodnie, bo trzeba:
1. Wymyslić pozycjonowanie i pricing.
2. Zaprojektować funnel od acquisition do close.
3. Napisać wszystkie materiały.
4. Wybrać konta i budować strategie outreachowe.

A wszystko to robi jeden mózg z ograniczonymi perspektywami.

### Rozwiązanie
Tutaj pracuje **4 specjalistów jednocześnie**, każdy odpowiada za inny obszar. Ale najważniejsze — **dyskutują ze sobą** i się nawzajem kwestionują. 

Zamiast jednego planu — dostajesz plan, który przeszedł krytykę wszystkich czterech perspektyw.

---

## Jak to działa — prosty przykład

Wyobraź sobie taki dialog:

**Marcus** (Offer Architect): *"Wyceniam Team Extension w DACH na CHF 25K/miesiąc per senior. Jest to porównywalne z lokalnym kosztem CHF 180K rocznie."*

**Elena** (Funnel Architect): *"Czekaj. Przy tej cenie conversion na discovery call spada do 0.3%. My szukamy 5 dużych dealów w 6 miesięcy, ale pipeline nie przetrwa przy tej konwersji."*

**Marcus**: *"Dobry punkt. Obniżam Starter do CHF 19K, ale Scale i Enterprise zostawiam wysoko. To powinno być lepiej."*

**Kai** (Copywriter): *"Zaraz, DACH nie będzie rozmawiać o cenie na landing page. CTO rozumie koszt porównawczo, ale nie lubi go widzieć na stronie. Zróbmy TCO Calculator za email-gate."*

**David** (Lead Strategist): *"A ja dodaję: w kontach które znalazłem w danych prospektowych, mają aktywne oferty pracy dla Scala developerów. Otwieramy z tym — 'widzieliśmy, że szukasz senior Scala inżyniera, zamiast hiring przez 6 miesięcy...'."*

Po 2-3 rundach takiej dyskusji masz plan, który **przeszedł krytykę** wszystkich czterech perspektyw. I właśnie taki plan jest w `output/FINAL_PROPOSAL.md`.

---

## Czym są ci czterej agenci

### Marcus - Offer Architect
- Decyduje: ile kosztuje, jak to pozycjonujemy, jaki jest hook do klienta.
- Używa: Gap Selling, Challenger Sale, strategie pricing.
- Output: sekcja OFFER — positioning per market, pricing tiers, Challenger pitch.

### Elena - Funnel Architect  
- Decyduje: jak leady wchodzą, jaki jest path do conversion, ile czasu trwa sprzedaż.
- Używa: MEDDIC (framework kwalifikacji), pipeline math, nurture strategy.
- Output: sekcja LEJEK — funnel per geo, MEDDIC questions, realistic conversions.

### Kai - Copywriter
- Decyduje: co się pisze na landing page, jakie są subject lines emaili, co się mówi na LinkedInie.
- Używa: They Ask You Answer, StoryBrand, PAS copywriting.
- Output: sekcja COPY — hero headlines, cold emails, webinar invites per locale.

### David - Lead Strategist
- Decyduje: które konta targetujemy konkretnie, w jakiej kolejności, jakie triggery używamy.
- Używa: ABM Playbook, Signal-Based Selling, 12-Touch Cadence.
- Output: sekcja KONTA — Dream 20 tabela, konkretne e-maile i adresy e-mail, 12-touch plan outreach.

---

## Dyskusja między agentami

Agenci **nie rozmawiają w czacie**. Zamiast tego:

1. **Runda 1:** Każdy pisze swoje stanowisko niezależnie. Marcus pisze ofertę, Elena pisze funnel, Kai pisze copy, David wybiera konta. To wszystko jednocześnie.

2. **Runda 2:** Każdy czyta co napisali pozostali i pisze odpowiedź. "Ale Marcus, jeśli pricing będzie tak wysoki, to konwersja spadnie." Albo: "Kai, to jest zbyt techniczne dla CTO."

3. **Runda 3:** Dochodzą do konsensusu lub spisują gdzie się nie zgadzają.

Wszystko jest zapisane w plikach (Runda 1 w `discussion/round_1_*.md`, Runda 2 w `discussion/round_2_*.md`). Dzięki temu można śledzić całą debatę.

---

## Co dostajesz na koniec

Plik `output/FINAL_PROPOSAL.md` zawiera:

- **OFFER** — konkretne pricing, positioning per kraj, Challenger pitch z danymi TCO.
- **LEJEK** — funnel per geography, ile discovery calls, co to kosztuje, jak długo trwa.
- **COPY** — gotowe do wklejenia: hero headlines, cold email templates, webinar zaproszenia.
- **KONTA** — konkretne 20 firm, z emailami CTOs, 12-touch outreach schedule.

Wszystko to jest spójne — to nie jest 4 sklejone ze sobą dokumenty, tylko jeden plan, który przeszedł krytykę wszystkich czterech perspektyw.

---

## Konkretny przykład — kampania JVM/Rust dla DACH/London/Stockholm

W tym repo jest już gotowe uruchomienie kampanii. Agenci dyskutowali o tym, jak sprzedawać Team Extension w trzech geografiach:

- **DACH pricing:** CHF 19-22K Starter (suchy, liczbowy, TCO-focused)
- **London positioning:** "7 months hiring pipeline, 2 weeks ours" (velocity story)
- **Nordic framing:** "Zero arbetsgivaravgifter + 30-day exit" (risk reduction)

Każdy z 4 agentów miał inny pomysł na start. Po 2 rundach osiągnęli konsensus — ceny, messaging i wybór kont były już spójne.

To wszystko masz w `output/FINAL_PROPOSAL.md` — czyli ostateczny plan kampanii.

---

## Po co mi to?

Jeśli pracujesz w Scalac i musisz:
- Uruchomić nową kampanię sprzedażową (np. dla nowego segmentu),
- Wycenić nową ofertę,
- Zbudować funnel dla nowej geografii,
- Wybrać Dream 100 kont i outreach sequence,

...zamiast robić to sam lub prosić cztery różne osoby — robisz to wszystko **w 30-60 minut** za pomocą czterech specjalistów agentów. Każdy może pracować równolegle, dyskusja jest natychmiastowa.

---

## Co jest w tym repo

Repo zawiera dwa poziomy:

1. Warstwa orkiestracji agentów dla VS Code Copilot i Cursor.
2. Uniwersalny, przenośny system w Pythonie w katalogu `scalac_council_v2`, który działa w wielu IDE.

W praktyce masz gotowy workflow:

- przygotuj brief w `shared/brief.md`,
- wygeneruj prompty,
- uruchom 4 agentów równolegle,
- złóż finalny dokument.

---

## Aktualny stan (zweryfikowany)

- W repo jest kompletne uruchomienie kampanii JVM/Rust dla DACH, London, Stockholm.
- Dyskusja ma 2 rundy i 8 plików w `scalac_council_v2/shared/discussion/`.
- Final jest zapisany w `scalac_council_v2/output/FINAL_PROPOSAL.md`.
- Przykładowe briefy i battlecards są dostępne w `scalac_council_v2/shared/`.

---

## Struktura katalogów

```text
scalac_ai_council/
|
|- README.md
|- scalac_battlecards.docx.md
|- scalac_content_plan.docx.md
|- .gitignore
|
|- .github/
|  |- agents/
|     |- scalac-council.agent.md
|     |- marcus.agent.md
|     |- elena.agent.md
|     |- kai.agent.md
|     |- david.agent.md
|
|- .cursor/
|  |- rules/
|     |- scalac-council.mdc
|
|- scalac_council_v2/
    |- orchestrator.py
    |- README.md
    |- ARCHITECTURE.md
    |- WEBINAR_GUIDE.md
    |
    |- agents/
    |  |- marcus_agent.py
    |  |- marcus_agent_enhanced.py
    |  |- elena_agent.py
    |  |- kai_agent.py
    |  |- kai_webinar.py
    |  |- david_agent.py
    |
    |- prompts/
    |  |- marcus_prompt.md
    |  |- elena_prompt.md
    |  |- kai_prompt.md
    |  |- david_prompt.md
    |
    |- shared/
    |  |- brief.md
    |  |- brief_webinar.md
    |  |- battlecards.md
    |  |- content_plan.md
    |  |- discussion/
    |     |- round_1_marcus.md
    |     |- round_1_elena.md
    |     |- round_1_kai.md
    |     |- round_1_david.md
    |     |- round_2_marcus.md
    |     |- round_2_elena.md
    |     |- round_2_kai.md
    |     |- round_2_david.md
    |
    |- output/
        |- FINAL_PROPOSAL.md
```

---

## Dane prospektowe (niepubliczne)

**UWAGA: Dane potencjalnych klientów nie są dostępne w tym publicznym repozytorium ze względów prywatności i bezpieczeństwa.**

W rzeczywistej implementacji system przetwarza dane z plików CSV zawierających:
- Listy CTO i decyzyjnych osób w firmach technologicznych
- Oferty pracy wskazujące na potrzeby rekrutacyjne
- Dane kontaktowe i profile LinkedIn

Te dane są przetwarzane do postaci pliku `target_accounts.md` zawierającego intelligence o kontach.

**Aby używać systemu:**
- Przygotuj własne pliki CSV z danymi prospektowymi (zachowując prywatność)
- Umieść je w katalogu `csv/` (który jest ignorowany przez .gitignore)
- Uruchom `python orchestrator.py` aby przetworzyć dane do `shared/target_accounts.md`

---

## Dwa sposoby pracy

### 1) VS Code Copilot native agents

Konfiguracja jest w `.github/agents/`.

- `scalac-council.agent.md` - orchestrator, który deleguje do 4 agentów.
- `marcus.agent.md`, `elena.agent.md`, `kai.agent.md`, `david.agent.md` - agenci wyspecjalizowani.

To podejście jest wygodne, kiedy chcesz pracować komendą typu `@Scalac Council ...`.

### 2) Uniwersalny orchestrator Python

Skrypt: `scalac_council_v2/orchestrator.py`.

Działa tak:

1. Wczytuje kontekst z:
    - `shared/brief.md`
    - `shared/battlecards.md`
    - `shared/content_plan.md`
    - `shared/target_accounts.md` (jeśli istnieje)
    - `shared/discussion/*.md`
2. Generuje self-contained prompty do `prompts/*.md`.
3. Dla Kimi Code próbuje auto-spawn przez `sessions_spawn`.
4. Dla innych IDE drukuje instrukcje uruchomienia.

Flagi:

- `python orchestrator.py` - setup, status, generacja promptów, ewentualny spawn.
- `python orchestrator.py --monitor` - status dyskusji i ewentualna auto-agregacja po konsensusie.
- `python orchestrator.py --final` - ręczna agregacja finalnego dokumentu.

---

## Jak przygotować brief

Edytuj `scalac_council_v2/shared/brief.md` przed nową kampanią.

Przykładowy minimalny szablon:

```markdown
# Brief Projektu: [nazwa]

## Projekt: [1 zdanie]

### Kontekst
[dlaczego ten temat teraz]

### Cel
[np. pipeline, discovery calls, SQL]

### Target
- Segment: [...]
- Geo: [...]
- Decision Maker: [...]
- Pain Points: [...]
- Budget: [...]

### Constraints
- Timeline: [...]
- Zasoby: [...]
- Pipeline target: [...]

### Deliverables
1. Marcus: [...]
2. Elena: [...]
3. Kai: [...]
4. David: [...]

### Konta do rozważenia (opcjonalne)
[lista firm i sygnałów]
```

Im więcej konkretu, tym lepszy output.

---

## Differential injection danych (jak działa)

W `orchestrator.py` jest logika:

- David dostaje pełne dane z `target_accounts.md` (jeśli plik istnieje).
- Marcus, Elena i Kai dostają tylko sekcje `## 4. Key Intelligence` (lub fallback na pierwsze 2000 znaków, jeśli nagłówek nie istnieje).

To celowe, bo David odpowiada za ABM i potrzebuje pełnych danych kont.

---

## Agenci i role

### Marcus - Offer Architect

- Projektuje pozycjonowanie i pricing.
- Pliki: `agents/marcus_agent.py`, `agents/marcus_agent_enhanced.py`.

### Elena - Funnel Architect

- Projektuje funnel, kwalifikacje i pipeline.
- Plik: `agents/elena_agent.py`.

### Kai - Copywriter

- Tworzy copy: hero, e-maile, hooki.
- Pliki: `agents/kai_agent.py`, `agents/kai_webinar.py`.

### David - Lead Strategist

- Prowadzi ABM, wybiera konta, buduje sekwencje.
- Plik: `agents/david_agent.py`.

---

## Jak uruchomić (workflow krok po kroku)

```bash
cd scalac_council_v2
python orchestrator.py
```

Po tym:

1. Otwórz 4 sesje/agenty równolegle.
2. Użyj plików z `prompts/`:
    - `prompts/marcus_prompt.md`
    - `prompts/elena_prompt.md`
    - `prompts/kai_prompt.md`
    - `prompts/david_prompt.md`
3. Po zakończeniu rund uruchom:

```bash
python orchestrator.py --final
```

4. Odbierz final:

```bash
cat output/FINAL_PROPOSAL.md
```

Monitor statusu:

```bash
python orchestrator.py --monitor
```

---

## Agregacja finala (co skrypt składa)

Przy `--final` orchestrator próbuje dołączyć:

- `output/marcus_offer.md`
- `output/elena_funnel.md`
- `output/kai_copy.md`
- `output/david_abm.md`

Następnie zapisuje wspólny dokument jako `output/FINAL_PROPOSAL.md`.

Jeśli któregoś pliku cząstkowego brakuje, skrypt to raportuje i nadal tworzy final z dostępnych fragmentów.

---

## Webinar mode

Tryb webinarowy jest opisany w `scalac_council_v2/WEBINAR_GUIDE.md`.

Powiazane pliki:

- `shared/brief_webinar.md`
- `agents/marcus_agent_enhanced.py`
- `agents/kai_webinar.py`

To osobna sciezka, kiedy celem sa pomysly webinarowe i messaging wydarzenia.

---

## Co dostajesz out-of-the-box

W repo jest juz historyczny material referencyjny:

- komplet kontekstu (`battlecards.md`, `content_plan.md`, `target_accounts.md`),
- zapis dyskusji agentow (runda 1 i 2),
- finalny dokument kampanii w `output/FINAL_PROPOSAL.md`.

Dzieki temu mozesz:

1. wystartowac nowa kampanie od razu (podmieniajac brief),
2. albo analizowac poprzedni run jako benchmark.

---

## Najczestsze komendy

```bash
# 1) Generacja promptow i instrukcji
cd scalac_council_v2 && python orchestrator.py

# 2) Status rund
python orchestrator.py --monitor

# 3) Reczna agregacja finala
python orchestrator.py --final

# 4) Podglad rundy
cat shared/discussion/round_1_marcus.md

# 5) Lista wszystkich postow
ls shared/discussion/
```

---

## Dokumentacja techniczna

- Architektura: `scalac_council_v2/ARCHITECTURE.md`
- Szczegoly runtime i przykladow: `scalac_council_v2/README.md`
- Tryb webinar: `scalac_council_v2/WEBINAR_GUIDE.md`

---

## Uwaga o aktualizacji danych

Gdy dodajesz nowe dane prospektowe:

1. przygotuj pliki CSV z danymi kontaktowymi (zachowując prywatność),
2. umieść je w katalogu `csv/` (ignorowanym przez .gitignore),
3. uruchom `python orchestrator.py` aby przetworzyć dane do `shared/target_accounts.md`,
4. wygenerowane prompty od razu uwzględnią nowe dane.

To wszystko - nie trzeba zmieniać kodu orchestratora.

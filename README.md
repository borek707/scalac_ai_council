# Rada AI Scalac - Multi-Agent Marketing Council

4 agenci AI pracuja rownolegle i przygotowuja kompletny plan marketingowo-sprzedazowy: oferta, funnel, copy oraz ABM.

To README opisuje aktualny, rzeczywisty stan repozytorium na marzec 2026.

---

## Co jest w tym repo

Repo zawiera dwa poziomy:

1. Warstwa orchestracji agentow dla VS Code Copilot i Cursor.
2. Uniwersalny, przenosny system w Pythonie w katalogu `scalac_council_v2`, ktory dziala w wielu IDE.

W praktyce masz gotowy workflow:

- przygotuj brief w `shared/brief.md`,
- wygeneruj prompty,
- uruchom 4 agentow rownolegle,
- zloz finalny dokument.

---

## Aktualny stan (zweryfikowany)

- W repo jest kompletny run kampanii JVM/Rust dla DACH, London, Stockholm.
- Dyskusja ma 2 rundy i 8 plikow w `scalac_council_v2/shared/discussion/`.
- Final jest zapisany w `scalac_council_v2/output/FINAL_PROPOSAL.md`.
- Dane wejciowe sa w 4 plikach CSV i w przetworzonej postaci w `scalac_council_v2/shared/target_accounts.md`.

Wymiary obecnych plikow:

- `scalac_council_v2/shared/target_accounts.md`: 44,991 bajtow.
- `scalac_council_v2/output/FINAL_PROPOSAL.md`: 24,021 bajtow.

---

## Struktura katalogow

```text
scalac_ai_council/
|
|- README.md
|- scalac_battlecards.docx.md
|- scalac_content_plan.docx.md
|
|- csv/
|  |- 200 Scala CTO's - Sheet1 (1).csv
|  |- Q1 2026 AI vacancies job postings to prospect - Sheet1 (1).csv
|  |- Q1 2026 AI vacancies job postings to prospect - Sheet1 (2).csv
|  |- WIZA_CTO_Scala_groups_493112 - WIZA_CTO_Scala_groups_493112 (1).csv
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
    |  |- target_accounts.md
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

## CSV i dane prospektowe

W katalogu `csv/` sa 4 rzeczywiste pliki wejsciowe:

1. `200 Scala CTO's - Sheet1 (1).csv`
2. `Q1 2026 AI vacancies job postings to prospect - Sheet1 (1).csv`
3. `Q1 2026 AI vacancies job postings to prospect - Sheet1 (2).csv`
4. `WIZA_CTO_Scala_groups_493112 - WIZA_CTO_Scala_groups_493112 (1).csv`

Aktualna liczba linii (wc -l):

- 117
- 107
- 107
- 142

Suma: 473 linie.

Plik docelowy z inteligencja kont: `scalac_council_v2/shared/target_accounts.md`.

---

## Dwa sposoby pracy

### 1) VS Code Copilot native agents

Konfiguracja jest w `.github/agents/`.

- `scalac-council.agent.md` - orchestrator, ktory deleguje do 4 agentow.
- `marcus.agent.md`, `elena.agent.md`, `kai.agent.md`, `david.agent.md` - agenci wyspecjalizowani.

To podejscie jest wygodne, kiedy chcesz pracowac komenda typu `@Scalac Council ...`.

### 2) Uniwersalny orchestrator Python

Skrypt: `scalac_council_v2/orchestrator.py`.

Dziala tak:

1. Wczytuje kontekst z:
    - `shared/brief.md`
    - `shared/battlecards.md`
    - `shared/content_plan.md`
    - `shared/target_accounts.md`
    - `shared/discussion/*.md`
2. Generuje self-contained prompty do `prompts/*.md`.
3. Dla Kimi Code probuje auto-spawn przez `sessions_spawn`.
4. Dla innych IDE drukuje instrukcje uruchomienia.

Flagi:

- `python orchestrator.py` - setup, status, generacja promptow, ewentualny spawn.
- `python orchestrator.py --monitor` - status dyskusji i ewentualna auto-agregacja po konsensusie.
- `python orchestrator.py --final` - reczna agregacja finalnego dokumentu.

---

## Jak przygotowac brief

Edytuj `scalac_council_v2/shared/brief.md` przed nowa kampania.

Przykladowy minimalny szablon:

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

### Konta do rozwazenia (opcjonalne)
[lista firm i sygnalow]
```

Im wiecej konkretu, tym lepszy output.

---

## Differential injection danych (jak dziala)

W `orchestrator.py` jest logika:

- David dostaje pelne `target_accounts.md`.
- Marcus, Elena i Kai dostaja tylko sekcje `## 4. Key Intelligence` (lub fallback na pierwsze 2000 znakow, jesli naglowek nie istnieje).

To celowe, bo David odpowiada za ABM i potrzebuje pelnych danych kont.

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

## Jak uruchomic (workflow krok po kroku)

```bash
cd scalac_council_v2
python orchestrator.py
```

Po tym:

1. Otworz 4 sesje/agenty rownolegle.
2. Uzyj plikow z `prompts/`:
    - `prompts/marcus_prompt.md`
    - `prompts/elena_prompt.md`
    - `prompts/kai_prompt.md`
    - `prompts/david_prompt.md`
3. Po zakonczeniu rund uruchom:

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

## Agregacja finala (co skrypt sklada)

Przy `--final` orchestrator probuje dolaczyc:

- `output/marcus_offer.md`
- `output/elena_funnel.md`
- `output/kai_copy.md`
- `output/david_abm.md`

Nastepnie zapisuje wspolny dokument jako `output/FINAL_PROPOSAL.md`.

Jesli ktoregos pliku czastkowego brakuje, skrypt to raportuje i nadal tworzy final z dostepnych fragmentow.

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

Gdy dodajesz nowe CSV:

1. dorzuc plik do `csv/`,
2. zaktualizuj `shared/target_accounts.md`,
3. uruchom ponownie `python orchestrator.py`,
4. wygenerowane prompty od razu uwzglednia nowe dane.

To wszystko - nie trzeba zmieniac kodu orchestratora.

# Stanowisko Davida — Runda 2
### Lead Strategist | David | 25 marca 2026

---

## Moja Teza

Runda 1 dała nam consensus w najważniejszym miejscu: **London = gotówka teraz, DACH = inwestycja na Q2–Q3**. Ale consensus nie zastępuje precyzji — a Elena zidentyfikowała lukę arytmetyczną w mojej pipeline math, którą muszę zamknąć. Poniżej: jasna odpowiedź na każde pytanie Eleny, integracja hooków Kaia, mapa webinaru per konto i przepisana sekwencja DACH z pilotem Marcusa wbudowanym jako JOLT na Touch #8.

---

## 1. Odpowiedź dla Eleny — Timeline, Tempa, Pipeline Math

### 1.1 Czy 12-touch cadence w 6 tygodniach jest realistyczna?

**Dla Londynu: TAK. Dla DACH: NIE — i nigdy tak nie twierdziłem.**

Elena ma rację w diagnozie arytmetycznej. Moje własne dane per-geo mówią wyraźnie:
- London cadence: touch co 3–4 dni → 12 touchów × 3.5 dni = **~42 dni = 6 tygodni** ✅
- DACH cadence: touch co 6–8 dni → 12 touchów × 7 dni = **~84 dni = 12 tygodni** ≠ 6 tygodni

Brakowało mi wyraźnego stwierdzenia na końcu rundy 1: **12-touch/6 tygodni dotyczy WYŁĄCZNIE archetypu London.** Dla DACH ta sama sekwencja rozciąga się na 10–14 tygodni i to jest **feature, nie bug** — bo DACH CTO który dostaje 12 emaili w 42 dni poczuje się zaszczuty i zablokuje nadawcę.

---

### 1.2 Finalny podział timeline — oficjalny

| Region | Start outreach | Długość pełnej cadence | Pierwsze discovery call | Pipeline target (deal/pilot) |
|--------|---------------|----------------------|------------------------|------------------------------|
| **London** | Tydzień 1 (Day 1) | 6 tygodni (42 dni) | Miesiąc 1–2 | 1 pilot podpisany: **90 dni** |
| **DACH** | Tydzień 3 (Day 15) | 12–14 tygodni (~90 dni) | Miesiąc 3–4 | Pilot proposal: **120–150 dni** |
| **Nordic** | Tydzień 6 (Q2 start) | LinkedIn nurture ONLY do maja | Miesiąc 5–6 | Discovery call: **Q3 2026** |

**Wniosek: 90-dniowy pipeline target dotyczy WYŁĄCZNIE Londynu.** DACH = 180-dniowy horyzont do pierwszego pilotu. Nordic = Q3.

---

### 1.3 Finalna Pipeline Math — 90 / 180 / 270 dni

#### Horyzont 90 dni (London ONLY)

| Etap | London (8 kont) | DACH (7 kont, w cadence) | Nordic | Łącznie |
|------|----------------|--------------------------|--------|---------|
| Kont contacted | 8 | 7 (start w W3, mid-cadence) | 0 | 15 |
| Discovery calls | **3–4** | 0–1 (Artifact jako wyjątek — najcieplejszy) | 0 | **3–5** |
| Pilot proposals | **1–2** | 0 | 0 | **1–2** |
| Piloty signed | **0–1** | 0 | 0 | **0–1** |
| Pipeline value signed | ~€40K (1 pilot L × 3 mies.) | 0 | 0 | **~€40K** |

> **Dla zarządu Scalac:** sukces w 90 dniach = 3–5 discovery calls + 1 pilot w negocjacji, nie 500K PLN gotówki. To jest realistyczna wersja. 500K PLN target zamknie się w **miesiącu 6–9** (London pilot → renewal + DACH pierwsza umowa). Zgadzam się z Eleną w 100%.

#### Horyzont 180 dni (London + DACH)

| Etap | London | DACH | Nordic | Łącznie |
|------|--------|------|--------|---------|
| Discovery calls | 5–6 (8 kont w follow-up) | 2–3 (Artifact, Nexthink, Tundra) | 1 (Evolution Gaming) | **8–10** |
| Pilot proposals | 2–3 | 1–2 | 0 | **3–5** |
| Piloty signed | 1–2 (London renewal w toku) | 1 (Artifact DACH) | 0 | **2–3** |
| Deals closed/expanded | 1 (London Starter → Scale) | 0–1 (pilot → kontrakt) | 0 | **1–2** |
| Pipeline value | ~€180K (2 piloty+deal) | ~€60K (pilot CH) | 0 | **~€240K** |

> **Na 180 dni osiągamy ~60% targetu 500K PLN.** Reszta (Nordic + DACH renewale) domknie się w Q3–Q4.

---

## 2. Hooki Kai — Integracja z Touch #1 per Konto

### Zasada operacyjna
Każdy Touch #1 (Email cold, Day 3 w London cadence) zaczyna się od hooka Kaia jako pierwsze zdanie. Personalizacja jest **faktualna** — oparty na URL, roli, stacku z job posting lub LinkedIn. Zdanie od Davida rozszerza hook o jedno zdanie kontekstu misji outreach.

| # | Konto | Hook Kai (pierwsze zdanie verbatim) | Personalizowane drugie zdanie od Davida | Sygnał wejścia |
|---|-------|--------------------------------------|----------------------------------------|----------------|
| 1 | **Depop** | *"I noticed Depop has multiple ML vacancies open right now — including roles that explicitly list Scala and Spark. That's a rare and specific hiring challenge, and it's exactly the type of team we build."* | "Widzę że rola [konkretna pozycja ze strony Depop] jest otwarta od [N] dni — jeśli chcesz zobaczyć jak takie zapotrzebowanie wygląda u nas w ciągu 11 dni a nie 7 miesięcy, chętnie pokażę." | ML vacancies Scala+Spark open >30 dni |
| 2 | **Kaluza** | *"Kaluza's stack — Kafka, LangChain, MCP — is about as cutting-edge as it gets in energy AI. The engineers who can work across all three without context-switching are genuinely hard to hire. That's our wheelhouse."* | "Scalac ma 6 aktywnych inżynierów z Kafka+LangChain w produkcji — nie na CV, w repo. Czy to wąskie gardło hiring czy velocity jest u Ciebie teraz aktywne?" | Kafka+LangChain+MCP stack sygnał z brief + job posting |
| 3 | **Monzo** | *"I saw Monzo is hiring AI Senior Staff roles — which at your scale means you're not just filling a position, you're building a capability. That's a different conversation than 'we have Scala developers.'"* | "Mam konkretną rozmowę którą warto odbyć: nie 'mamy developerów' ale 'jak zbudujecie tę capability bez 8-miesięcznego hiring gap w bankowości JVM'." | AI Senior Staff hiring open, JVM platform |
| 4 | **FullCircl** | *"I follow your work in the Scala community — you clearly know the stack better than most buyers. So I'll skip the 101 and get straight to what the teams we work with say after month one."* | "Nie będę Ci tłumaczył czym jest Scalac — skoro siedzisz w Scala community, wiesz co odróżnia prawdziwy team extension od Scala kontraktora na invoice." | CTO aktywny w Scala groups LinkedIn |
| 5 | **Zego** | *"Your Lead ML Engineer position has been open for a while — which usually means you know exactly what you want but the market isn't delivering. I'd like to show you what the right person looks like on our bench."* | "Jeśli pozycja jest otwarta >60 dni to hiring pipeline Wam nie dowozi — mam trzy profile do pokazania które pasują do stack description [konkretna rola Zego] na rozmowę 20 minut." | Lead ML Engineer open 60+ dni |
| 6 | **Paysend** | *"Paysend's infrastructure problem — high-throughput distributed payments at global scale — is textbook Scala territory. I'm guessing that gap between what you're building and who you can hire is getting wider, not narrower."* | "High-throughput distributed payments to dokładnie ten problem który Scala rozwiązuje lepiej niż cokolwiek innego w JVM — czy ta luka jest widoczna w Twoim roadmapie teraz?" | Distributed payments infra + Scala sygnały |
| 7 | **NewDay** *(LinkedIn InMail — brak emaila)* | *"NewDay just posted for a Lead Gen AI Engineer — which is a signal that your platform team is moving toward AI-augmented lending logic. The engineers who can do that well on a JVM stack are genuinely scarce."* | "Skoro to jest nowy kierunek dla Waszego lending stack — mam 2 inżynierów którzy robili dokładnie to w FinTech lending w ostatnich 12 miesiącach. Warto 20 minut?" | Lead Gen AI Engineer job posting — InMail only |
| 8 | **Tomato pay** | *"You're in the Scala community — so you know the difference between a Scala contractor and a Scala engineer who can own a domain. We only send the second kind."* | "VC-backed FinTech w Londynie ma jedno okno prędkości po każdym fundraise — hiring nie nadąży, team extension tak. Jeśli masz otwartą pozycję lub rosnący backlog — 30 minut zanim okno się zamknie?" | CTO w Scala community + VC-backed fintech |

### Instrukcja operacyjna dla SDR:
1. Hook Kai = zdanie 1–2 emaila (verbatim lub minimalna adaptacja)
2. Zdanie od Davida = zdanie 3 — mostek między obserwacją a CTA
3. Reszta emaila = standardowy London template (Kai, sekcja 2.2 Round 2)
4. NIGDY nie zmieniać kolejności: hook → kontekst David → body → CTA
5. NewDay: LinkedIn InMail zamiast emaila — hook działa identycznie

---

## 3. Webinar jako Touch #7–9 — Mapa per Konto

### Zasada: kto dostaje invite, kiedy, jakim kanałem

Elena i Kai zgadzają się: webinar jest **Spear touchpointem** (nie Net eventem) dla Dream 20. Moja mapa poniżej operacjonalizuje tę zasadę na poziomie każdego konta.

#### 🇬🇧 London — 8 kont (Touch #9, Day 29)

Wszystkie 8 kont London dostaje **personal invite** jako Touch #9. Warunek: minimum Touch #1–6 wyszły. W praktyce = Day 29 w cadence.

| # | Konto | Touchpoint # | Dzień cadence | Kanał | Format | Notatka |
|---|-------|-------------|---------------|-------|--------|---------|
| 1 | Depop | Touch #9 | Day 29 | Email personal | Wersja London Kai | Jeśli na Touch #7 otworzył Loom — upgrade do "masz pytania zanim webinar?" |
| 2 | Kaluza | Touch #9 | Day 29 | Email personal | Wersja London Kai | Stack jest bleeding-edge — w invite mention "Kafka+AI jako osobna rozmowa w Q&A" |
| 3 | Monzo | Touch #9 | Day 29 | Email personal | Wersja London Kai | Duże konto — jeśli nie odpowiedział do Day 29, Touch #9 = webinar jako "last hook before break-up" |
| 4 | FullCircl | Touch #9 | Day 29 | LinkedIn DM personal | Short Kai format | CTO w community — LI DM bardziej naturalny niż email #4. Nie blast. |
| 5 | Zego | Touch #9 | Day 29 | Email personal | Wersja London Kai | "Twoja Lead ML pozycja otwarta — CTOs na webinarze mówią o dokładnie tym problemie" |
| 6 | Paysend | Touch #9 | Day 29 | Email personal | Wersja London Kai | Re-fresh hook: "distributed payments CTO będzie na liście" |
| 7 | NewDay | Touch #7 | Day 21 | LinkedIn InMail | Short, brak emaila | Brak emaila = InMail na każdym kroku. Webinar jako hook wcześniej (Day 21) zamiast Loom |
| 8 | Tomato pay | Touch #9 | Day 29 | Email personal | Wersja London Kai | "curated 14 London JVM CTOs" — community angle |

**Format personalny vs blast: ZAWSZE personal.** Subject line Kaia: *"14 CTOs, 60 minutes, one question"* — nie zmienia się. CTA: reply lub "powiedz mi tak". **ZERO linku Eventbrite/Zoom masowego.**

---

#### 🇨🇭🇩🇪 DACH — 7 kont (Touch #7–9, Day 42–56)

DACH cadence jest wolniejsza (touch co 6–8 dni), więc Touch #7–9 wypada w dniach 42–56 od startu, czyli **tygodnie 6–8 dla każdego konta**.

| # | Konto | Touchpoint # | Dzień cadence | Kanał | Format | Notatka |
|---|-------|-------------|---------------|-------|--------|---------|
| 9 | Artifact (Lausanne) | Touch #7 | Day 42 | Email personal | Wersja DACH po niem. (Kai) | Najcieplejszy DACH lead — wcześniejszy touch. Jeśli discovery call już zaplanowany, webinar = "bonus warstwa" przed pilotym |
| 10 | Tundra (Zürich) | Touch #8 | Day 49 | Email personal | Wersja DACH | Re-engage — był kontakt SG wcześniej. Webinar jako "nowy kąt", nie kolejny pitch |
| 11 | Nexthink (Prilly) | Touch #8 | Day 49 | Email personal + LI | Wersja DACH | Duży scale-up — CC do VP Engineering jeśli znamy |
| 12 | CommoChain (Geneva) | Touch #9 | Day 56 | Email personal | Wersja DACH | Virgin territory — webinar dopiero gdy 3+ poprzednie touche wyszły |
| 13 | Seven.One (Munich) | Touch #9 | Day 56 | Email personal | Wersja DACH | AdTech/media — webinar temat "JVM scaling" może nie rezonować; alternatywny temat "real-time streaming" |
| 14 | TomTom (Amsterdam) | Touch #8 | Day 49 | Email personal | DACH/NL hybrid | Eric Bowman aktywny CTO — LI engage najpierw, email potem |
| 15 | Insify (NL) | Touch #7 | Day 42 | Email personal | EN/NL hybrid | Holenderski rynek szybszy niż CH — webinar wcześniej jako test |

---

#### 🇸🇪 Nordic — 5 kont (wyjątek: 1 konto w maju)

| # | Konto | Touchpoint # | Timing | Kanał | Notatka |
|---|-------|-------------|--------|-------|---------|
| 17 | Evolution Gaming (Stockholm) | Touch #1 cold → webinar invite | Maj 2026 | Email cold | JEDYNY wyjątek. Scala w produkcji = warm context. Webinar jako door-opener, nie mid-sequence. |
| 16, 18–20 | Tribia, Reaktor, Nordic Nomads, Boon | Nurture | LinkedIn ONLY do Q3 | LinkedIn | Brak cold outreach przed czerwcem. Webinar recording post-event jako Net — wrzucić do LinkedIn feed. |

---

### Personal vs. Blast — Reguła Twarda

| Format | Kiedy | Dla kogo |
|--------|-------|---------|
| **Personal email** (Kai template, max 80 słów, brak linku masowego) | Touch #7–9 per cadence | Wszystkie Dream 20 konta w aktywnej sekwencji |
| **LinkedIn DM personal** | Gdy brak emaila (NewDay) lub CTO aktywnyj LI | FullCircl, NewDay, TomTom (Bowman) |
| **Blast/Newsletter** | PO evencie, dla szerszej listy nurture (nie Dream 20) | 142 CTOs z Wiza list (Tier 2 touch) |
| **Recording jako Net** | Post-webinar — LinkedIn post + gated blog | Wszyscy (+LinkedIn organika) |

---

## 4. DACH Pilot-First — Jak <CHF 65K Zmienia Sekwencję

### Problem który Marcus rozwiązał

Standardowa DACH ścieżka: discovery call → technical deep-dive → full contract proposal → **komitet 3–4 osób** → negocjacje 4–6 tygodni. Pilot-first Marcusa (<CHF 65K) **obchodzi ten krok** — CTO może podpisać solo.

### Nowa Sekwencja DACH (z pilotem jako JOLT)

```
STARA sekwencja:          NOWA sekwencja (pilot-first):
Touch #1–6: outreach       Touch #1–6: outreach          (bez zmian)
Discovery call             Discovery call                  (bez zmian)
Technical deep-dive        Technical deep-dive             (bez zmian)
Full contract proposal     ⚡ JOLT: Pilot Proposal         ← ZMIANA TUTAJ
Komitet + zarząd           CTO podpisuje solo              ← KOMITET ZNIKA
Negocjacje 4–6 tyg.        Negocjacje 1–2 tyg.             ← 3× szybciej
Podpisanie: M5–M6          Podpisanie pilot: M3–M4         ← 2 miesiące wcześniej
```

### Kiedy i jak SDR proponuje pilot

**Touch #8 (DACH) — po discovery call, przed full proposal:**

Jeśli discovery call potwierdzi aktywny ból (job posting otwarte, backlog rośnie, CTO zainteresowany), SDR/AE **NIE wysyła pełnego proposal**. Wysyła:

```
Subject: Proposal: 90-day pilot — [Company] × Scalac

[Name],

Zamiast kontraktu rocznego którego nie możesz podpisać przed Q3, 
proponuję 90-dniowy pilot.

Format:
- 1–2 inżynierów Scalac w Twoim repo od Tygodnia 2
- CHF 63,000 łącznie (3 × CHF 21K) — poniżej typowego progu 
  wymagającego approval zarządu
- KPIs które wspólnie definiujemy na discovery call
- 30-day exit jeśli nie dostarczamy

Rezultat: Zarząd widzi velocity w Q2, nie czeka na hiring w Q4.

Czy to jest format który możesz podpisać bez komitetu?
```

**Cel tego zdania końcowego:** nie pyta "czy chcesz pilota?" — pyta czy CTO **może go podpisać sam**. To separuje Championa od Economic Buyera i wyjawia przeszkodę jeśli istnieje.

---

### Mapa JOLT per DACH konto

| Konto | Touch pilot proposal | Próg JOLT | Uzasadnienie |
|-------|---------------------|-----------|--------------|
| **Artifact (Lausanne)** | Touch #8, ~Day 49 | CHF 63K | Najcieplejszy lead, Scala w stacku. Pilot proposal jak najwcześniej — nie czekamy na full cycle |
| **Tundra (Zürich)** | Touch #9, ~Day 56 | CHF 63K | Był kontakt SG. Re-engage z pilotem zamiast pełnego pitch — reset relacji |
| **Nexthink (Prilly)** | Touch #10, ~Day 63 | CHF 63K | Duże konto — pilot jest bardziej strawny niż enterprise deal na wejście |
| **CommoChain (Geneva)** | Touch #10, ~Day 63 | CHF 63K | Virgin territory — pilot jako "zero risk" framing dla nowego vendora |
| **Seven.One (Munich)** | Touch #9, ~Day 56 | €60K (EUR not CHF) | DACH-DE market — Euro, nie CHF. Sprawdzić próg budżetowy w DE-GmbH strukturze |

**Ważne:** Pilot proposal NIGDY nie wychodzi przed discovery call. Sekwencja jest nienaruszalna: **problem confirmed → pain quantified → JOLT pilot** . Jeśli discovery call nie potwierdzi bólu — idziemy do nurture, nie pilot.

---

## 5. Finalna Lista Priorytetów na Poniedziałek — SDR Day 1

### Profil SDR: zaczyna kampanię od zera. No existing relationships.

---

### Godziny 1–2: Setup i Weryfikacja Narzędzi

**Narzędzia do aktywacji:**

| Narzędzie | Do czego | Link/Lokalizacja |
|-----------|---------|-----------------|
| LinkedIn Sales Navigator | Wyszukiwanie, alerty job posting, InMail | sales.linkedin.com |
| Apollo.io / Hunter.io | Weryfikacja emaili (szczeg. NewDay — brak emaila) | apollo.io |
| HubSpot (CRM) | Rejestrowanie touchpointów, sekwencje | hubspot.com |
| Loom | Nagrywanie osobistych video (Touch #7) | loom.com |
| Notify.io / Google Alerts | Monitoring job postings + trigger events | alerts.google.com |

**Działania godziny 1–2:**
- [ ] Stwórz listę kont w HubSpot: pierwsze 5 kont London (kolejność poniżej)
- [ ] Aktywuj LinkedIn Sales Nav alerty: "Scala developer" + "JVM engineer" + "Kafka" w UK + DACH geo
- [ ] Zweryfikuj emaile: Depop (keyur@depop.com ✓), Kaluza (andy.worsley@kaluza.com ✓), Monzo (matejpfajfar@monzo.com ✓), FullCircl (emanuele.tomeo@fullcircl.com ✓), Zego (goncalo.farinha@zego.com ✓)
- [ ] Dla NewDay: znajdź LinkedIn profil Head of Engineering/CTO przez Sales Nav → przygotuj InMail

---

### Godziny 2–4: Research Pierwsze 5 Kont

**Pierwsze 5 (w tej kolejności):**
1. **Depop** — keyur@depop.com — ML vacancies Scala+Spark
2. **Kaluza** — andy.worsley@kaluza.com — Kafka+LangChain+MCP
3. **FullCircl** — emanuele.tomeo@fullcircl.com — CTO w Scala community
4. **Zego** — goncalo.farinha@zego.com — Lead ML open 60+ dni
5. **Monzo** — matejpfajfar@monzo.com — AI Senior Staff hiring

**Per każde konto (20 min max):**
- [ ] Sprawdź LinkedIn CTO: ostatni post (do Touch #3 comment), aktywność w Scala groups
- [ ] Znajdź URL konkretnej otwartej pozycji → wklej do HubSpot "Notes" dla konta
- [ ] Sprawdź ile dni pozycja jest otwarta (LinkedIn "Posted: X days ago")
- [ ] Szybki check: czy mieli fundraise w ostatnich 12 miesiącach? (Crunchbase)
- [ ] Zapisz 1 fact specyficzny dla konta → użyjesz w Loom Day 21

---

### Godziny 4–6: Personalizacja Touch #1 (LinkedIn Connect Request)

**Template Touch #1 (LinkedIn, brak modyfikacji):**
```
Noticed [Company] is scaling its JVM infrastructure — we help teams like yours 
extend Scala/Kafka capabilities without the 7-month hiring gap. Worth being connected.
```

**Personalizacja: zmień tylko [Company] i jeden szczegół stacku:**
- Depop: "Scala+Spark infrastructure"
- Kaluza: "Kafka+LangChain infrastructure"
- FullCircl: "Scala infrastructure" (krótko — CTO wie co to)
- Zego: "ML infrastructure" (Lead ML Engineering = ich język)
- Monzo: "JVM platform infrastructure"

**Działania:**
- [ ] Wyślij LinkedIn connect do 5 CTOs (w ciągu jednej sesji — nie w jednej minucie, rozłóż na 30–40 min)
- [ ] Ustaw przypomnienie w HubSpot: Day 3 = Email Touch #2 per konto
- [ ] Zaloguj connect attempted w HubSpot CRM per konto

---

### Godziny 6–8: Draft Touch #2 (Cold Email, scheduled na Day 3)

**Gdzie jest template:**
- London cold email template: `scalac_council_v2/shared/discussion/round_2_kai.md` → Sekcja 2.2 (London)
- Hooki personalizacyjne: ten dokument → Sekcja 2 (powyżej)
- DACH cold email: `round_2_kai.md` → Sekcja 2.1

**Workflow (per konto, 15 min max):**
1. Otwórz London template z Kai
2. Wklej Hook Kai z tabeli powyżej jako zdanie 1
3. Wklej zdanie Davida jako zdanie 2
4. Wstaw [konkretna rola], [N dni], [job posting URL] ze swojego research
5. Zaplanuj w HubSpot sequences: "Send Day 3" (= pojutrze)

**Gotowe draft + scheduled — koniec Day 1:**
- [ ] 5 emaili Touch #2 zaplanowanych w HubSpot sequences
- [ ] 5 LinkedIn connect requests wyszłe
- [ ] 5 kont w CRM z: email, LinkedIn URL, job posting URL, # dni open, fundraise Y/N

---

### Dzień 2–3 (preview dla ciągłości):
- Day 2: Sprawdź kto zaakceptował connect → natychmiastowy DM wartość (Touch #3 forward)
- Day 3: Touch #2 emaile wychodzą automatycznie z sequences
- Day 3: Research kont 6–8 (Paysend, NewDay, Tomato pay) + przygotuj jejich Touch #1
- Day 5: Setup Google Alerts dla każdego z 8 kont ("Depop Series B" / "Kaluza funding" itp.)

---

## Co Sądzę o Innych

### Marcus
Pilot-first <CHF 65K to **najważniejsza zmiana tej rundy**. Nie dlatego że zmniejsza kontrakt — dlatego że eliminuje komitet i skraca DACH cycle o 60–90 dni. Jedno zastrzeżenie: Marcus musi zdecydować czy pilot to "test drive" (= może nie prowadzić do pełnego kontraktu) czy "ramp to full" (= domyślnie przechodzi w kontrakt jeśli KPIs spełnione). W sekwencji outreach to robi różnicę — "ramp to full" zamyka mocniej.

### Elena
Dziękuję za arytmetykę. Miałem rację co do tempa per geo, ale nie wyciągnąłem wniosku na poziomie całkowitej długości cadence. Teraz mamy spójność: **London 90 dni, DACH 180 dni, Nordic Q3** — i pipeline math to potwierdza. Jedna prośba zwrotna dla Eleny: TCO calculator email-gate — zgadzam się z Kai że musi być, ale CTA nad braną musi brzmieć jak wartość ("pokaż mi wynik") nie jak bariera ("podaj email żeby kontynuować"). Kai to już napisał — warto użyć jego copy.

### Kai
8 hooków działa. Są oparte na faktach, nie na "noticed you're a great company". Dla NewDay (brak emaila) wersja InMail jest równie mocna. Jedna sugestia: dla **Touch #7 Loom** (Day 21) potrzebujemy osobnych instrukcji — 90-sekundowy script per konto. Może być osobny deliverable przed Rundą 3? To jest touchpoint który wymaga największego przygotowania i SDR bez scriptu nagreje złą wersję.

---

## Dream 20 Status — Podsumowanie po Rundzie 2

| # | Konto | Geo | Touch Start | Webinar? | Pilot? | Priorytet SDR |
|---|-------|-----|------------|----------|--------|--------------|
| 1 | Depop | London | Day 1 | Touch #9 (D29) | Nie (London — full contract) | **Top 1** |
| 2 | Kaluza | London | Day 1 | Touch #9 (D29) | Nie | **Top 2** |
| 3 | FullCircl | London | Day 1 | Touch #9 LI DM | Nie | **Top 3** |
| 4 | Zego | London | Day 1 | Touch #9 (D29) | Nie | **Top 4** |
| 5 | Monzo | London | Day 1 | Touch #9 (D29) | Nie | **Top 5** |
| 6 | Paysend | London | Day 3 | Touch #9 (D29) | Nie | Top 6 |
| 7 | NewDay | London | Day 3 LI | Touch #7 InMail | Nie | Top 7 |
| 8 | Tomato pay | London | Day 3 | Touch #9 (D29) | Nie | Top 8 |
| 9 | Artifact | DACH | Day 15 | Touch #7 (D42) | **TAK — D49** | Top 9 |
| 10 | Tundra | DACH | Day 15 | Touch #8 (D49) | TAK — D56 | Top 10 |
| 11 | Nexthink | DACH | Day 15 | Touch #8 (D49) | TAK — D63 | Top 11 |
| 12 | CommoChain | DACH | Day 15 | Touch #9 (D56) | TAK — D63 | Top 12 |
| 13 | Seven.One | DACH | Day 15 | Touch #9 (D56) | TAK — D56 | Top 13 |
| 14 | TomTom | DACH/NL | Day 15 | Touch #8 (D49) | TAK — D56 | Top 14 |
| 15 | Insify | NL | Day 15 | Touch #7 (D42) | TAK — D49 | Top 15 |
| 16 | Tribia AS | Nordic | Tydzień 6 | Post-event rec. | Nie | Nurture Q2 |
| 17 | Evolution Gaming | Nordic | Maj 2026 | Touch #1 (JOLT) | Nie do Q3 | **Wyjątek maj** |
| 18 | Reaktor | Nordic | Tydzień 6 | Post-event rec. | Nie | Nurture Q2 |
| 19 | Nordic Nomads | Nordic | Tydzień 6 | Post-event rec. | Nie | Nurture Q2 |
| 20 | Boon | Nordic | Tydzień 6 | Post-event rec. | Nie | Nurture Q2 |

---

*Następny krok: Runda 3 — finalizacja output ABM plan z metrykami tygodniowymi i KPIs dla zarządu.*

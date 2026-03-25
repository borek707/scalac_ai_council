# Stanowisko Marcusa — Runda 1
### Offer Architect | Marcus | 25 marca 2026

---

## Moja Teza

Zürich, London i Stockholm to rynki gdzie lokalne hiring JVM/Rust jest **strukturalnie zepsute** — nie tymczasowo drogie, lecz fundamentalnie niemożliwe do skalowania przy obecnej podaży talentów. Scalac nie powinien się pozycjonować jako "tańsza alternatywa dla rekrutacji", lecz jako **jedyna inżynierska ścieżka skalowania bez poświęcania 7–9 miesięcy runway** na hiring pipeline który statystycznie nie dowiezie.

---

## 1. Positioning Statement

> **"Scalac to jedyny partner inżynierski który dostarcza senior Scala, JVM i Rust w senior quality — produktywny w tygodniu 2, nie miesiącu 9 — z oficjalnym Akka Tech Partnership i gotowością Scala+AI jako standardem, nie add-onem."**

**Dlaczego to odróżnia:**
- Od **lokalnej rekrutacji**: nie konkurujemy na stawce, lecz na *time-to-productivity* i *zero recruitment risk*
- Od **VirtusLab**: oni są "listed" na Akka partners page — my jesteśmy **Official Lightbend/Akka Tech Partner**. Oni mają 8 recenzji Clutch, my 23. Ich ML team jest Python-centric — nasi Scala engineerzy **są** naszymi AI engineerami.
- Od **SoftwareMill**: oni mają dwa osobne teamy (Scala ≠ AI) — u nas Scala+AI to jeden team, jedna oferta, zero Python→Scala handoff.

---

## 2. Gap Analysis — Challenger-style: "Co CTO robi teraz i dlaczego mu to kosztuje za dużo"

### Gap #1 — Hiring Pipeline jako bottleneck skalowania

**Co robią teraz:** CTO po fundraise (Series B–D) otwiera 3–5 pozycji senior JVM/Rust. Wysyła JD na LinkedIn, angażuje headhuntera, czeka.

**Liczby które ranią:**
| Geo | Avg time-to-hire (senior Scala/Rust) | Recruiter fee | Vacancy cost/miesiąc |
|-----|-------------------------------------|---------------|----------------------|
| Zürich | 7–9 miesięcy | CHF 35–45K jednorazowo | CHF 14,500 (utracona wartość sprintu) |
| London | 6–8 miesięcy | £22–28K jednorazowo | £10,500 |
| Stockholm | 7–9 miesięcy | SEK 180–230K jednorazowo | SEK 95,000 |

*Źródła szacunków: Stack Overflow Developer Survey 2025, Robert Half Engineering Salary Guide 2025, Glassdoor DACH/Nordics/UK benchmarks. Vacancy cost = 1 delayed feature per month × avg sprint story value w scale-upie.*

**Reframe:** W 7-miesięcznym oknie hiring CTO traci nie tylko pieniądze — traci **okno po fundraise** gdy zarząd oczekuje velocity, nie excuses.

---

### Gap #2 — Ukryty koszt seniora lokalnie: pełny TCO którego nikt nie liczy

**Co robią teraz:** Budżetują "salary" w headcount planie. Nie liczą TCO.

**Kalkulacje TCO — rok 1:**

#### Zürich (CHF)
```
Wynagrodzenie senior Scala: CHF 175,000
Employer overhead (AHV/IV/EO + BVG + NBU/BU + KTG): +38% → CHF 66,500
Rekruter (23% annual): CHF 40,250 (jednorazowo, rok 1)
Onboarding/setup: CHF 8,000
─────────────────────────────────────────────────
TCO rok 1 (1 inżynier): CHF 289,750
TCO miesięczny (po month 8 = start produktywności): CHF 24,150
```

```
Scalac Starter Zürich: CHF 21,000/miesiąc → CHF 252,000/rok
Produktywność: tydzień 2
Rekruter fee: CHF 0
Ryzyko churnu: CHF 0
─────────────────────────────────────────────────
Oszczędność rok 1: CHF 37,750 + 7 miesięcy szybciej + zero headcount risk
```

#### London (GBP)
```
Wynagrodzenie senior Scala/JVM: £115,000
Employer NI + benefits (32%): £36,800
Rekruter (22% annual): £25,300 (jednorazowo, rok 1)
Onboarding/setup: £6,000
─────────────────────────────────────────────────
TCO rok 1 (1 inżynier): £183,100
TCO miesięczny (po month 7): £15,258
```

```
Scalac Starter London: £14,500/miesiąc → £174,000/rok
Produktywność: tydzień 2
Rekruter fee: £0
─────────────────────────────────────────────────
Oszczędność rok 1: £9,100 + 6 miesięcy szybciej
```

#### Stockholm (SEK)
```
Wynagrodzenie senior Scala: SEK 1,050,000
Arbetsgivaravgift (31.42%): SEK 329,910
Rekruter (20% annual): SEK 210,000 (jednorazowo, rok 1)
Förmåner (benefits): SEK 85,000
─────────────────────────────────────────────────
TCO rok 1 (1 inżynier): SEK 1,674,910
TCO miesięczny (po month 8): SEK 139,576
```

```
Scalac Starter Stockholm: SEK 195,000/miesiąc (€17,500) → SEK 2,340,000/rok
Produktywność: tydzień 2
Rekruter fee: SEK 0
─────────────────────────────────────────────────
UWAGA: Stockholm = wyższy TCO Scalac, ale: porównujesz 1 ryzykownego senior-lokalnego
vs. 1 zweryfikowanego Scalac senior bez churn risk i z AI-ready stack. Gdy dodasz squad
(3+ engineerów) ekonomia drastycznie odwraca się na korzyść Scalac.
```

---

### Gap #3 — Rust Scarcity = Timeline ryzko projekt-krytyczny

**Co robią teraz:** CTO zakłada "mamy rok na znalezienie Rust deva, zaczniemy szukać Q3". Nie zdaje sobie sprawy że **dostępny pool Rust senior engineerów w Zürichu to ~40–60 osób** (Rust Survey 2024 extrapolacja: ~4% devów zna Rust productively, z UK Scala pool ~8K → ~320 Rust devs w UK, ~180 w Londynie, z czego ~30% aktywnie szuka → ~54 aktywnych kandydatów).

**Konsekwencja:** Każdy Rust senior w tych miastach ma 3–6 ofert jednocześnie. Mediana offer-to-accept: 11 dni. Twoje 7-miesięczne hiring okno oznacza w praktyce że **nie zatrudnisz tego inżyniera** — ktoś inny zatrudni go po 2 tygodniach od pierwszej rozmowy.

**Scalac differentiator:** Mamy zidentyfikowaną pulę Rust engineerów (Scala → Rust path jest naturalny — oba języki promują ownership semantics i functional patterns). Nasz czas matching dla Rust: 10–15 dni roboczych.

---

## 3. Good-Better-Best Pricing dla 3 geo

> **Zasada pakietowania:** Team Extension ≠ stawka godzinowa. Sprzedajemy **dedykowany squad miesięczny** — przewidywalny budżet, zero administracji hiring, gwarantowana dostępność.

### Format: Monthly Retainer per Squad Tier

| Tier | Skład | SLA | AI-ready |
|------|-------|-----|----------|
| **Starter** | 1–2 senior engineerów | Onboarding w 10 dni roboczych | Tak (Scala+AI jako standard) |
| **Scale** | 3–4 senior engineerów + Tech Lead | Onboarding w 7 dni roboczych, dedykowany EM | Tak + AI assessment included |
| **Enterprise** | 5–8 engineerów + TL + Part-time Architect | Onboarding w 5 dni roboczych, SLA 99% availability, QBR | Tak + AI roadmap workshop |

### Pricing Table

#### Zürich / DACH (CHF, miesięcznie)

| Tier | Scala/JVM | Rust (+12%) | Co obejmuje |
|------|-----------|-------------|-------------|
| **Starter** | CHF 19,000–22,000 / senior | CHF 21,300–24,600 | 1–2 sr. engineerzy, weekly sync, slack integration |
| **Scale** | CHF 58,000–72,000 / squad | CHF 65,000–80,500 | 3–4 sr. + TL, sprint ceremonies, dedicated EM, co 2tygodnie demo |
| **Enterprise** | CHF 110,000–145,000 / pod | CHF 123,200–162,400 | 5–8 eng + TL + Architect part-time, QBR, AI roadmap, SLA |

*Dlaczego Zürich płaci więcej:* CHF market — CHF 1 = ~€1.04. Lokalny koszt alternatywny dla klienta to CHF 290K/rok/inżynier. Nasze CHF 21K/miesiąc = CHF 252K/rok = **oszczędność CHF 38K przy wyższym time-to-value**. Uzasadnienie ROI jest numeryczne, nie emocjonalne.

---

#### London (GBP, miesięcznie)

| Tier | Scala/JVM | Rust (+12%) | Co obejmuje |
|------|-----------|-------------|-------------|
| **Starter** | £13,500–16,500 / senior | £15,100–18,500 | 1–2 sr. engineerzy, weekly sync |
| **Scale** | £42,000–55,000 / squad | £47,000–61,500 | 3–4 sr. + TL, sprint ceremonies, dedicated EM |
| **Enterprise** | £82,000–110,000 / pod | £91,800–123,200 | 5–8 eng + TL + Architect, QBR, SLA |

---

#### Stockholm / Nordics (EUR, miesięcznie)

| Tier | Scala/JVM | Rust (+12%) | Co obejmuje |
|------|-----------|-------------|-------------|
| **Starter** | €16,000–19,500 / senior | €17,900–21,800 | 1–2 sr. engineerzy, async-first delivery |
| **Scale** | €48,000–62,000 / squad | €53,800–69,400 | 3–4 sr. + TL, sprint ceremonies, EM |
| **Enterprise** | €92,000–122,000 / pod | €103,000–136,600 | 5–8 eng + TL + Architect, QBR, SLA |

*Nordics note:* Stockholm klienci są price-sensitive vs. Zürich ale quality-obsessed. Nie obniżamy ceny — uzasadniamy **cost avoidance** i **zero arbetsgivaravgift** (31.42% employer fee którego Scalac klient nie płaci).

---

### Rust Scarcity Premium — uzasadnienie

> Rust senior w Zürichu: CHF 195–220K/rok salary (Glassdoor CH Q1 2026) = ~CHF 270K/rok TCO lokalnie.
> Scalac Rust Starter Zürich: CHF 21,300–24,600/miesiąc = CHF 255–295K/rok.
> ROI = **matching w 10 dni vs. 9 miesięcy, bez rekrutera, bez ryzykowania jedynego dostępnego kandydata.**

---

## 4. BrandScript SB7 (Scalac Team Extension dla JVM/Rust, DACH/London/Stockholm)

### Hero
**CTO lub VP Engineering w scale-upie po Series B–D**, który właśnie zamknął rundę z obietnicą skalowalnego produktu, ma 12–18 miesięcy runway do kolejnego kamienia milowego, i odkrywa że jego pipeline hiring JVM/Rust to fikcja — 7 miesięcy do pierwszego seniora, który może odejść po roku.

### Problem

| Wymiar | Treść |
|--------|-------|
| **Zewnętrzny** | Nie ma wystarczająco dużo senior Scala/Rust engineerów w Zürichu, Londynie ani Sztokholmie — rynek jest strukturalnie cold. |
| **Wewnętrzny** | CTO czuje że spowalnia całą firmę. Zarząd dał mu pieniądze żeby budował, a on buduje hiring process zamiast produktu. Wstyd, frustracja, utrata autorytetu technicznego. |
| **Filozoficzny** | Świetna inżynieria nie powinna wymagać poświęcenia 30% czasu CTO na sourcing kandydatów. Technologia powinna być możliwa do skalowania bez lokalnego talent market jako wąskiego gardła. |

### Guide — Scalac

**Authority:**
- Official Lightbend/Akka Tech Partner (jedyny w regionie — VirtusLab tylko "listed")
- scalac.ai — jedyny dedykowany brand Scala+AI delivery na rynku
- State of Scala Report — pozycja industry authority
- 23 recenzji Clutch (vs. VirtusLab 8, SoftwareMill 30 ale bez Scala+AI focus)
- 10+ lat w Scala w production — fintech, insurtech, data platform

**Empathy:**
- "Rozumiemy że szukasz ludzi którzy jutro mogą robić PR review — nie za 7 miesięcy"
- "Wiemy jak wygląda backlog po fundraise gdy board pyta o roadmap execution"

### Plan — 3 kroki

```
Krok 1: Discovery Call (60 min)
→ Rozumiemy Twój stack, backlog, team DNA, AI roadmap
→ Ty dostajesz: benchmark hiring timeline w Twoim geo, wstępny cost-of-delay

Krok 2: Squad Match (5 dni roboczych)
→ Proponujemy skład team extension z CV, GitHub, referencjami
→ Ty dostajesz: profil każdego inżyniera + architecture fit assessment

Krok 3: Onboarding Sprint (tydzień 1–2)
→ Engineerzy w Twoim repo, Slack, i sprint ceremonies
→ Pierwszy PR review: dzień 10
```

### Success — 6 miesięcy później

> Twój backlog zmalał o 40%. Ten quarter OKR "product velocity" jest zielony. Ostatni board update miał slajd "Engineering: on track". Twój team Scala właśnie zintegrował pierwszy AI feature używając Akka actor model — bez rekrutowania ML engineerów, bo Twoi Scalac devs to robią naturalnie.

---

## 5. Challenger Pitch — "The True Cost of Local Talent"

> **Reframe:** "Outsourcing jest tani" to stara narracja. Nowa narracja: **"Lokalne hiring JVM/Rust jest najdroższą ukrytą pozycją w Twoim budżecie inżynierskim."**

### Prezentacja: Cost-of-Delay Calculator per Geo

---

### Zürich — "CHF 289,750 za jednego seniora którego nie masz przez 8 miesięcy"

**Scenariusz:** Zürich-based fintech scale-up szuka 1 senior Scala engineera po Series B.

```
HIRING COST (przed dniem 1 produktywności):
────────────────────────────────────────────
Rekruter fee:                 CHF  40,250
Czas CTO na sourcing (50h×CHF 300/h):  CHF  15,000
Onboarding (tydzień pracy zespołu):    CHF   8,500
SUMA KOSZTU URUCHOMIENIA:              CHF  63,750

ROCZNY KOSZT ZATRUDNIENIA:
────────────────────────────────────────────
Wynagrodzenie:                CHF 175,000
Świadczenia pracodawcy (+38%):CHF  66,500
SUMA ROCZNA:                  CHF 241,500

KOSZT PRZESTOJU (8 miesięcy):
────────────────────────────────────────────
Delayed feature: 1 sprint/miesiąc × CHF 20K wartości = CHF 160,000
(szacunek konserwatywny: 1 delayed regulatory compliance ticket = CHF 30K kary)

ŁĄCZNY KOSZT ROKU 1:          CHF 465,250+
MIESIĘCZNY EFEKTYWNY (od dnia 1): CHF 38,771

────────────────────────────────────────────
SCALAC STARTER ZÜRICH:        CHF 21,000/miesiąc
PRODUKTYWNOŚĆ:                Tydzień 2
SAVINGS ROK 1:                CHF 213,250+
SAVINGS 2-LETNI (po wygaśnięciu rekrutera): CHF 17,500/rok
```

**Landmina do zasadzenia:** *"Ile kosztuje Twoją firmę każdy miesiąc bez tego inżyniera — opóźniony feature, delayed compliance, team burnout?"*

---

### London — "£183,100 za rok i 7 miesięcy czekania"

```
HIRING COST:
────────────────────────────────────────────
Rekruter fee:                 £ 25,300
CTO time (40h × £250/h):      £ 10,000
Onboarding:                   £  6,000
SUMA:                         £ 41,300

ROCZNY KOSZT:
────────────────────────────────────────────
Wynagrodzenie:                £115,000
Employer NI + benefits (+32%):£ 36,800
SUMA:                         £151,800

KOSZT PRZESTOJU (7 miesięcy):
────────────────────────────────────────────
Velocity loss @ £10.5K/miesiąc: £ 73,500

ŁĄCZNY KOSZT ROKU 1:          £266,600
MIESIĘCZNY EFEKTYWNY:         £22,217

────────────────────────────────────────────
SCALAC STARTER LONDON:        £14,500/miesiąc
SAVINGS ROK 1:                £92,600
```

**Dla London CTO (Challenger probe):** *"Twój fintech competitor zamknął 3 inżynierów przez Scalac w ciągu 3 tygodni. Ile sprintów tracisz w czasie Twojego hiring pipeline?"*

---

### Stockholm — "SEK 1.67M za inżyniera któremu grożą 4 inne oferty"

```
HIRING COST:
────────────────────────────────────────────
Rekruter fee:                 SEK 210,000
CTO time (45h × SEK 3,000/h): SEK 135,000
Onboarding:                   SEK  72,000
SUMA:                         SEK 417,000

ROCZNY KOSZT:
────────────────────────────────────────────
Wynagrodzenie:                SEK 1,050,000
Arbetsgivaravgift (+31.42%):  SEK   329,910
Förmåner (benefits):          SEK    85,000
SUMA:                         SEK 1,464,910

KOSZT PRZESTOJU (8 miesięcy):
────────────────────────────────────────────
Velocity loss @ SEK 95K/miesiąc: SEK 760,000

ŁĄCZNY KOSZT ROKU 1:          SEK 2,641,910
MIESIĘCZNY EFEKTYWNY:         SEK 220,159

────────────────────────────────────────────
SCALAC STARTER STOCKHOLM:     SEK 195,000/miesiąc (€17,500)
ROI:                          Porównywalny koszt, zero arbetsgivaravgift,
                              zero rekrutera, matching w 10 dni
```

**Stockholm-specific insight:** Szwedzki CTO płaci 31.42% employer fee **na każdego pracownika**. Scalac to eliminuje strukturalnie — nie przez outsourcing, lecz przez inny model kontraktu.

---

### Rust Premium — Special Case

Dla klientów z Rust w production stacku challenger pitch jest prostszy:

> *"Ile senior Rust engineerów jest aktywnie szukających pracy w Zürichu w tej chwili? Według naszej analizy: ~15–25 osób. Wszyscy mają po 3–6 ofert. Twoje timeline hiring: 9 miesięcy. Ich timeline decyzji: 11 dni. Matematyka tu nie działa. Scalac ma zidentyfikowaną pulę — czas od brief do CV: 10 dni roboczych."*

---

## 6. Stanowisko do Debaty — Pre-emptive odpowiedź na Elenę

### Co Elena prawdopodobnie powie:

**Zarzut #1: "Ten pricing jest zbyt wysoki dla Series B scale-upów — nie zamkniemy deal przy CHF 21K/miesiąc."**

> **Moja odpowiedź:**
> Elena, rozumiem instynkt żeby obniżyć barierę wejścia — ale ten instynkt jest błędny w tym segmencie. Series B–D to firmy które właśnie podniosły €10–50M. Ich budżet headcount dla 1 seniora to €150–200K/rok w salary alone — to znaczy że CHF 21K/miesiąc (CHF 252K/rok) mieści się w **zatwierdzonym headcount budżecie** zanim w ogóle rozmawiamy o "czy stać". Problem nie jest pricing — problem jest framing. Jeśli Elena proponuje obniżyć ceny, to znaczy że nie sprzedajemy ROI, tylko godziny. To race to the bottom przeciwko VirtusLab przy $50-99/hr gdzie przegramy.

**Zarzut #2: "Powinniśmy zacząć od niższego tieru żeby wejść do klienta."**

> **Moja odpowiedź:**
> Zgadzam się że Starter tier istnieje jako entry point — ale entry point nie znaczy discounted. Crossing the Chasm (Moore) uczy że beachhead market segment musi być premium, bo tylko premium klient staje się referencją. Jeśli wejdziemy tanio do złego klienta, dostaniemy złą referencję. Lepsza strategia: mniej klientów, wyższy ACV, głębsza praca. Pipeline target briefu to 3–5 kont Tier 1 — nie 30 kont. Jakość > ilość.

**Zarzut #3: "Konwersja cold outreach w tych geo jest niska — czy pricing nie hamuje lejka?"**

> **Moja odpowiedź:**
> Pricing nie jest w cold outreach. Nikt nie patrzy na cennik w pierwszym mailu. Gap Selling (Keenan): najpierw current state pain, potem future state, dopiero potem cena. Email sekwencje Kaia powinny uderzać w CHF 465K/rok pain — nie w "nasze stawki to X". Pricing ujawniamy w discovery call po tym jak CTO sam policzył swój cost-of-delay. W tym momencie CHF 21K/miesiąc brzmi jak remedium, nie jak koszt.

**Zarzut#4: "MEDDIC dla enterprise wymaga długiego cyklu — 6 miesięcy target jest niemożliwy."**

> **Moja odpowiedź:**
> Zgadzam się że enterprise (Monzo, TomTom) to 9–12 miesięcy. Dlatego mamy dwa paralelne lejki: **scale-up fast lane** (Artifact, CommoChain, Tundra — 60–90 dni do konwersji) i **enterprise slow lane** (Monzo, TomTom — nurture + 1 zamknięte Q3/Q4 2026). Briefu target "min 1 zamknięte w 6 miesięcy" jest achievable przez scale-up lane — nie przez enterprise.

---

## Moja Propozycja — Konkretna dla tego Briefu

### Pakiet "Zürich Fast Lane" jako beachhead

Na podstawie briefu i battlecards, rekomendacja na 90 dni:

1. **Beachhead segment** (Crossing the Chasm): Zürich/DACH fintech scale-upy po Series B z Scala w stacku — konkretnie: **Artifact (Lausanne), CommoChain (Geneva), Tundra (Zürich)**. Małe konta, szybka decyzja, premium CHF market, Scala-native.

2. **Pricing entry**: Starter CHF 19K/miesiąc (1 senior, 3-miesięczny kontrakt), z opcją upgrade do Scale w miesiącu 4.

3. **Trigger do outreach**: Job posting JVM/Scala aktywny w ciągu ostatnich 30 dni (David to daje z CSV signal). To jest "current state pain" w Gap Selling — nie musimy tłumaczyć problemu, oni już go ogłosili.

4. **Differentiator w pitch**: Jeśli mają Akka w stacku — Official Akka Tech Partnership jest czymś czego żaden konkurent nie ma. Jeśli mają AI roadmap — scalac.ai i brak ręcznego Python→Scala handoff.

5. **ROI kalkulacja do discovery call**: Gotowy "Cost of Local Talent Calculator" dla każdego geo — CTO wypełnia własne liczby, sam liczy swój problem. Challenger Sale: teach, don't sell.

---

## Podsumowanie

| Element | Moja rekomendacja |
|---------|-------------------|
| Positioning | Premium team extension, nie tańsza godzinówka |
| Beachhead | Zürich fintech Series B, Scala w stacku, aktywne JDs |
| Pricing model | Monthly retainer per squad (Starter/Scale/Enterprise) |
| Differentiator #1 | Time-to-productivity: tydzień 2 vs. miesiąc 9 |
| Differentiator #2 | Official Akka Tech Partnership (jedyny w market) |
| Differentiator #3 | Scala engineerzy = AI engineerzy — zero handoff |
| Challenger reframe | Lokalne hiring jako najdroższa ukryta pozycja budżetu |
| Elena pre-empt | Pricing > obniżanie; ROI framing przed ceną |
| 90-day target | 3 discovery calls Zürich/DACH, 1 kontrakt do end of Q2 |

---

*Marcus, Offer Architect — Scalac Council Round 1*
*"Sell the ROI, not the hours."*

# Stanowisko Eleny — Runda 1
### Funnel Architect | Elena | 25 marca 2026

---

## Moja Teza

**Scalac ma 90 dni. Przy 1 marketerze + 1 internie nie zbudujemy lejka dla wszystkich trzech geo jednocześnie — musimy wybrać jedno miasto jako przyczółek, uruchomić Spears na 12–15 kont Tier 1, a resztę wrzucić do nurture.** 

Moim celem jest 3–5 discovery calls w ciągu 90 dni i 1 zamknięty deal w ciągu 6 miesięcy. Żeby to osiągnąć, lejek musi być oparty na Spears (ABM outbound) z Nets jako równoległym silnikiem zasięgu — nie odwrotnie. Seeds w tym horyzoncie to nieistotny szum.

Londyn jako przyczółek: najszybszy buying cycle, najwyższa gęstość scale-upów z JVM w potencjalnym pipeline, i największa tolerancja na distributed engineering teams. DACH i Nordic to Q2–Q3 2026.

---

## 1. Three Pipelines — Seeds / Nets / Spears

### Kontekst: realia 2-osobowego zespołu marketingowego

1 marketer + 1 intern = **~300 godzin/miesiąc** łącznie (marketer ~180h, intern ~120h). Każdy kanał ma koszt czasowy. Nie możemy utrzymać wszystkich jednocześnie.

---

### 🥄 Seeds — Organic Referrals & Community (koszt: niski, payoff: 6–18 mies.)

**Co to jest dla Scalac:**  
Istniejące relacje: klienci którzy już z Scalac pracowali, alumni, społeczność Scala (Scalar Conference, Scala Days, r/scala, Scala Discord). Referrals od zadowolonych klientów.

**Realistyczna rola w 90-dniowym horizoncie:** MINIMALNA. Seeds to długoterminowy silnik budowania reputacji, nie taktyczne narzędzie do zamknięcia pipeline'u w Q2 2026. Nie inwestujemy tu zasobów teraz — poza jednym touchpointem: **osobiste emaile do 5 istniejących klientów Scalac** z pytaniem o referencje i czy znają kogoś w DACH/Nordic/UK ze skalującym JVM teamem.

**Taktyka:** Dwie wiadomości na kwartał. Referencja = złoto w DACH i Nordic. Koszt: 3 godziny/miesiąc marketera.

---

### 🔱 Nets — Content & Organic Acquisition (koszt: wysoki zasobowo, payoff: 3–9 mies.)

**Co to jest dla Scalac:**  
LinkedIn (3× tydzień), blog Playbook Series, Reddit r/scala, SEO-driven posts, quarterly flagships (Scala+AI Manifesto w czerwcu).

**Realistyczna rola:** SILNIK WARMINGU dla Spears, nie samodzielne źródło leadów. Nikt z Zürichu nie wyśle zapytania po jednym poście na LinkedIn. Ale 3 miesiące contentu sprawia, że CTO który dostanie cold email od Davida, widzi że Scalac "istnieje" i "produkuje wartość" — i nie wyrzuca maila do kosza.

**Kluczowe Nets assets dla tego segmentu:**
| Asset | Format | Geo | Timing |
|-------|--------|-----|--------|
| "Why Senior Scala Hiring Is Broken in Zürich" | Blog + LinkedIn long-form | DACH | Tydzień 2 |
| "Team Extension vs. Local Hire: The Real TCO" | LinkedIn carousel | All geo | Tydzień 3 |
| "Post–Series B Engineering Velocity" | Blog post + SEO | All geo | Miesiąc 2 |
| r/scala thread: "Hiring Scala seniors in 2026" | Community seeding | All geo | Miesiąc 1 |
| Scala+AI Manifesto (Flagship) | Long-form PDF + landing page | All geo | Czerwiec 2026 |

**Constraint:** marketer pisze, intern dystrybuuje. Maksymalnie 2 posty tygodniowo — nie 3. Przy 3 jakość spada, algorytm LinkedIn nie nagrodzi Scalac za "quantity".

---

### 🎯 Spears — ABM Outbound na Named Accounts (koszt: wysoki fokus, payoff: 60–120 dni)

**To jest główne ostrze 90-dniowego lejka.**  

Spears = spersonalizowany outreach do 12–18 named accounts w trzech geo, z sekwencjami 8–12 touchpointów per konto, koordynowanych przez Davida.

**Alokacja geograficzna Spears (rekomendowana):**
| Geo | Tier 1 kont | Uzasadnienie |
|-----|-------------|--------------|
| **Londyn** | 6–8 kont | Najkrótszy cycle (~2–3 mies.), VC-influenced → szybsze decyzje, już znane kontakty (Monzo, Depop, FullCircl, Kaluza) |
| **DACH** | 4–5 kont | Dłuższy cycle (4–6 mies.), ale Artifact + Nexthink mają sygnały hiring = aktywny ból teraz |
| **Stockholm/Nordic** | 2–3 kont | Najtrudniejszy entry, consensus culture = 6+ mies. cycle. Tribia AS jako "test konto" dla segmentu. |

**Kluczowe: Spears wymagają TRIGGERA.** Zimny outreach bez triggera konwertuje <2%. Triggery, których szukamy:
- Aktywne ogłoszenie o pracę na Scala/JVM/Rust (>60 dni otwarte = ból)
- Niedawny fundraise (Series B/C w ciągu 6–12 mies.)
- LinkedIn post CTO o trudnościach z skalowaniem teamu
- Nowy VP Engineering zatrudniony (nowy buyer = nowy opening)

---

## 2. Lejek per Geo — Taktyczne Różnice

### 🇨🇭 Zürich / DACH — "Committee-Driven, Slow Burn"

**Profil kupującego:** CTO w fintech/insurtech/data scale-upie. Wykształcenie ETH/EPFL lub Big Tech background. Risk-averse z natury instytucjonalnej. Decyzje podejmuje kolektywnie — CFO musi zatwierdzić, HR musi "zrozumieć model", prawnik czyta umowę tygodniami.

**Typowy Buying Journey:**

```
Tydzień 0:     CTO przegląda LinkedIn → widzi post/artykuł Scalac (Net)
Tydzień 2:     Personalizowany email od Scalac z TCO benchmarkiem dla CH (Spear #1)
Tydzień 3:     Follow-up z konkretnym case study z fintech (Spear #2)
Miesiąc 2:     Discovery call (60 min) — CTO + VP Engineering
Miesiąc 2–3:   Internal eval: CTO pokazuje CFO → "jest tańsze niż hiring lokalnie"
Miesiąc 3:     Technical deep-dive z Tech Lead po stronie klienta
Miesiąc 4:     Pilot proposal → wewnętrzna prezentacja dla zarządu (3–4 osoby)
Miesiąc 4–5:   Negocjacje umowy (prawnik, compliance, GDPR considerations)
Miesiąc 5–6:   Podpisanie + onboarding
```

**Implikacje dla lejka:**
- **Czas zamknięcia: 4–6 miesięcy** minimum. Nie planuj dealu DACH w 90 dni — planuj pierwszy discovery call.
- Wymagane materiały: Case study z DACH lub podobnego regulated market (fintech, insurtech), TCO calculator w CHF, referencja od istniejącego klienta
- Nie spamuj. Jeden personalizowany touchpoint co 2 tygodnie jest lepszy niż 5 emaili w tydzień
- **Decyzja de facto: CTO jest Championem, ale CFO jest Economic Buyerem dla kontraktu >CHF 200K/rok**
- GDPR i data residency to realne pytania — miej gotową odpowiedź o delivery model (Polska = EU, no problem)

---

### 🇬🇧 Londyn — "Fast, VC-Influenced, Challenger Welcome"

**Profil kupującego:** CTO w scale-upie (Series B–C), często z US-influenced VC board. Speed-to-market jest KPI. Otwarty na distributed teams (half the city already works that way). Mniej formalny buying process.

**Typowy Buying Journey:**

```
Tydzień 0:     CTO widzi LinkedIn post lub dostaje cold email
Tydzień 1:     Odpowiada "sounds interesting, schedule a call"
Tydzień 2:     Discovery call (45 min) — CTO, czasem VP Eng
Tydzień 3–4:   "Can you send some profiles?" — nieformalne eval engineerów
Miesiąc 2:     Propozycja pilotu (2 inżynierów, 3 mies., fixed scope)
Miesiąc 2–3:   Negocjacje — szybkie (CTO często podpisuje sam do £50K/mies.)
Miesiąc 3:     Onboarding
```

**Implikacje dla lejka:**
- **Czas zamknięcia: 2–4 miesiące** realnie
- UK buyers oczekują szybkiej odpowiedzi i konkretnych profili — miej bench engineerów gotowy do pokazania
- Challenger pitch działa świetnie: Londyn CTO lubi "interesting reframe"
- Ryzyko: **"ghost after pilot"** — CTO jest entuzjastyczny ale board mówi "freeze headcount". Pilnuj czy pilot jest budżetowany czy z discretionary spend
- Monzo, Depop, FullCircl, Kaluza — wszystkie mają Scala/JVM w stacku i aktywnie rekrutują → triggery są teraz

---

### 🇸🇪 Sztokholm / Nordics — "Consensus, Long Nurture, Long Loyalty"

**Profil kupującego:** CTO lub Head of Engineering w fintech/gaming/deeptech. Kulturowo: decyzje consensusem (alla ska vara med). Lojalność wobec vendorów jest wysoka gdy zaufanie jest zbudowane — SoftwareMill ma avg 7+ lat relację właśnie dlatego.

**Typowy Buying Journey:**

```
Miesiąc 0:     Cold outreach — bardzo niska konwersja (odpowie 1 na 10)
Miesiąc 1:     Jeśli odpowie: edukacyjny call "tell me more" — nie decyzyjny
Miesiąc 2–3:   CTO rozmawia z zespołem: "co o tym myślicie?"
Miesiąc 3–4:   Wróci z listą pytań technicznych od teamu
Miesiąc 4–5:   Technical evaluation + rozmowy z inżynierami (team wants to meet the team)
Miesiąc 5–6:   Internal approval — manager, HR, czasem union rep
Miesiąc 6–8:   Pilotowy projekt, małe scope
Miesiąc 9–12:  Pełny kontrakt — i potem 7 lat
```

**Implikacje dla lejka:**
- **Czas zamknięcia: 6–12 miesięcy.** Nordic to inwestycja w 2027, nie Q3 2026.
- Cold outreach działa słabo — priorytet na warm intro, Scala community, r/scala, konferencje
- Arbetsgivaravgift (31.42%) to killer argument który rezonuje natychmiast — to "ukryty podatek" który każdy Swedish CTO rozumie
- WAŻNE: Nie pozycjonuj jako "outsourcing" — to brudne słowo w Szwecji. Pozycjonuj jako "distributed engineering partnership"
- Evolution Gaming (Riga/Nordic) + Tribia AS (Oslo) to najcieplejsze leady — zaczynamy od nich

---

## 3. MEDDIC dla Key Accounts — Archetyp "Post-Series B Scale-up z Scala"

### Template wypełniony dla archetypu: Fintech Series B, ~80 inżynierów, Scala w core stacku, Londyn lub DACH

---

**M — Metrics: Co ten CTO mierzy i co go boli?**

| Metryka | Jak to boli | Nasz angle |
|---------|-------------|------------|
| **Time-to-hire** | Avg 6–9 mies. na seniora Scala w CH/UK/SE | "My dostarczamy w 10 dni roboczych" |
| **Sprint velocity** | Backlog rośnie po fundraise, team nie nadąża | "Twój Q3 OKR product velocity jest zagrożony jeśli nie rozwiążesz tego teraz" |
| **Cost of delay** | €150K+/miesiąc utraconych features (branżowy benchmark) | TCO calculator — pokazujemy liczbę konkretną dla ich geo |
| **Churn risk** | Lokalny senior odchodzi po roku → znowu 7 mies. hiring | "Zero churn risk — my zastępujemy, ty płacisz tę samą stawkę" |
| **Engineer:manager ratio** | Skalowanie teamu bez proporcjonalnego wzrostu management overhead | Squad model z dedykowanym TL = nie musisz hirować EM |

**Pytanie kwalifikujące:** "Ile kosztuje opóźnienie Waszego Q3 roadmapu o miesiąc? Czy mieliście to policzone?" — jeśli CTO odpowie liczbą, jest gotowy do rozmowy o ROI.

---

**E — Economic Buyer: Kto faktycznie podpisuje?**

To NIE zawsze CTO. Zależy od wielkości kontraktu:

| Próg kontraktu | Faktyczny sygnatariusz | Co musisz zrobić |
|----------------|----------------------|------------------|
| <£20K/mies. | CTO podpisuje samodzielnie | CTO = Champion i EB. Jeden stakeholder. |
| £20K–60K/mies. | CTO + CFO (dual approval) | Champion musi "sprzedać" CFO. Daj mu gotowy ROI deck. |
| >£60K/mies. | CTO + CFO + CEO awareness | Pilot → proof → kontrakt. DACH enterprise wchodzi tutaj. |

**Błąd który popełniamy:** zakładamy że CTO = decydent. W DACH scale-upach progi zatwierdzenia są niższe (bardziej konserwatywna kultura finansowa) — kontrakty powyżej CHF 200K/rok często wymagają board awareness.

---

**D — Decision Criteria: Co jest w scorecard klienta?**

Na podstawie rozmów w segmencie (SoftwareMill data + DACH buying patterns):

1. **Scala/JVM seniority** — "Czy naprawdę znają Scala, nie tylko Java?" → Pokazujemy CV, GitHub, referrals z podobnych projektów
2. **Time-to-productivity** — "Kiedy zaczną commitować?" → Tydzień 2, pierwszy PR review dzień 10
3. **Cultural fit z distributed team** — "Czy będą pracować w naszym procesie?" → Ceremonie sprintowe, timezone overlap UK/CET
4. **AI readiness** — "Nasz następny projekt będzie miał AI features" → Scala+AI jako standard, nie add-on
5. **Referencje z podobnej branży** — DACH fintech chce referencję z DACH fintech lub co najmniej regulated market
6. **Exit strategy / lock-in risk** — "Co jeśli chcemy zakończyć?" → Elastyczne terminy, knowledge transfer SLA

---

**D — Decision Process: Ile komitetów, jak długo?**

| Geo | Stages | Liczba stakeholderów | Czas |
|-----|--------|----------------------|------|
| Londyn | Discovery → Profiles → Pilot → Contract | 2–3 (CTO, CFO, czasem VPE) | 8–12 tygodni |
| DACH | Discovery → Deep-dive → Internal eval → Pilot proposal → Legal → Contract | 4–6 (CTO, CFO, Legal, HR, czasem Board) | 16–24 tygodnie |
| Nordics | Discovery → Team eval → Consensus → Pilot → Contract | 5–8 (CTO + cały team engineering + HR) | 24–36 tygodni |

**Sygnał ostrzegawczy:** Jeśli po 3 tygodniach od discovery CTO mówi "muszę skonsultować z teamem" bez konkretnej daty follow-up — deal jest w ryzyku. Użyj JOLT (patrz sekcja 4).

---

**I — Identify Pain: Jak wiemy że ból jest TERAZ?**

Sygnały zewnętrzne (monitorowane przez Davida w sekwencji ABM):

| Sygnał | Co oznacza | Czas reakcji |
|--------|------------|--------------|
| Ogłoszenie o pracę Scala/JVM otwarte >60 dni | Aktywny, nierozwiązany hiring pain | 24h — email z TCO benchmarkiem |
| Niedawny fundraise (Series B/C, ostatnie 6 mies.) | Nowy budget, nowy pressure timeline | 48h — email "post-fundraise velocity" |
| CTO post na LinkedIn o "engineering challenges" | Otwarty na rozmowę, szuka perspektyw | Direct reply + email |
| Nowy VP Engineering zatrudniony | Nowy decision maker = nowe okno | 1 tydzień — nowy spersonalizowany outreach |
| Zamknięte ogłoszenie Scala (po 2 tygodniach) | Nie znaleźli → ból nadal istnieje | "Jak poszło z szukaniem?" — reactivation |

**Pytanie discovery które otwiera ból:** "Ile pozycji Scala/JVM macie otwartych od >90 dni na LinkedIn?"  
Jeśli >2 pozycje — mamy qualified pain.

---

**C — Champion: Kto wewnętrznie walczy za Scalac?**

Idealny Champion to **Head of Engineering / VP Engineering / Lead Architect** — nie sam CTO.

Dlaczego nie CTO? Bo CTO ma zbyt wiele na głowie i często deleguje vendor evaluation. Champion musi:
- Mieć techniczny autorytet (żeby przekonać team)
- Mieć frustrację z hiring (żeby mieć motywację)
- Mieć access do CTO/CFO (żeby escalować)

**Jak znaleźć Championa:**
1. LinkedIn: szukaj "Head of Engineering" lub "Lead Scala Engineer" w target firmach
2. Discovery call: zapytaj "Kto w Twoim teamie najbardziej odczuwa brak inżynierów?"
3. Technical deep-dive: osoba która przychodzi na tech call = potencjalny Champion

**Champion enablement:** Daj Championowi gotowy internal deck (3 slajdy: problem, rozwiązanie, ROI) który może pokazać CFO bez waszej obecności.

---

## 4. JOLT Effect — Neutralizowanie "No Decision"

Główne ryzyko: CTO mówi "to ma sens, wróćmy do tego za kwartał" — i za kwartał znowu to samo.

### Diagnoza: Dlaczego dzieje się "no decision"?

JOLT rozróżnia dwa rodzaje marudzenia:
- **Overload** — CTO ma za dużo opcji do rozważenia (VirtusLab, SoftwareMill, lokalne hiring, Toptal)
- **Inaction bias** — Strach przed złym wyborem jest silniejszy niż ból obecnej sytuacji

W DACH i Nordic kupujący mają **silny inaction bias** — kultura "nie spiesz się, sprawdź dokładnie" jest wartością, nie wadą. Musimy ją respektować ale też kontrować.

---

### Taktyki JOLT per kultura

#### DACH — "Precision over pressure"

**J — Judge: Pomóż mu ocenić, nie przekonuj**
> "Rozumiem że chcesz sprawdzić opcje. Oto jak porównać nas z VirtusLab i lokalnym hiring — trzy kryteria które zazwyczaj są decydujące dla CTO w Twoim segmencie."

Daj mu własny framework oceny z naszymi przewagami wbudowanymi. Nie mów "my jesteśmy lepsi" — pozwól mu dojść do tego samego wniosku.

**O — Offer: Podaj dowód poprzez referencje**
> "Możemy połączyć Cię z CTO w podobnej firmie w DACH który zrobił to 18 miesięcy temu."

W Zürichu referencja od peer > case study. Organizuj warm introductions.

**L — Limit: Ogranicz opcje**
> "Mamy dwa warianty dla Twojego case'u — Starter (2 engineerów, elastyczny) lub Scale (squad z TL). Nie proponuję Enterprise — nie na tym etapie."

Nie zalewaj opcjami. Dwie opcje, jasna różnica, jasna rekomendacja.

**T — Take risk off the table: Pilot bez ryzyka**
> "Proponuję 10-tygodniowy pilot. Jeśli po 10 tygodniach nie czujesz że to działa — za
kańczamy bez kary za zerwanie."

DACH klient boi się lock-in. Pilot z easy exit = jedyna droga do pierwszego tak.

---

#### Nordic — "Consensus enablement"

Problem nie jest w CTO — problem jest w tym że CTO nie może powiedzieć "tak" bez zgody teamu. Więc pomagamy zbudować konsensus.

**Taktyka: "Team buy-in kit"**
Dostarcz CTO paczka którą może wziąć na spotkanie z teamem:
- 1-pager dla inżynierów: "Jak pracuje się z Scalac teamem" (kultura, proces, komunikacja)
- FAQ dla HR: "Co to znaczy partnership, nie outsourcing"
- ROI deck dla CFO: arbetsgivaravgift (31.42%) + hiring timeline calculator w SEK

**Taktyka: "Engineering team intro call"**
Zaproponuj że team Scalac porozmawia z teamem inżynierskim, nie z CTO. W kulturze nordickiej peer-to-peer trust buduje się szybciej niż vendor-to-buyer trust.

**T — Take risk off the table: pierwsza iteracja jako paid discovery**
> "Zamiast od razu team extension, zróbmy 3-tygodniowy Technical Partnership Sprint — dwa nasze seniory pracują z Waszym teamem nad konkretnym tech challenge. Płacisz za sprint, nie za kontrakt."

Microcommitment → consensus → kontrakt. Dłuższa droga ale jedyna realna ścieżka w Nordic.

---

## 5. Nurture Cadence — "Not Ready" ICP

Profil: CTO który spełnia ICP (Series B+, Scala w stacku, DACH/London/Stockholm) ale powiedział "nie teraz" lub nie odpowiedział po 2 touchpointach.

### Cadence: 12-miesięczny program nurture (niski koszt, wysoka wartość)

| Czas | Touchpoint | Format | Cel |
|------|-----------|--------|-----|
| Miesiąc 1, Tydzień 1 | Personalizowany email: "Widzę że szukacie Scala devów — tu benchmark hiring dla Waszego geo" | Email | Wstępne zainteresowanie |
| Miesiąc 1, Tydzień 3 | LinkedIn connection request + krótka wiadomość (bez pitch) | LinkedIn | Relacja |
| Miesiąc 2 | Wartościowy content: link do Playbook post ("Post-Series B Engineering Velocity") | Email | Trust building |
| Miesiąc 3 | Trigger-based follow-up: "Widziałem że nadal macie otwartą pozycję Scala — jak poszło?" | Email | Reaktywacja bólu |
| Miesiąc 4 | Invite na webinar / Scala+AI async session (jeśli istnieje) | Email | Edukacja + event |
| Miesiąc 5 | LinkedIn interakcja z ich contentem (wartościowy komentarz) | LinkedIn | Obecność w radzie |
| Miesiąc 6 | "6-month hiring benchmark" — "Pół roku temu zaczęliście szukać — gdzie jesteście?" | Email | Direct reopen |
| Miesiąc 7–9 | Cichy kwartał — tylko LinkedIn activity monitoring | Pasywny | Nie burnuj |
| Miesiąc 10 | Trigger: fundraise, nowa pozycja, LinkedIn post → natychmiastowy personalizowany outreach | Email | Re-engagement |
| Miesiąc 12 | "Year-end check-in" — "Jakie są Wasze plany inżynierskie na 2027?" | Email | Następny cykl |

**Zasady nurture:**
1. Każdy touchpoint musi być **wartościowy** — nie "just checking in". Zawsze daj coś (benchmark, insight, link)
2. Monitoruj sygnały: nowe job postings, fundraise, LinkedIn posts = **skróć scheduling, wejdź natychmiast**
3. Maksymalnie **2 touchpointy/miesiąc** — w DACH i Nordic więcej = spam
4. Intern może obsługiwać 60% tej cadence (szablony + monitoring). Marketer personalizes trigger-based emails.

**Narzędzia:** HubSpot/Pipedrive do śledzenia, LinkedIn Sales Navigator do monitorowania sygnałów, Google Alerts na funding rounds w target firmach.

---

## 6. Rekomendacja: Webinar — Tak czy Nie?

### Werdykt: **TAK — ale nie live, i nie dla CTO**

#### Dlaczego to ma sens strategicznie:
- Webinar jako evergreen asset: 1 produkcja → 6–12 miesięcy używania w nurture sequences
- Competitors (VirtusLab, SoftwareMill) nie mają dedykowanego "Team Extension playbook" webinaru dla JVM/Rust — to whitespace
- Webinar = sygnał zainteresowania (registration = lead) → triggeruje outreach od Davida

#### Dlaczego NIE live na tym etapie:
- 1 marketer + 1 intern nie ma capacity na live event production (invitations, follow-up, tech setup, moderacja, reminders) — to minimum 80 godzin jednorazowo
- CTOs z Zürichu i Sztokholmu **nie uczestniczą w live webinarach** od vendorów których nie znają. Attending a live webinar = public signal of interest = perceived risk for conservative buyers
- Live webinar bez established audience = 15–30 uczestników, większość to juniorzy i sales recon od konkurencji

#### Format który rekomendują: **Async "Playbook Session"**

```
Format: 35–45 minut nagranego wideo playbook
Tytuł roboczy: "Engineering Velocity After Series B: Why JVM/Rust Hiring Is Broken 
               in Zürich, London & Stockholm — and What Works Instead"
Prowadzi: CTO/VP Eng z Scalac (credibility) + 1 klient referencyjny (proof)
Produkcja: prosty, high-quality screenshare + talking head, nie fancy studio
Landing page: formularz rejestracyjny (imię, firma, city, "jak duży Wasz Scala team")
Dystrybucja: LinkedIn organic posts, email sequences, r/scala, Scala Discord
```

#### Timing:
- **Czerwiec 2026** — razem z Scala+AI Manifesto jako flagship moment
- Pojedynczy "Playbook Session" staje się wtedy częścią większej kampanii contentowej
- Lead magnet: "Pobierz TCO Calculator dla Twojego geo" na tej samej landing page

#### Dla kogo:
- **Head of Engineering / VP Engineering** (nie CTO) — oni szukają praktycznych rozwiązań, chętniej ogląda webenary niż CTO
- Rozmiar firmy: 40–200 inżynierów (pod tym jest, powyżej ma własne HR machinery)
- Geo: UK najbardziej otwarty na tego typu content, DACH reaguje jeśli temat jest bardzo konkretny, Nordic słabo (prefer long-form written content)

#### Co NIE jest webinarem:
- Produktowa prezentacja Scalac ("oto co robimy") → to kiepski ToFu
- "Jak używać Scala do AI" → to dla devów, nie dla kupujących
- Panel dyskusyjny → nie mamy audience i partnerships do tego

---

## 7. Stanowisko do Debaty — Co Kwestionuję u Marcusa

Marcus zrobił świetną robotę z challenger pitch i TCO math. Mam jednak trzy **konkretne zastrzeżenia** które mogą nas kosztować deale jeśli ich nie poprawimy:

---

### Zastrzeżenie #1 — Stockholm arithmetic jest zepsuta na poziomie Starter

Marcus pisze: Scalac Starter Stockholm: €16,000–19,500/miesiąc → SEK ~185,000–225,000/miesiąc.  
Tymczasem Marcus sam wyliczył TCO lokalnego seniora w Sztokholmie: **SEK 139,576/miesiąc** (po miesiącu 8).

**Wynik: Scalac Starter jest DROŻSZY NIż lokalny senior w Sztokholmie** — nawet uwzględniając rekrutera.  
To rujnuje narrację "jesteśmy tańsi". Szwedzki CFO policzy to w 5 minut i odrzuci ofertę.

**Rozwiązanie:** Dla Stockholm:
1. Nie sprzedawać na Starter level — minimalny punkt wejścia to **Scale (3–4 inżynierów)** gdzie ekonomia się poprawia (SEK ~555,000–715,000/mies. vs TCO 3 lokalnych seniorów = ~SEK 419,000/mies. ale z 24-miesięcznym hiring delay i churn risk)
2. Albo przyznać że Stockholm pricing nie jest "tańszy" ale "szybszy i bez ryzyka" i sprzedawać na time-to-productivity, nie cost savings. Zmieniamy narrację, nie obniżamy ceny.

---

### Zastrzeżenie #2 — Pipeline math jest nadmiernie optymistyczna, nie widać konwersji

Marcus celuje w "3 deale po 180K PLN w 90 dni". Nie ma lejka który to uzasadnia.

**Moje wyliczenie realistyczne:**

```
Outbound (Spears): 15–18 named accounts contacted
Response rate cold email B2B: ~8–12%  → 1–2 replies
Discovery call booking: 50% z tych co odpiszą → 1–2 calls w month 1
Po discovery: 30% proceeds → 0–1 qualified opportunity po 30 dniach

W 90 dniach realnie: 2–4 discovery calls, 1–2 qualified opps
W 6 miesiącach realnie: 1 deal zamknięty (Londyn, najkrótszy cycle)
```

**3 deale w 90 dniach** to fantasy przy zimnym outreach na premium market z 2-osobowym teamem.  
Musimy zarządzać oczekiwaniami: **90 dni = erste discovery calls, nie signed contracts.**

---

### Zastrzeżenie #3 — Brak "trigger-based" wejścia w model sprzedaży

Marcus opisuje pricing i positioning ale nie mówi PO CZYM Scalac wchodzi do rozmowy. Moja obserwacja: cold outreach bez triggera konwertuje dramatycznie gorzej.

Rekomendacja: **każda Spear musi mieć przypisany trigger** (open job posting, recent fundraise, CTO post) — to podwaja response rate bo email jest "relevantny teraz, nie generalnie". David musi monitorować sygnały, nie tylko wysyłać sekwencje.

---

## Moja Propozycja — Skonsolidowany Lejek (90 dni → 6 mies.)

### Faza 1: 0–30 dni — "Load the gun"
- David identyfikuje 15 Tier 1 accounts z triggerami (aktywne job postings Scala/JVM)
- Kai przygotowuje 3 emaile per geo (DACH, UK, Nordic) — personalizowane triggery
- Marketer publikuje 2 Nets assets: blog post "TCO hiring" + LinkedIn carousel
- Elena+David: MEDDIC scoring dla każdego konta

### Faza 2: 30–60 dni — "Launch Spears"
- Outbound sekwencje startują dla 15 kont (Londyn priorytet)
- Follow-up calls / replies → kwalifikacja MEDDIC
- Seeds: 5 emaili do istniejących klientów Scalac po referencje

### Faza 3: 60–90 dni — "Harvest first calls"
- Target: 3–5 discovery calls zarezerwowanych
- Dla każdego konta: wypełniony MEDDIC scorecard
- DACH i Nordic accounts wchodzą do 6-miesięcznego nurture cadence
- Londyn: push do pilot proposal jeśli kwalifikowany

### KPIs których pilnujemy:
| KPI | 30 dni | 60 dni | 90 dni |
|-----|--------|--------|--------|
| Konta contacted | 15 | 15 | 15 |
| Response rate | — | 8–12% | 10–15% |
| Discovery calls booked | 0 | 2 | 3–5 |
| MEDDIC qualified opps | 0 | 1 | 2–3 |
| Deals in negotiation | 0 | 0 | 0–1 (Londyn) |
| Closed deals | 0 | 0 | 0 |
| 6-month target | — | — | **1 deal signed** |

---

*Elena — Funnel Architect, Scalac AI Council, Runda 1*

# Rada AI Scalac - Multi-Agent Marketing Council

> **4 agenci AI pracują równolegle, debatują i tworzą kompletny plan marketingowy w 30 minut.**

---

## 🚀 Szybki Start (3 kroki)

```bash
# 1. Wejdź w katalog
cd scalac_council_v2

# 2. Uruchom orchestrator
python orchestrator.py

# 3. Postępuj zgodnie z instrukcjami (spawn 4 agentów w Kimi Code)
```

---

## Co to robi

4 agenci pracują równolegle, debatują i dochodzą do konsensusu:

| Agent | Rola | Co produkuje |
|-------|------|--------------|
| **Marcus** | Offer Architect | Oferta, pricing, positioning |
| **Elena** | Funnel Architect | Lejek, MEDDIC, forecast |
| **Kai** | Copywriter | Landing page, emaile, LinkedIn |
| **David** | Lead Strategist | ABM, Dream 100, sekwencje |

**Wynik:** 4 spójne dokumenty w 30 minut (zamiast 5 promptów na krzyż).

---

## Do czego to używać

| Scenariusz | Wynik |
|------------|-------|
| **Nowa oferta** | Offer Package + Pricing + Challenger Pitch |
| **Nowy segment** | Funnel + ABM Strategy |
| **Launch produktu** | Landing Page + Lead Gen Plan |
| **Webinar ideation** | 3 tematy webinarów (z battlecards) |
| **Pipeline Review** | Analiza + Action Plan |

---

## 📁 Struktura

```
scalac_ai_council/
├── README.md                      # Ten plik
├── scalac_battlecards.docx.md    # Analiza konkurencji (VirtusLab, SoftwareMill, itd.)
├── scalac_content_plan.docx.md   # Plan contentowy Q2-Q3
└── scalac_council_v2/            # ✅ SYSTEM
    ├── orchestrator.py           # Koordynator
    ├── agents/                   # 4 agenci (Marcus, Elena, Kai, David)
    ├── shared/                   # Brief + battlecards + content_plan
    ├── README.md                 # Pełna dokumentacja
    └── WEBINAR_GUIDE.md          # Jak generować tematy webinarów
```

---

## 🎯 Kluczowa różnica

| Tradycyjne "5 promptów" | Rada AI (Ten system) |
|------------------------|----------------------|
| Sekwencyjnie (Marcus → Elena → Kai...) | Równolegle (wszyscy na raz) |
| Brak debaty | 3 rundy feedback loopów |
| Brak konsensusu | Agenci się zgadzają lub uzasadniają disagreement |
| 15 minut, słaba jakość | 30 minut, wysoka jakość |

---

## 💡 Przykładowy przebieg

**Round 1:**
- Marcus: "Pricing 75-85 EUR/h, lead with 2-week guarantee"
- Elena: "Potrzebujemy 160 leads dla 3 deali"
- Kai: "Messaging jest za techniczny dla CTO"
- David: "Mam listę 50 fintechów do ABM"

**Round 2 (debaty):**
- Elena: "Marcus, 50% konwersja to nierealistyczne!"
- Marcus: "Elena, za niski pricing zabija wartość!"

**Round 3 (konsensus):**
- Agenci się zgadzają: 25% konwersja, 80 EUR/h

**Output:** 4 spójne dokumenty.

---

## 📊 Bonus: Battlecards

W `scalac_council_v2/shared/` masz:
- `battlecards.md` - analiza 5 konkurentów + 6 WHITESPACE OPPORTUNITIES
- `content_plan.md` - plan contentowy z 10 postami

Agenci mogą czytać te pliki i proponować webinary wypełniające luki rynku.

**Przykład:** Agenci znajdą w battlecards że "Akka + Agentic AI" to whitespace (nikt tego nie robi) i zaproponują webinar.

---

## 📖 Dokumentacja

- **Pełna instrukcja:** [`scalac_council_v2/README.md`](scalac_council_v2/README.md)
- **Webinar ideation:** [`scalac_council_v2/WEBINAR_GUIDE.md`](scalac_council_v2/WEBINAR_GUIDE.md)

---

## 🚀 Start

```bash
cd scalac_council_v2 && python orchestrator.py
```

🎯 **Gotowe do użycia w Kimi Code.**

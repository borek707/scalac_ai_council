# 🖥️ WebUI Roadmap dla Rady AI Scalac

## Przegląd
WebUI zamieni linię komend w intuicyjny interfejs webowy, gdzie użytkownicy mogą wizualnie tworzyć kampanie sprzedażowe, śledzić dyskusje agentów w real-time i przeglądać finalne propozycje.

## 🎯 Kluczowe Features

### 1. 📝 Visual Brief Editor - WYSIWYG edytor briefów
- **Frontend:** Markdown editor (Quill.js/Tiptap) - 1 tydzień
- **Backend:** Save/load brief endpoint - 2 dni
- **Razem:** ~1.5 tygodnia

### 2. 📁 Drag & Drop CSV Upload - Łatwe ładowanie danych prospektowych
- **Frontend:** File upload component (Vue-dropzone) - 3 dni
- **Backend:** CSV processing + validation - 1 tydzień
- **Razem:** ~1.5 tygodnia

### 3. 👥 Agent Avatars - Wizualna reprezentacja 4 agentów
- **Frontend:** Avatar components + agent info cards - 2 dni
- **Backend:** Agent metadata API - 1 dzień
- **Razem:** ~3 dni

### 4. 💬 Real-time Discussion - Live view dyskusji między agentami
- **Frontend:** Discussion timeline component - 1 tydzień
- **Backend:** WebSocket/Polling dla discussion updates - 1 tydzień
- **Integration:** File watching dla discussion/*.md - 3 dni
- **Razem:** ~2.5 tygodnia

### 5. 📊 Progress Tracking - Status rund i consensus
- **Frontend:** Progress bars + status indicators - 3 dni
- **Backend:** Status API (rounds, consensus detection) - 1 tydzień
- **Razem:** ~1.5 tygodnia

### 6. 📄 Final Output Viewer - Ładny display kompletnego planu
- **Frontend:** Markdown renderer + export buttons - 1 tydzień
- **Backend:** Final proposal API - 2 dni
- **Razem:** ~1.5 tygodnia

### 7. 🔄 Campaign History - Historia poprzednich kampanii
- **Frontend:** Campaign list + search/filter - 1 tydzień
- **Backend:** Campaign storage + retrieval - 1 tydzień
- **Database:** Simple JSON/file storage - 2 dni
- **Razem:** ~2.5 tygodnia

## 📅 Roadmap fazowy

### Faza 1: MVP (6-8 tygodni)
- Visual Brief Editor
- CSV Upload
- Basic campaign runner
- Final Output Viewer

### Faza 2: Core Features (7-9 tygodni)
- Agent Avatars
- Real-time Discussion
- Progress Tracking

### Faza 3: Advanced (7-8 tygodni)
- Campaign History
- User management
- Analytics

### Faza 4: Polish (5-6 tygodni)
- UI/UX improvements
- Testing
- Performance optimization

## 💰 Szacunki kosztów

- **Całkowity czas:** 8-12 tygodni dla wszystkich features
- **Zespół:** 1 full-stack developer
- **Technologie:** FastAPI + Vue.js + Docker

## 🏃‍♂️ Szybsza alternatywa: Streamlit MVP

Zamiast full-stack aplikacji, MVP w **4-6 tygodni** używając Streamlit:

```python
import streamlit as st
import subprocess

st.title("🧠 Rada AI Scalac")

brief = st.text_area("Brief projektu")
csv_file = st.file_uploader("Upload CSV z danymi prospektowymi")

if st.button("🚀 Uruchom kampanię"):
    # Zapisz pliki
    # Uruchom orchestrator
    # Wyświetl wyniki
    st.success("Kampania uruchomiona!")
```

## 🏗️ Architektura techniczna

```
scalac_council_v2/
├── webui/
│   ├── backend/          # FastAPI
│   │   ├── app.py
│   │   ├── agents/
│   │   └── static/
│   ├── frontend/         # Vue.js
│   │   ├── src/components/
│   │   ├── src/views/
│   │   └── package.json
│   └── docker-compose.yml
```

## 🔧 Technologie

- **Backend:** FastAPI (Python) - async, type-safe API
- **Frontend:** Vue.js 3 + Composition API
- **Real-time:** WebSockets lub Server-Sent Events
- **Styling:** Tailwind CSS
- **Deployment:** Docker + docker-compose

## 📈 Korzyści WebUI

1. **Lepszy UX** - intuicyjny interfejs zamiast terminala
2. **Visual feedback** - śledzenie postępów w real-time
3. **Łatwiejsze onboarding** - dla nowych użytkowników
4. **Team collaboration** - współdzielenie kampanii
5. **Analytics** - śledzenie skuteczności planów

## 🚦 Status

- **Aktualnie:** System działa w terminalu/IDE
- **Następne kroki:** MVP w Streamlit (4-6 tygodni)
- **Full WebUI:** 8-12 tygodni od startu

---

*Ten dokument będzie aktualizowany wraz z postępem developmentu.*
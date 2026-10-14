# 🐮 RAGUL - Voice-First Self-Hosted Dairy AI Assistant

> **RAGUL**: Real-time Agro Guidance & Utilitarian Livestock Assistant
> Fully self-hosted, 100% open-weight stack without OpenAI APIs or external subscriptions.
> Native support for **Tanglish** (Tamil + English code-mixing), **Tamil**, **Hindi**, **Hinglish**, and **English**.

---

## 🏛️ Architecture

```
USER VOICE
    │
    ▼ (Microphone: navigator.mediaDevices.getUserMedia() / 16kHz PCM)
SILERO VAD (Voice Activity Detection & Interruption Trigger)
    │
    ▼ (Real-time Speech Chunk Stream)
FASTER-WHISPER (Multilingual STT - Preserves Tanglish/Tamil/Hindi)
    │
    ▼ (Unfiltered Mixed-Language Transcript)
RAGUL BACKEND (FastAPI + WebSocket Server)
    │
    ▼ (Sliding Window Session Memory + Pronoun Resolver)
SELF-HOSTED LLM (vLLM / llama.cpp - Qwen2.5-7B / Llama-3-8B)
    │
    ▼ (Dynamic Tool Calling: get_cow_health_summary, mastitis_risk, etc.)
FASTAPI FARM TOOLS ──► PostgreSQL / SQLite Database (Cattle, Milk, Feed, Health)
    │
    ▼ (Natural Synthesized Response)
SELF-HOSTED TTS (AI4Bharat Indic-TTS / Kokoro / Browser-Native)
    │
    ▼ (Audio Stream / WebSocket)
FARMER HEARS ANSWER (Jarvis-style instant interruption support)
```

---

## 🚀 Key Features

1. **Zero OpenAI Dependencies**: Built on open-source, open-weight tools (`faster-whisper`, `silero-vad`, `vLLM` / `llama.cpp`, `AI4Bharat Indic-TTS`).
2. **Jarvis-Style Interruption**: When RAGUL is speaking and the farmer starts talking, Silero VAD detects speech instantly and halts audio playback immediately.
3. **Multilingual Code-Mixing (Tanglish / Hinglish / Tamil / Hindi)**: Preserves farmer expressions like *"Ragul cow 37 ku milk yen kammiya iruku?"* without forcing machine translation.
4. **Lightweight Custom Tool Router**: No heavy frameworks (LangChain / CrewAI / AutoGen). Direct, predictable tool execution against the farm database.
5. **Contextual Memory & Anti-Repetition**: Resolves pronouns like *"What should I do now?"* or *"Why did her yield drop?"* by linking to recent entity context (e.g. Cow 37).
6. **Live Cattle Telemetry Dashboard**: Real-time monitoring of somatic cell counts, mastitis quarters, estrus heat detection cycles, and feed ration deficits.

---

## 📦 Project Structure

```
d:/Ragul Ai/
├── backend/
│   ├── app/
│   │   ├── audio/
│   │   │   ├── vad.py            # Silero VAD speech detection & interruption logic
│   │   │   ├── stt.py            # faster-whisper multilingual transcriber
│   │   │   └── tts.py            # AI4Bharat / Kokoro TTS adapter
│   │   ├── database/
│   │   │   ├── db.py             # Async SQLAlchemy engine
│   │   │   ├── models.py         # Cattle, MilkReading, HealthEvent, FeedRecord, Session models
│   │   │   └── seed_data.py      # Seed data (Cow 37 mastitis case, Cow 14 heat cycle, etc.)
│   │   ├── llm/
│   │   │   ├── client.py         # Universal vLLM / llama.cpp / local reasoning client
│   │   │   ├── prompts.py        # Domain-tuned dairy prompts & entity resolution
│   │   │   └── router.py         # Lightweight custom tool router
│   │   ├── memory/
│   │   │   └── session_manager.py # Sliding window memory & conversation sessions
│   │   ├── tools/
│   │   │   └── farm_tools.py     # Farm DB tools (health summary, mastitis, milk trends, estrus)
│   │   ├── config.py             # Environment configurations
│   │   └── main.py               # FastAPI app with REST and WebSocket endpoints
│   ├── requirements.txt
│   └── run_server.py             # Backend launcher
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Header.tsx            # Brand header & telemetry indicator
    │   │   ├── VoiceSphere.tsx       # Glowing Jarvis orb with live waveform visualizer
    │   │   ├── ConversationFeed.tsx  # Chat stream & live tool call visualizer
    │   │   ├── FarmTelemetryPanel.tsx # Live herd statistics, Cow 37 & Cow 14 alerts
    │   │   └── QuickQueryBar.tsx     # One-click farmer query chips
    │   ├── services/
    │   │   └── audioEngine.ts        # Browser-native AudioContext + WebSocket streamer
    │   ├── store/
    │   │   └── useRagulStore.ts      # Zustand state store
    │   ├── App.tsx
    │   ├── index.css                 # Glassmorphism & dark aesthetic stylesheet
    │   └── main.tsx
    ├── package.json
    └── vite.config.ts
```

---

## 🛠️ Quick Start

### 1. Start the Backend

```bash
cd backend
pip install -r requirements.txt
python run_server.py
```
*Backend will be running on `http://localhost:8000` with Swagger docs at `http://localhost:8000/docs`.*

### 2. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```
*Frontend will be running on `http://localhost:5173`.*

---

## 🔌 Connecting to Local LLM Engines

In `backend/app/config.py` (or via `.env`):

- **vLLM**:
  ```env
  LLM_PROVIDER=vllm
  LLM_API_BASE=http://localhost:8000/v1
  LLM_MODEL_NAME=Qwen/Qwen2.5-7B-Instruct
  ```
- **llama.cpp**:
  ```env
  LLM_PROVIDER=llamacpp
  LLM_API_BASE=http://localhost:8080/v1
  ```
- **Ollama**:
  ```env
  LLM_PROVIDER=ollama
  LLM_API_BASE=http://localhost:11434/v1
  LLM_MODEL_NAME=qwen2.5:7b
  ```

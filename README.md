# 🐮 RAGUL - Voice-First Multilingual AI Dairy Farm Supervisor

> **RAGUL**: Real-time Agro Guidance & Utilitarian Livestock Assistant  
> Intelligent voice assistant powered by **JarvisLabs Cloud LLM** inference and **Supabase Cloud PostgreSQL** telemetry.  
> Native multilingual support for **Tanglish** (Tamil + English code-mixing), **Tamil**, **Hindi**, **Hinglish**, and **English**.

---

## 🏛️ System Architecture

```
                    ┌─────────────────────────┐
                    │  FARMER / USER VOICE    │
                    │  (Microphone / WebMic)  │
                    └───────────┬─────────────┘
                                │ 16kHz PCM Audio Stream
                                ▼
         ┌─────────────────────────────────────────────────┐
         │       SILERO VAD (Voice Activity Detection)     │
         │       Instant Interruption Detection Trigger    │
         └──────────────────────┬──────────────────────────┘
                                │ Active Speech Chunks
                                ▼
         ┌─────────────────────────────────────────────────┐
         │            FASTER-WHISPER (STT Engine)          │
         │   Tanglish / Tamil / Hindi / English Transcriber│
         └──────────────────────┬──────────────────────────┘
                                │ Text Transcript
                                ▼
         ┌─────────────────────────────────────────────────┐
         │           FASTAPI + WEBSOCKET SERVER            │
         │    Sliding Window Session Memory & Pronouns     │
         └───────┬───────────────────────────────┬─────────┘
                 │                               │
                 ▼                               ▼
  ┌──────────────────────────────┐ ┌──────────────────────────────┐
  │      JARVISLABS CLOUD LLM    │ │       SUPABASE CLOUD DB      │
  │  (GLM-5.3-Flash / vLLM / OSS)│ │   (PostgreSQL Async Engine)  │
  │  Autonomous Tool Calling &   │ │   Cattle Records, Milk Yield,│
  │  Farm Decision Reasoning     │ │   Mastitis, Worker Shifts    │
  └──────────────┬───────────────┘ └──────────────┬───────────────┘
                 │                                │
                 └───────────────┬────────────────┘
                                 │
                                 ▼
         ┌─────────────────────────────────────────────────┐
         │       RAG ENGINE (Veterinary QA & Catalog)      │
         └──────────────────────┬──────────────────────────┘
                                │ Synthesized Text & Tool Result
                                ▼
         ┌─────────────────────────────────────────────────┐
         │             TTS & 3D AVATAR INTERFACE           │
         │  Browser-Native Speech Synthesis & Hologram     │
         └─────────────────────────────────────────────────┘
```

---

## 🚀 Key Highlights & Capabilities

1. **JarvisLabs High-Performance Cloud LLM**:
   - Ultra-low latency inference powered by **JarvisLabs** (`https://models.jarvislabs.net/v1`).
   - Supports models such as `glm-5.3-flash`, `gpt-oss-120b`, and open-source models with OpenAI-compatible API endpoints.
   - Flexible fallback to local Ollama or vLLM instances for offline operation.

2. **Supabase Cloud PostgreSQL Integration**:
   - Real-time cloud database hosting production cattle records, milk production logs, health events, and worker schedules.
   - Automated tool calls query live database records to answer questions like:
     - *"Which cattle gave the highest milk yield today?"*
     - *"எந்த மாட்டிற்கு மடிநோய் அறிகுறி உள்ளது?"* (Which cow shows symptoms of mastitis?)
     - *"Inniku morning ethanai workers check in pannanga?"* (How many workers checked in this morning?)

3. **Multilingual Code-Mixing (Tanglish & Hinglish)**:
   - Understands natural mixed speech without requiring translation layers (e.g., *"Cow 37 ku milk yen kammiya iruku?"*).

4. **Zero-Lag Voice Interruption (Silero VAD)**:
   - When RAGUL is speaking, speaking into the microphone immediately triggers Silero VAD to halt audio playback and attend to the user.

5. **3D Avatar & Farm Telemetry Dashboard**:
   - React 18 + Vite dashboard with 3D talking avatar, live audio orb visualizer, quick query chips, and real-time herd metrics.

---

## 📦 Project Structure

```
Ragul Ai/
├── .gitignore                      # Git exclusion rules
├── docker-compose.yml              # Multi-container orchestration (Backend + Frontend + Ollama)
├── README.md                       # Documentation
│
├── backend/
│   ├── Dockerfile                  # Container build for backend
│   ├── .dockerignore
│   ├── .env                        # Local credentials (JarvisLabs & Supabase)
│   ├── .env.example                # Configuration template
│   ├── requirements.txt            # Python dependencies
│   ├── run_server.py               # Uvicorn server launcher
│   ├── test_agent.py               # Multilingual CLI test suite
│   ├── app/
│   │   ├── audio/
│   │   │   ├── vad.py              # Silero VAD speech detection & interruption
│   │   │   ├── stt.py              # faster-whisper multilingual transcriber
│   │   │   └── tts.py              # Text-to-speech adapter
│   │   ├── database/
│   │   │   ├── db.py               # Async SQLAlchemy engine
│   │   │   ├── models.py           # Cattle, MilkReading, HealthEvent, Worker, Feed models
│   │   │   ├── supabase_client.py  # Supabase cloud client
│   │   │   └── seed_data.py        # Seed script for initial records
│   │   ├── knowledge/
│   │   │   └── rag_engine.py       # RAG retriever for catalog & veterinary QA
│   │   ├── llm/
│   │   │   ├── client.py           # JarvisLabs & OpenAI-compatible client
│   │   │   ├── prompts.py          # Domain-tuned dairy supervisor prompts
│   │   │   └── router.py           # Dynamic tool calling & message routing
│   │   ├── memory/
│   │   │   └── session_manager.py  # Conversation history & sliding context
│   │   ├── tools/
│   │   │   └── farm_tools.py       # Database query tools (milk yield, health, workers)
│   │   ├── config.py               # Pydantic settings
│   │   └── main.py                 # FastAPI application & WebSocket server
│   ├── data/knowledge_base/
│   │   ├── products_catalog.json   # Dairy medicine & nutritional products
│   │   └── veterinary_qa.json      # Clinical veterinary diagnosis knowledge
│   └── supabase/
│       ├── 01_schema.sql           # Database schema definition
│       └── 02_seed_september_2026.sql # Sample farm dataset
│
└── frontend/
    ├── Dockerfile                  # Nginx production container
    ├── .dockerignore
    ├── nginx.conf                  # Reverse proxy configuration
    ├── index.html
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    ├── public/                     # Avatar graphics and icons
    └── src/
        ├── components/
        │   ├── Header.tsx              # System status & metrics
        │   ├── VoiceSphere.tsx         # Holographic glowing audio orb
        │   ├── TalkingRagul3D.tsx      # 3D interactive avatar
        │   ├── RagulAvatar.tsx         # Dynamic facial expression avatar
        │   ├── ConversationFeed.tsx    # Live dialogue stream
        │   ├── FarmTelemetryPanel.tsx  # Live herd stats & alerts
        │   └── QuickQueryBar.tsx       # Pre-configured farmer query chips
        ├── services/
        │   └── audioEngine.ts          # Web Audio API & WebSocket client
        ├── store/
        │   └── useRagulStore.ts        # Zustand UI & session state
        ├── App.tsx
        ├── index.css                   # Glassmorphism styling
        └── main.tsx
```

---

## ⚙️ Environment Configuration

Create or update your `backend/.env` using the provided [`.env.example`](backend/.env.example):

```env
# ==========================================
# LLM Provider - JarvisLabs Cloud
# ==========================================
LLM_PROVIDER=jarvislabs
JARVISLABS_API_KEY=your_jarvislabs_api_key_here
LLM_API_BASE=https://models.jarvislabs.net/v1
LLM_MODEL_NAME=glm-5.3-flash
LLM_TEMPERATURE=0.2

# ==========================================
# Supabase Cloud PostgreSQL Database
# ==========================================
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_anon_or_service_role_key
DATABASE_URL=postgresql+asyncpg://postgres:your_password@db.your-project-id.supabase.co:5432/postgres

# ==========================================
# Audio Speech-to-Text & VAD
# ==========================================
WHISPER_MODEL_SIZE=tiny
WHISPER_DEVICE=cpu
WHISPER_COMPUTE_TYPE=int8
VAD_SAMPLE_RATE=16000
VAD_THRESHOLD=0.5
TTS_ENGINE=browser_native
DEFAULT_LANGUAGE=en-US
```

---

## 🛠️ Quick Start

### 1. Run the Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server
python run_server.py
```
- API server will start at: `http://localhost:8000`
- Interactive Swagger docs: `http://localhost:8000/docs`

### 2. Run the Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
- Web dashboard will be available at: `http://localhost:5173`

### 3. Run Multilingual CLI Test Suite

To verify JarvisLabs and Supabase query responses across Tamil, Tanglish, Hindi, and English:

```bash
cd backend
python test_agent.py
```

---

## 🐳 Running with Docker (Optional)

To start the entire stack (FastAPI Backend, Nginx Frontend, and optional Ollama service) in containerized mode:

```bash
docker-compose up --build
```
- Web Dashboard: `http://localhost`
- API Backend: `http://localhost:8000`

---

## 📄 License

Proprietary & Developed for Dairy Herd Management.

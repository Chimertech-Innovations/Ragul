# 🐮 RAGUL - Voice-First Multilingual AI Dairy Farm Supervisor

<div align="center">

![RAGUL AI Banner](frontend/public/ragul_transparent.png)

### **RAGUL**: **R**eal-time **A**gro **G**uidance & **U**tilitarian **L**ivestock Assistant
*The Next-Generation Voice & Vision AI Dairy Farm Manager Powered by JarvisLabs Cloud LLM, Supabase Cloud PostgreSQL & NASEM 2021 Nutrition Science*

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%200.110+-009688.svg?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%2018%20%7C%20TypeScript%20%7C%20Vite-61DAFB.svg?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![Apache ECharts](https://img.shields.io/badge/Analytics-Apache%20ECharts%206.1-AA344D.svg?style=flat-square&logo=apacheecharts&logoColor=white)](https://echarts.apache.org)
[![PostgreSQL](https://img.shields.io/badge/Database-Supabase%20Cloud%20PostgreSQL-3ECF8E.svg?style=flat-square&logo=supabase&logoColor=white)](https://supabase.com)
[![LLM Inference](https://img.shields.io/badge/LLM%20Inference-JarvisLabs%20GLM--5.3--Flash-FF6F00.svg?style=flat-square)](https://jarvislabs.ai)
[![Audio VAD](https://img.shields.io/badge/Voice%20VAD-Silero%20VAD%20v4-blue.svg?style=flat-square)](https://github.com/snakers4/silero-vad)
[![STT](https://img.shields.io/badge/STT-faster--whisper%20Multilingual-4A154B.svg?style=flat-square)](https://github.com/SYSTRAN/faster-whisper)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg?style=flat-square)](#-license)

</div>

---

## 📑 Table of Contents

- [Overview & Vision](#-overview--vision)
- [System Architecture](#-system-architecture)
- [Key Features & Highlights](#-key-features--highlights)
  - [Zero-Lag Voice Activity Detection & Interruption](#1-zero-lag-voice-activity-detection--interruption)
  - [Dairy Phonetic STT Normalization](#2-dairy-phonetic-stt-normalization)
  - [Autonomous Tool-Calling Agent Router](#3-autonomous-tool-calling-agent-router)
  - [Interactive ECharts Analytics Panel](#4-interactive-echarts-analytics-panel)
  - [NASEM 2021 Dairy Nutrition Engine](#5-nasem-2021-dairy-nutrition-engine)
  - [Veterinary Q&A Clinical Knowledge Base & RAG](#6-veterinary-qa-clinical-knowledge-base--rag)
  - [Multi-Tenant Auth & Data Isolation](#7-multi-tenant-auth--data-isolation)
  - [CCTV Vision Telemetry & Image Proxy](#8-cctv-vision-telemetry--image-proxy)
- [Tech Stack](#-tech-stack)
- [Project Directory Structure](#-project-directory-structure)
- [Database Schema & Data Models](#-database-schema--data-models)
- [REST & WebSocket API Reference](#-rest--websocket-api-reference)
- [Environment Configuration](#-environment-configuration)
- [Quick Start & How to Run](#-quick-start--how-to-run)
  - [Prerequisites](#prerequisites)
  - [1. Backend Setup](#1-backend-setup)
  - [2. Frontend Setup](#2-frontend-setup)
  - [3. Running with Docker Compose](#3-running-with-docker-compose-optional)
  - [4. Verification & CLI Test Suite](#4-verification--cli-test-suite)
- [Troubleshooting & FAQs](#-troubleshooting--faqs)
- [License](#-license)

---

## 🌟 Overview & Vision

**RAGUL** is an enterprise-grade, voice-first AI dairy farm supervisor and livestock telemetry platform designed to bridge cutting-edge artificial intelligence with daily dairy operations. Built specifically for Indian dairy farmers and farm managers, RAGUL natively supports code-mixed **Tanglish** (Tamil + English), **Tamil**, **Hindi**, **Hinglish**, and **English**.

Equipped with real-time computer vision telemetry from **PashuX AI CCTV cameras**, RAGUL monitors cattle health, body condition scores (BCS), estrus cycles, feeding frequency, drinking habits, and worker shifts. Farm managers can simply speak to RAGUL from their mobile browser or desktop to receive verified, instantaneous auditory and visual answers, backed by authoritative agricultural science and live database records.

---

## 🏛️ System Architecture

```
                               ┌─────────────────────────────────────────┐
                               │           FARMER / USER VOICE           │
                               │      (Web Audio API / 16kHz PCM)        │
                               └────────────────────┬────────────────────┘
                                                    │
                                                    ▼
                               ┌─────────────────────────────────────────┐
                               │        SILERO VAD (Voice Activity)      │
                               │  - Real-time Interruption Detection     │
                               │  - Noise & Hallucination Filter         │
                               └────────────────────┬────────────────────┘
                                                    │ Active Speech Frames
                                                    ▼
                               ┌─────────────────────────────────────────┐
                               │       FASTER-WHISPER STT ENGINE         │
                               │  - Multilingual Code-Mixing             │
                               │  - Dairy Phonetics Normalizer           │
                               └────────────────────┬────────────────────┘
                                                    │ Verified User Query
                                                    ▼
                     ┌─────────────────────────────────────────────────────────────┐
                     │            FASTAPI CORE & WEBSOCKET GATEWAY                 │
                     │  - Session Manager & Sliding Context Memory                 │
                     │  - Multi-Tenant Authentication & Farm UUID Scoping          │
                     └──────┬──────────────────────┬────────────────────────┬──────┘
                            │                      │                        │
                            ▼                      ▼                        ▼
       ┌───────────────────────────┐ ┌───────────────────────────┐ ┌───────────────────────────┐
       │   JARVISLABS CLOUD LLM    │ │     SUPABASE POSTGRESQL   │ │     NASEM 2021 ENGINE     │
       │  - Model: glm-5.3-flash   │ │  - Cattle Records         │ │  - 8th Revised Edition    │
       │  - Zero-Shot Tool Calling │ │  - PashuX AI Vision Feeds │ │  - DMI, FWI, Energy (NEL) │
       │  - Temporal Isolation     │ │  - Worker Shifts & Health │ │  - Ca/P/Mg/K/Na Minerals  │
       └────────────┬──────────────┘ └─────────────┬─────────────┘ └────────────┬──────────────┘
                    │                              │                            │
                    └──────────────────────────────┼────────────────────────────┘
                                                   │
                                                   ▼
                               ┌─────────────────────────────────────────┐
                               │   VETERINARY RAG & PRODUCTS CATALOG     │
                               │  - 104 Canonical Topics / 1,040 QA      │
                               │  - Clinical Red-Flags & First-Aid       │
                               └───────────────────┬─────────────────────┘
                                                   │
                                                   ▼
                     ┌─────────────────────────────────────────────────────────────┐
                     │                 INTERACTIVE USER DASHBOARD                  │
                     │  - 3D Talking Holographic Avatar with Lip-Sync Dynamics    │
                     │  - Apache ECharts Analytics Drawer (Census / BCS / Activity)│
                     │  - Authenticated CCTV Proof Snapshot Viewer                 │
                     │  - Browser-Native Male Speech Synthesis (TTS)               │
                     └─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Key Features & Highlights

### 1. Zero-Lag Voice Activity Detection & Interruption
- **Silero VAD v4**: Integrated directly into the WebSocket audio pipeline.
- **Bi-Directional Barge-In**: When RAGUL is speaking, speaking into the microphone immediately triggers an `interrupt` packet, stopping browser TTS synthesis instantly.
- **Clap & Sharp Sound Wake-Up**: In-browser audio processor detects claps and hand-taps, instantly toggling microphone recording and waking RAGUL from idle mode.
- **Acoustic Breath & Hallucination Filter**: Filters out ambient farm noise, throat clearing, and Whisper ghost subtitles (e.g., *"thank you for watching"*, *"amara.org"*).

### 2. Dairy Phonetic STT Normalization
Acoustic speech-to-text models often mishear technical dairy terminology in noisy farm environments. RAGUL features an intelligent regex phonetics pre-processor:
- *"my statis"*, *"my status"*, *"mass titis"*, *"mustard is"* $\rightarrow$ **`mastitis`**
- *"quad master"*, *"card master"*, *"god master"* $\rightarrow$ **`quadmastest`** (CMT paddle)
- *"is trust"*, *"extra"*, *"east rus"*, *"s stress"* $\rightarrow$ **`estrus`** (heat detection)
- *"father grass"*, *"further grass"* $\rightarrow$ **`fodder grass`**
- *"cy lage"*, *"sai lage"* $\rightarrow$ **`silage`**

### 3. Autonomous Tool-Calling Agent Router
- Powered by high-speed inference on **JarvisLabs Cloud** (`https://models.jarvislabs.net/v1`) using `glm-5.3-flash`.
- **Strict Temporal Rules**: Explicitly separates *Today* from *Yesterday*. Never presents historical records as current day events.
- **Confidence Enforcement**: Automatically discards vision estrus events with confidence scores $\le 85\%$ when showing photographic evidence.
- **Fallback Architecture**: Compatible with local Ollama (`qwen2.5:3b`) or self-hosted vLLM instances for air-gapped farm setups.

### 4. Interactive ECharts Analytics Panel
- Dynamic drawer sliding out from the left displaying live herd analytics.
- **Census & Breed Distribution**: Interactive Donut and Bar charts visualizing cattle breeds (Gir, Holstein Friesian, Jersey, Murrah Buffalo, Sahiwal, Crossbred).
- **BCS & Health Metrics**: Body condition score distribution, average herd weight, and lactating ratios.
- **Vision Telemetry Activity**: Tracks hourly manger feeding detections, standing time, and estrus mounts.

### 5. NASEM 2021 Dairy Nutrition Engine
Complies with the **NASEM 2021 Nutrient Requirements of Dairy Cattle, 8th Revised Edition**:
- **Dry Matter Intake (DMI)**:
  - Lactating Cows (Equation 2-1):
    $$\text{DMI} = \left(3.7 + 5.7 \cdot P + 0.305 \cdot \text{MilkE} + 0.022 \cdot \text{BW} + (-0.689 - 1.87 \cdot P) \cdot \text{BCS}\right) \times \left(1 - (0.212 + 0.136 \cdot P) \cdot e^{-0.053 \cdot \text{DIM}}\right)$$
  - Growing Heifers (Equation 2-3 & 2-4).
  - Dry Cows (Equation 12-1).
- **Free Water Intake (FWI)**:
  - Equation 9-1 for lactating cows accounting for dry matter intake, ration DM%, sodium, potassium, crude protein, and mean ambient temperature ($^\circ\text{C}$).
- **Energy & Minerals**:
  - Net Energy of Lactation ($\text{NE}_L$) for maintenance, lactation, and gestation.
  - Complete dietary supply and balance checks for Calcium (Ca), Phosphorus (P), Magnesium (Mg), Potassium (K), Sodium (Na), Chlorine (Cl), and Sulfur (S).

### 6. Veterinary Q&A Clinical Knowledge Base & RAG
- **104 Canonical Topics** across **15 Clinical Categories**:
  - Udder Health & Mastitis (Subclinical vs Clinical, CMT, dry cow therapy)
  - Metabolic Disorders (Ketosis, Milk Fever/Hypocalcemia, Acidosis/SARA)
  - Reproduction & Estrus (Standing heat symptoms, AI timing, Silent estrus)
  - Infectious Diseases (FMD, Lumpy Skin Disease, Hemorrhagic Septicemia)
  - Calving & Neonatal Care (Colostrum feeding, Navel ill, Calving paralysis)
- **1,040 Searchable Phrasings** in English, Tanglish, and Tamil.
- **Safety Red-Flags**: Automated escalation triggers recommending urgent veterinary intervention for acute symptoms (e.g., toxic mastitis, recumbency, bloat).

### 7. Multi-Tenant Auth & Data Isolation
- **Authentication**: Secure phone-number based login supporting international and domestic Indian formats (`+91`, `91`, 10-digit).
- **Password Security**: Standard `bcrypt` hashing with multi-version compatibility fallback (`$2b$`, `$2a$`).
- **Data Scoping**: Every API request and WebSocket session is strictly scoped to the authenticated user's `farm_id`. Multi-tenant isolation ensures zero cross-farm data leakage.

### 8. CCTV Vision Telemetry & Image Proxy
- Integration with **PashuX AI Vision Cameras** monitoring cattle pens, feeding mangers, and milking parlors.
- Secure media proxy endpoint (`/api/media/image`) fetching authenticated CCTV snapshot proof images from Supabase Storage with dynamic fallback directory resolution.

---

## 🛠️ Tech Stack

| Domain | Technology / Library | Purpose |
| :--- | :--- | :--- |
| **Backend Framework** | **FastAPI** (`>=0.110.0`) | High-concurrency async REST & WebSocket server |
| **ASGI Server** | **Uvicorn** (`>=0.28.0`) | Lightning-fast ASGI web server implementation |
| **LLM Inference** | **JarvisLabs Cloud** / **vLLM** | Cloud inference for `glm-5.3-flash` & open models |
| **Database** | **Supabase Cloud PostgreSQL** | Async connection pool via `asyncpg` & SQLAlchemy |
| **Speech-to-Text** | **faster-whisper** (`tiny`/`base`) | Low-latency multilingual speech transcription |
| **Voice Detection** | **Silero VAD v4** | Real-time 16kHz speech frame & barge-in detection |
| **Frontend Framework**| **React 18** + **TypeScript** | Responsive modern reactive UI architecture |
| **Build Tool** | **Vite 5** | Instant hot module replacement (HMR) & bundling |
| **Visual Charts** | **Apache ECharts 6.1** | Interactive herd census, BCS, and activity analytics |
| **State Management**| **Zustand 4.5** | Fast, decoupled global state management |
| **Styling** | **Vanilla CSS + Glassmorphism**| High-performance responsive UI with dual Dark/Light mode |
| **Containerization** | **Docker** & **Docker Compose** | Single-command multi-container orchestration |

---

## 📂 Project Directory Structure

```text
Ragul Ai/
├── .gitignore
├── docker-compose.yml              # Container orchestration (Backend + Frontend + Ollama)
├── README.md                       # Comprehensive Project Documentation
│
├── backend/
│   ├── Dockerfile                  # Container build for backend
│   ├── .dockerignore
│   ├── .env                        # Local environment variables
│   ├── .env.example                # Configuration template
│   ├── requirements.txt            # Python dependencies
│   ├── run_server.py               # Uvicorn entry launcher
│   ├── test_agent.py               # Multilingual query test suite
│   ├── app/
│   │   ├── auth.py                 # Multi-tenant phone + bcrypt authentication
│   │   ├── config.py               # Pydantic v2 application settings
│   │   ├── main.py                 # FastAPI application, REST & WebSockets
│   │   ├── audio/
│   │   │   ├── vad.py              # Silero VAD speech detection & interruption
│   │   │   ├── stt.py              # faster-whisper transcription engine
│   │   │   └── tts.py              # Speech synthesis adapter
│   │   ├── database/
│   │   │   ├── db.py               # Async SQLAlchemy engine & session factory
│   │   │   ├── models.py           # Database ORM models
│   │   │   ├── supabase_client.py  # Supabase asyncpg client & connection pool
│   │   │   └── seed_data.py        # Database seed routines
│   │   ├── knowledge/
│   │   │   ├── nasem_calculator.py # NASEM 2021 Dairy Nutrition Engine
│   │   │   └── rag_engine.py       # Veterinary clinical Q&A and catalog RAG
│   │   ├── llm/
│   │   │   ├── client.py           # JarvisLabs & OpenAI-compatible LLM client
│   │   │   ├── prompts.py          # Domain system prompts & guidelines
│   │   │   └── router.py           # Agent router, phonetics & tool execution
│   │   ├── memory/
│   │   │   └── session_manager.py  # Sliding conversation history manager
│   │   └── tools/
│   │       └── farm_tools.py       # Autonomous Supabase query & analytics tools
│   ├── data/knowledge_base/
│   │   ├── nasem_feed_nutrition_rules.json  # NASEM 2021 mathematical ruleset
│   │   ├── products_catalog.json   # Approved veterinary medicines & supplements
│   │   └── veterinary_qa.json      # 104 clinical topics with 1,040 QA variants
│   └── supabase/
│       ├── 01_schema.sql           # Database tables, foreign keys & indexes
│       └── 02_seed_september_2026.sql # Cattle herd records & activity datasets
│
└── frontend/
    ├── Dockerfile                  # Nginx production container
    ├── .dockerignore
    ├── nginx.conf                  # Reverse proxy & SPA routing config
    ├── index.html                  # HTML5 entry template
    ├── package.json                # Frontend dependencies & scripts
    ├── tsconfig.json               # TypeScript compiler config
    ├── vite.config.ts              # Vite configuration
    ├── public/                     # Static graphics, avatars & favicon
    └── src/
        ├── App.tsx                 # Root application component
        ├── index.css               # Glassmorphism design system & theme variables
        ├── main.tsx                # React DOM render entry
        ├── components/
        │   ├── Header.tsx          # Status bar, theme switch & user profile
        │   ├── LoginModal.tsx      # Phone & password authentication modal
        │   ├── TalkingRagul3D.tsx  # Interactive talking avatar & audio visualizer
        │   ├── LeftDiagramPanel.tsx# Apache ECharts herd analytics drawer
        │   ├── ConversationFeed.tsx# Live chat dialogue stream with proof images
        │   ├── FarmTelemetryPanel.tsx # Live metrics, cameras, and alerts drawer
        │   └── QuickQueryBar.tsx   # Pre-configured farmer query chips
        ├── services/
        │   └── audioEngine.ts      # Web Audio API, clap detector & WebSocket client
        └── store/
            └── useRagulStore.ts    # Zustand state store
```

---

## 🗄️ Database Schema & Data Models

The system is powered by PostgreSQL hosted on Supabase:

```mermaid
erDiagram
    FARMS ||--o{ USERS : employs
    FARMS ||--o{ CAMERAS : operates
    FARMS ||--o{ CATTLE : owns
    FARMS ||--o{ FARM_ACTIVITIES : logs
    CATTLE ||--o{ MILK_READINGS : yields
    CATTLE ||--o{ FARM_ACTIVITIES : detected_in

    FARMS {
        uuid id PK
        string farm_code UK
        string farm_name
        string owner_name
        string owner_phone
        string location
        timestamp created_at
    }

    USERS {
        uuid id PK
        uuid farm_id FK
        string phone UK
        string password_hash
        string full_name
        string role
        boolean is_verified
    }

    CAMERAS {
        uuid id PK
        uuid farm_id FK
        string camera_id
        string camera_name
        string rtsp_stream_url
        string location_description
        boolean is_active
    }

    CATTLE {
        uuid id PK
        uuid farm_id FK
        string cattle_id UK
        string breed
        date date_of_birth
        string lactation_stage
        float bcs_score
        float current_weight_kg
        string disease_status
    }

    FARM_ACTIVITIES {
        uuid activity_id PK
        uuid farm_id FK
        string camera_id
        string cattle_id
        string activity_type
        date detection_date
        timestamp start_time
        timestamp end_time
        float confidence_score
        string captured_image_storage_path
        text description
    }

    MILK_READINGS {
        uuid id PK
        string cattle_id FK
        date reading_date
        string session
        float yield_liters
        float fat_percentage
        float snf_percentage
    }
```

---

## 📡 REST & WebSocket API Reference

### 1. Authentication Endpoints

- **`POST /api/auth/login`**
  - **Body**: `{"phone": "+919876543210", "password": "farmerpassword"}`
  - **Response**: Authenticated user record with associated `farm_id`, `farm_code`, and `role`.
- **`POST /api/auth/register`**
  - **Body**: `{"phone": "9876543210", "password": "...", "full_name": "...", "farm_name": "..."}`
- **`POST /api/auth/reset-password`**
  - **Body**: `{"phone": "9876543210", "new_password": "..."}`

### 2. Telemetry & Analytics Endpoints

- **`GET /api/health`**
  - Returns backend health, database connection state, loaded VAD/STT models, and LLM configuration.
- **`GET /api/farm/overview?farm_id={farm_id}`**
  - Fetches herd counts, camera states, today's activity count, and high-confidence estrus alerts.
- **`GET /api/farm/analytics?farm_id={farm_id}`**
  - Provides data payloads for Apache ECharts visualization: breed census breakdown, average BCS, weight metrics, and single-day activity timeline.
- **`GET /api/farm/activities?farm_id={farm_id}&activity_type=estrus&limit=25`**
  - Queries filtered camera detection activities.
- **`GET /api/media/image?path={storage_path}`**
  - Authenticated proxy delivering CCTV detection proof snapshots from private Supabase Storage.

### 3. Dialogue & Voice Endpoints

- **`POST /api/chat`**
  - Standard text chat endpoint.
  - **Body**: `{"message": "How many cattle are in the farm?", "farm_id": "...", "language": "tanglish"}`
  - **Response**: Assistant response text, executed `tool_meta`, and camera `proof_images`.
- **`WebSocket /api/ws/voice`** (or `/ws/audio`)
  - Full-duplex audio stream for live voice conversations.
  - **Client to Server**:
    - Raw 16kHz 16-bit Mono PCM audio chunks (binary frames).
    - JSON control messages:
      - `{"type": "ping"}`
      - `{"type": "set_farm", "farm_id": "<uuid>"}`
      - `{"type": "chat_text", "text": "...", "farm_id": "<uuid>"}`
      - `{"type": "reset_vad"}`
  - **Server to Client**:
    - `{"type": "interrupt"}`: Signals user voice barge-in; halts frontend speech playback.
    - `{"type": "vad_status", "status": "speech" | "idle" | "processing"}`
    - `{"type": "user_transcript", "text": "...", "language": "en"}`
    - `{"type": "agent_response", "user_text": "...", "response_text": "...", "proof_images": [...]}`
    - Binary PCM audio chunks for server-synthesized speech (if server TTS is enabled).

---

## ⚙️ Environment Configuration

Create a file named `backend/.env` based on [`backend/.env.example`](backend/.env.example):

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
# Audio Speech-to-Text & Voice Activity Detection
# ==========================================
WHISPER_MODEL_SIZE=tiny
WHISPER_DEVICE=cpu
WHISPER_COMPUTE_TYPE=int8
VAD_SAMPLE_RATE=16000
VAD_THRESHOLD=0.65
VAD_MIN_SPEECH_DURATION_MS=280
VAD_MIN_SILENCE_DURATION_MS=3000
VAD_ENERGY_THRESHOLD=0.038

# ==========================================
# Speech Synthesis (TTS)
# ==========================================
TTS_ENGINE=browser_native
DEFAULT_LANGUAGE=en-US

# ==========================================
# Supabase Cloud PostgreSQL Database
# ==========================================
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_anon_or_service_role_key
DATABASE_URL=postgresql+asyncpg://postgres:your_password@db.your-project-id.supabase.co:5432/postgres

# ==========================================
# Farm Defaults
# ==========================================
TARGET_FARM_ID=584cab92-d75d-4aa0-824a-c07423aa6453
```

---

## 🚀 Quick Start & How to Run

### Prerequisites

- **Python**: Version `3.10` or higher
- **Node.js**: Version `18.x` or higher (with `npm`)
- **Git**
- **Microphone Access**: Modern web browser (Chrome, Edge, Safari, Firefox)

---

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate Python virtual environment
python -m venv venv

# On Windows:
.\venv\Scripts\activate
# On Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure your environment
cp .env.example .env
# Edit .env with your credentials (JarvisLabs API key & Supabase URL/key)

# Launch the FastAPI server
python run_server.py
```

- **REST API & WebSockets**: `http://localhost:8000`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`

---

### 2. Frontend Setup

```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start the Vite development server
npm run dev
```

- **Web Dashboard**: `http://localhost:5173`

---

### 3. Running with Docker Compose (Optional)

To launch the complete containerized stack in one command:

```bash
docker-compose up --build
```

- **Web App**: `http://localhost`
- **FastAPI API**: `http://localhost:8000`
- **Local Ollama (if enabled)**: `http://localhost:11434`

---

### 4. Verification & CLI Test Suite

Verify that LLM tool routing, multilingual Tanglish/Hindi processing, and Supabase database querying function properly:

```bash
cd backend
python test_agent.py
```

---

## 💡 Troubleshooting & FAQs

### 1. Microphone not triggering or speech not recognized?
- Ensure browser permissions allow microphone access (`chrome://settings/content/microphone`).
- Verify that your WebSocket connection to `ws://localhost:8000/api/ws/voice` is established (check the browser DevTools Console).
- You can wake RAGUL at any time by clapping or clicking the central microphone button.

### 2. Camera proof images not displaying?
- Confirm that your Supabase Storage bucket `pashux-activity-images` has read permissions or that `SUPABASE_KEY` in `backend/.env` is a valid service role or authenticated key.
- The `/api/media/image` endpoint proxies authenticated requests automatically.

### 3. Using offline / local LLM instead of JarvisLabs?
- In `backend/.env`, set:
  ```env
  LLM_PROVIDER=ollama
  LLM_API_BASE=http://localhost:11434/v1
  LLM_MODEL_NAME=qwen2.5:3b
  ```
- Start your local Ollama service: `ollama run qwen2.5:3b`.

---

## 📄 License

Proprietary and Confidential. Developed for Intelligent Dairy Herd Management and Livestock Telemetry.  
Copyright © 2026 Chimertech Innovations. All rights reserved.

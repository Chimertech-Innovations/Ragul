import json
import logging
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import settings
from .database.supabase_client import supabase_db
from .tools.farm_tools import FARM_TOOLS, get_cow_health_summary, get_milk_production_trends, get_daily_farm_comprehensive_summary
from .llm.router import tool_router
from .memory.session_manager import session_manager
from .audio.vad import vad_processor
from .audio.stt import stt_engine
from .audio.tts import tts_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ragul_api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing RAGUL Supabase PostgreSQL Connection Pool...")
    try:
        pool = await supabase_db.get_pool()
        c_count = await supabase_db.fetch_val("SELECT count(*) FROM cattle")
        w_count = await supabase_db.fetch_val("SELECT count(*) FROM workers")
        logger.info(f"Connected to Supabase PostgreSQL: {c_count} cattle, {w_count} workers ready.")
    except Exception as e:
        logger.error(f"Error connecting to Supabase: {e}")
    yield
    await supabase_db.close()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    language: Optional[str] = "tanglish"

class ChatResponse(BaseModel):
    session_id: str
    response: str
    tool_meta: Optional[Dict[str, Any]] = None
    detected_language: str

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "Supabase PostgreSQL (Live)",
        "llm_provider": settings.LLM_PROVIDER,
        "vad_loaded": vad_processor.model is not None,
        "stt_loaded": stt_engine.model is not None,
        "tts_engine": settings.TTS_ENGINE
    }

@app.get("/api/farm/overview")
async def get_farm_overview():
    farm = await supabase_db.fetch_one("SELECT * FROM farms LIMIT 1")
    cows = await supabase_db.fetch_all("SELECT * FROM cattle")
    alerts = await supabase_db.fetch_all("SELECT * FROM farm_alerts WHERE is_resolved = false ORDER BY date DESC")
    summary = await supabase_db.fetch_one("SELECT * FROM daily_summaries ORDER BY date DESC LIMIT 1")

    high_risk_count = sum(1 for c in alerts if "mastitis" in c.get("type", "").lower())
    in_estrus_count = sum(1 for c in alerts if "estrus" in c.get("type", "").lower())
    total_yield = float(summary.get("total_milk_litres", 130.0)) if summary else 130.0

    return {
        "farm_name": farm.get("name", "Green Valley Dairy Farm") if farm else "Green Valley Dairy Farm",
        "location": farm.get("location", "Tamil Nadu, India") if farm else "Tamil Nadu, India",
        "total_cows": len(cows),
        "high_risk_mastitis": high_risk_count,
        "in_estrus_cows": in_estrus_count,
        "total_daily_yield_litres": round(total_yield, 1),
        "active_health_alerts": alerts,
        "daily_summary": summary.get("summary_text") if summary else "All operations running normally."
    }

@app.get("/api/cows")
async def list_cows():
    cows = await supabase_db.fetch_all("SELECT * FROM cattle ORDER BY cattle_id ASC")
    return cows

@app.get("/api/cows/{cow_id}")
async def get_cow_detail(cow_id: str):
    summary = await get_cow_health_summary(cow_id)
    if "status" in summary and summary["status"] == "error":
        raise HTTPException(status_code=404, detail="Cow not found")
    return summary

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    session_id = await session_manager.get_or_create_session(request.session_id)
    history = await session_manager.get_recent_history(session_id)
    
    # Save user message
    await session_manager.save_message(
        session_id=session_id,
        role="user",
        content=request.message,
        detected_language=request.language or "tanglish"
    )
    
    # Process with custom Supabase Tool Router
    response_text, tool_meta = await tool_router.process_user_message(
        user_text=request.message,
        history=history,
        session_id=session_id
    )
    
    # Save assistant response
    await session_manager.save_message(
        session_id=session_id,
        role="assistant",
        content=response_text,
        tool_calls=tool_meta.get("arguments") if tool_meta else None,
        tool_results=tool_meta.get("result") if tool_meta else None,
        detected_language=request.language or "tanglish"
    )
    
    return ChatResponse(
        session_id=session_id,
        response=response_text,
        tool_meta=tool_meta if tool_meta.get("executed") else None,
        detected_language=request.language or "tanglish"
    )

@app.websocket("/api/ws/voice")
@app.websocket("/ws/audio")
async def websocket_voice_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = await session_manager.get_or_create_session(None)
    logger.info(f"[WS] Voice Client Connected. Session ID: {session_id}")

    try:
        while True:
            data = await websocket.receive()
            if "bytes" in data and data["bytes"]:
                audio_bytes = data["bytes"]
                
                # Check speech with VAD
                has_speech, confidence = vad_processor.process_chunk(audio_bytes)
                if not has_speech:
                    continue
                
                # Transcribe with Whisper STT
                stt_result = await stt_engine.transcribe_audio_bytes(audio_bytes)
                user_text = stt_result.get("text", "").strip()
                if not user_text:
                    continue
                
                # Process with Agent Router (Direct Supabase)
                history = await session_manager.get_recent_history(session_id)
                response_text, tool_meta = await tool_router.process_user_message(
                    user_text=user_text,
                    history=history,
                    session_id=session_id
                )
                
                # Send text and metadata
                await websocket.send_json({
                    "type": "agent_response",
                    "user_text": user_text,
                    "response_text": response_text,
                    "tool_meta": tool_meta
                })
                
                # Synthesize TTS Audio
                tts_audio = await tts_engine.synthesize_speech(response_text)
                if tts_audio:
                    await websocket.send_bytes(tts_audio)
                    
            elif "text" in data and data["text"]:
                try:
                    payload = json.loads(data["text"])
                    if payload.get("type") == "ping":
                        await websocket.send_json({"type": "pong"})
                except Exception:
                    pass

    except WebSocketDisconnect:
        logger.info(f"[WS] Voice Client Disconnected: {session_id}")
    except Exception as e:
        logger.error(f"[WS] WebSocket Error: {e}")
        try:
            await websocket.close()
        except Exception:
            pass


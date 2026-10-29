import json
import logging
import re
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any
import httpx

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import settings
from .database.supabase_client import supabase_db
from .tools.farm_tools import (
    FARM_TOOLS,
    get_farm_overview as fetch_farm_overview,
    get_estrus_and_heat_alerts,
    get_feed_and_nutrition,
    get_cameras_status,
    get_cow_activity_history,
    get_cctv_proof_and_images,
    get_farm_herd_summary,
    get_single_day_cattle_graphical_analytics
)
from .llm.router import tool_router
from .memory.session_manager import session_manager
from .audio.vad import vad_processor
from .audio.stt import stt_engine
from .audio.tts import tts_engine
from .auth import router as auth_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ragul_api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing RAGUL Supabase PostgreSQL Connection Pool...")
    try:
        pool = await supabase_db.get_pool()
        f_count = await supabase_db.fetch_val("SELECT count(*) FROM public.farms") or 0
        a_count = await supabase_db.fetch_val("SELECT count(*) FROM public.farm_activities") or 0
        u_count = await supabase_db.fetch_val("SELECT count(*) FROM public.users") or 0
        logger.info(f"Connected to Supabase PostgreSQL: {f_count} farms, {u_count} users, {a_count} live AI activities ready.")
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

app.include_router(auth_router)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    language: Optional[str] = "tanglish"
    farm_id: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    response: str
    tool_meta: Optional[Dict[str, Any]] = None
    proof_images: Optional[List[Dict[str, Any]]] = None
    detected_language: str

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "Supabase PostgreSQL (Live PashuX)",
        "llm_provider": settings.LLM_PROVIDER,
        "vad_loaded": vad_processor.model is not None,
        "stt_loaded": stt_engine.model is not None,
        "tts_engine": settings.TTS_ENGINE
    }

@app.get("/api/media/image")
async def get_media_image(path: str = Query(...)):
    """Proxies and caches camera detection proof images from private Supabase Storage."""
    clean_path = path.lstrip("/")
    supabase_url = settings.SUPABASE_URL.rstrip("/")
    key = settings.SUPABASE_KEY
    storage_url = f"{supabase_url}/storage/v1/object/authenticated/pashux-activity-images/{clean_path}"

    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            r = await client.get(storage_url, headers=headers)
            if r.status_code == 200:
                media_type = r.headers.get("content-type", "image/jpeg")
                return Response(
                    content=r.content,
                    media_type=media_type,
                    headers={
                        "Cache-Control": "public, max-age=86400",
                        "Access-Control-Allow-Origin": "*"
                    }
                )

            # Fallback: If 400/404, check other storage folder prefixes for the exact image filename
            filename = clean_path.split("/")[-1]
            candidate_prefixes = [
                "098b67ef-059a-4c2d-965a-06399e5a1bdf/images",
                "732fd751-a34b-4de7-80fd-9330ce729a35/images",
                "584cab92-d75d-4aa0-824a-c07423aa6453/images"
            ]
            for prefix in candidate_prefixes:
                alt_path = f"{prefix}/{filename}"
                if alt_path == clean_path:
                    continue
                alt_url = f"{supabase_url}/storage/v1/object/authenticated/pashux-activity-images/{alt_path}"
                alt_r = await client.get(alt_url, headers=headers)
                if alt_r.status_code == 200:
                    logger.info(f"[Media] Successfully resolved image {filename} via fallback path: {alt_path}")
                    media_type = alt_r.headers.get("content-type", "image/jpeg")
                    return Response(
                        content=alt_r.content,
                        media_type=media_type,
                        headers={
                            "Cache-Control": "public, max-age=86400",
                            "Access-Control-Allow-Origin": "*"
                        }
                    )

            logger.warning(f"[Media] Storage fetch returned {r.status_code} for path: {clean_path}")
            raise HTTPException(status_code=r.status_code, detail="Image not found in farm storage")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Media] Error proxying image: {e}")
        raise HTTPException(status_code=404, detail="Could not retrieve camera image")

@app.get("/api/farm/overview")
async def get_farm_overview_endpoint(farm_id: Optional[str] = Query(None)):
    overview = await fetch_farm_overview(farm_id)
    return overview

@app.get("/api/farm/activities")
@app.get("/api/activities")
async def get_farm_activities(
    farm_id: Optional[str] = Query(None),
    activity_type: Optional[str] = Query(None),
    camera_id: Optional[str] = Query(None),
    cattle_id: Optional[str] = Query(None),
    limit: int = Query(25, ge=1, le=100)
):
    query = """
        SELECT 
            activity_id, farm_id, camera_id, cattle_id, worker_id,
            activity_type, detection_date, start_time, end_time,
            activity_duration, confidence_score, description,
            captured_image_storage_path, captured_video_storage_path,
            video_source, status, created_at
        FROM public.farm_activities
        WHERE 1=1
    """
    params = []
    if farm_id and farm_id != "all":
        params.append(farm_id)
        query += f" AND farm_id = ${len(params)}::uuid"
    if activity_type and activity_type != "all":
        params.append(activity_type)
        query += f" AND activity_type = ${len(params)}"
    if camera_id and camera_id != "all":
        params.append(camera_id)
        query += f" AND camera_id = ${len(params)}"
    if cattle_id and cattle_id != "all":
        params.append(f"%{cattle_id}%")
        query += f" AND cattle_id ILIKE ${len(params)}"

    query += f" ORDER BY start_time DESC LIMIT {limit};"
    rows = await supabase_db.fetch_all(query, *params)
    
    result = []
    for r in rows:
        d = dict(r)
        if d.get("captured_image_storage_path"):
            d["image_url"] = f"/api/media/image?path={d['captured_image_storage_path']}"
        result.append(d)
    return result

@app.get("/api/farm/cameras")
async def get_farm_cameras_endpoint(farm_id: Optional[str] = Query(None)):
    return await get_cameras_status(farm_id)

@app.get("/api/cows/{cow_id}")
async def get_cow_detail(cow_id: str, farm_id: Optional[str] = Query(None)):
    summary = await get_cow_activity_history(cow_id, farm_id)
    return summary

@app.get("/api/farm/analytics")
async def get_farm_analytics_endpoint(farm_id: Optional[str] = Query(None)):
    """Provides ground-truth cattle statistics and vision telemetry for Apache ECharts visualization."""
    herd = await get_farm_herd_summary(farm_id)
    activity = await get_single_day_cattle_graphical_analytics(farm_id, target_date="yesterday")
    return {
        "status": "success",
        "herd": herd,
        "activity": activity
    }

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
    
    # Process with custom Supabase Tool Router passing farm_id
    response_text, tool_meta = await tool_router.process_user_message(
        user_text=request.message,
        history=history,
        session_id=session_id,
        farm_id=request.farm_id
    )
    
    # Extract proof images
    proof_images = tool_meta.get("proof_images") if tool_meta else None
    
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
        tool_meta=tool_meta if (tool_meta and (tool_meta.get("executed") or tool_meta.get("requires_login"))) else None,
        proof_images=proof_images,
        detected_language=request.language or "tanglish"
    )

@app.websocket("/api/ws/voice")
@app.websocket("/ws/audio")
async def websocket_voice_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = await session_manager.get_or_create_session(None)
    client_farm_id: Optional[str] = None
    logger.info(f"[WS] Voice Client Connected. Session ID: {session_id}")
    audio_buffer = bytearray()

    try:
        while True:
            data = await websocket.receive()
            if "bytes" in data and data["bytes"]:
                chunk = data["bytes"]
                has_speech, vad_state = vad_processor.process_chunk(chunk)
                
                if has_speech:
                    audio_buffer.extend(chunk)
                    if vad_state == "speech_start":
                        await websocket.send_json({"type": "interrupt"})
                        await websocket.send_json({"type": "vad_status", "status": "speech"})
                    # Safety cap buffer at ~10 seconds of 16kHz PCM16 (320,000 bytes)
                    if len(audio_buffer) > 320000:
                        audio_buffer = audio_buffer[-320000:]
                elif vad_state == "speech_end":
                    if len(audio_buffer) >= 16000:
                        speech_bytes = bytes(audio_buffer)
                        audio_buffer.clear()
                        await websocket.send_json({"type": "vad_status", "status": "processing"})
                        
                        # Transcribe clean buffered speech
                        stt_result = await stt_engine.transcribe_audio_bytes(speech_bytes)
                        user_text = stt_result.get("text", "").strip()
                        quality = stt_result.get("quality", "low_confidence")
                        confidence = stt_result.get("confidence", 0.0)
                        
                        # Filter out ambient noise hallucinations and acoustic breath triggers
                        GHOST_HALLUCINATIONS = {
                            "thank you", "thank you.", "thank you for watching", "subtitles by",
                            "amara.org", "english subtitles", "you", "subscribe", "please subscribe",
                            "the end", "i don't know", "bye bye", "watching video", "hide over",
                            "shh", "uh", "um", "ah", "hmm", "okay", "yes", "so", "pashux", "cough",
                            "laughter", "applause", "music", "...", ".", "?", "-", "--", "huh", "oh", "er"
                        }
                        lower_text = user_text.lower().strip()
                        clean_letters = re.sub(r'[^a-zA-Z0-9\u0B80-\u0BFF\u0900-\u097F]', '', lower_text)

                        is_noise_filler = (
                            not user_text
                            or len(clean_letters) < 3
                            or quality == "low_confidence"
                            or confidence < 0.45
                            or stt_result.get("no_speech_prob", 0.0) > 0.55
                            or lower_text in GHOST_HALLUCINATIONS
                            or clean_letters in {"uh", "um", "ah", "hmm", "shh", "huh", "mm", "er", "ha", "you", "so", "oh"}
                            or any(g in lower_text for g in ["subtitles by", "amara.org", "thank you for watching", "please subscribe"])
                        )
                        if is_noise_filler:
                            logger.info(f"[WS] Dropped noise transcript: '{user_text}' (conf: {confidence:.2f}, clean: '{clean_letters}')")
                            await websocket.send_json({"type": "vad_status", "status": "idle"})
                            continue
                    
                    # Notify frontend of high-confidence transcript
                    await websocket.send_json({
                        "type": "user_transcript",
                        "text": user_text,
                        "language": stt_result.get("language", "auto")
                    })

                    # Process with Agent Router (Direct Supabase with farm_id)
                    history = await session_manager.get_recent_history(session_id)
                    response_text, tool_meta = await tool_router.process_user_message(
                        user_text=user_text,
                        history=history,
                        session_id=session_id,
                        farm_id=client_farm_id
                    )
                    
                    proof_images = tool_meta.get("proof_images") if tool_meta else None

                    # Send text and metadata
                    await websocket.send_json({
                        "type": "agent_response",
                        "user_text": user_text,
                        "response_text": response_text,
                        "tool_meta": tool_meta,
                        "proof_images": proof_images
                    })
                    
                    # Synthesize TTS Audio
                    tts_audio = await tts_engine.synthesize_speech(response_text)
                    if tts_audio:
                        await websocket.send_bytes(tts_audio)
                    
            elif "text" in data and data["text"]:
                try:
                    payload = json.loads(data["text"])
                    msg_type = payload.get("type")
                    if msg_type == "ping":
                        await websocket.send_json({"type": "pong"})
                    elif msg_type == "reset_vad":
                        vad_processor.reset()
                        audio_buffer.clear()
                        await websocket.send_json({"type": "vad_status", "status": "idle"})
                    elif msg_type == "set_farm":
                        client_farm_id = payload.get("farm_id")
                        logger.info(f"[WS] Socket associated with farm_id: {client_farm_id}")
                        await websocket.send_json({"type": "farm_set", "farm_id": client_farm_id})
                    elif msg_type == "chat_text":
                        user_text = payload.get("text", "").strip()
                        farm_id = payload.get("farm_id") or client_farm_id
                        if user_text:
                            history = await session_manager.get_recent_history(session_id)
                            response_text, tool_meta = await tool_router.process_user_message(
                                user_text=user_text,
                                history=history,
                                session_id=session_id,
                                farm_id=farm_id
                            )
                            proof_images = tool_meta.get("proof_images") if tool_meta else None
                            await websocket.send_json({
                                "type": "agent_response",
                                "user_text": user_text,
                                "response_text": response_text,
                                "tool_meta": tool_meta,
                                "proof_images": proof_images
                            })
                except Exception as ex:
                    logger.warning(f"[WS] Message parse error: {ex}")

    except WebSocketDisconnect:
        logger.info(f"[WS] Voice Client Disconnected: {session_id}")
    except Exception as e:
        logger.error(f"[WS] WebSocket Error: {e}")
        try:
            await websocket.close()
        except Exception:
            pass

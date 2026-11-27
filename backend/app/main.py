import json
import logging
import re
import base64
import urllib.parse
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any
import httpx

from fastapi import (
    FastAPI,
    Request,
    WebSocket,
    WebSocketDisconnect,
    HTTPException,
    Query,
    Response,
    File,
    UploadFile,
    Form
)
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
from .audio.stt import stt_engine, detect_language_from_text
from .audio.tts import tts_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ragul_api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing RAGUL Supabase PostgreSQL Connection Pool...")
    try:
        pool = await supabase_db.get_pool()
        f_count = await supabase_db.fetch_val("SELECT count(*) FROM public.farms") or 0
        a_count = await supabase_db.fetch_val("SELECT count(*) FROM public.farm_activities") or 0
        logger.info(f"Connected to Supabase PostgreSQL: {f_count} farms, {a_count} live AI activities ready.")
    except Exception as e:
        logger.warning(f"Note: Supabase PostgreSQL pool could not be initialized at startup: {e}")
    yield
    await supabase_db.close()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="RAGUL Voice-First AI Dairy Farm Supervisor API with Input STT, Reasoning, and Output TTS Pipeline",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================================
# ROOT & SERVICE DISCOVERY
# =========================================================================

@app.get("/", tags=["system"])
async def root():
    """Service discovery dashboard preventing 404 on root."""
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "RAGUL Voice-First AI Dairy Farm Supervisor API",
        "interactive_docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/health",
        "pipelines": {
            "input_speech_to_text": {
                "endpoint": "POST /api/stt",
                "format": "multipart/form-data (upload audio file)",
                "description": "Transcribes spoken audio into text"
            },
            "output_text_to_speech": {
                "http_audio_link": "GET /api/tts?text={text}&language={language}",
                "post_synthesis": "POST /api/tts",
                "format": "audio/mpeg stream",
                "description": "Synthesizes text into spoken speech MP3 stream"
            },
            "full_voice_chat_pipeline": {
                "voice_upload": "POST /api/chat/audio",
                "text_or_base64_chat": "POST /api/chat",
                "websocket_stream": "ws://localhost:8000/api/ws/voice"
            }
        }
    }

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

# =========================================================================
# DATA SCHEMAS
# =========================================================================

class ChatRequest(BaseModel):
    message: Optional[str] = None
    audio_base64: Optional[str] = None
    filename: Optional[str] = "audio.wav"
    session_id: Optional[str] = None
    language: Optional[str] = "auto"
    farm_id: Optional[str] = None
    return_audio_base64: Optional[bool] = False

class ChatResponse(BaseModel):
    status: str = "success"
    session_id: str
    user_text: str
    response: str
    audio_url: Optional[str] = None
    audio_base64: Optional[str] = None
    tool_meta: Optional[Dict[str, Any]] = None
    proof_images: Optional[List[Dict[str, Any]]] = None
    detected_language: str
    stt_confidence: Optional[float] = None

class TTSRequest(BaseModel):
    text: str
    language: Optional[str] = "en"
    return_base64: Optional[bool] = False

# =========================================================================
# TELEMETRY & HEALTH
# =========================================================================

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "Supabase PostgreSQL",
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

            # Fallback: check candidate storage prefixes for the exact image filename
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
                    media_type = alt_r.headers.get("content-type", "image/jpeg")
                    return Response(
                        content=alt_r.content,
                        media_type=media_type,
                        headers={
                            "Cache-Control": "public, max-age=86400",
                            "Access-Control-Allow-Origin": "*"
                        }
                    )

            raise HTTPException(status_code=404, detail="Image not found in farm storage")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Media] Error proxying image: {e}")
        raise HTTPException(status_code=404, detail="Could not retrieve camera image")

@app.get("/api/farm/overview")
async def get_farm_overview_endpoint(farm_id: Optional[str] = Query(None)):
    try:
        overview = await fetch_farm_overview(farm_id)
        return overview
    except Exception as e:
        logger.error(f"[API] Error in get_farm_overview: {e}")
        return {
            "farm_name": "PashuX Dairy Farm",
            "farm_code": "FARM_MAIN",
            "monitored_cattle_count": 0,
            "total_activities_detected": 0,
            "active_estrus_count": 0,
            "cameras_connected": 0,
            "cameras": [],
            "error": "Database currently offline or paused"
        }

@app.get("/api/farm/activities")
@app.get("/api/activities")
async def get_farm_activities(
    farm_id: Optional[str] = Query(None),
    activity_type: Optional[str] = Query(None),
    camera_id: Optional[str] = Query(None),
    cattle_id: Optional[str] = Query(None),
    limit: int = Query(25, ge=1, le=100)
):
    try:
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
    except Exception as e:
        logger.error(f"[API] Error fetching farm activities: {e}")
        return []

@app.get("/api/farm/cameras")
async def get_farm_cameras_endpoint(farm_id: Optional[str] = Query(None)):
    try:
        return await get_cameras_status(farm_id)
    except Exception as e:
        logger.error(f"[API] Error in get_farm_cameras: {e}")
        return {"cameras": [], "total_cameras": 0, "active_cameras": 0}

@app.get("/api/cows/{cow_id}")
async def get_cow_detail(cow_id: str, farm_id: Optional[str] = Query(None)):
    try:
        summary = await get_cow_activity_history(cow_id, farm_id)
        return summary
    except Exception as e:
        logger.error(f"[API] Error getting cow detail for {cow_id}: {e}")
        return {"cattle_id": cow_id, "activities": []}

@app.get("/api/farm/analytics")
async def get_farm_analytics_endpoint(farm_id: Optional[str] = Query(None)):
    """Provides ground-truth cattle statistics and vision telemetry for Apache ECharts visualization."""
    try:
        herd = await get_farm_herd_summary(farm_id)
        activity = await get_single_day_cattle_graphical_analytics(farm_id, target_date="yesterday")
        return {
            "status": "success",
            "herd": herd,
            "activity": activity
        }
    except Exception as e:
        logger.error(f"[API] Error generating analytics: {e}")
        return {
            "status": "fallback",
            "herd": {
                "total_registered_cattle": 0,
                "average_bcs_score": 0.0,
                "average_weight_kg": 0.0,
                "breed_breakdown": [],
                "active_cameras_count": 0
            },
            "activity": {
                "total_vision_events": 0,
                "unique_cattle_count": 0,
                "cattle_details": []
            }
        }

# =========================================================================
# OUTPUT TEXT-TO-SPEECH (TTS) AUDIO PIPELINE & HTTP LINKS
# =========================================================================

@app.get("/api/tts")
async def get_tts_audio_stream(
    text: str = Query(..., description="Text string to synthesize to speech audio"),
    language: Optional[str] = Query("en", description="Target language: en, ta, hi, or tanglish")
):
    """
    Playable Direct HTTP Audio Link for Text-to-Speech (TTS).
    Plays immediately in any browser, mobile app, or audio player:
    <audio src="http://localhost:8000/api/tts?text=Hello+Sir&language=en" autoplay controls />
    """
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Text query parameter is required.")

    audio_bytes = await tts_engine.synthesize_speech(text, language)
    if not audio_bytes:
        raise HTTPException(status_code=500, detail="Failed to synthesize speech audio.")

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline; filename=ragul_speech.mp3",
            "Cache-Control": "public, max-age=3600",
            "Access-Control-Allow-Origin": "*"
        }
    )

@app.post("/api/tts")
async def post_tts_audio(request: TTSRequest):
    """
    POST Text-to-Speech endpoint.
    Returns either raw audio/mpeg stream or JSON with base64 audio data.
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Field 'text' is required.")

    if request.return_base64:
        return await tts_engine.synthesize(request.text, request.language or "en")

    audio_bytes = await tts_engine.synthesize_speech(request.text, request.language or "en")
    if not audio_bytes:
        raise HTTPException(status_code=500, detail="Failed to synthesize speech audio.")

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline; filename=ragul_speech.mp3",
            "Cache-Control": "public, max-age=3600",
            "Access-Control-Allow-Origin": "*"
        }
    )

# =========================================================================
# CHATBOT API ENDPOINTS (VOICE IN -> TEXT -> LLM -> TTS OUT)
# =========================================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(http_req: Request, request: ChatRequest):
    """
    Main Chatbot Text & Base64 Audio API endpoint.
    - If 'audio_base64' is provided: Converts speech to text using faster-whisper, then queries LLM.
    - If 'message' is provided: Directly queries LLM.
    - Automatically returns:
        1. 'response': Full assistant text response.
        2. 'audio_url': Direct streaming HTTP link to play synthesized audio.
        3. 'audio_base64': Optional inline base64 MP3 audio (if return_audio_base64=True).
    """
    user_text = ""
    stt_conf = None
    detected_lang = "en"

    if request.audio_base64 and request.audio_base64.strip():
        try:
            audio_bytes = base64.b64decode(request.audio_base64.strip())
            stt_res = await stt_engine.transcribe_file(
                file_bytes=audio_bytes,
                filename=request.filename or "audio.wav",
                language=request.language
            )
            user_text = stt_res.get("text", "").strip()
            stt_conf = stt_res.get("confidence")
            detected_lang = stt_res.get("language") or "en"
        except Exception as ex:
            logger.error(f"[ChatAPI] Error decoding base64 audio: {ex}")
            raise HTTPException(status_code=400, detail="Invalid audio_base64 data.")
    elif request.message and request.message.strip():
        user_text = request.message.strip()
        req_lang = request.language
        if req_lang and req_lang.lower() not in {"auto", "all", "multilingual", "none", "null"}:
            detected_lang = req_lang
        else:
            detected_lang = detect_language_from_text(user_text)

    if not user_text:
        raise HTTPException(
            status_code=400,
            detail="Either 'message' (text) or 'audio_base64' (audio data) must be provided."
        )

    session_id = await session_manager.get_or_create_session(request.session_id)
    history = await session_manager.get_recent_history(session_id)

    # Save user message with accurate detected language (ta, tanglish, hi, hinglish, en)
    await session_manager.save_message(
        session_id=session_id,
        role="user",
        content=user_text,
        detected_language=detected_lang
    )

    # Process with custom Agent Router with language context
    try:
        response_text, tool_meta = await tool_router.process_user_message(
            user_text=user_text,
            history=history,
            session_id=session_id,
            farm_id=request.farm_id,
            detected_language=detected_lang
        )
    except Exception as e:
        logger.error(f"[ChatText] Error processing user message: {e}", exc_info=True)
        if detected_lang in {"ta", "tamil"}:
            response_text = "வணக்கம் ஐயா! பண்ணை தகவல்களை பெறுவதில் தற்காலிக தாமதம் ஏற்பட்டுள்ளது. நான் உங்களுக்கு உதவ தயாராக உள்ளேன், உங்கள் கேள்வியை மீண்டும் கேட்கலாம்."
        elif detected_lang in {"hi", "hindi"}:
            response_text = "नमस्ते सर! फार्म डेटा प्राप्त करने में थोड़ी देरी हो रही है। मैं आपकी सहायता के लिए तैयार हूँ, कृपया अपना प्रश्न दोबारा पूछें।"
        elif detected_lang == "tanglish":
            response_text = "Vanakkam sir! Farm data load aagarathula konjam issue irukku. Naan ungalukku help panna ready-ah irukken, unga question-ah thirumbi kelunga."
        else:
            response_text = "Hello! There was a brief delay retrieving the live farm data. I am ready to help, please feel free to ask your question again."
        tool_meta = None

    proof_images = tool_meta.get("proof_images") if tool_meta else None

    # Save assistant response
    await session_manager.save_message(
        session_id=session_id,
        role="assistant",
        content=response_text,
        tool_calls=tool_meta.get("arguments") if tool_meta else None,
        tool_results=tool_meta.get("result") if tool_meta else None,
        detected_language=detected_lang
    )

    # Generate playable TTS Audio HTTP Link & Optional Base64
    clean_speech = tts_engine.clean_text(response_text)
    clean_speech_snippet = clean_speech[:350].strip()
    encoded_query = urllib.parse.quote_plus(clean_speech_snippet)
    base_url = str(http_req.base_url).rstrip("/")
    audio_url = f"{base_url}/api/tts?text={encoded_query}&language={detected_lang}"

    audio_b64 = None
    if request.return_audio_base64 and clean_speech:
        tts_res = await tts_engine.synthesize(clean_speech_snippet, detected_lang)
        audio_b64 = tts_res.get("audio_base64")

    return ChatResponse(
        status="success",
        session_id=session_id,
        user_text=user_text,
        response=response_text,
        audio_url=audio_url,
        audio_base64=audio_b64,
        tool_meta=tool_meta if (tool_meta and tool_meta.get("executed")) else None,
        proof_images=proof_images,
        detected_language=detected_lang,
        stt_confidence=stt_conf
    )

@app.post("/api/chat/audio")
@app.post("/api/chat/voice")
async def chat_audio_upload_endpoint(
    http_req: Request,
    file: UploadFile = File(..., description="Recorded audio file (.wav, .mp3, .m4a, .aac, .ogg, .webm)"),
    session_id: Optional[str] = Form(None, description="Optional conversation session ID"),
    language: Optional[str] = Form("auto", description="Target language: 'auto' (default: transcribes all languages spoken), or 'ta', 'hi', 'en'"),
    farm_id: Optional[str] = Form(None, description="Optional target farm UUID"),
    return_audio_base64: Optional[bool] = Form(False, description="Whether to return inline base64 audio")
):
    """
    Mobile App Full Voice Pipeline Endpoint (Multipart Form Upload).
    1. Input STT: Receives audio recording file, transcribes to text with multilingual faster-whisper.
    2. Reasoning: Executes autonomous database tools and LLM supervisor response.
    3. Output TTS: Returns complete text response PLUS:
       - 'audio_url': Direct streaming HTTP URL to play synthesized audio.
       - 'audio_base64': Optional inline base64 MP3 if return_audio_base64 is true.
    """
    try:
        audio_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read audio file: {e}")

    if not audio_bytes or len(audio_bytes) < 32:
        raise HTTPException(status_code=400, detail="Uploaded audio file is empty.")

    # 1. Input STT: Transcribe audio to text
    stt_res = await stt_engine.transcribe_file(
        file_bytes=audio_bytes,
        filename=file.filename or "audio.wav",
        language=language
    )
    transcribed_text = stt_res.get("text", "").strip()
    detected_lang = stt_res.get("language", language or "auto")
    confidence = stt_res.get("confidence", 0.0)

    if not transcribed_text:
        return {
            "status": "no_speech_detected",
            "session_id": session_id or "",
            "transcript": "",
            "response": "Could not detect clear speech in the audio. Please try speaking again closer to the microphone.",
            "audio_url": None,
            "audio_base64": None,
            "detected_language": detected_lang,
        "stt_provider": stt_res.get("provider", "local_faster_whisper"),
            "stt_confidence": confidence,
            "duration": stt_res.get("duration", 0),
            "tool_meta": None,
            "proof_images": None
        }

    # 2. Process with LLM Router
    session_id = await session_manager.get_or_create_session(session_id)
    history = await session_manager.get_recent_history(session_id)

    await session_manager.save_message(
        session_id=session_id,
        role="user",
        content=transcribed_text,
        detected_language=detected_lang
    )

    try:
        response_text, tool_meta = await tool_router.process_user_message(
            user_text=transcribed_text,
            history=history,
            session_id=session_id,
            farm_id=farm_id,
            detected_language=detected_lang
        )
    except Exception as e:
        logger.error(f"[ChatAudio] Error processing user message: {e}", exc_info=True)
        if detected_lang in {"ta", "tamil"}:
            response_text = "வணக்கம் ஐயா! பண்ணை தகவல்களை பெறுவதில் தற்காலிக தாமதம் ஏற்பட்டுள்ளது. நான் உங்களுக்கு உதவ தயாராக உள்ளேன், உங்கள் கேள்வியை மீண்டும் கேட்கலாம்."
        elif detected_lang in {"hi", "hindi"}:
            response_text = "नमस्ते सर! फार्म डेटा प्राप्त करने में थोड़ी देरी हो रही है। मैं आपकी सहायता के लिए तैयार हूँ, कृपया अपना प्रश्न दोबारा पूछें।"
        elif detected_lang == "tanglish":
            response_text = "Vanakkam sir! Farm data load aagarathula konjam issue irukku. Naan ungalukku help panna ready-ah irukken, unga question-ah thirumbi kelunga."
        else:
            response_text = "Hello! There was a brief delay retrieving the live farm data. I am ready to help, please feel free to ask your question again."
        tool_meta = None

    proof_images = tool_meta.get("proof_images") if tool_meta else None

    await session_manager.save_message(
        session_id=session_id,
        role="assistant",
        content=response_text,
        tool_calls=tool_meta.get("arguments") if tool_meta else None,
        tool_results=tool_meta.get("result") if tool_meta else None,
        detected_language=detected_lang
    )

    # 3. Output TTS: Generate direct playable audio URL & optional base64
    clean_speech = tts_engine.clean_text(response_text)
    clean_speech_snippet = clean_speech[:350].strip()
    encoded_query = urllib.parse.quote_plus(clean_speech_snippet)
    base_url = str(http_req.base_url).rstrip("/")
    audio_url = f"{base_url}/api/tts?text={encoded_query}&language={detected_lang}"

    audio_b64 = None
    if return_audio_base64 and clean_speech:
        tts_res = await tts_engine.synthesize(clean_speech_snippet, detected_lang)
        audio_b64 = tts_res.get("audio_base64")

    return {
        "status": "success",
        "session_id": session_id,
        "transcript": transcribed_text,
        "response": response_text,
        "audio_url": audio_url,
        "audio_base64": audio_b64,
        "detected_language": detected_lang,
        "stt_provider": stt_res.get("provider", "local_faster_whisper"),
        "stt_confidence": confidence,
        "duration": stt_res.get("duration", 0),
        "tool_meta": tool_meta if (tool_meta and tool_meta.get("executed")) else None,
        "proof_images": proof_images
    }

# =========================================================================
# INPUT SPEECH-TO-TEXT (STT) STANDALONE
# =========================================================================

@app.post("/api/stt")
async def standalone_stt_endpoint(
    file: UploadFile = File(..., description="Audio file to transcribe (.wav, .mp3, .m4a, .aac, .ogg, .webm)"),
    language: Optional[str] = Form(None, description="Optional language code (e.g. 'ta', 'hi', 'en')")
):
    """
    Standalone Input Speech-to-Text (STT) API.
    Upload any audio file and get the multilingual transcription back.
    """
    audio_bytes = await file.read()
    if not audio_bytes or len(audio_bytes) < 32:
        raise HTTPException(status_code=400, detail="Uploaded audio file is empty.")

    return await stt_engine.transcribe_file(
        file_bytes=audio_bytes,
        filename=file.filename or "audio.wav",
        language=language
    )

# =========================================================================
# WEBSOCKET REAL-TIME AUDIO & BARGE-IN INTERRUPT STREAM
# =========================================================================

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
                    if len(audio_buffer) > 320000:
                        audio_buffer = audio_buffer[-320000:]
                elif vad_state == "speech_end":
                    if len(audio_buffer) >= 16000:
                        speech_bytes = bytes(audio_buffer)
                        audio_buffer.clear()
                        await websocket.send_json({"type": "vad_status", "status": "processing"})
                        
                        stt_result = await stt_engine.transcribe_audio_bytes(speech_bytes)
                        user_text = stt_result.get("text", "").strip()
                        quality = stt_result.get("quality", "low_confidence")
                        confidence = stt_result.get("confidence", 0.0)
                        
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
                    
                    await websocket.send_json({
                        "type": "user_transcript",
                        "text": user_text,
                        "language": stt_result.get("language", "auto")
                    })

                    history = await session_manager.get_recent_history(session_id)
                    stt_lang = stt_result.get("language", "auto")
                    response_text, tool_meta = await tool_router.process_user_message(
                        user_text=user_text,
                        history=history,
                        session_id=session_id,
                        farm_id=client_farm_id,
                        detected_language=stt_lang
                    )
                    
                    proof_images = tool_meta.get("proof_images") if tool_meta else None
                    clean_snippet = re.sub(r'[*_#`~]', '', response_text)[:300].strip()
                    encoded_q = urllib.parse.quote_plus(clean_snippet)
                    audio_link = f"/api/tts?text={encoded_q}&language={stt_lang}"

                    await websocket.send_json({
                        "type": "agent_response",
                        "user_text": user_text,
                        "response_text": response_text,
                        "audio_url": audio_link,
                        "tool_meta": tool_meta,
                        "proof_images": proof_images
                    })
                    
                    # Synthesize and stream binary speech bytes
                    tts_audio = await tts_engine.synthesize_speech(response_text, language=stt_lang)
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
                            clean_snippet = re.sub(r'[*_#`~]', '', response_text)[:300].strip()
                            encoded_q = urllib.parse.quote_plus(clean_snippet)
                            audio_link = f"/api/tts?text={encoded_q}&language=en"

                            await websocket.send_json({
                                "type": "agent_response",
                                "user_text": user_text,
                                "response_text": response_text,
                                "audio_url": audio_link,
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

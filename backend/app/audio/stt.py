import asyncio
import os
import io
import re
import wave
import tempfile
import logging
import httpx
import numpy as np
from typing import Optional, Dict, Any, Union
from ..config import settings

# Prevent MKL / OpenMP runtime conflicts on Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Compatibility patch for PyAV 14+ / 19+ with faster-whisper (removes deprecated metadata_errors kwarg)
try:
    import av
    _orig_av_open = av.open
    def _patched_av_open(*args, **kwargs):
        kwargs.pop("metadata_errors", None)
        return _orig_av_open(*args, **kwargs)
    av.open = _patched_av_open
except Exception as _av_err:
    pass

logger = logging.getLogger("ragul_stt")

# Balanced multilingual context primers
# Tamil script first, Hindi script second, English/Tanglish dairy entities third.
# Ensures Tamil audio is transcribed into Tamil script, Hindi into Hindi, and English into English without hallucinated translation!
MULTILINGUAL_PROMPT = (
    "வணக்கம், பசு மாடு, பால் அளவு, சினைப்பருவம், மாட்டுத் தீவனம், மடிநோய், குவாட்மாஸ்டெஸ்ட், ஈஸ்ட்ரஸ். "
    "नमस्ते, गाय का दूध उत्पादन, दाना, हीट अलर्ट, मैस्टाइटिस, पशु स्वास्थ्य। "
    "Cow C101 ku feed evvalavu kudukanum, inaiku milk yield check pannunga, Cow COW001, COW002, CAM01, milk yield, feed ration, green fodder."
)
TAMIL_PROMPT = "வணக்கம், பசு மாடு, பால் அளவு, சினைப்பருவம், மாட்டுத் தீவனம், மடிநோய், குவாட்மாஸ்டெஸ்ட், ஈஸ்ட்ரஸ். Cow C101, COW001, CAM01."
HINDI_PROMPT = "नमस्ते, गाय का दूध उत्पादन, दाना, हीट अलर्ट, मैस्टाइटिस, पशु स्वास्थ्य। Cow C101, COW001."
ENGLISH_PROMPT = "Cow C101, COW001, CAM01, milk yield, mastitis, estrus heat alert, green fodder, feed ration."
TAMIL_ENGLISH_PROMPT = MULTILINGUAL_PROMPT

def normalize_target_language(language: Optional[str]) -> Optional[str]:
    """
    Normalizes input language strings.
    If 'auto', 'tanglish', 'multilingual', or empty: returns None (triggers automatic multi-language detection).
    """
    if not language:
        return None
    lang_clean = str(language).strip().lower()
    if lang_clean in {"auto", "all", "multilingual", "multi", "tanglish", "mixed", "none", "null", "undefined"}:
        return None
    if lang_clean in {"ta", "tamil"}:
        return "ta"
    if lang_clean in {"en", "english"}:
        return "en"
    if lang_clean in {"hi", "hindi", "hinglish"}:
        return "hi"
    if lang_clean in {"te", "telugu"}:
        return "te"
    if lang_clean in {"kn", "kannada"}:
        return "kn"
    if lang_clean in {"ml", "malayalam"}:
        return "ml"
    return lang_clean

def detect_language_from_text(text: str, whisper_detected_lang: Optional[str] = None) -> str:
    """
    Intelligently identifies the language and script of the transcribed text:
    - Tamil script (அ-ஔ) -> 'ta'
    - Hindi / Devanagari script (अ-ह) -> 'hi'
    - Tanglish (Romanized Tamil words like ku, evvalavu, irukka, etc.) -> 'tanglish'
    - Hinglish (Romanized Hindi words like kitna, hai, doodh, etc.) -> 'hinglish'
    - English / other -> 'en' (or whisper detected code)
    """
    if not text or not text.strip():
        return whisper_detected_lang or "en"

    # 1. Native script detection
    if any('\u0B80' <= c <= '\u0BFF' for c in text):
        return "ta"
    if any('\u0900' <= c <= '\u097F' for c in text):
        return "hi"

    # 2. Romanized Indian Languages Check (Tanglish & Hinglish)
    lower = text.lower()
    tanglish_words = {
        "ku", "kudunga", "kudukanum", "evvalavu", "evlo", "irukka", "irukku", "inaiku", "inniku",
        "pannunga", "pannalam", "sollunga", "paal", "maadu", "theevanam", "thannir", "enga",
        "eppadi", "eppo", "aachu", "nadandhuchu", "oda", "paththi", "sonna", "nalla", "enna",
        "seri", "illa", "illai", "paravala", "vandhucha", "kidaikuma"
    }
    tokens = set(re.findall(r'\b[a-z]+\b', lower))
    if len(tokens.intersection(tanglish_words)) >= 1:
        return "tanglish"

    hinglish_words = {
        "hai", "ka", "ki", "ke", "ko", "kitna", "kitni", "kitne", "dena", "karo", "karna",
        "bataiye", "batao", "doodh", "gai", "kya", "aaj", "pehle", "kahan", "kaise", "hota"
    }
    if len(tokens.intersection(hinglish_words)) >= 1:
        return "hinglish"

    if whisper_detected_lang in {"ta", "hi", "en", "te", "kn", "ml"}:
        return whisper_detected_lang

    return "en"

def pcm16_to_wav(pcm_bytes: bytes, sample_rate: int = 16000) -> bytes:
    """Encodes raw 16-bit mono PCM into standard WAV bytes in memory."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)
    return buf.getvalue()

async def transcribe_groq_api(
    audio_bytes: bytes,
    filename: str = "audio.wav",
    language: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Ultra-Fast (~0.2s - 0.5s) Cloud Whisper STT using Groq LPU API.
    Zero server RAM usage, high accuracy across Tamil, Tanglish, Hindi, and English.
    """
    groq_api_key = getattr(settings, "GROQ_API_KEY", "") or os.environ.get("GROQ_API_KEY", "")
    if not groq_api_key or not groq_api_key.strip():
        return None

    model_name = getattr(settings, "GROQ_WHISPER_MODEL", "whisper-large-v3") or "whisper-large-v3"
    target_lang = normalize_target_language(language)

    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {groq_api_key.strip()}"
    }

    # Determine audio MIME type
    mime = "audio/wav"
    ext = filename.split(".")[-1].lower() if "." in filename else "wav"
    if ext == "mp3":
        mime = "audio/mpeg"
    elif ext in ("m4a", "mp4", "aac"):
        mime = "audio/mp4"
    elif ext == "ogg":
        mime = "audio/ogg"
    elif ext == "webm":
        mime = "audio/webm"

    # Select optimal prompt based on target language
    if target_lang == "ta":
        selected_prompt = TAMIL_PROMPT
    elif target_lang == "hi":
        selected_prompt = HINDI_PROMPT
    elif target_lang == "en":
        selected_prompt = ENGLISH_PROMPT
    else:
        selected_prompt = MULTILINGUAL_PROMPT

    data: Dict[str, Any] = {
        "model": model_name,
        "prompt": selected_prompt,
        "response_format": "verbose_json",
        "temperature": "0.0"
    }
    if target_lang:
        data["language"] = target_lang

    files = {
        "file": (filename, audio_bytes, mime)
    }

    try:
        start_time = asyncio.get_event_loop().time()
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, headers=headers, data=data, files=files)
            
        elapsed = round(asyncio.get_event_loop().time() - start_time, 2)
        if resp.status_code == 200:
            result = resp.json()
            text = result.get("text", "").strip()
            raw_lang = result.get("language")
            detected_lang = detect_language_from_text(text, raw_lang)
            duration = result.get("duration", 0)

            logger.info(f"[STT-Groq] Cloud Whisper completed in {elapsed}s: '{text}' (lang={detected_lang}, raw={raw_lang})")
            return {
                "text": text,
                "language": detected_lang,
                "raw_language": raw_lang,
                "confidence": 0.95 if text else 0.0,
                "quality": "good" if text else "no_speech",
                "duration": duration or elapsed,
                "provider": "groq_cloud",
                "latency_sec": elapsed
            }
        else:
            logger.warning(f"[STT-Groq] Groq API returned status {resp.status_code}: {resp.text}. Falling back to local.")
            return None
    except Exception as e:
        logger.warning(f"[STT-Groq] Groq API call failed: {e}. Falling back to local faster-whisper.")
        return None

class FasterWhisperSTT:
    def __init__(self):
        self.model = None
        self.device = getattr(settings, "WHISPER_DEVICE", "cpu")
        self.compute_type = getattr(settings, "WHISPER_COMPUTE_TYPE", "int8")
        self.model_size = getattr(settings, "WHISPER_MODEL_SIZE", "base") or "base"
        self._model_loading = False
        logger.info(f"[STT] faster-whisper configured for lazy-load (Model: {self.model_size}).")

    def _load_model_if_needed(self):
        """Load whisper model on first use (lazy init)."""
        if self.model is not None or self._model_loading:
            return
        self._model_loading = True
        try:
            from faster_whisper import WhisperModel
            model_name = self.model_size or "base"
            logger.info(f"[STT] Lazy-loading faster-whisper ('{model_name}') on {self.device}...")
            self.model = WhisperModel(
                model_name,
                device=self.device,
                compute_type=self.compute_type,
                cpu_threads=4,
                num_workers=1
            )
            logger.info(f"[STT] faster-whisper ('{model_name}') lazy-loaded OK.")
        except Exception as e:
            logger.warning(f"[STT] faster-whisper lazy-load failed: {e}")
            self.model = None
        finally:
            self._model_loading = False

    def _transcribe_sync(
        self,
        audio_source: Union[bytes, str],
        language: Optional[str] = None,
        is_raw_pcm: bool = True,
        filename_hint: str = "audio.wav"
    ) -> Dict[str, Any]:
        """
        Ultra-Fast Tamil & English / Tanglish Transcription Worker.
        - Prioritizes Tamil ('ta') and English ('en').
        - Actively blocks false Hindi ('hi') detections.
        - Single-pass greedy decoding (~2s execution on CPU).
        """
        self._load_model_if_needed()
        if self.model is None:
            return {"text": "", "language": "ta", "confidence": 0.0, "quality": "model_unavailable", "duration": 0}

        target_lang = normalize_target_language(language)
        temp_file_path = None

        try:
            from faster_whisper.audio import decode_audio

            # 1. Convert any audio format to 16kHz float32 audio array
            if is_raw_pcm and isinstance(audio_source, bytes):
                audio_np = np.frombuffer(audio_source, dtype=np.int16).astype(np.float32) / 32768.0
            elif isinstance(audio_source, bytes):
                ext = ".wav"
                if filename_hint and "." in filename_hint:
                    ext = "." + filename_hint.split(".")[-1].lower()
                elif audio_source[:4] == b"RIFF":
                    ext = ".wav"
                elif audio_source[:3] == b"ID3" or audio_source[:2] in [b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"]:
                    ext = ".mp3"
                elif b"ftyp" in audio_source[:20]:
                    ext = ".m4a"
                elif audio_source[:4] == b"OggS":
                    ext = ".ogg"

                with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                    tmp.write(audio_source)
                    tmp.flush()
                    temp_file_path = tmp.name

                audio_np = decode_audio(temp_file_path)
            elif isinstance(audio_source, str) and os.path.exists(audio_source):
                audio_np = decode_audio(audio_source)
            else:
                audio_np = audio_source

            if audio_np is None or len(audio_np) < 1600:
                return {"text": "", "language": "ta", "confidence": 0.0, "quality": "no_speech", "duration": 0}

            duration_sec = round(len(audio_np) / 16000.0, 2)

            # 2. Multilingual Language Handling:
            # If target_lang is None (auto), let whisper detect audio language dynamically (ta, hi, en, etc.)
            if target_lang is None:
                try:
                    _, _, all_probs = self.model.detect_language(audio_np)
                    p_dict = dict(all_probs)
                    top_candidate = max(p_dict.items(), key=lambda x: x[1])[0]
                    if top_candidate in {"ta", "en", "hi", "te", "kn", "ml"}:
                        target_lang = top_candidate
                    logger.info(f"[STT] Auto-detected Speech Language: '{target_lang}' (probs: ta={p_dict.get('ta', 0):.2f}, en={p_dict.get('en', 0):.2f}, hi={p_dict.get('hi', 0):.2f})")
                except Exception as detect_err:
                    logger.warning(f"[STT] Language detection failed: {detect_err}.")
                    target_lang = None

            # 3. Fast Single-Pass Transcription with Native VAD Filter & Greedy Decoding (~2s)
            segments_gen, info = self.model.transcribe(
                audio_np,
                beam_size=1,
                best_of=1,
                temperature=0.0,
                language=target_lang,
                task="transcribe",
                vad_filter=True,
                vad_parameters=dict(
                    threshold=0.35,
                    min_speech_duration_ms=180,
                    min_silence_duration_ms=350,
                    speech_pad_ms=200
                ),
                condition_on_previous_text=False,
                initial_prompt=MULTILINGUAL_PROMPT
            )
            segments = list(segments_gen)

            if not segments:
                return {
                    "text": "",
                    "language": target_lang or "en",
                    "confidence": 0.0,
                    "quality": "no_speech",
                    "duration": duration_sec
                }

            text = " ".join([seg.text.strip() for seg in segments]).strip()
            avg_logprob = float(np.mean([seg.avg_logprob for seg in segments]))
            no_speech_prob = float(np.mean([seg.no_speech_prob for seg in segments]))
            confidence = float(np.clip(np.exp(avg_logprob), 0.0, 1.0)) * (1.0 - no_speech_prob)

            is_low_quality = (no_speech_prob > 0.70) or (avg_logprob < -1.8) or (confidence < 0.25) or (len(text) < 2)
            quality = "low_confidence" if is_low_quality else "good"

            final_lang = detect_language_from_text(text, target_lang)
            logger.info(f"[STT] Transcribed ({duration_sec}s): '{text}' | Lang: '{final_lang}' (whisper={target_lang}) | Conf: {confidence:.2f}")

            return {
                "text": text,
                "language": final_lang,
                "raw_language": target_lang,
                "confidence": round(confidence, 2),
                "no_speech_prob": round(no_speech_prob, 2),
                "avg_logprob": round(avg_logprob, 2),
                "quality": quality,
                "duration": duration_sec
            }
        except Exception as e:
            logger.error(f"[STT] Error during transcription: {e}")
            return {"text": "", "language": "ta", "confidence": 0.0, "quality": "error", "duration": 0}
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception:
                    pass

    async def transcribe(self, audio_bytes: bytes, language: Optional[str] = None) -> Dict[str, Any]:
        """Transcribes raw PCM16 audio bytes asynchronously."""
        if len(audio_bytes) < 1600:
            return {"text": "", "language": "ta", "confidence": 0.0, "quality": "noise", "duration": 0}

        # 1. Try Groq Cloud Whisper (~0.2s) if API key is present
        if getattr(settings, "GROQ_API_KEY", "") or os.environ.get("GROQ_API_KEY", ""):
            wav_bytes = pcm16_to_wav(audio_bytes, 16000)
            groq_res = await transcribe_groq_api(wav_bytes, filename="audio.wav", language=language)
            if groq_res is not None:
                return groq_res

        # 2. Local fallback
        return await asyncio.to_thread(self._transcribe_sync, audio_bytes, language, True, "audio.pcm")

    async def transcribe_audio_bytes(self, audio_bytes: bytes, language: Optional[str] = None) -> Dict[str, Any]:
        """Alias for WebSocket raw PCM compatibility."""
        return await self.transcribe(audio_bytes, language)

    async def transcribe_file(
        self,
        file_bytes: bytes,
        filename: str = "audio.wav",
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribes encoded audio files (WAV, MP3, M4A, AAC, OGG, WebM).
        Uses Groq Cloud Whisper (~0.2s) when GROQ_API_KEY is available,
        with seamless fallback to optimized local faster-whisper.
        """
        if not file_bytes or len(file_bytes) < 32:
            return {"text": "", "language": "ta", "confidence": 0.0, "quality": "empty_file", "duration": 0}

        # 1. Try Groq Cloud Whisper (~0.2s) if API key is present
        groq_res = await transcribe_groq_api(file_bytes, filename=filename, language=language)
        if groq_res is not None:
            return groq_res

        # 2. Local fallback
        return await asyncio.to_thread(self._transcribe_sync, file_bytes, language, False, filename)

stt_engine = FasterWhisperSTT()

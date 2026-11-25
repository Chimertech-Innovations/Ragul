import asyncio
import os
import io
import tempfile
import logging
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

# Context Primer strictly for Tamil & English / Tanglish Dairy Speech
# (Hindi is explicitly excluded so Whisper never hallucinates Hindi)
TAMIL_ENGLISH_PROMPT = (
    "வணக்கம் ரகுல், பசு மாடு, பால் அளவு, சினைப் பருவம், மாட்டுத் தீவனம், மடிநோய், குவாட்மாஸ்டெஸ்ட், ஈஸ்ட்ரஸ். "
    "Cow C101, COW001, COW002, COW003, CAM01, milk yield, mastitis, CMT paddle, estrus, feed ration, green fodder. "
    "Cow C101 ku feed evvalavu kudukanum, heat alert irukka, inaiku status enna."
)

def normalize_target_language(language: Optional[str]) -> Optional[str]:
    """
    Normalizes input language strings.
    If 'auto', 'tanglish', 'multilingual', or empty: returns None (triggers smart Tamil vs English detection).
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
    return lang_clean

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

            # 2. Smart Language Filter:
            # If language is auto/tanglish/None, strictly select between 'ta' (Tamil) and 'en' (English).
            # Hindi ('hi') is prevented from falsely hijacking the Tamil speech!
            if target_lang is None:
                try:
                    _, _, all_probs = self.model.detect_language(audio_np)
                    p_dict = dict(all_probs)
                    ta_prob = p_dict.get("ta", 0.0)
                    en_prob = p_dict.get("en", 0.0)
                    hi_prob = p_dict.get("hi", 0.0)

                    # If clear English (>0.60 probability), use 'en'; otherwise default to 'ta' (Tamil/Tanglish)
                    if en_prob > 0.60 and ta_prob < 0.20:
                        target_lang = "en"
                    else:
                        target_lang = "ta"

                    logger.info(f"[STT] Filtered Language Probs: ta={ta_prob:.2f}, en={en_prob:.2f}, hi(blocked)={hi_prob:.2f} -> Chosen: '{target_lang}'")
                except Exception as detect_err:
                    logger.warning(f"[STT] Language detection failed: {detect_err}. Defaulting to 'ta'.")
                    target_lang = "ta"

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
                initial_prompt=TAMIL_ENGLISH_PROMPT
            )
            segments = list(segments_gen)

            if not segments:
                return {
                    "text": "",
                    "language": target_lang,
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

            logger.info(f"[STT] Transcribed ({duration_sec}s): '{text}' | Lang: '{target_lang}' | Conf: {confidence:.2f}")

            return {
                "text": text,
                "language": target_lang,
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
        Transcribes encoded audio files (WAV, MP3, M4A, AAC, OGG, WebM) uploaded by mobile apps or web clients.
        """
        if not file_bytes or len(file_bytes) < 32:
            return {"text": "", "language": "ta", "confidence": 0.0, "quality": "empty_file", "duration": 0}

        return await asyncio.to_thread(self._transcribe_sync, file_bytes, language, False, filename)

stt_engine = FasterWhisperSTT()

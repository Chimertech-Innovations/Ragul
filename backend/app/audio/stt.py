import asyncio
import os
import logging
import numpy as np
from typing import Optional, Dict, Any
from ..config import settings

# Prevent MKL / OpenMP runtime conflicts on Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

logger = logging.getLogger("ragul_stt")

class FasterWhisperSTT:
    def __init__(self):
        self.model = None
        self.device = settings.WHISPER_DEVICE
        self.compute_type = settings.WHISPER_COMPUTE_TYPE
        self.model_size = settings.WHISPER_MODEL_SIZE
        self._model_loading = False
        # Lazy load: model is NOT loaded at startup to save RAM.
        # It will be loaded on first actual audio transcription request.
        logger.info("[STT] faster-whisper configured for lazy-load (saves startup RAM).")

    def _load_model_if_needed(self):
        """Load whisper model on first use (lazy init)."""
        if self.model is not None or self._model_loading:
            return
        self._model_loading = True
        try:
            from faster_whisper import WhisperModel
            model_name = self.model_size or "tiny"
            logger.info(f"[STT] Lazy-loading faster-whisper ('{model_name}') on {self.device}...")
            self.model = WhisperModel(
                model_name,
                device=self.device,
                compute_type=self.compute_type,
                cpu_threads=2,
                num_workers=1
            )
            logger.info(f"[STT] faster-whisper ('{model_name}') lazy-loaded OK.")
        except Exception as e:
            logger.warning(f"[STT] faster-whisper lazy-load failed: {e}")
            self.model = None
        finally:
            self._model_loading = False

    def _transcribe_sync(self, audio_bytes: bytes, language: Optional[str] = None) -> Dict[str, Any]:
        """Synchronous CPU worker run inside thread pool."""
        self._load_model_if_needed()
        try:
            audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

            if self.model is not None:
                segments_gen, info = self.model.transcribe(
                    audio_np,
                    beam_size=3,
                    best_of=3,
                    language=language,
                    task="transcribe",
                    vad_filter=True,
                    vad_parameters=dict(
                        threshold=0.55,
                        min_speech_duration_ms=250,
                        min_silence_duration_ms=500,
                        speech_pad_ms=150
                    ),
                    condition_on_previous_text=False,
                    initial_prompt="Hello Ragul, vanakkam, namaste, dairy farm AI, cattle, cow, COW001, COW002, COW003, CAM01, milk yield, mastitis, subclinical mastitis, Quadmastest, CMT screening, estrus heat detection, artificial insemination, manger feeding, green fodder, dry fodder, silage, rumination, bloat, fever, teat hygiene, farm workers."
                )
                segments = list(segments_gen)

                if not segments:
                    return {"text": "", "language": getattr(info, "language", "auto"), "confidence": 0.0, "quality": "no_speech", "duration": getattr(info, "duration", 0)}

                text = " ".join([seg.text.strip() for seg in segments]).strip()
                
                avg_logprob = float(np.mean([seg.avg_logprob for seg in segments]))
                no_speech_prob = float(np.mean([seg.no_speech_prob for seg in segments]))
                confidence = float(np.clip(np.exp(avg_logprob), 0.0, 1.0)) * (1.0 - no_speech_prob)

                is_low_quality = (no_speech_prob > 0.65) or (avg_logprob < -1.4) or (confidence < 0.35) or (len(text) < 2)
                quality = "low_confidence" if is_low_quality else "good"

                detected_lang = getattr(info, "language", "auto")
                logger.info(f"[STT] Detected Lang: '{detected_lang}' | Text: '{text}' | Conf: {confidence:.2f} | Quality: {quality}")
                
                return {
                    "text": text,
                    "language": detected_lang,
                    "confidence": round(confidence, 2),
                    "no_speech_prob": round(no_speech_prob, 2),
                    "avg_logprob": round(avg_logprob, 2),
                    "quality": quality,
                    "duration": round(getattr(info, "duration", 0), 2)
                }
        except Exception as e:
            logger.error(f"[STT] Error during multilingual faster-whisper transcription: {e}")

        return {"text": "", "language": "auto", "confidence": 0.0, "quality": "error", "duration": 0}

    async def transcribe(self, audio_bytes: bytes, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribes PCM16 audio bytes asynchronously in a thread pool to avoid blocking the event loop.
        """
        if len(audio_bytes) < 1600:
            return {"text": "", "language": "auto", "confidence": 0.0, "quality": "noise", "duration": 0}

        return await asyncio.to_thread(self._transcribe_sync, audio_bytes, language)

    async def transcribe_audio_bytes(self, audio_bytes: bytes, language: Optional[str] = None) -> Dict[str, Any]:
        """Alias for WebSocket compatibility."""
        return await self.transcribe(audio_bytes, language)

stt_engine = FasterWhisperSTT()

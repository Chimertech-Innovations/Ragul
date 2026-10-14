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

    async def transcribe(self, audio_bytes: bytes, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribes PCM16 audio bytes with confidence, no-speech probability, and multilingual language detection.
        """
        if len(audio_bytes) < 1600: # Less than 0.1s
            return {"text": "", "language": "auto", "confidence": 0.0, "quality": "noise", "duration": 0}

        # Lazy-load model on first real transcription
        self._load_model_if_needed()

        try:
            # Convert raw PCM16 bytes directly to Float32 numpy array
            audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

            if self.model is not None:
                segments_gen, info = self.model.transcribe(
                    audio_np,
                    beam_size=3,
                    best_of=3,
                    language=language, # None enables automatic language detection (Tamil, Hindi, English, etc.)
                    task="transcribe",
                    vad_filter=False, # Silero VAD already segments speech cleanly
                    condition_on_previous_text=False,
                    initial_prompt="Hello Ragul, vanakkam, namaste, dairy farm AI, cattle, cow, milk yield, mastitis, feed, staff."
                )
                segments = list(segments_gen)

                if not segments:
                    return {"text": "", "language": getattr(info, "language", "auto"), "confidence": 0.0, "quality": "no_speech", "duration": getattr(info, "duration", 0)}

                text = " ".join([seg.text.strip() for seg in segments]).strip()
                
                # Calculate aggregate confidence and no_speech probability
                avg_logprob = float(np.mean([seg.avg_logprob for seg in segments]))
                no_speech_prob = float(np.mean([seg.no_speech_prob for seg in segments]))
                
                # Convert logprob (-inf to 0) to a normalized 0.0 - 1.0 confidence score
                confidence = float(np.clip(np.exp(avg_logprob), 0.0, 1.0)) * (1.0 - no_speech_prob)

                # Quality determination
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

    async def transcribe_audio_bytes(self, audio_bytes: bytes, language: Optional[str] = None) -> Dict[str, Any]:
        """Alias for WebSocket compatibility."""
        return await self.transcribe(audio_bytes, language)

stt_engine = FasterWhisperSTT()

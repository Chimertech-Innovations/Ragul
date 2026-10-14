import numpy as np
import logging
from typing import Tuple

logger = logging.getLogger("ragul_vad")

class SileroVADProcessor:
    """
    Voice Activity Detection using Silero VAD (512-sample frame slicing) / Energy fallback.
    Detects:
    - User started talking (interruption trigger to immediately cut off RAGUL speech)
    - User still talking
    - User stopped talking (STT transcription trigger)
    """
    def __init__(self, sample_rate: int = 16000, threshold: float = 0.5):
        self.sample_rate = sample_rate
        self.threshold = threshold
        self.window_size_samples = 512 if sample_rate == 16000 else 256
        self.model = None
        self._model_tried = False
        self.is_speaking = False
        self.silence_chunks = 0
        self.speech_chunks = 0
        self.buffer = np.array([], dtype=np.float32)
        # Lazy load: do NOT load silero at startup (saves ~500MB RAM + torch init time)
        logger.info("[VAD] Silero VAD configured for lazy-load (saves startup RAM).")

    def _load_model_if_needed(self):
        if self._model_tried:
            return
        self._model_tried = True
        try:
            import torch
            model, _ = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=True
            )
            self.model = model
            logger.info("[VAD] Silero VAD lazy-loaded OK.")
        except Exception as e:
            logger.info(f"[VAD] Using energy-based VAD fallback: {e}")
            self.model = None

    def process_chunk(self, audio_bytes: bytes) -> Tuple[bool, str]:
        """
        Processes PCM16 audio chunk by slicing into exact 512-sample windows for Silero VAD.
        Returns: (is_voice_detected, state: 'speech_start' | 'speaking' | 'speech_end' | 'silence')
        """
        self._load_model_if_needed()
        try:
            # Convert incoming bytes to float32 (-1.0 to +1.0)
            new_samples = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            
            if len(new_samples) == 0:
                return False, "silence"

            self.buffer = np.concatenate([self.buffer, new_samples])
            
            # If buffer doesn't have enough for at least one 512-sample frame
            if len(self.buffer) < self.window_size_samples:
                return self.is_speaking, "speaking" if self.is_speaking else "silence"

            speech_probs = []

            # Process in exact 512-sample slices
            while len(self.buffer) >= self.window_size_samples:
                frame = self.buffer[:self.window_size_samples]
                self.buffer = self.buffer[self.window_size_samples:]

                if self.model is not None:
                    import torch
                    tensor_audio = torch.from_numpy(frame)
                    prob = self.model(tensor_audio, self.sample_rate).item()
                    speech_probs.append(prob)
                else:
                    # RMS fallback
                    rms = np.sqrt(np.mean(frame**2))
                    speech_probs.append(1.0 if rms > 0.018 else 0.0)

            max_prob = max(speech_probs) if speech_probs else 0.0
            is_voice = max_prob > self.threshold

            if is_voice:
                self.speech_chunks += 1
                self.silence_chunks = 0
                if not self.is_speaking and self.speech_chunks >= 1:
                    self.is_speaking = True
                    return True, "speech_start" # Interruption trigger!
                return True, "speaking"
            else:
                self.silence_chunks += 1
                if self.is_speaking and self.silence_chunks >= 3:
                    self.is_speaking = False
                    self.speech_chunks = 0
                    return False, "speech_end" # Speech ended -> STT trigger
                return False, "silence"

        except Exception as e:
            logger.error(f"[VAD] Error processing chunk: {e}")
            return False, "silence"

    def reset(self):
        self.is_speaking = False
        self.silence_chunks = 0
        self.speech_chunks = 0
        self.buffer = np.array([], dtype=np.float32)
        if self.model is not None and hasattr(self.model, 'reset_states'):
            try:
                self.model.reset_states()
            except Exception:
                pass

vad_processor = SileroVADProcessor()

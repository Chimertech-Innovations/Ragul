import numpy as np
import logging
from collections import deque
from typing import Tuple
from ..config import settings

logger = logging.getLogger("ragul_vad")

class SileroVADProcessor:
    """
    Robust Voice Activity Detection using Silero VAD (512-sample frame slicing)
    with Energy Noise-Gating and Sustained Speech Duration checks.
    
    Prevents false triggers from:
    - Ambient room noise (fans, air conditioning)
    - Transient clicks, keyboard clatter, breathing pops
    - Intermittent mic hiss
    """
    def __init__(
        self,
        sample_rate: int = 16000,
        threshold: float = None,
        min_speech_duration_ms: int = None,
        min_silence_duration_ms: int = None,
        energy_threshold: float = None
    ):
        self.sample_rate = sample_rate or getattr(settings, "VAD_SAMPLE_RATE", 16000)
        self.threshold = threshold if threshold is not None else getattr(settings, "VAD_THRESHOLD", 0.58)
        min_speech_ms = min_speech_duration_ms if min_speech_duration_ms is not None else getattr(settings, "VAD_MIN_SPEECH_DURATION_MS", 250)
        min_silence_ms = min_silence_duration_ms if min_silence_duration_ms is not None else getattr(settings, "VAD_MIN_SILENCE_DURATION_MS", 800)
        self.energy_threshold = energy_threshold if energy_threshold is not None else getattr(settings, "VAD_ENERGY_THRESHOLD", 0.022)

        self.window_size_samples = 512 if self.sample_rate == 16000 else 256
        # Frame duration at 16kHz = 512 / 16000 = 32ms
        self.frame_duration_ms = (self.window_size_samples / self.sample_rate) * 1000.0

        # Number of frames required to confirm speech onset (~250ms = ~8 frames)
        self.min_speech_frames = max(4, int(min_speech_ms / self.frame_duration_ms))
        # Number of silence frames required to confirm speech end (~800ms = ~25 frames)
        self.min_silence_frames = max(10, int(min_silence_ms / self.frame_duration_ms))

        self.model = None
        self._model_tried = False
        self.is_speaking = False
        self.speech_frames = 0
        self.silence_frames = 0
        self.buffer = np.array([], dtype=np.float32)
        
        # Pre-speech buffer (ring buffer of last ~250ms frames to preserve onset phonemes)
        self.pre_speech_frames = deque(maxlen=self.min_speech_frames)

        logger.info(
            f"[VAD] Configured Silero VAD: threshold={self.threshold:.2f}, "
            f"min_speech_frames={self.min_speech_frames} ({min_speech_ms}ms), "
            f"min_silence_frames={self.min_silence_frames} ({min_silence_ms}ms), "
            f"energy_threshold={self.energy_threshold:.3f}"
        )

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
            logger.info("[VAD] Silero VAD neural network loaded OK.")
        except Exception as e:
            logger.warning(f"[VAD] Silero VAD load fallback to energy detector: {e}")
            self.model = None

    def process_chunk(self, audio_bytes: bytes) -> Tuple[bool, str]:
        """
        Processes PCM16 audio chunk by slicing into exact 512-sample frames.
        Returns: (has_speech, vad_state)
        vad_state in: 'speech_start' | 'speaking' | 'speech_end' | 'silence'
        """
        self._load_model_if_needed()
        try:
            # Convert incoming bytes to float32 (-1.0 to +1.0)
            new_samples = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            if len(new_samples) == 0:
                return self.is_speaking, "speaking" if self.is_speaking else "silence"

            self.buffer = np.concatenate([self.buffer, new_samples])

            # Need at least one 512-sample frame to evaluate
            if len(self.buffer) < self.window_size_samples:
                return self.is_speaking, "speaking" if self.is_speaking else "silence"

            result_state = "speaking" if self.is_speaking else "silence"

            # Evaluate sequentially frame-by-frame (each frame is 32ms)
            while len(self.buffer) >= self.window_size_samples:
                frame = self.buffer[:self.window_size_samples]
                self.buffer = self.buffer[self.window_size_samples:]

                # 1. Energy Noise Gate (RMS)
                rms = float(np.sqrt(np.mean(frame**2)))
                if rms < self.energy_threshold:
                    # Below noise floor -> definite silence / ambient hiss
                    is_speech_frame = False
                    speech_prob = 0.0
                else:
                    # 2. Silero VAD Neural Network
                    if self.model is not None:
                        import torch
                        tensor_audio = torch.from_numpy(frame)
                        speech_prob = float(self.model(tensor_audio, self.sample_rate).item())
                        is_speech_frame = speech_prob >= self.threshold
                    else:
                        # RMS Energy Fallback: require robust human voice level (> 0.045)
                        speech_prob = 1.0 if rms > 0.045 else 0.0
                        is_speech_frame = speech_prob >= 1.0

                if is_speech_frame:
                    self.speech_frames += 1
                    self.silence_frames = 0
                    if not self.is_speaking:
                        # Require sustained speech frames before declaring speech_start
                        if self.speech_frames >= self.min_speech_frames:
                            self.is_speaking = True
                            result_state = "speech_start"
                    else:
                        result_state = "speaking"
                else:
                    self.silence_frames += 1
                    if not self.is_speaking:
                        self.speech_frames = 0
                        result_state = "silence"
                    else:
                        # Speaking was active; check if silence lasted long enough to finalize utterance
                        if self.silence_frames >= self.min_silence_frames:
                            self.is_speaking = False
                            self.speech_frames = 0
                            self.silence_frames = 0
                            result_state = "speech_end"
                            if self.model is not None and hasattr(self.model, 'reset_states'):
                                try:
                                    self.model.reset_states()
                                except Exception:
                                    pass
                        else:
                            # Natural pause between words, still considered part of active sentence
                            result_state = "speaking"

            has_speech = (result_state in ("speech_start", "speaking"))
            return has_speech, result_state

        except Exception as e:
            logger.error(f"[VAD] Error processing chunk: {e}")
            return False, "silence"

    def reset(self):
        """Reset internal speech detector states and clear unaligned buffer."""
        self.is_speaking = False
        self.silence_frames = 0
        self.speech_frames = 0
        self.buffer = np.array([], dtype=np.float32)
        if self.model is not None and hasattr(self.model, 'reset_states'):
            try:
                self.model.reset_states()
            except Exception:
                pass

vad_processor = SileroVADProcessor()

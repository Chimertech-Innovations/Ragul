import io
import re
import base64
import asyncio
import logging
from typing import Optional, Dict, Any
from gtts import gTTS
from ..config import settings

logger = logging.getLogger("ragul_tts")

def clean_text_for_tts(text: str) -> str:
    """Strips markdown asterisks, backticks, URLs, emojis, and code fences so speech is natural."""
    if not text:
        return ""
    # 1. Remove code blocks
    clean = re.sub(r'```[\s\S]*?```', '', text)
    # 2. Remove URLs and markdown links
    clean = re.sub(r'\[(.*?)\]\([^)]*\)', r'\1', clean)
    clean = re.sub(r'https?://\S+', '', clean)
    # 3. Remove symbols & markdown formatting (*, _, #, `, ~, |, >)
    clean = re.sub(r'[*_#`~|>]', '', clean)
    # 4. Remove emojis
    clean = re.sub(r'[\U00010000-\U0010ffff]', '', clean)
    # 5. Clean whitespace
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

class TTSEngine:
    """
    Neural Text-to-Speech Adapter supporting:
    - Multilingual synthesis (English Indian accent, Tamil, Hindi)
    - Dynamic language switching based on text characters
    - Binary audio streaming via HTTP and WebSockets
    """
    def __init__(self):
        self.engine_type = getattr(settings, "TTS_ENGINE", "gtts")
        logger.info(f"[TTS] Initialized TTS Engine (Mode: {self.engine_type})")

    def clean_text(self, text: str) -> str:
        return clean_text_for_tts(text)

    def _synthesize_sync(self, text: str, language: str = "en") -> Optional[bytes]:
        try:
            clean = self.clean_text(text)
            if not clean:
                return None

            # Detect language script
            lang = "en"
            tld = "co.in"
            if language:
                l_lower = language.lower()
                if "ta" in l_lower or "tamil" in l_lower:
                    lang = "ta"
                elif "hi" in l_lower or "hindi" in l_lower:
                    lang = "hi"
                elif "en" in l_lower or "english" in l_lower or "tanglish" in l_lower:
                    lang = "en"
                    tld = "co.in"

            # Auto-detect Tamil or Devanagari Unicode
            if any('\u0B80' <= c <= '\u0BFF' for c in clean):
                lang = "ta"
                tld = "com"
            elif any('\u0900' <= c <= '\u097F' for c in clean):
                lang = "hi"
                tld = "com"

            tts = gTTS(text=clean, lang=lang, tld=tld)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            return fp.getvalue()
        except Exception as e:
            logger.error(f"[TTS] Error during speech synthesis: {e}")
            return None

    async def synthesize_speech(self, text: str, language: str = "en") -> Optional[bytes]:
        """Synthesizes text into MP3 audio bytes asynchronously."""
        if not text or not text.strip():
            return None
        return await asyncio.to_thread(self._synthesize_sync, text, language)

    async def synthesize(self, text: str, language: str = "en") -> Dict[str, Any]:
        """Generates audio payload with base64 data for client playback."""
        clean = self.clean_text(text)
        audio_bytes = await self.synthesize_speech(clean, language)
        b64_audio = base64.b64encode(audio_bytes).decode("utf-8") if audio_bytes else None

        return {
            "text": clean,
            "language": language,
            "audio_format": "mp3",
            "audio_base64": b64_audio,
            "has_audio": audio_bytes is not None
        }

tts_engine = TTSEngine()

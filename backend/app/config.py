import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_file_encoding="utf-8"
    )

    APP_NAME: str = "RAGUL - Multilingual Voice-First Dairy AI Assistant"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database (Supabase PostgreSQL / Cloud)
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    DATABASE_URL: str = "postgresql+asyncpg://postgres:RAGul.phd12@db.gyuyfugxyauoiwfvmwjv.supabase.co:5432/postgres"
    
    # LLM Settings (JarvisLabs / OpenAI / Groq / Ollama / vLLM)
    LLM_PROVIDER: str = "jarvislabs"
    JARVISLABS_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    LLM_API_BASE: str = "https://models.jarvislabs.net/v1"
    LLM_MODEL_NAME: str = "gpt-oss-120b"
    LLM_TEMPERATURE: float = 0.2
    
    # Audio & STT (faster-whisper)
    WHISPER_MODEL_SIZE: str = "base"
    WHISPER_DEVICE: str = "cpu"
    WHISPER_COMPUTE_TYPE: str = "int8"
    
    # VAD Settings (Silero VAD)
    VAD_SAMPLE_RATE: int = 16000
    VAD_THRESHOLD: float = 0.5
    VAD_MIN_SPEECH_DURATION_MS: int = 250
    VAD_MIN_SILENCE_DURATION_MS: int = 700
    
    # TTS Settings
    TTS_ENGINE: str = "browser_native"
    DEFAULT_LANGUAGE: str = "en-US"

settings = Settings()

# app/core/config.py

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Research Multi-Agent System"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"  # development | production
    DEBUG: bool = True

    # Security
    API_KEY_HEADER: str = "X-API-Key"
    API_KEYS: str = "dev-key-123,test-key-456"  # comma separated

    

    # LLM
    OPENAI_API_KEY: Optional[str] = None
    API_KEY_ROLES: str = "admin,user" 
    GROQ_API_KEY: Optional[str] = None
    DEFAULT_LLM_PROVIDER: str = "groq"  # groq | openai

    # Memory
    SESSION_TTL_SECONDS: int = 3600  # 1 hour
    MAX_HISTORY_LENGTH: int = 20

    # Search
    MAX_SEARCH_RESULTS: int = 5
    SEARCH_TIMEOUT_SECONDS: int = 10

    # Retry
    MAX_RETRIES: int = 3
    RETRY_DELAY_SECONDS: float = 1.0

    # Evaluation
    ENABLE_EVALUATION: bool = True
    EVAL_SAMPLE_RATE: float = 0.1  # 10% requests evaluate karo

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
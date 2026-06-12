import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # LLM Settings
    LLM_PROVIDER: str = "openai"  # "openai" or "anthropic"
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # or "text-embedding-3-small"
    
    # Vector store
    CHROMA_DB_PATH: str = "./chroma_db"
    COLLECTION_NAME: str = "stackoverflow_python"
    TOP_K_RETRIEVAL: int = 5
    
    # Paths
    DATA_PATH: str = "./data/raw"
    
    # Runtime Configuration
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    MAX_TOKENS: int = 1024
    TEMPERATURE: float = 0.2
    
    # Load config from .env relative to project location
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

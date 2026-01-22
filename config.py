"""
config.py - Configuração centralizada da ALICI™
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # Banco de dados
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/alici")
    
    # Segurança
    SECRET_KEY: str = os.getenv("SECRET_KEY", "alici-secret-dev-only-change-in-prod")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # API
    API_TITLE: str = "ALICI™ API"
    API_VERSION: str = "1.0.0"
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 3600  # segundos
    
    # Embeddings
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_DIMENSION: int = 384
    
    # Features
    ENABLE_RAG: bool = True
    ENABLE_FILE_UPLOAD: bool = True
    MAX_FILE_SIZE_MB: int = 50
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

"""
Core configuration for ALICI Platform
"""
import secrets
from typing import List, Optional
from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "ALICI Platform"
    app_version: str = "2.2.0"
    debug: bool = False
    env: str = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = Field(default=8000, validation_alias=AliasChoices("PORT", "port"))

    # Database
    database_url: str = Field(
        default="sqlite:///./alici.db",
        validation_alias=AliasChoices("DATABASE_URL", "database_url"),
    )

    # Security
    secret_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        validation_alias=AliasChoices("SECRET_KEY", "secret_key", "SECRET"),
    )
    jwt_secret_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        validation_alias=AliasChoices("JWT_SECRET_KEY", "jwt_secret_key", "JWT_SECRET"),
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(
        default=30,
        validation_alias=AliasChoices("ACCESS_TOKEN_EXPIRE_MINUTES", "access_token_expire_minutes"),
    )
    refresh_token_expire_days: int = Field(
        default=7,
        validation_alias=AliasChoices("REFRESH_TOKEN_EXPIRE_DAYS", "refresh_token_expire_days"),
    )

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        validation_alias=AliasChoices("CORS_ORIGINS", "CORS_ALLOWED_ORIGINS", "cors_origins"),
    )

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    # AI Services
    openai_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    mistral_api_key: Optional[str] = None
    local_llm_endpoint: Optional[str] = None

    # AI architecture defaults
    default_model_provider: str = "openai"
    default_vector_provider: str = "memory"

    # Vector providers
    supabase_vector_url: Optional[str] = None
    supabase_vector_api_key: Optional[str] = None
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    weaviate_url: Optional[str] = None
    weaviate_api_key: Optional[str] = None

    web_search_enabled: bool = True
    web_search_timeout_seconds: int = 12

    # Billing
    stripe_secret_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    stripe_price_pro: Optional[str] = None
    stripe_price_enterprise: Optional[str] = None

    # Analytics
    mixpanel_token: Optional[str] = None

    # File Storage
    s3_bucket: Optional[str] = None
    s3_region: Optional[str] = None
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None

    # Redis (optional)
    redis_url: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("REDIS_URL", "redis_url"),
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return []
            if text.startswith("[") and text.endswith("]"):
                # Pydantic handles JSON-like list strings after returning as-is.
                return value
            return [item.strip() for item in text.split(",") if item.strip()]
        return value


# Global settings instance
settings = Settings()
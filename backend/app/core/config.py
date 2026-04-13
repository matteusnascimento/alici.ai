import warnings
import json
from urllib.parse import urlparse
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_KEYS = {"change-me", "secret", "changeme", "dev", "development", "troque-esta-chave-por-uma-chave-forte"}
_LOCAL_SQLITE_FALLBACK = "sqlite:///./axi.db"


def _is_valid_database_url(value: str) -> bool:
    raw = (value or "").strip()
    if not raw:
        return False
    if raw.startswith("sqlite"):
        return True

    parsed = urlparse(raw)
    return parsed.scheme in {"postgresql", "postgresql+psycopg"} and bool(parsed.netloc)


class Settings(BaseSettings):
    app_name: str = "AXI Platform"
    app_env: str = "development"
    debug: bool = True
    database_url: str = _LOCAL_SQLITE_FALLBACK
    enable_dev_seed_user: bool = True
    dev_seed_name: str = "AXI Dev"
    dev_seed_username: str = "devaxi"
    dev_seed_email: str = "dev@axi-platform.com"
    dev_seed_phone: str = "11990000000"
    dev_seed_password: str = ""
    secret_key: str = "change-me-local-dev-secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    default_ai_provider: str = "openai"
    openai_api_key: str = ""
    openai_api_key_rotated: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_timeout_seconds: float = 30.0
    openai_model_chat_general: str = "gpt-4o-mini"
    openai_model_support: str = "gpt-4o-mini"
    openai_model_copy: str = "gpt-4o-mini"
    openai_model_agent_runtime: str = "gpt-4o-mini"
    openai_model_summarization: str = "gpt-4o-mini"
    openai_model_classifier: str = "gpt-4o-mini"
    openai_model_knowledge_qa: str = "gpt-4o-mini"
    openai_model_vision: str = "gpt-4o-mini"
    openai_image_model: str = "gpt-image-1"
    openai_model_transcription: str = "gpt-4o-transcribe"
    openai_model_embeddings: str = "text-embedding-3-small"
    database_url_rotated: str = ""
    cors_allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173", "http://localhost:3000"])

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_cors(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return []
            if raw.startswith("["):
                parsed = json.loads(raw)
                if not isinstance(parsed, list):
                    raise ValueError("CORS_ALLOWED_ORIGINS JSON deve ser uma lista de strings")
                return [item.strip() for item in parsed if isinstance(item, str) and item.strip()]
            return [item.strip() for item in raw.split(",") if item.strip()]
        return [item.strip() for item in value if isinstance(item, str) and item.strip()]

    def __init__(self, **data):
        super().__init__(**data)

        raw_database_url = (self.database_url or "").strip()
        if not _is_valid_database_url(raw_database_url):
            if self.app_env.lower() == "production":
                raise ValueError("Invalid DATABASE_URL for production environment")
            warnings.warn(
                "Invalid DATABASE_URL detected in local environment. Falling back to SQLite.",
                RuntimeWarning,
            )
            object.__setattr__(self, "database_url", _LOCAL_SQLITE_FALLBACK)
        elif raw_database_url != self.database_url:
            object.__setattr__(self, "database_url", raw_database_url)

        if self.app_env != "development" and self.secret_key.lower() in _INSECURE_KEYS:
            raise ValueError(
                "Insecure SECRET_KEY detected for non-development environment. "
                "Set a strong SECRET_KEY via environment variable."
            )

        if self.should_seed_dev_user and not self.dev_seed_password:
            raise ValueError(
                "ENABLE_DEV_SEED_USER=true requires DEV_SEED_PASSWORD to be set via environment variable."
            )

        if self.app_env != "development":
            object.__setattr__(self, "debug", False)

    @property
    def sqlalchemy_database_url(self) -> str:
        effective_database_url = self.database_url_rotated or self.database_url
        if effective_database_url.startswith("postgresql://") and not effective_database_url.startswith("postgresql+psycopg://"):
            return effective_database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        return effective_database_url

    @property
    def effective_openai_api_key(self) -> str:
        # During key rotation, OPENAI_API_KEY_ROTATED takes precedence.
        return self.openai_api_key_rotated or self.openai_api_key

    @property
    def should_seed_dev_user(self) -> bool:
        return (
            self.enable_dev_seed_user
            and self.app_env.lower() != "production"
            and self.sqlalchemy_database_url.startswith("sqlite")
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

import warnings
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_KEYS = {"change-me", "secret", "changeme", "dev", "development", "troque-esta-chave-por-uma-chave-forte"}
_REQUIRED_IN_ALL_ENVS = ("secret_key", "database_url")


class Settings(BaseSettings):
    app_name: str = "AXI Platform"
    app_env: str = "development"
    debug: bool = True
    database_url: str
    enable_dev_seed_user: bool = True
    dev_seed_name: str = "AXI Dev"
    dev_seed_username: str = "devaxi"
    dev_seed_email: str = "dev@axi-platform.com"
    dev_seed_phone: str = "11990000000"
    dev_seed_password: str = ""
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    default_ai_provider: str = "openai"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_timeout_seconds: float = 30.0
    cors_allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173", "http://localhost:3000"])

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_cors(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    def __init__(self, **data):
        super().__init__(**data)
        missing_required = [key.upper() for key in _REQUIRED_IN_ALL_ENVS if not getattr(self, key, "")]
        if missing_required:
            joined = ", ".join(missing_required)
            raise ValueError(f"Missing required environment variable(s): {joined}")

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
        if self.database_url.startswith("postgresql://") and not self.database_url.startswith("postgresql+psycopg://"):
            return self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        return self.database_url

    @property
    def should_seed_dev_user(self) -> bool:
        return (
            self.enable_dev_seed_user
            and self.app_env.lower() != "production"
            and self.database_url.startswith("sqlite")
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

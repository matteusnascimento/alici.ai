import warnings
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_KEYS = {"change-me", "secret", "changeme", "dev", "development", "troque-esta-chave-por-uma-chave-forte"}


class Settings(BaseSettings):
    app_name: str = "AXI Platform"
    app_env: str = "development"
    debug: bool = True
    database_url: str = "sqlite:///./axi.db"
    enable_dev_seed_user: bool = True
    dev_seed_name: str = "AXI Dev"
    dev_seed_username: str = "devaxi"
    dev_seed_email: str = "dev@axi-platform.com"
    dev_seed_phone: str = "11990000000"
    dev_seed_password: str = "AxiDev#2026"
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
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
        if self.app_env != "development" and self.secret_key.lower() in _INSECURE_KEYS:
            warnings.warn(
                "SECRET_KEY não segura detectada em ambiente de produção. "
                "Defina uma chave forte via variável de ambiente SECRET_KEY.",
                stacklevel=2,
            )
        if self.app_env != "development":
            object.__setattr__(self, "debug", False)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

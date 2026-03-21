from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AXI Platform"
    debug: bool = True
    database_url: str = "sqlite:///./axi.db"
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080
    cors_allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173", "http://localhost:3000"])

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_cors(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

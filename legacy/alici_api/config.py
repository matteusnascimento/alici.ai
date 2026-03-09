"""Application configuration and environment parsing."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _as_int(value: str | None, default: int) -> int:
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _parse_origins(value: str | None) -> list[str]:
    if not value:
        return []
    return [origin.strip() for origin in value.split(",") if origin.strip()]


@dataclass(frozen=True)
class Settings:
    env: str
    cors_allowed_origins: list[str]
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int
    rate_limit_enabled: bool
    rate_limit_window_seconds: int
    rate_limit_max_requests: int


def get_settings() -> Settings:
    env = os.getenv("ENV", "development").strip().lower()
    configured_origins = _parse_origins(os.getenv("CORS_ALLOWED_ORIGINS"))

    if env == "production":
        cors_allowed_origins = configured_origins
    else:
        cors_allowed_origins = configured_origins or ["*"]

    return Settings(
        env=env,
        cors_allowed_origins=cors_allowed_origins,
        access_token_expire_minutes=_as_int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"), 60),
        refresh_token_expire_minutes=_as_int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"), 60 * 24 * 7),
        rate_limit_enabled=_as_bool(os.getenv("RATE_LIMIT_ENABLED"), True),
        rate_limit_window_seconds=_as_int(os.getenv("RATE_LIMIT_WINDOW_SECONDS"), 60),
        rate_limit_max_requests=_as_int(os.getenv("RATE_LIMIT_MAX_REQUESTS"), 60),
    )

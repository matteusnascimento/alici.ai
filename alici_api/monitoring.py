"""Minimal production monitoring hooks for Sentry and OpenTelemetry."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI

from alici_api.config import Settings, get_settings
from logger import get_logger

logger_monitoring = get_logger("monitoring")
_initialized = False
_instrumented_app_ids: set[int] = set()


def init_monitoring(app: FastAPI | None = None, settings: Settings | None = None) -> None:
    global _initialized
    settings = settings or get_settings()

    if not _initialized and settings.sentry_dsn:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            from sentry_sdk.integrations.starlette import StarletteIntegration

            sentry_sdk.init(
                dsn=settings.sentry_dsn,
                environment=settings.env,
                release=f"{settings.app_name}@{settings.app_version}",
                traces_sample_rate=settings.sentry_traces_sample_rate,
                profiles_sample_rate=settings.sentry_profiles_sample_rate,
                integrations=[FastApiIntegration(), StarletteIntegration()],
                send_default_pii=False,
            )
            _initialized = True
            logger_monitoring.info("sentry_initialized")
        except Exception as exc:
            logger_monitoring.warning("sentry_init_failed", extra={"error": str(exc)})

    if app is not None and id(app) not in _instrumented_app_ids:
        try:
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

            FastAPIInstrumentor.instrument_app(app)
            _instrumented_app_ids.add(id(app))
            logger_monitoring.info("otel_fastapi_instrumented")
        except Exception as exc:
            logger_monitoring.warning("otel_init_skipped", extra={"error": str(exc)})


def set_monitoring_user(user: dict[str, Any] | None) -> None:
    if not user:
        return
    try:
        import sentry_sdk

        sentry_sdk.set_user({"id": str(user.get("id")), "email": user.get("email"), "plano": user.get("plano")})
    except Exception:
        return


def capture_critical_event(
    message: str,
    *,
    level: str = "error",
    tags: dict[str, str] | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    logger_monitoring.error(message, extra={**(tags or {}), **(extra or {})})
    try:
        import sentry_sdk

        with sentry_sdk.push_scope() as scope:
            for key, value in (tags or {}).items():
                scope.set_tag(key, value)
            for key, value in (extra or {}).items():
                scope.set_extra(key, value)
            sentry_sdk.capture_message(message, level=level)
    except Exception:
        return

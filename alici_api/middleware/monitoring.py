"""Request context and monitoring middleware."""

from __future__ import annotations

import re
import time
from collections.abc import Awaitable, Callable
from contextvars import ContextVar
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from alici_api.config import get_settings

_REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)
user_id_ctx: ContextVar[str | None] = ContextVar("user_id", default=None)


def get_current_request_id() -> str | None:
    return request_id_ctx.get()


def get_current_user_id() -> str | None:
    return user_id_ctx.get()


def _safe_request_id(raw_value: str | None) -> str:
    if raw_value and _REQUEST_ID_RE.match(raw_value):
        return raw_value
    return uuid4().hex


def _set_sentry_context(request: Request, request_id: str) -> None:
    settings = get_settings()
    if not settings.sentry_dsn:
        return

    try:
        import sentry_sdk
    except Exception:
        return

    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("request_id", request_id)
        scope.set_tag("http.method", request.method)
        scope.set_tag("http.route", request.url.path)
        if request.client:
            scope.set_extra("client_host", request.client.host)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach request id, timing and monitoring context to every request."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request_id = _safe_request_id(request.headers.get("X-Request-ID"))
        request.state.request_id = request_id
        request_id_token = request_id_ctx.set(request_id)
        user_id_token = user_id_ctx.set(None)
        start = time.perf_counter()

        _set_sentry_context(request, request_id)

        try:
            response = await call_next(request)
        finally:
            request_id_ctx.reset(request_id_token)
            user_id_ctx.reset(user_id_token)

        elapsed_ms = int((time.perf_counter() - start) * 1000)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-ms"] = str(elapsed_ms)
        return response


# Backward-compatible name used by older imports.
RequestIDMiddleware = RequestContextMiddleware

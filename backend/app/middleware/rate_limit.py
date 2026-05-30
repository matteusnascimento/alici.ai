from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith(("/uploads/", "/exports/")):
            lowered = request.url.path.lower()
            if lowered.startswith(("/uploads/chat/", "/uploads/agent_knowledge/")):
                return JSONResponse(status_code=404, content={"detail": "Not found"})
            blocked_suffixes = (".env", ".key", ".pem", ".sqlite", ".db", ".log", ".py", ".json")
            if "/." in lowered or lowered.endswith(blocked_suffixes):
                return JSONResponse(status_code=404, content={"detail": "Not found"})

        if not settings.rate_limit_enabled or request.url.path in {"/health", "/ready", "/"}:
            return await call_next(request)

        now = time.monotonic()
        window = settings.rate_limit_window_seconds
        limit = settings.rate_limit_max_requests
        client = request.client.host if request.client else "unknown"
        key = f"{client}:{request.url.path}"
        hits = self._hits[key]
        while hits and now - hits[0] > window:
            hits.popleft()
        if len(hits) >= limit:
            return JSONResponse(status_code=429, content={"detail": "Limite de requisicoes atingido. Tente novamente em instantes."})
        hits.append(now)
        response = await call_next(request)
        if request.url.path.startswith(("/uploads/", "/exports/")):
            response.headers["Cache-Control"] = f"private, max-age={settings.public_upload_max_age_seconds}"
            response.headers["X-Content-Type-Options"] = "nosniff"
        return response

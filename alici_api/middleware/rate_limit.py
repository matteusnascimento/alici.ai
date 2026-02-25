"""In-memory rate limiting middleware."""

from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._bucket: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        if request.url.path in {"/health", "/"}:
            return await call_next(request)

        ip = request.client.host if request.client else "unknown"
        key = f"{ip}:{request.url.path}"
        now = time.time()
        dq = self._bucket[key]

        while dq and now - dq[0] > self.window_seconds:
            dq.popleft()

        if len(dq) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "status": "erro",
                    "code": "ERR-RATE-429",
                    "message": "Muitas requisições. Tente novamente em instantes.",
                },
            )

        dq.append(now)
        return await call_next(request)

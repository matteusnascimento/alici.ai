"""Redis-backed rate limiting middleware.

No production request counters live in Python memory. This keeps limits
consistent across multiple web workers and protects paid AI endpoints from
cost spikes.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any

from fastapi import Request
from jose import JWTError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from alici_api.config import Settings, get_settings
from alici_api.responses import Codes, error_payload
from alici_api.services.redis_client import get_redis_client
from auth import verify_token
from logger import get_logger

logger_rate = get_logger("rate_limit")

_TOKEN_RE = re.compile(r"^Bearer\s+(.+)$", re.IGNORECASE)
_LONG_SEGMENT_RE = re.compile(r"/[A-Za-z0-9_-]{16,}(?=/|$)")
_NUMERIC_SEGMENT_RE = re.compile(r"/\d+(?=/|$)")

_INCR_EXPIRE_SCRIPT = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
  redis.call('EXPIRE', KEYS[1], tonumber(ARGV[1]))
end
local ttl = redis.call('TTL', KEYS[1])
return {current, ttl}
"""


@dataclass(frozen=True)
class RateLimitRule:
    name: str
    key: str
    limit: int
    window_seconds: int


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Apply global, per-IP, per-user and per-endpoint limits through Redis."""

    def __init__(
        self,
        app,
        *,
        settings: Settings | None = None,
        max_requests: int | None = None,
        window_seconds: int | None = None,
    ):
        super().__init__(app)
        self.settings = settings or get_settings()
        self.window_seconds = int(window_seconds or self.settings.rate_limit_window_seconds)
        self.legacy_max_requests = int(max_requests or self.settings.rate_limit_max_requests)
        self.prefix = f"{self.settings.redis_prefix}:rl:{self.settings.env}"
        self.excluded_paths = tuple(self.settings.excluded_rate_limit_paths)

    async def dispatch(self, request: Request, call_next) -> Response:
        if not self.settings.rate_limit_enabled or self._is_excluded(request.url.path) or self._is_html_page_request(request):
            return await call_next(request)

        try:
            blocked = await self._check_limits(request)
        except Exception as exc:
            logger_rate.exception("rate_limit_redis_unavailable", extra={"path": request.url.path})
            if self.settings.is_production:
                return JSONResponse(
                    status_code=503,
                    content=error_payload(
                        Codes.SERVICE_UNAVAILABLE,
                        "Protecao de limite temporariamente indisponivel. Tente novamente em instantes.",
                    ),
                    headers={"Retry-After": "5"},
                )
            request.state.rate_limit_degraded = True
            logger_rate.warning("rate_limit_fail_open_development", extra={"error": str(exc)})
            return await call_next(request)

        if blocked is not None:
            return blocked

        return await call_next(request)

    def _is_excluded(self, path: str) -> bool:
        if path.startswith("/assets/") or path.startswith("/static/"):
            return True
        for excluded in self.excluded_paths:
            if not excluded:
                continue
            if path == excluded or path.startswith(excluded.rstrip("/") + "/"):
                return True
        return False

    def _is_html_page_request(self, request: Request) -> bool:
        if request.method.upper() != "GET":
            return False
        if request.url.path not in {"/", "/login", "/register", "/chat", "/dashboard", "/jobs", "/app"} and not request.url.path.startswith("/app/"):
            return False
        accept = request.headers.get("accept", "")
        return not accept or "text/html" in accept or "*/*" in accept

    async def _check_limits(self, request: Request) -> JSONResponse | None:
        identity = self._identity(request)
        endpoint = self._endpoint_key(request)
        rules = self._rules(identity=identity, endpoint=endpoint)

        worst_retry_after = 1
        violated: dict[str, Any] | None = None

        for rule in rules:
            current, ttl = await self._increment(rule)
            retry_after = max(1, ttl if ttl > 0 else rule.window_seconds)
            if current > rule.limit:
                worst_retry_after = max(worst_retry_after, retry_after)
                violated = {
                    "scope": rule.name,
                    "limit": rule.limit,
                    "window_seconds": rule.window_seconds,
                    "retry_after": retry_after,
                }
                break

        if violated is None:
            return None

        logger_rate.info(
            "rate_limit_blocked",
            extra={
                "scope": violated["scope"],
                "path": request.url.path,
                "method": request.method,
                "retry_after": violated["retry_after"],
            },
        )
        return JSONResponse(
            status_code=429,
            content=error_payload(
                Codes.RATE_LIMIT,
                "Muitas requisicoes. Tente novamente em instantes.",
                **violated,
            ),
            headers={
                "Retry-After": str(worst_retry_after),
                "X-RateLimit-Scope": str(violated["scope"]),
                "X-RateLimit-Limit": str(violated["limit"]),
                "X-RateLimit-Window": str(violated["window_seconds"]),
            },
        )

    async def _increment(self, rule: RateLimitRule) -> tuple[int, int]:
        result = await get_redis_client(self.settings).eval(
            _INCR_EXPIRE_SCRIPT,
            1,
            rule.key,
            rule.window_seconds,
        )
        current = int(result[0])
        ttl = int(result[1])
        return current, ttl

    def _rules(self, *, identity: dict[str, str], endpoint: str) -> list[RateLimitRule]:
        window = self.window_seconds
        user_or_anon = identity.get("user_id") or f"anon:{identity['ip_hash']}"
        return [
            RateLimitRule(
                "global",
                f"{self.prefix}:global",
                int(self.settings.rate_limit_global_max_requests),
                window,
            ),
            RateLimitRule(
                "ip",
                f"{self.prefix}:ip:{identity['ip_hash']}",
                int(self.settings.rate_limit_ip_max_requests or self.legacy_max_requests),
                window,
            ),
            RateLimitRule(
                "endpoint",
                f"{self.prefix}:endpoint:{endpoint}",
                int(self.settings.rate_limit_endpoint_max_requests or self.legacy_max_requests),
                window,
            ),
            RateLimitRule(
                "user",
                f"{self.prefix}:user:{user_or_anon}",
                int(self.settings.rate_limit_user_max_requests or self.legacy_max_requests),
                window,
            ),
        ]

    def _identity(self, request: Request) -> dict[str, str]:
        ip = self._client_ip(request)
        user_id = self._user_id_from_auth(request.headers.get("Authorization"))
        if user_id:
            request.state.rate_limit_user_id = user_id
        return {
            "ip": ip,
            "ip_hash": self._hash(ip),
            "user_id": user_id or "",
        }

    def _client_ip(self, request: Request) -> str:
        for header in ("CF-Connecting-IP", "X-Real-IP", "X-Forwarded-For"):
            raw_value = request.headers.get(header)
            if raw_value:
                return raw_value.split(",", 1)[0].strip()[:128] or "unknown"
        return (request.client.host if request.client else "unknown")[:128]

    def _user_id_from_auth(self, authorization: str | None) -> str | None:
        if not authorization:
            return None
        match = _TOKEN_RE.match(authorization.strip())
        if not match:
            return None
        try:
            payload = verify_token(match.group(1), expected_type="access")
            subject = payload.get("sub")
            return str(subject) if subject is not None else None
        except (JWTError, ValueError, TypeError):
            return None
        except Exception:
            return None

    def _endpoint_key(self, request: Request) -> str:
        normalized = _NUMERIC_SEGMENT_RE.sub("/:id", request.url.path)
        normalized = _LONG_SEGMENT_RE.sub("/:token", normalized)
        raw = f"{request.method.upper()}:{normalized}"
        return self._hash(raw)

    @staticmethod
    def _hash(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()[:32]

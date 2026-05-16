"""Security-related HTTP middlewares."""

from __future__ import annotations

from collections.abc import Callable, Awaitable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attach conservative security headers to every response."""

    def __init__(
        self,
        app,
        *,
        enabled: bool = True,
        csp_enabled: bool = True,
        csp: str = "",
        hsts_enabled: bool = True,
        hsts_max_age: int = 31_536_000,
        referrer_policy: str = "strict-origin-when-cross-origin",
        permissions_policy: str = "camera=(), microphone=(), geolocation=(), payment=()",
        production: bool = False,
    ):
        super().__init__(app)
        self.enabled = enabled
        self.csp_enabled = csp_enabled
        self.csp = csp
        self.hsts_enabled = hsts_enabled
        self.hsts_max_age = hsts_max_age
        self.referrer_policy = referrer_policy
        self.permissions_policy = permissions_policy
        self.production = production

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        response = await call_next(request)
        if not self.enabled:
            return response

        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("X-DNS-Prefetch-Control", "off")
        response.headers.setdefault("X-Download-Options", "noopen")
        response.headers.setdefault("X-Permitted-Cross-Domain-Policies", "none")
        response.headers.setdefault("Referrer-Policy", self.referrer_policy)
        response.headers.setdefault("Permissions-Policy", self.permissions_policy)
        response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        response.headers.setdefault("Cross-Origin-Resource-Policy", "same-origin")
        response.headers.setdefault("Origin-Agent-Cluster", "?1")

        if request.url.path.startswith(("/auth", "/billing", "/webhooks")):
            response.headers.setdefault("Cache-Control", "no-store")

        if self.csp_enabled and self.csp:
            response.headers.setdefault("Content-Security-Policy", self.csp)

        if self.production and self.hsts_enabled:
            response.headers.setdefault(
                "Strict-Transport-Security",
                f"max-age={self.hsts_max_age}; includeSubDomains; preload",
            )

        return response

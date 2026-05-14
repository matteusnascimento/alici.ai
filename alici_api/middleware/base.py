"""Central middleware setup for the FastAPI app."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from alici_api.config import Settings, get_settings
from alici_api.middleware.monitoring import RequestContextMiddleware
from alici_api.middleware.rate_limit import RateLimitMiddleware
from alici_api.middleware.security import SecurityHeadersMiddleware


def setup_middlewares(app: FastAPI, settings: Settings | None = None) -> FastAPI:
    """Register middlewares in one place.

    The order is intentional:
    - TrustedHost and CORS are protocol/access controls.
    - RateLimit can short-circuit abusive requests.
    - SecurityHeaders wraps application and rate-limit responses.
    - RequestContext is outermost, so every response gets request id/timing.
    """

    settings = settings or get_settings()

    trusted_hosts = settings.trusted_hosts
    if trusted_hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )

    if settings.rate_limit_enabled:
        app.add_middleware(
            RateLimitMiddleware,
            settings=settings,
        )

    app.add_middleware(
        SecurityHeadersMiddleware,
        enabled=settings.security_headers_enabled,
        csp_enabled=settings.security_csp_enabled,
        csp=settings.security_csp,
        hsts_enabled=settings.security_hsts_enabled,
        hsts_max_age=settings.security_hsts_max_age,
        referrer_policy=settings.security_referrer_policy,
        permissions_policy=settings.security_permissions_policy,
        production=settings.is_production,
    )

    app.add_middleware(RequestContextMiddleware)
    return app

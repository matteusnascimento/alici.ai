"""Shared Redis connection utilities.

Redis is a production dependency for rate limiting, AI cache and Arq jobs.
Development can fall back to localhost to keep onboarding simple.
"""

from __future__ import annotations

from redis.asyncio import Redis

from alici_api.config import Settings, get_settings

_redis_client: Redis | None = None


def get_redis_client(settings: Settings | None = None) -> Redis:
    global _redis_client

    settings = settings or get_settings()
    if _redis_client is None:
        _redis_client = Redis.from_url(
            settings.resolved_redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
            health_check_interval=30,
        )
    return _redis_client


async def close_redis_client() -> None:
    global _redis_client

    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None


async def ping_redis(settings: Settings | None = None) -> bool:
    client = get_redis_client(settings)
    return bool(await client.ping())

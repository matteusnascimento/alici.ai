"""Redis cache for AI prompt/result pairs."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any

from alici_api.config import Settings, get_settings
from alici_api.services.ai.base import AIResponse
from alici_api.services.redis_client import get_redis_client
from logger import get_logger

logger_cache = get_logger("ai_cache")


class AICache:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.prefix = f"{self.settings.redis_prefix}:ai-cache:v1"

    def build_key(self, *, operation: str, prompt: str, system_prompt: str = "") -> str:
        payload = {
            "operation": operation,
            "prompt": prompt,
            "system_prompt": system_prompt,
        }
        digest = hashlib.sha256(
            json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest()
        return f"{self.prefix}:{digest}"

    async def get_response(self, *, operation: str, prompt: str, system_prompt: str = "") -> AIResponse | None:
        if not self.settings.ai_cache_enabled:
            return None

        key = self.build_key(operation=operation, prompt=prompt, system_prompt=system_prompt)
        try:
            raw_value = await get_redis_client(self.settings).get(key)
            if not raw_value:
                return None
            payload: dict[str, Any] = json.loads(raw_value)
            response = AIResponse(
                content=str(payload.get("content") or ""),
                provider=str(payload.get("provider") or "cache"),
                model=str(payload.get("model") or "cached"),
                response_time_ms=0,
                estimated_tokens=int(payload.get("estimated_tokens") or 0),
                cached=True,
            )
            logger_cache.info("ai_cache_hit", extra={"operation": operation, "provider": response.provider})
            return response
        except Exception as exc:
            logger_cache.warning("ai_cache_read_failed", extra={"operation": operation, "error": str(exc)})
            return None

    async def set_response(
        self,
        *,
        operation: str,
        prompt: str,
        system_prompt: str = "",
        response: AIResponse,
    ) -> None:
        if not self.settings.ai_cache_enabled:
            return
        if not response.content:
            return

        key = self.build_key(operation=operation, prompt=prompt, system_prompt=system_prompt)
        payload = asdict(response)
        payload["cached"] = False
        try:
            await get_redis_client(self.settings).setex(
                key,
                int(self.settings.ai_cache_ttl_seconds),
                json.dumps(payload, ensure_ascii=False),
            )
            logger_cache.info(
                "ai_cache_store",
                extra={"operation": operation, "provider": response.provider, "model": response.model},
            )
        except Exception as exc:
            logger_cache.warning("ai_cache_write_failed", extra={"operation": operation, "error": str(exc)})

    async def get_payload(self, *, operation: str, prompt: str, system_prompt: str = "") -> dict[str, Any] | None:
        """Return a generic cached payload for non-text AI operations."""
        if not self.settings.ai_cache_enabled:
            return None

        key = self.build_key(operation=operation, prompt=prompt, system_prompt=system_prompt)
        try:
            raw_value = await get_redis_client(self.settings).get(key)
            if not raw_value:
                logger_cache.info("ai_cache_miss", extra={"operation": operation})
                return None
            payload = json.loads(raw_value)
            if not isinstance(payload, dict):
                return None
            logger_cache.info("ai_cache_hit", extra={"operation": operation, "kind": "payload"})
            return payload
        except Exception as exc:
            logger_cache.warning("ai_cache_payload_read_failed", extra={"operation": operation, "error": str(exc)})
            return None

    async def set_payload(
        self,
        *,
        operation: str,
        prompt: str,
        payload: dict[str, Any],
        system_prompt: str = "",
    ) -> None:
        """Store a generic cached payload for media/job results."""
        if not self.settings.ai_cache_enabled or not payload:
            return

        key = self.build_key(operation=operation, prompt=prompt, system_prompt=system_prompt)
        try:
            await get_redis_client(self.settings).setex(
                key,
                int(self.settings.ai_cache_ttl_seconds),
                json.dumps(payload, ensure_ascii=False),
            )
            logger_cache.info("ai_cache_store", extra={"operation": operation, "kind": "payload"})
        except Exception as exc:
            logger_cache.warning("ai_cache_payload_write_failed", extra={"operation": operation, "error": str(exc)})

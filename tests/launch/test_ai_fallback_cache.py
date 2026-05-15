from __future__ import annotations

import pytest

from alici_api.services.ai.base import AIResponse, BaseAIProvider
from alici_api.services.ai.manager import AIManager
from alici_api.services.ai_cache import AICache


class FailingProvider(BaseAIProvider):
    async def chat(self, prompt: str, system_prompt: str = "") -> AIResponse:
        raise RuntimeError("provider unavailable")


class WorkingProvider(BaseAIProvider):
    async def chat(self, prompt: str, system_prompt: str = "") -> AIResponse:
        return AIResponse(content=f"ok:{prompt}", provider="groq", model="llama-3.1-8b-instant")


class CostService:
    def calculate_cost(self, *, job_type, provider=None, model=None, **kwargs):
        return {"grok": 1, "groq": 1, "gemini": 2, "openai": 9}.get(provider, 5)


@pytest.mark.asyncio
async def test_ai_manager_falls_back_from_grok_to_groq():
    manager = AIManager(default_provider="grok", credit_service=CostService())
    manager.providers = {"grok": FailingProvider(), "groq": WorkingProvider()}
    manager.__class__._provider_failure_counts.clear()
    manager.__class__._provider_disabled_until.clear()

    response = await manager.chat("ola")

    assert response.content == "ok:ola"
    assert response.provider == "groq"
    assert manager.__class__._provider_failure_counts["grok"] == 1


class FakeRedis:
    def __init__(self):
        self.values = {}

    async def get(self, key):
        return self.values.get(key)

    async def setex(self, key, ttl, value):
        self.values[key] = value
        return True


@pytest.mark.asyncio
async def test_ai_cache_roundtrip(monkeypatch):
    redis = FakeRedis()
    monkeypatch.setattr("alici_api.services.ai_cache.get_redis_client", lambda settings: redis)
    cache = AICache()
    response = AIResponse(content="cached answer", provider="grok", model="grok-3-mini-fast", estimated_tokens=3)

    await cache.set_response(operation="chat", prompt="pergunta", system_prompt="sistema", response=response)
    cached = await cache.get_response(operation="chat", prompt="pergunta", system_prompt="sistema")

    assert cached is not None
    assert cached.cached is True
    assert cached.content == "cached answer"
    assert cached.provider == "grok"

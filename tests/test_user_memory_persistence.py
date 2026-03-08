"""User memory persistence tests."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import create_tables
from main import app
from app.services.ai_orchestrator import settings as orchestrator_settings


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def _register_user(client: AsyncClient) -> str:
    create_tables()
    email = f"mem_{uuid.uuid4().hex[:10]}@alici.ai"
    org_name = f"Memory Org {uuid.uuid4().hex[:8]}"

    response = await client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "StrongPass123!",
            "full_name": "Memory User",
            "organization_name": org_name,
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.mark.anyio
async def test_memory_is_captured_from_chat_message(monkeypatch):
    monkeypatch.setattr(orchestrator_settings, "openai_api_key", "test-key", raising=False)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        send = await client.post(
            "/api/chat/message",
            json={"message": "Meu restaurante abre as 8h"},
            headers=headers,
        )
        assert send.status_code == 200

        memory = await client.get("/api/user/memory", headers=headers)
        assert memory.status_code == 200
        payload = memory.json()

        assert any(item["key"] == "restaurant_opening_hours" and "8h" in item["value"] for item in payload)


@pytest.mark.anyio
async def test_memory_upsert_endpoint_roundtrip():
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        create = await client.post(
            "/api/user/memory",
            json={"key": "preferred_language", "value": "pt-BR"},
            headers=headers,
        )
        assert create.status_code == 200

        update = await client.post(
            "/api/user/memory",
            json={"key": "preferred_language", "value": "en-US"},
            headers=headers,
        )
        assert update.status_code == 200

        memory = await client.get("/api/user/memory", headers=headers)
        assert memory.status_code == 200
        payload = memory.json()

        assert any(item["key"] == "preferred_language" and item["value"] == "en-US" for item in payload)

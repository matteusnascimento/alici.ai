"""Phase 5 and 6 tests: history quality and profile validation."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from app.core.database import create_tables
from app.services.ai_orchestrator import settings as orchestrator_settings


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def _register_user(client: AsyncClient) -> str:
    create_tables()
    email = f"phase56_{uuid.uuid4().hex[:10]}@alici.ai"
    org_name = f"Phase56 Org {uuid.uuid4().hex[:8]}"
    register = await client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "StrongPass123!",
            "full_name": "Phase Five Six",
            "organization_name": org_name,
        },
    )
    assert register.status_code == 200
    return register.json()["access_token"]


@pytest.mark.anyio
async def test_history_list_includes_last_message_timestamp(monkeypatch):
    monkeypatch.setattr(orchestrator_settings, "openai_api_key", "test-key", raising=False)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        send = await client.post(
            "/api/chat/message",
            json={"message": "Mensagem para validar historico"},
            headers=headers,
        )
        assert send.status_code == 200

        history = await client.get("/api/conversations", headers=headers)
        assert history.status_code == 200
        items = history.json()
        assert len(items) >= 1
        assert "last_message" in items[0]
        assert "last_message_at" in items[0]


@pytest.mark.anyio
async def test_conversation_pagination_contract(monkeypatch):
    monkeypatch.setattr(orchestrator_settings, "openai_api_key", "test-key", raising=False)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        for idx in range(3):
            response = await client.post(
                "/api/conversations",
                json={"title": f"Conversa {idx + 1}"},
                headers=headers,
            )
            assert response.status_code == 200

        page = await client.get("/api/conversations?limit=2&offset=0", headers=headers)
        assert page.status_code == 200
        items = page.json()
        assert len(items) <= 2


@pytest.mark.anyio
async def test_profile_update_rejects_blank_name():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        update = await client.put("/api/user", json={"full_name": "   "}, headers=headers)
        assert update.status_code == 400


@pytest.mark.anyio
async def test_password_update_requires_strong_password():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        weak = await client.put(
            "/api/user/password",
            json={"current_password": "StrongPass123!", "new_password": "weakpass"},
            headers=headers,
        )
        assert weak.status_code == 400


@pytest.mark.anyio
async def test_user_settings_roundtrip():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        update = await client.put(
            "/api/user/settings",
            json={"language": "en-US", "theme": "light", "notifications_enabled": False},
            headers=headers,
        )
        assert update.status_code == 200

        current = await client.get("/api/user/settings", headers=headers)
        assert current.status_code == 200
        payload = current.json()
        assert payload["language"] == "en-US"
        assert payload["theme"] == "light"
        assert payload["notifications_enabled"] is False

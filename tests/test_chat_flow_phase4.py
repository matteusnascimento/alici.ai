"""Phase 4 chat flow tests: send message and verify persistence."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from app.core.database import create_tables
from app.services.ai_orchestrator import settings as orchestrator_settings


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_chat_message_flow_persists_user_and_ai_messages(monkeypatch):
    monkeypatch.setattr(orchestrator_settings, "openai_api_key", "test-key", raising=False)
    create_tables()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        email = f"phase4_{uuid.uuid4().hex[:10]}@alici.ai"
        org_name = f"Phase4 Org {uuid.uuid4().hex[:8]}"

        register = await client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "StrongPass123!",
                "full_name": "Phase Four",
                "organization_name": org_name,
            },
        )
        assert register.status_code == 200

        tokens = register.json()
        access_token = tokens["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        send = await client.post(
            "/api/chat/message",
            json={"message": "Explique o status atual da plataforma"},
            headers=headers,
        )
        assert send.status_code == 200
        payload = send.json()

        assert payload.get("conversation_id")
        assert payload.get("message")
        assert payload.get("response")
        assert payload.get("resposta")

        conversation_id = payload["conversation_id"]

        conversations = await client.get("/api/chat/conversations", headers=headers)
        assert conversations.status_code == 200
        conv_list = conversations.json()
        assert any(item["id"] == conversation_id for item in conv_list)

        messages = await client.get(f"/api/chat/conversations/{conversation_id}/messages", headers=headers)
        assert messages.status_code == 200
        message_list = messages.json()

        assert len(message_list) >= 2
        roles = [item["role"] for item in message_list]
        assert "user" in roles
        assert "assistant" in roles

"""Web search fallback integration tests."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import create_tables
from main import app
from app.api.routes.chat import orchestrator
from app.core.config import settings


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def _register_user(client: AsyncClient) -> str:
    create_tables()
    email = f"web_{uuid.uuid4().hex[:10]}@alici.ai"
    org_name = f"Web Org {uuid.uuid4().hex[:8]}"

    response = await client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "StrongPass123!",
            "full_name": "Web Search User",
            "organization_name": org_name,
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.mark.anyio
async def test_chat_fallbacks_to_web_search_when_provider_unavailable(monkeypatch):
    monkeypatch.setattr(settings, "openai_api_key", None, raising=False)
    monkeypatch.setattr(settings, "web_search_enabled", True, raising=False)

    def fake_search(query: str) -> dict:
        return {
            "found": True,
            "answer": "O dolar comercial fechou em 5,00 na simulacao de teste.",
            "source": "https://example.com/cotacao",
            "confidence": 0.9,
        }

    monkeypatch.setattr(orchestrator.web_search_service, "search", fake_search)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.post(
            "/api/chat/message",
            json={"message": "Qual a cotacao do dolar hoje?"},
            headers=headers,
        )

        assert response.status_code == 200
        payload = response.json()
        assert "dolar comercial" in payload["content"].lower()
        assert "fonte:" in payload["content"].lower()

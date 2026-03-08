"""Coverage tests for expanded enterprise endpoints.

Focus: response envelope and basic functional behavior.
"""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import create_tables
from main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def _register_user(client: AsyncClient) -> str:
    create_tables()
    email = f"exp_{uuid.uuid4().hex[:10]}@alici.ai"
    org_name = f"Expansion Org {uuid.uuid4().hex[:8]}"

    response = await client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "StrongPass123!",
            "full_name": "Expansion User",
            "organization_name": org_name,
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.mark.anyio
async def test_expansion_models_tools_and_logs_contract():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        models = await client.get("/api/models", headers=headers)
        assert models.status_code == 200
        payload = models.json()
        assert payload["status"] == "success"
        assert payload["error"] is None

        tools = await client.get("/api/tools", headers=headers)
        assert tools.status_code == 200
        assert tools.json()["status"] == "success"

        run = await client.post(
            "/api/tools/run",
            json={"tool": "generate_document", "input": "doc test"},
            headers=headers,
        )
        assert run.status_code == 200
        assert run.json()["status"] == "success"

        logs = await client.get("/api/logs", headers=headers)
        assert logs.status_code == 200
        assert logs.json()["status"] == "success"


@pytest.mark.anyio
async def test_expansion_chat_lifecycle_contract():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        create = await client.post("/api/chat/create", json={"title": "Contrato"}, headers=headers)
        assert create.status_code == 200
        create_payload = create.json()
        assert create_payload["status"] == "success"
        conversation_id = create_payload["data"]["id"]

        rename = await client.patch(
            "/api/chat/rename",
            json={"conversation_id": conversation_id, "title": "Renomeada"},
            headers=headers,
        )
        assert rename.status_code == 200
        assert rename.json()["status"] == "success"

        pin = await client.patch(
            "/api/chat/pin",
            json={"conversation_id": conversation_id, "pinned": True},
            headers=headers,
        )
        assert pin.status_code == 200
        assert pin.json()["status"] == "success"

        history = await client.get("/api/chat/history", headers=headers)
        assert history.status_code == 200
        assert history.json()["status"] == "success"

        details = await client.get(f"/api/chat/{conversation_id}", headers=headers)
        assert details.status_code == 200
        assert details.json()["status"] == "success"

        deleted = await client.delete(f"/api/chat/{conversation_id}", headers=headers)
        assert deleted.status_code == 200
        assert deleted.json()["status"] == "success"

"""Phase 2 and 3 contract tests for auth-protected routes."""

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_openapi_contains_phase2_phase3_paths():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json().get("paths", {})

    assert "/api/auth/register" in paths
    assert "/api/auth/login" in paths
    assert "/api/conversations" in paths
    assert "/api/user/password" in paths
    assert "/api/user/settings" in paths


@pytest.mark.anyio
async def test_user_endpoint_requires_authentication():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/user")

    assert response.status_code in (401, 403)


@pytest.mark.anyio
async def test_conversations_endpoint_requires_authentication():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/conversations")

    assert response.status_code in (401, 403)


@pytest.mark.anyio
async def test_integrations_endpoint_requires_authentication():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/integrations")

    assert response.status_code in (401, 403)


@pytest.mark.anyio
async def test_analytics_endpoint_requires_authentication():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/analytics")

    assert response.status_code in (401, 403)


@pytest.mark.anyio
async def test_knowledge_query_requires_authentication():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/knowledge/query", json={"query": "teste"})

    assert response.status_code in (401, 403)

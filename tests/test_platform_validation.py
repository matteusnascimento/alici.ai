"""Platform validation tests for core routes and API contract."""

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_landing_page_available():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


@pytest.mark.anyio
async def test_dashboard_page_available():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/dashboard")

    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


@pytest.mark.anyio
async def test_integrations_page_available():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/integrations")

    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


@pytest.mark.anyio
async def test_openapi_contains_core_platform_routes():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/openapi.json")

    assert response.status_code == 200
    payload = response.json()
    paths = payload.get("paths", {})

    assert "/api/chat/message" in paths
    assert "/api/auth/login" in paths
    assert "/api/conversations" in paths
    assert "/api/user" in paths
    assert "/api/user/settings" in paths
    assert "/api/user/memory" in paths
    assert "/api/billing/plans" in paths
    assert "/api/billing/subscription" in paths
    assert "/api/billing/webhook" in paths
    assert "/api/integrations" in paths
    assert "/api/knowledge/upload" in paths
    assert "/api/knowledge/query" in paths
    assert "/api/analytics" in paths
    assert "/api/agents/" in paths
    assert "/api/platform/overview" in paths
    assert "/api/chat/create" in paths
    assert "/api/chat/history" in paths
    assert "/api/chat/rename" in paths
    assert "/api/chat/pin" in paths
    assert "/api/models" in paths
    assert "/api/models/select" in paths
    assert "/api/models/train" in paths
    assert "/api/models/status" in paths
    assert "/api/tools" in paths
    assert "/api/tools/run" in paths
    assert "/api/integrations/list" in paths
    assert "/api/integrations/remove" in paths
    assert "/api/analytics/usage" in paths
    assert "/api/analytics/messages" in paths
    assert "/api/analytics/tokens" in paths
    assert "/api/billing/subscribe" in paths
    assert "/api/billing/cancel" in paths
    assert "/api/billing/history" in paths
    assert "/api/org/create" in paths
    assert "/api/org/invite" in paths
    assert "/api/org/members" in paths
    assert "/api/api-keys/create" in paths
    assert "/api/api-keys" in paths
    assert "/api/logs" in paths
    assert "/api/logs/errors" in paths
    assert "/api/files/upload" in paths
    assert "/api/files" in paths
    assert "/api/files/{file_id}" in paths
    assert "/api/voice/stt" in paths
    assert "/api/voice/tts" in paths
    assert "/api/vision/analyze" in paths
    assert "/api/vision/generate" in paths
    assert "/api/code/generate" in paths
    assert "/api/code/explain" in paths


@pytest.mark.anyio
async def test_protected_platform_endpoint_requires_authentication():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/platform/overview")

    assert response.status_code in (401, 403)

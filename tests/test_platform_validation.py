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
    assert "/api/agents/" in paths
    assert "/api/platform/overview" in paths


@pytest.mark.anyio
async def test_protected_platform_endpoint_requires_authentication():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/platform/overview")

    assert response.status_code in (401, 403)

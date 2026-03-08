"""Knowledge upload and query flow tests."""

import io
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
    email = f"kb_{uuid.uuid4().hex[:10]}@alici.ai"
    org_name = f"Knowledge Org {uuid.uuid4().hex[:8]}"

    response = await client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "StrongPass123!",
            "full_name": "Knowledge User",
            "organization_name": org_name,
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.mark.anyio
async def test_upload_txt_and_query_returns_references():
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        content = b"O restaurante Alameda abre as 8h e fecha as 22h todos os dias."
        files = {"file": ("restaurante.txt", io.BytesIO(content), "text/plain")}

        upload = await client.post("/api/knowledge/upload", files=files, headers=headers)
        assert upload.status_code == 200
        upload_payload = upload.json()
        assert upload_payload["file_type"] == "txt"
        assert upload_payload["total_chunks"] >= 1

        query = await client.post(
            "/api/knowledge/query",
            json={"query": "Que horas o restaurante abre?", "top_k": 3},
            headers=headers,
        )
        assert query.status_code == 200
        payload = query.json()
        assert payload["references"]
        assert "trechos relevantes" in payload["answer"].lower()


@pytest.mark.anyio
async def test_upload_csv_is_supported():
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        content = b"produto,preco\nCafe,9.90\nCha,7.50"
        files = {"file": ("tabela.csv", io.BytesIO(content), "text/csv")}

        upload = await client.post("/api/knowledge/upload", files=files, headers=headers)
        assert upload.status_code == 200
        assert upload.json()["file_type"] == "csv"


@pytest.mark.anyio
async def test_upload_rejects_unsupported_extension():
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        files = {"file": ("arquivo.exe", io.BytesIO(b"fake"), "application/octet-stream")}
        upload = await client.post("/api/knowledge/upload", files=files, headers=headers)

        assert upload.status_code == 400
        assert "unsupported file type" in upload.json()["detail"].lower()

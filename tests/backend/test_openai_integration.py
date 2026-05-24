import uuid

from fastapi.testclient import TestClient

from app.main import app


def test_openai_integration():
    unique = str(uuid.uuid4())[:8]

    with TestClient(app) as client:
        reg = client.post(
            "/api/auth/register",
            json={
                "name": "OpenAI Test",
                "username": f"openai_test_{unique}",
                "email": f"openai_{unique}@example.com",
                "phone": f"1199{unique[:4]}0000",
                "password": "Senha1234",
            },
        )

        assert reg.status_code == 200

        token = reg.json().get("access_token")
        assert token is not None

        headers = {"Authorization": f"Bearer {token}"}
        resp = client.post("/api/integrations/openai/test", headers=headers, json={})

        assert resp.status_code == 200

        data = resp.json()
        assert "status" in data
        assert "message" in data

        print("Integration OK:", data)

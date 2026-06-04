from app.core.config import settings


def test_admin_overview_rejects_non_owner(client, auth_headers):
    response = client.get("/api/admin/overview", headers=auth_headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "Administracao restrita ao owner/admin."


def test_admin_overview_allows_dev_owner(client):
    login = client.post(
        "/api/auth/login",
        json={"email": "dev@axi-platform.com", "password": "AXITestDev123!"},
    )
    assert login.status_code == 200
    assert login.json()["user"]["role"] == "owner"

    response = client.get(
        "/api/admin/overview",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "usuarios" in payload
    assert "billing" in payload
    assert "seguranca" in payload
    assert "auditoria" in payload


def test_admin_overview_allows_admin_role(client, auth_headers, monkeypatch):
    monkeypatch.setattr(settings, "admin_emails", ["ana@example.com"])

    response = client.get("/api/admin/overview", headers=auth_headers)

    assert response.status_code == 200
    assert "usuarios" in response.json()


def test_admin_owner_creates_company_and_blocks_duplicates(client):
    login = client.post(
        "/api/auth/login",
        json={"email": "dev@axi-platform.com", "password": "AXITestDev123!"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    payload = {
        "nome": "Hotel Vista Azul",
        "razao_social": "Hotel Vista Azul LTDA",
        "cnpj": "12.345.678/0001-99",
        "email": "admin@hotelvistaazul.com.br",
        "telefone": "(47) 99999-9999",
        "plano": "pro",
        "modules": ["Revenue", "Chats", "AXI Assistant"],
    }
    response = client.post("/api/admin/companies", json=payload, headers=headers)

    assert response.status_code == 201
    created = response.json()
    assert created["name"] == "Hotel Vista Azul"
    assert created["plan"] == "pro"
    assert created["users_count"] == 1

    companies = client.get("/api/admin/companies", headers=headers)
    assert companies.status_code == 200
    assert any(company["name"] == "Hotel Vista Azul" for company in companies.json())

    duplicate = client.post("/api/admin/companies", json=payload, headers=headers)
    assert duplicate.status_code == 409

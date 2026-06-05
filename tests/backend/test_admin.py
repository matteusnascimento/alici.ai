from app.core.config import settings


def _owner_headers(client):
    login = client.post(
        "/api/auth/login",
        json={"email": "dev@axi-platform.com", "password": "AXITestDev123!"},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


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


def test_admin_users_rejects_member_and_allows_owner_admin(client, auth_headers, monkeypatch):
    member_response = client.get("/api/admin/users", headers=auth_headers)
    assert member_response.status_code == 403

    owner_response = client.get("/api/admin/users", headers=_owner_headers(client))
    assert owner_response.status_code == 200

    monkeypatch.setattr(settings, "admin_emails", ["ana@example.com"])
    admin_response = client.get("/api/admin/users", headers=auth_headers)
    assert admin_response.status_code == 200


def test_admin_owner_creates_company_and_blocks_duplicates(client):
    headers = _owner_headers(client)

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


def test_admin_invite_creates_user_and_returns_email_warning(client):
    headers = _owner_headers(client)
    response = client.post(
        "/api/admin/users/invite",
        json={
            "name": "Joao Santos",
            "email": "joao@pousadamaresol.com.br",
            "job_title": "Atendimento",
            "permissions": {"revenue": "read", "chats": "write"},
        },
        headers=headers,
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["email_delivery"] == "unavailable"
    assert payload["message"] == "Convite criado, mas envio de email indisponivel."
    assert payload["user"]["email"] == "joao@pousadamaresol.com.br"
    assert payload["user"]["status"] == "pending"
    assert payload["user"]["permissions"]["chats"] == "write"

    users = client.get("/api/admin/users", headers=headers)
    assert users.status_code == 200
    assert any(user["email"] == "joao@pousadamaresol.com.br" for user in users.json())


def test_admin_permissions_save_correctly(client):
    headers = _owner_headers(client)
    invited = client.post(
        "/api/admin/users/invite",
        json={
            "name": "Maria Oliveira",
            "email": "maria@pousadamaresol.com.br",
            "permissions": {"revenue": "read"},
        },
        headers=headers,
    )
    user_id = invited.json()["user"]["id"]

    response = client.put(
        f"/api/admin/users/{user_id}/permissions",
        json={"permissions": {"revenue": "admin", "chats": "write", "marketing": "read"}},
        headers=headers,
    )

    assert response.status_code == 200
    permissions = response.json()["permissions"]
    assert permissions["revenue"] == "admin"
    assert permissions["chats"] == "write"
    assert permissions["marketing"] == "read"
    assert permissions["studio"] == "none"

    persisted = client.get(f"/api/admin/users/{user_id}/permissions", headers=headers)
    assert persisted.status_code == 200
    assert persisted.json()["permissions"]["revenue"] == "admin"


def test_admin_audit_records_events(client):
    headers = _owner_headers(client)
    client.post(
        "/api/admin/users/invite",
        json={
            "name": "Mateus Nascimento",
            "email": "mateus@pousadamaresol.com.br",
            "permissions": {"assistant": "read"},
        },
        headers=headers,
    )

    response = client.get("/api/admin/audit", headers=headers)

    assert response.status_code == 200
    actions = [event["acao"] for event in response.json()["events"]]
    assert "usuario_convidado" in actions

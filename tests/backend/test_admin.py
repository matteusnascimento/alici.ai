def test_admin_overview_rejects_non_owner(client, auth_headers):
    response = client.get("/api/admin/overview", headers=auth_headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "Administracao restrita ao owner."


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

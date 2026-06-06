def test_marketing_operations_endpoints_return_real_empty_states(client, auth_headers):
    overview = client.get("/api/marketing/overview", headers=auth_headers)
    assert overview.status_code == 200
    assert overview.json()["status"] == "empty"
    assert overview.json()["projects_count"] == 0

    kpis = client.get("/api/marketing/kpis", headers=auth_headers)
    assert kpis.status_code == 200
    assert all(item["status"] == "empty" for item in kpis.json())

    funnel = client.get("/api/marketing/funnel", headers=auth_headers)
    assert funnel.status_code == 200
    assert funnel.json()["stages"] == []


def test_marketing_campaigns_reuses_real_projects(client, auth_headers):
    project = client.post(
        "/api/marketing/projects",
        headers=auth_headers,
        json={
            "name": "Campanha real",
            "audience": "Casais",
            "objective": "Aumentar reservas",
            "offer": "Pacote direto",
            "tone": "premium",
            "channels": "Meta Ads, Google Ads",
            "budget": 1500,
        },
    )
    assert project.status_code == 200

    campaigns = client.get("/api/marketing/campaigns", headers=auth_headers)
    assert campaigns.status_code == 200
    payload = campaigns.json()
    assert payload["status"] == "partial"
    assert payload["campaigns"][0]["name"] == "Campanha real"
    assert payload["campaigns"][0]["source"] == "marketing_projects"
    assert payload["campaigns"][0]["channels"] == "Meta Ads, Google Ads"

    publish = client.post(
        f"/api/marketing/campaigns/{project.json()['id']}/publish",
        headers=auth_headers,
        json={"channels": ["Meta Ads"]},
    )
    assert publish.status_code == 424
    assert "missing_providers" in publish.json()["detail"]

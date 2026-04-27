from app.services.ai_service import AIService, AIServiceError


def test_marketing_copy_returns_ai_error_when_rate_limited(client, auth_headers, monkeypatch):
    def _raise_rate_limit(self, **kwargs):
        raise AIServiceError("OpenAI rate limit reached", user_message="rate", status_code=429, code="rate_limit")

    monkeypatch.setattr(AIService, "generate_text", _raise_rate_limit)

    response = client.post("/api/marketing/generate-copy", headers=auth_headers, json={"prompt": "Lancamento premium"})

    assert response.status_code == 429
    assert response.json()["detail"] == "rate"


def test_marketing_campaign_returns_ai_error_when_rate_limited(client, auth_headers, monkeypatch):
    def _raise_rate_limit(self, **kwargs):
        raise AIServiceError("OpenAI rate limit reached", user_message="rate", status_code=429, code="rate_limit")

    monkeypatch.setattr(AIService, "generate_structured_output", _raise_rate_limit)

    response = client.post(
        "/api/marketing/campaign",
        headers=auth_headers,
        json={
            "company_name": "Alici",
            "audience": "Hoteis",
            "objective": "Gerar reservas",
            "offer": "Automacao comercial",
            "tone": "premium",
        },
    )

    assert response.status_code == 429
    assert response.json()["detail"] == "rate"


def test_marketing_generate_content_matches_frontend_contract(client, auth_headers, monkeypatch):
    def _fake_structured_output(self, **kwargs):
        return {
            "copies": ["Copy principal", "Variacao curta"],
            "cta": "Fale com a equipe",
            "hook": "Gancho comercial",
            "hashtags": ["#marketing", "#vendas"],
        }

    monkeypatch.setattr(AIService, "generate_structured_output", _fake_structured_output)

    project_response = client.post(
        "/api/marketing/projects",
        headers=auth_headers,
        json={
            "name": "Alici",
            "audience": "Hoteis",
            "objective": "Gerar reservas",
            "offer": "Automacao comercial",
            "tone": "premium",
        },
    )
    assert project_response.status_code == 200

    response = client.post(
        "/api/marketing/generate-content",
        headers=auth_headers,
        json={
            "project_id": project_response.json()["id"],
            "context": "Campanha de baixa temporada",
            "type": "social_post",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["copies"] == ["Copy principal", "Variacao curta"]
    assert body["cta"] == "Fale com a equipe"
    assert body["hook"] == "Gancho comercial"
    assert body["hashtags"] == ["#marketing", "#vendas"]


def test_studio_caption_generate_returns_ai_error_when_rate_limited(client, auth_headers, monkeypatch):
    def _raise_rate_limit(self, **kwargs):
        raise AIServiceError("OpenAI rate limit reached", user_message="rate", status_code=429, code="rate_limit")

    monkeypatch.setattr(AIService, "generate_structured_output", _raise_rate_limit)

    response = client.post(
        "/api/studio/caption/generate",
        headers=auth_headers,
        json={
            "campaign_context": "Campanha de reativacao",
            "channel": "instagram",
            "tone": "direto",
            "include_cta": True,
            "include_hashtags": True,
            "variations": 3,
        },
    )

    assert response.status_code == 429
    assert response.json()["detail"] == "rate"

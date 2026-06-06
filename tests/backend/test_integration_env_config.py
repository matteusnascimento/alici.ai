from urllib.parse import parse_qs, urlparse

from app.core.config import settings
from app.models.integration_account import IntegrationAccount
from app.models.user import User


def _set_meta(monkeypatch, *, configured: bool) -> None:
    monkeypatch.setattr(settings, "meta_client_id", "meta-client" if configured else "")
    monkeypatch.setattr(settings, "meta_client_secret", "meta-secret" if configured else "")
    monkeypatch.setattr(settings, "meta_oauth_client_id", "")
    monkeypatch.setattr(settings, "meta_app_secret", "")
    monkeypatch.setattr(settings, "meta_oauth_redirect_uri", "")
    monkeypatch.setattr(
        settings,
        "meta_redirect_uri",
        "http://127.0.0.1:8000/api/integrations/meta/callback" if configured else "",
    )
    monkeypatch.setattr(settings, "meta_oauth_scopes", "instagram_basic,ads_read" if configured else "")
    monkeypatch.setattr(settings, "app_secret_key", "test-app-secret" if configured else "")
    monkeypatch.setattr(settings, "secret_key", "test-secret-key")


def _set_google(monkeypatch, *, configured: bool) -> None:
    monkeypatch.setattr(settings, "google_client_id", "google-client" if configured else "")
    monkeypatch.setattr(settings, "google_client_secret", "google-secret" if configured else "")
    monkeypatch.setattr(settings, "google_oauth_client_id", "")
    monkeypatch.setattr(settings, "google_oauth_client_secret", "")
    monkeypatch.setattr(settings, "google_oauth_redirect_uri", "")
    monkeypatch.setattr(
        settings,
        "google_redirect_uri",
        "http://127.0.0.1:8000/api/integrations/google/callback" if configured else "",
    )
    monkeypatch.setattr(settings, "google_oauth_scopes", "https://www.googleapis.com/auth/adwords" if configured else "")
    monkeypatch.setattr(settings, "app_secret_key", "test-app-secret" if configured else "")
    monkeypatch.setattr(settings, "secret_key", "test-secret-key")


def test_meta_connect_without_env_returns_503(client, auth_headers, monkeypatch):
    _set_meta(monkeypatch, configured=False)

    response = client.get("/api/integrations/meta/connect?provider=whatsapp", headers=auth_headers)

    assert response.status_code == 503
    assert "Integração Meta não configurada" in response.json()["detail"]


def test_meta_connect_with_env_returns_authorization_url(client, auth_headers, monkeypatch):
    _set_meta(monkeypatch, configured=True)

    response = client.get("/api/integrations/meta/connect?provider=instagram", headers=auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "instagram"
    assert payload["authorization_url"].startswith("https://www.facebook.com/v20.0/dialog/oauth?")
    assert "client_id=meta-client" in payload["authorization_url"]
    state = parse_qs(urlparse(payload["authorization_url"]).query)["state"][0]

    from app.api.routes.integrations import _parse_state

    parsed = _parse_state(state, "meta")
    assert parsed["provider"] == "instagram"
    assert parsed["user_id"].isdigit()
    assert parsed["company_id"].startswith("axi-")
    assert parsed["nonce"]
    assert int(parsed["expires_at"]) > int(parsed["created_at"])


def test_meta_connect_production_requires_company(client, auth_headers, monkeypatch):
    _set_meta(monkeypatch, configured=True)
    monkeypatch.setattr(settings, "app_env", "production")

    response = client.get("/api/integrations/meta/connect?provider=whatsapp", headers=auth_headers)

    assert response.status_code == 422
    assert "empresa ativa" in response.json()["detail"].lower()


def test_meta_connect_state_uses_active_company(client, auth_headers, db_session, monkeypatch):
    _set_meta(monkeypatch, configured=True)
    user = db_session.query(User).filter(User.email == "ana@example.com").first()
    user.company = "Pousada Passargada"
    db_session.commit()

    response = client.get("/api/integrations/meta/connect?provider=whatsapp", headers=auth_headers)

    assert response.status_code == 200
    state = parse_qs(urlparse(response.json()["authorization_url"]).query)["state"][0]

    from app.api.routes.integrations import _parse_state

    parsed = _parse_state(state, "meta")
    assert parsed["company_id"] == "pousada-passargada"
    assert parsed["company_name"] == "Pousada Passargada"


def test_meta_callback_persists_tenant_metadata(client, auth_headers, db_session, monkeypatch):
    _set_meta(monkeypatch, configured=True)
    user = db_session.query(User).filter(User.email == "ana@example.com").first()
    user.company = "Pousada Passargada"
    db_session.commit()

    from app.api.routes import integrations as integrations_routes

    state = integrations_routes._build_state(user, "instagram", "meta")

    class _FakeResponse:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    class _FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def get(self, url, params=None, headers=None):
            if url.endswith("/oauth/access_token"):
                return _FakeResponse({"access_token": "provider-token", "expires_in": 3600})
            if url.endswith("/me"):
                return _FakeResponse({"id": "ig-123", "name": "Pousada Passargada IG"})
            raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr(integrations_routes.httpx, "Client", _FakeClient)

    response = client.get(f"/api/integrations/meta/callback?code=valid-code&state={state}", follow_redirects=False)

    assert response.status_code == 303
    account = db_session.query(IntegrationAccount).filter(IntegrationAccount.provider == "instagram").first()
    assert account is not None
    metadata = integrations_routes.ChannelIntegrationService(db_session)._load_json(account.metadata_json)
    assert metadata["tenant"]["company_id"] == "pousada-passargada"
    assert metadata["tenant"]["company_name"] == "Pousada Passargada"


def test_meta_connect_invalid_provider_returns_400(client, auth_headers, monkeypatch):
    _set_meta(monkeypatch, configured=True)

    response = client.get("/api/integrations/meta/connect?provider=linkedin", headers=auth_headers)

    assert response.status_code == 400


def test_google_connect_without_env_returns_503(client, auth_headers, monkeypatch):
    _set_google(monkeypatch, configured=False)

    response = client.get("/api/integrations/google/connect?provider=google_ads", headers=auth_headers)

    assert response.status_code == 503
    assert "Integração Google não configurada" in response.json()["detail"]


def test_google_connect_with_env_returns_authorization_url(client, auth_headers, monkeypatch):
    _set_google(monkeypatch, configured=True)

    response = client.get("/api/integrations/google/connect?provider=google_analytics", headers=auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "google_analytics"
    assert payload["authorization_url"].startswith("https://accounts.google.com/o/oauth2/v2/auth?")
    assert "client_id=google-client" in payload["authorization_url"]


def test_google_connect_invalid_provider_returns_400(client, auth_headers, monkeypatch):
    _set_google(monkeypatch, configured=True)

    response = client.get("/api/integrations/google/connect?provider=youtube", headers=auth_headers)

    assert response.status_code == 400


def test_website_widget_without_public_urls_returns_503(client, auth_headers, monkeypatch):
    monkeypatch.setattr(settings, "public_backend_url", "")
    monkeypatch.setattr(settings, "axi_tracker_public_url", "")
    monkeypatch.setattr(settings, "axi_widget_public_url", "")

    response = client.get("/api/integrations/website-chat/widget-script", headers=auth_headers)

    assert response.status_code == 503
    assert "Website Tracker não configurado" in response.json()["detail"]


def test_website_widget_with_public_urls_returns_script(client, auth_headers, monkeypatch):
    monkeypatch.setattr(settings, "public_backend_url", "http://127.0.0.1:8000")
    monkeypatch.setattr(settings, "axi_tracker_public_url", "http://127.0.0.1:8000/api/tracker/script.js")
    monkeypatch.setattr(settings, "axi_widget_public_url", "http://127.0.0.1:8000/static/axi-widget.js")

    response = client.get("/api/integrations/website-chat/widget-script", headers=auth_headers)

    assert response.status_code == 200
    script = response.json()["script"]
    assert "data-axi-endpoint=\"http://127.0.0.1:8000/api/tracker/events\"" in script
    assert "axi-widget.js" in script


def test_studio_provider_without_key_returns_503(client, auth_headers, monkeypatch):
    monkeypatch.setattr(settings, "removebg_api_key", "")

    response = client.post(
        "/api/studio/image/remove-background",
        headers=auth_headers,
        json={"asset_url": "https://example.com/image.png", "options": {}},
    )

    assert response.status_code == 503
    assert "Provider Remove.bg não configurado" in response.json()["detail"]


def test_assistant_without_ai_provider_key_returns_503(client, auth_headers, monkeypatch):
    monkeypatch.setattr(settings, "default_ai_provider", "openai")
    monkeypatch.setattr(settings, "openai_api_key", "")
    monkeypatch.setattr(settings, "openai_api_key_rotated", "")
    monkeypatch.setattr(settings, "groq_api_key", "")
    monkeypatch.setattr(settings, "gemini_api_key", "")
    monkeypatch.setattr(settings, "ollama_enabled", False)

    response = client.post(
        "/api/ai/platform-assistant",
        headers=auth_headers,
        json={"prompt": "Analise minha receita."},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "Provider de IA não configurado."

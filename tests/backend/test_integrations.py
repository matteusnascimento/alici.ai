def test_integrations_endpoints(client, auth_headers, monkeypatch):
    from app.core.config import settings

    for attr in (
        "meta_app_id",
        "meta_client_id",
        "meta_oauth_client_id",
        "meta_app_secret",
        "meta_client_secret",
        "google_client_id",
        "google_oauth_client_id",
        "google_client_secret",
        "google_oauth_client_secret",
    ):
        monkeypatch.setattr(settings, attr, "")

    list_response = client.get('/api/integrations', headers=auth_headers)
    assert list_response.status_code == 200
    providers = {item['provider'] for item in list_response.json()}
    assert providers == {'whatsapp', 'instagram'}

    whatsapp_card = next(item for item in list_response.json() if item['provider'] == 'whatsapp')
    assert whatsapp_card['status'] == 'disconnected'
    assert whatsapp_card['supports_activation'] is True

    create_response = client.post(
        '/api/integrations',
        headers=auth_headers,
        json={
            'provider': 'whatsapp',
            'external_account_id': 'waba-123',
            'external_account_name': 'Conta Comercial AXI',
            'access_token': 'meta-token',
            'metadata': {'source': 'test-suite'},
        },
    )
    assert create_response.status_code == 200
    assert create_response.json()['status'] == 'pending_setup'

    provider_status = client.get('/api/integrations/whatsapp/status', headers=auth_headers)
    assert provider_status.status_code == 200
    assert provider_status.json()['connected_accounts'] == 1
    assert provider_status.json()['status'] == 'pending_setup'

    openai_test_response = client.post('/api/integrations/openai/test', headers=auth_headers, json={})
    assert openai_test_response.status_code == 200
    assert openai_test_response.json()['provider'] == 'openai'

    whatsapp_response = client.post('/api/integrations/whatsapp/test', headers=auth_headers, json={})
    assert whatsapp_response.status_code == 200
    assert whatsapp_response.json()['status'] == 'pending_setup'

    instagram_response = client.post('/api/integrations/instagram/test', headers=auth_headers, json={})
    assert instagram_response.status_code == 200
    assert instagram_response.json()['status'] == 'disconnected'

    disconnect_response = client.post('/api/integrations/whatsapp/disconnect', headers=auth_headers)
    assert disconnect_response.status_code == 200
    assert disconnect_response.json()['status'] == 'disconnected'


def test_meta_webhook_verification_challenge(client, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "meta_webhook_verify_token", "axi_meta_webhook_2026_9f4d2a7c")

    response = client.get(
        "/api/integrations/meta/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "axi_meta_webhook_2026_9f4d2a7c",
            "hub.challenge": "123456",
        },
    )
    assert response.status_code == 200
    assert response.text == "123456"

    invalid = client.get(
        "/api/integrations/meta/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong",
            "hub.challenge": "123456",
        },
    )
    assert invalid.status_code == 403

from app.services.openai_service import OpenAIService


def test_dashboard_stats(client, auth_headers):
    client.post('/api/chat/send', headers=auth_headers, json={'text': 'Mensagem 1'})
    client.post(
        '/api/agents',
        headers=auth_headers,
        json={
            'nome': 'Closer IA',
            'funcao': 'Vendas inbound',
            'tipo': 'sales',
            'linguagem': 'pt-BR',
            'prompt': 'Conduzir leads até a proposta.',
            'ativo': True,
        },
    )

    response = client.get('/api/dashboard/stats', headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body['total_messages'] >= 2
    assert body['total_agents'] == 1
    assert len(body['usage_bars']) == 7

    overview_response = client.get('/api/dashboard/overview', headers=auth_headers)
    assert overview_response.status_code == 200
    assert overview_response.json()['total_agents'] == 1

    usage_response = client.get('/api/dashboard/usage', headers=auth_headers)
    assert usage_response.status_code == 200
    assert usage_response.json()['messages_limit'] >= 500

    metrics_response = client.get('/api/dashboard/metrics', headers=auth_headers)
    assert metrics_response.status_code == 200
    assert len(metrics_response.json()['items']) >= 4


def test_dashboard_ai_health(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        OpenAIService,
        'healthcheck',
        lambda self: {
            'status': 'error',
            'model': 'gpt-4o-mini',
            'error_type': 'rate_limit',
            'status_code': 429,
            'latency_ms': 321.5,
            'message': 'OpenAI rate limit reached',
        },
    )

    response = client.get('/api/dashboard/ai-health', headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body['provider'] == 'openai'
    assert body['status'] == 'error'
    assert body['error_type'] == 'rate_limit'
    assert body['status_code'] == 429


def test_dashboard_ai_metrics(client, auth_headers):
    response = client.get('/api/dashboard/ai-metrics?window=7d', headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body['window'] == '7d'
    assert 'total_requests' in body
    assert 'rate_limit_429' in body
    assert isinstance(body['trend'], list)
    assert isinstance(body['trend_429'], list)
    assert len(body['trend']) == 7

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

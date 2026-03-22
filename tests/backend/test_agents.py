def test_create_and_list_agents(client, auth_headers):
    create_response = client.post(
        '/api/agents',
        headers=auth_headers,
        json={
            'nome': 'Closer IA',
            'funcao': 'Vendas inbound',
            'tipo': 'sales',
            'linguagem': 'pt-BR',
            'prompt': 'Conduzir leads até a proposta.',
            'whatsapp': '11999999999',
            'instagram': '@axi',
            'api': 'https://api.example.com',
            'outros': 'telegram',
            'outros_nome': 'Telegram',
            'ativo': True,
        },
    )

    assert create_response.status_code == 200
    assert create_response.json()['nome'] == 'Closer IA'

    list_response = client.get('/api/agents', headers=auth_headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    agent_id = create_response.json()['id']
    get_response = client.get(f'/api/agents/{agent_id}', headers=auth_headers)
    assert get_response.status_code == 200

    patch_response = client.patch(
        f'/api/agents/{agent_id}',
        headers=auth_headers,
        json={
            'nome': 'Closer IA V2',
            'funcao': 'Vendas outbound',
            'tipo': 'sales',
            'linguagem': 'pt-BR',
            'prompt': 'Atualizar fluxo de venda.',
            'ativo': True,
        },
    )
    assert patch_response.status_code == 200
    assert patch_response.json()['nome'] == 'Closer IA V2'

    delete_response = client.delete(f'/api/agents/{agent_id}', headers=auth_headers)
    assert delete_response.status_code == 204

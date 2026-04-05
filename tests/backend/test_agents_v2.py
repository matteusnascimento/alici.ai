def _create_agent(client, auth_headers):
    response = client.post(
        '/api/agents/create',
        headers=auth_headers,
        json={
            'nome': 'Agente Ops',
            'funcao': 'Atendimento',
            'tipo': 'atendimento',
            'linguagem': 'pt-BR',
            'prompt': 'Responder clientes com contexto de negocio.',
            'ativo': False,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert 'agent' in body
    assert 'setup' in body
    assert body['setup']['progress_percent'] == 0
    return body['agent']['id']


def test_create_agent_full_payload_and_overview_fetch(client, auth_headers):
    response = client.post(
        '/api/agents',
        headers=auth_headers,
        json={
            'nome': 'AXI Reservas',
            'funcao': 'Reservas',
            'tipo': 'reservas',
            'linguagem': 'pt-BR',
            'tone': 'Consultivo',
            'objectives': ['Responder clientes', 'Fechar reservas'],
            'prompt': 'Atender reservas e confirmar dados do cliente.',
            'ativo': False,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body['id'], int)
    assert body['nome'] == 'AXI Reservas'

    overview = client.get(f"/api/agents/{body['id']}/overview", headers=auth_headers)
    assert overview.status_code == 200
    assert overview.json()['agent']['id'] == body['id']


def test_create_agent_validates_required_fields(client, auth_headers):
    response = client.post(
        '/api/agents',
        headers=auth_headers,
        json={
            'nome': '',
            'funcao': 'Atendimento',
            'tipo': 'atendimento',
        },
    )
    assert response.status_code == 422


def test_create_route_rejects_wrong_method(client, auth_headers):
    response = client.patch('/api/agents', headers=auth_headers, json={})
    assert response.status_code == 405


def test_agent_activation_and_pause_flow(client, auth_headers):
    agent_id = _create_agent(client, auth_headers)

    blocked_activate = client.post(f'/api/agents/{agent_id}/activate', headers=auth_headers)
    assert blocked_activate.status_code == 422
    detail = blocked_activate.json()['detail']
    assert detail['code'] == 'activation_blocked'
    assert len(detail['validation_errors']) >= 1

    pause = client.post(f'/api/agents/{agent_id}/pause', headers=auth_headers)
    assert pause.status_code == 200
    assert pause.json()['ativo'] is False


def test_agent_knowledge_actions_test_and_logs(client, auth_headers):
    agent_id = _create_agent(client, auth_headers)

    setup_before = client.get(f'/api/agents/{agent_id}/setup-status', headers=auth_headers)
    assert setup_before.status_code == 200
    assert setup_before.json()['recommended_next_step']['key'] == 'channels_connected'

    knowledge = client.post(
        f'/api/agents/{agent_id}/knowledge/files',
        headers=auth_headers,
        json={
            'title': 'Politica de atendimento',
            'kind': 'documento',
            'content': 'Atender com cordialidade e objetividade.',
            'enabled': True,
        },
    )
    assert knowledge.status_code == 200

    action = client.post(
        f'/api/agents/{agent_id}/actions',
        headers=auth_headers,
        json={
            'name': 'Capturar lead',
            'action_type': 'save_lead',
            'trigger_keywords': 'preco,orcamento',
            'enabled': True,
            'config': {},
        },
    )
    assert action.status_code == 200

    test_run = client.post(
        f'/api/agents/{agent_id}/test/run',
        headers=auth_headers,
        json={'text': 'Quero saber o preco', 'scenario': 'teste rapido', 'channel_type': 'api'},
    )
    assert test_run.status_code == 200
    assert 'response' in test_run.json()

    sessions = client.get(f'/api/agents/{agent_id}/test/sessions', headers=auth_headers)
    assert sessions.status_code == 200
    assert len(sessions.json()) >= 1

    logs = client.get(f'/api/agents/{agent_id}/logs', headers=auth_headers)
    assert logs.status_code == 200
    assert isinstance(logs.json(), list)

    analytics = client.get(f'/api/agents/{agent_id}/analytics', headers=auth_headers)
    assert analytics.status_code == 200
    assert 'total_conversations' in analytics.json()

    setup_after = client.get(f'/api/agents/{agent_id}/setup-status', headers=auth_headers)
    assert setup_after.status_code == 200
    body = setup_after.json()
    assert body['progress_percent'] >= 80
    assert body['activation_ready'] is True

    readiness = client.get(f'/api/agents/{agent_id}/readiness', headers=auth_headers)
    assert readiness.status_code == 200
    assert readiness.json()['activation_ready'] is True

    activate = client.post(f'/api/agents/{agent_id}/activate', headers=auth_headers)
    assert activate.status_code == 200
    assert activate.json()['ativo'] is True

    pause = client.post(f'/api/agents/{agent_id}/pause', headers=auth_headers)
    assert pause.status_code == 200
    assert pause.json()['ativo'] is False


def test_agent_settings_and_overview(client, auth_headers):
    agent_id = _create_agent(client, auth_headers)

    save_settings = client.put(
        f'/api/agents/{agent_id}/settings',
        headers=auth_headers,
        json={
            'basic': {
                'name': 'Agente Operacional',
                'role': 'Atendimento',
                'language': 'pt-BR',
                'tone': 'Consultivo',
                'working_hours': '08:00-18:00',
                'active': False,
                'fallback_to_human': True,
            },
            'advanced': {
                'instrucoes_principais_do_agente': 'Sempre confirmar dados do cliente.',
                'modelo': 'gpt-4.1-mini',
                'temperature': '0.2',
                'opcoes_avancadas': {'debug': False},
            },
        },
    )
    assert save_settings.status_code == 200

    get_settings = client.get(f'/api/agents/{agent_id}/settings', headers=auth_headers)
    assert get_settings.status_code == 200
    assert get_settings.json()['basic']['name'] == 'Agente Operacional'

    overview = client.get(f'/api/agents/{agent_id}/overview', headers=auth_headers)
    assert overview.status_code == 200
    assert 'kpis' in overview.json()
    assert 'setup' in overview.json()

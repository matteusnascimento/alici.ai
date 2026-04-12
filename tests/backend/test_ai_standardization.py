import pytest

from app.core.config import settings
from app.services.ai_service import AIConfigurationError, AIService, AIServiceError


def test_ai_service_uses_env_defaults(monkeypatch):
    monkeypatch.setattr(settings, 'default_ai_provider', 'openai', raising=False)
    monkeypatch.setattr(settings, 'openai_api_key', 'test-key', raising=False)
    monkeypatch.setattr(settings, 'openai_model', 'gpt-4o-mini', raising=False)

    service = AIService()

    assert service.provider == 'openai'
    assert service.default_model == 'gpt-4o-mini'
    assert service.is_configured() is True


def test_ai_service_fails_safely_without_key(monkeypatch):
    monkeypatch.setattr(settings, 'default_ai_provider', 'openai', raising=False)
    monkeypatch.setattr(settings, 'openai_api_key', '', raising=False)

    service = AIService()

    with pytest.raises(AIConfigurationError) as exc:
        service.generate_text(user_prompt='oi')

    assert exc.value.user_message == 'A integracao de IA nao esta configurada.'


def test_openai_integration_test_route_works(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        AIService,
        'healthcheck',
        lambda self: {
            'provider': 'openai',
            'status': 'ok',
            'model': 'gpt-4o-mini',
            'message': 'OK',
        },
    )

    response = client.get('/api/integrations/openai/test', headers=auth_headers)

    assert response.status_code == 200
    assert response.json()['provider'] == 'openai'
    assert response.json()['status'] == 'ok'
    assert response.json()['model'] == 'gpt-4o-mini'


def test_chat_route_uses_ai_service(client, auth_headers, monkeypatch):
    monkeypatch.setattr(AIService, 'generate_text', lambda self, **kwargs: 'Resposta centralizada da IA')

    response = client.post('/api/chat/send', headers=auth_headers, json={'text': 'Quero ajuda com chat'})

    assert response.status_code == 200
    assert response.json()['assistant_message']['text'] == 'Resposta centralizada da IA'


def test_agent_test_route_uses_ai_service(client, auth_headers, monkeypatch):
    monkeypatch.setattr(AIService, 'generate_text', lambda self, **kwargs: 'Resposta do agente via OpenAI padrao')

    create_response = client.post(
        '/api/agents',
        headers=auth_headers,
        json={
            'nome': 'Agente IA',
            'funcao': 'Atendimento',
            'tipo': 'atendimento',
            'linguagem': 'pt-BR',
            'prompt': 'Responder com clareza',
            'ativo': False,
        },
    )
    agent_id = create_response.json()['id']

    response = client.post(
        f'/api/agents/{agent_id}/test',
        headers=auth_headers,
        json={'text': 'Olá', 'channel_type': 'api'},
    )

    assert response.status_code == 200
    assert response.json()['response'] == 'Resposta do agente via OpenAI padrao'


def test_studio_generation_route_uses_ai_service(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        AIService,
        'generate_structured_output',
        lambda self, **kwargs: {'result': ['Headline premium 1', 'Headline premium 2', 'Headline premium 3']},
    )

    response = client.post(
        '/api/studio/generate/headline',
        headers=auth_headers,
        json={'prompt': 'Lançamento SaaS premium', 'options': {}},
    )

    assert response.status_code == 200
    assert response.json()['result']['result'][0] == 'Headline premium 1'


def test_ai_test_route_returns_health_data(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        AIService,
        'healthcheck',
        lambda self: {
            'provider': 'openai',
            'status': 'ok',
            'model': 'gpt-4o-mini',
            'message': 'OK',
            'latency_ms': 10.2,
        },
    )

    response = client.post('/api/ai/test', headers=auth_headers)

    assert response.status_code == 200
    assert response.json()['status'] == 'ok'
    assert response.json()['model_used'] == 'gpt-4o-mini'


def test_chat_route_no_silent_fallback_on_ai_error(client, auth_headers, monkeypatch):
    def _raise_ai_error(self, **kwargs):
        raise AIServiceError(
            'OpenAI rate limit reached',
            user_message='Servico de IA temporariamente indisponivel. Tente novamente.',
            status_code=429,
            code='rate_limit',
        )

    monkeypatch.setattr(AIService, 'generate_text', _raise_ai_error)

    response = client.post('/api/chat/send', headers=auth_headers, json={'text': 'Quero ajuda com chat'})

    assert response.status_code == 429
    assert response.json()['detail'] == 'Servico de IA temporariamente indisponivel. Tente novamente.'

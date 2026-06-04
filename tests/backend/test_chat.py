from pathlib import Path

from app.core.database import SessionLocal
from app.models.agent import Agent
from app.models.agent_conversation import AgentConversation
from app.models.user import User
from app.services.ai_service import AIService, AIServiceError


def test_chat_send_and_messages(client, auth_headers):
    send_response = client.post('/api/chat/send', headers=auth_headers, json={'text': 'Quero ajuda com marketing'})

    assert send_response.status_code == 200
    body = send_response.json()
    conversation_id = body['conversation']['id']
    assert body['assistant_message']['text']

    list_response = client.get('/api/chat/conversations', headers=auth_headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    messages_response = client.get(f'/api/chat/conversations/{conversation_id}/messages', headers=auth_headers)
    assert messages_response.status_code == 200
    assert len(messages_response.json()) == 2

    send_v2_response = client.post('/api/chat', headers=auth_headers, json={'text': 'Segunda mensagem'})
    assert send_v2_response.status_code == 200

    usage_response = client.get('/api/billing/usage', headers=auth_headers)
    assert usage_response.status_code == 200
    messages_usage = next(item for item in usage_response.json()['items'] if item['metric'] == 'messages')
    assert messages_usage['used'] == 2

    history_response = client.get('/api/chat/history', headers=auth_headers)
    assert history_response.status_code == 200
    assert len(history_response.json()) >= 1

    upload_response = client.post(
        '/api/chat/upload',
        headers=auth_headers,
        files={'file': ('brief.txt', b'briefing de campanha', 'text/plain')},
    )
    assert upload_response.status_code == 200
    upload_body = upload_response.json()
    assert upload_body['filename'] == 'brief.txt'
    stored_file = Path(__file__).resolve().parents[2] / 'backend' / upload_body['file_url'].lstrip('/')
    try:
        assert stored_file.exists()
        assert stored_file.read_bytes() == b'briefing de campanha'
    finally:
        stored_file.unlink(missing_ok=True)


def test_chat_send_returns_ai_error_when_openai_rate_limited(client, auth_headers, monkeypatch):
    def _raise_rate_limit(self, **kwargs):
        raise AIServiceError('OpenAI rate limit reached', user_message='rate', status_code=429, code='rate_limit')

    monkeypatch.setattr(AIService, 'generate_text', _raise_rate_limit)

    send_response = client.post('/api/chat/send', headers=auth_headers, json={'text': 'Quero ajuda urgente'})

    assert send_response.status_code == 429
    assert send_response.json()['detail'] == 'rate'


def test_omnichannel_quick_actions_do_not_fake_external_success(client, auth_headers):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == 'ana@example.com').first()
        assert user is not None

        agent = Agent(
            user_id=user.id,
            nome='Atendimento',
            funcao='Comercial',
            tipo='sales',
            linguagem='pt-BR',
            prompt='Responder clientes.',
            ativo=True,
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)

        conversation = AgentConversation(
            agent_id=agent.id,
            channel_type='whatsapp',
            channel_id='wa-1',
            external_user_id='11999999999',
            external_conversation_id='conv-chat-1',
            status='active_ai',
            sales_stage='novo_lead',
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        conversation_id = conversation.id
    finally:
        db.close()

    transfer_response = client.post(f'/api/chats/conversations/{conversation_id}/transfer', headers=auth_headers)
    assert transfer_response.status_code == 200
    assert transfer_response.json()['status'] == 'awaiting_human'
    assert transfer_response.json()['ai_mode'] == 'humano'

    quote_response = client.post(f'/api/chats/conversations/{conversation_id}/quote', headers=auth_headers)
    assert quote_response.status_code == 503
    assert 'canal conectado' in quote_response.json()['detail'].lower()

    task_response = client.post(f'/api/chats/conversations/{conversation_id}/tasks', headers=auth_headers)
    assert task_response.status_code == 501
    assert 'tarefas' in task_response.json()['detail'].lower()

    empty_tag_response = client.post(f'/api/chats/conversations/{conversation_id}/tags', headers=auth_headers, json={'tag': ''})
    assert empty_tag_response.status_code == 422

    tag_response = client.post(f'/api/chats/conversations/{conversation_id}/tags', headers=auth_headers, json={'tag': 'follow_up'})
    assert tag_response.status_code == 501
    assert 'tags persistentes' in tag_response.json()['detail'].lower()

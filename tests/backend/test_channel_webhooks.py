import hashlib
import hmac
import json

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.agent import Agent
from app.models.channel_message import ChannelMessage


def _create_active_agent(client, auth_headers) -> int:
    response = client.post(
        '/api/agents/create',
        headers=auth_headers,
        json={
            'nome': 'Agente Canal',
            'funcao': 'Atendimento',
            'tipo': 'atendimento',
            'linguagem': 'pt-BR',
            'prompt': 'Responder clientes com objetividade.',
            'ativo': True,
        },
    )
    assert response.status_code == 200
    agent_id = response.json()['agent']['id']

    db = SessionLocal()
    try:
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        assert agent is not None
        agent.ativo = True
        db.commit()
    finally:
        db.close()

    return agent_id


def test_integrations_accounts_list_and_channel_log_flow(client, auth_headers, monkeypatch):
    agent_id = _create_active_agent(client, auth_headers)

    connect = client.post(
        f'/api/agents/{agent_id}/channels/connect',
        headers=auth_headers,
        json={
            'provider': 'whatsapp',
            'integration': {
                'external_account_id': 'waba-900',
                'external_account_name': 'Conta Canal AXI',
                'access_token': 'meta-token-valid',
            },
            'endpoint': {
                'external_channel_id': 'phone-id-900',
                'channel_name': 'WhatsApp Operacao',
                'phone_number_or_handle': '+55 11 99999-9000',
            },
        },
    )
    assert connect.status_code == 200

    accounts = client.get('/api/integrations/accounts', headers=auth_headers)
    assert accounts.status_code == 200
    rows = accounts.json()
    assert len(rows) == 1
    assert rows[0]['provider'] == 'whatsapp'
    assert rows[0]['external_account_name'] == 'Conta Canal AXI'

    monkeypatch.setattr(settings, 'meta_app_secret', 'meta-secret-test')
    monkeypatch.setattr(settings, 'meta_webhook_verify_token', 'verify-token-axi')

    handshake = client.get(
        '/api/webhooks/meta/whatsapp?hub.mode=subscribe&hub.verify_token=verify-token-axi&hub.challenge=12345'
    )
    assert handshake.status_code == 200
    assert handshake.text.strip('"') == '12345'

    payload = {
        'phone_number_id': 'phone-id-900',
        'from': '5511999990000',
        'text': 'Mensagem real webhook',
        'wamid': 'wamid-900',
    }
    raw_payload = json.dumps(payload).encode('utf-8')
    signature = hmac.new(b'meta-secret-test', raw_payload, hashlib.sha256).hexdigest()

    webhook = client.post(
        '/api/webhooks/meta/whatsapp',
        data=raw_payload,
        headers={
            **auth_headers,
            'content-type': 'application/json',
            'x-hub-signature-256': f'sha256={signature}',
        },
    )
    assert webhook.status_code == 200
    assert webhook.json()['ok'] is True

    db = SessionLocal()
    try:
        logs = db.query(ChannelMessage).all()
        assert len(logs) >= 1
        last = logs[-1]
        assert last.provider == 'whatsapp'
        assert last.direction == 'inbound'
        assert last.status in {'ok', 'processing'}
    finally:
        db.close()


def test_webhook_signature_validation_blocks_invalid_signature(client, auth_headers, monkeypatch):
    monkeypatch.setattr(settings, 'meta_app_secret', 'meta-secret-test')

    payload = {'phone_number_id': 'phone-x', 'from': '5511999990000', 'text': 'oi'}
    webhook = client.post(
        '/api/webhooks/meta/whatsapp',
        json=payload,
        headers={
            **auth_headers,
            'x-hub-signature-256': 'sha256=invalid',
        },
    )

    assert webhook.status_code == 401


def test_webhook_signature_secret_is_required(client, monkeypatch):
    monkeypatch.setattr(settings, 'meta_app_secret', '')

    webhook = client.post(
        '/api/webhooks/meta/whatsapp',
        json={'phone_number_id': 'phone-x', 'from': '5511999990000', 'text': 'oi'},
        headers={'x-hub-signature-256': 'sha256=anything'},
    )

    assert webhook.status_code == 503


def test_webhook_verify_token_is_required(client, monkeypatch):
    monkeypatch.setattr(settings, 'meta_webhook_verify_token', '')

    handshake = client.get(
        '/api/webhooks/meta/whatsapp?hub.mode=subscribe&hub.verify_token=verify-token-axi&hub.challenge=12345'
    )

    assert handshake.status_code == 503


def test_legacy_runtime_webhooks_are_disabled(client):
    whatsapp = client.post('/api/agents/runtime/webhooks/whatsapp', json={})
    instagram = client.post('/api/agents/runtime/webhooks/instagram', json={})

    assert whatsapp.status_code == 410
    assert instagram.status_code == 410

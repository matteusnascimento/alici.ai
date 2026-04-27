from types import SimpleNamespace

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models.subscription import Subscription
from app.models.usage_log import UsageLog
from app.models.user import User


class _FakeCheckoutSession:
    def __init__(self, session_id: str, url: str):
        self.id = session_id
        self.url = url


def _enable_fake_stripe_config():
    settings = get_settings()
    settings.stripe_secret_key = "sk_test_123"
    settings.stripe_webhook_secret = "whsec_123"
    settings.stripe_price_pro_monthly = "price_pro_m"
    settings.stripe_price_pro_yearly = "price_pro_y"
    settings.stripe_price_business_monthly = "price_b_m"
    settings.stripe_price_business_yearly = "price_b_y"
    settings.app_base_url = "http://localhost:5173"
    settings.stripe_success_url = "http://localhost:5173/app/billing/success?session_id={CHECKOUT_SESSION_ID}"
    settings.stripe_cancel_url = "http://localhost:5173/app/billing/cancel"


def _agent_payload(name: str) -> dict:
    return {
        "nome": name,
        "funcao": "Vendas",
        "tipo": "chatbot",
        "linguagem": "pt-BR",
        "prompt": "Você é um assistente comercial.",
    }


def test_billing_plan_and_upgrade_flow(client, auth_headers):
    plans_response = client.get('/api/billing/plans', headers=auth_headers)
    assert plans_response.status_code == 200
    plans = plans_response.json()
    assert any(item['id'] == 'free' for item in plans)
    assert any(item['id'] == 'pro' for item in plans)

    current_response = client.get('/api/billing/current', headers=auth_headers)
    assert current_response.status_code == 200
    assert current_response.json()['plan_id'] == 'free'

    upgrade_response = client.post(
        '/api/billing/upgrade',
        headers=auth_headers,
        json={'plan_id': 'pro', 'billing_cycle': 'monthly'},
    )
    assert upgrade_response.status_code == 403

    settings = get_settings()
    previous_admins = list(settings.billing_admin_emails)
    settings.billing_admin_emails = ['ana@example.com']
    try:
        admin_upgrade_response = client.post(
            '/api/billing/upgrade',
            headers=auth_headers,
            json={'plan_id': 'pro', 'billing_cycle': 'monthly'},
        )
        assert admin_upgrade_response.status_code == 200
        assert admin_upgrade_response.json()['subscription']['plan_id'] == 'pro'
    finally:
        settings.billing_admin_emails = previous_admins

    usage_response = client.get('/api/billing/usage', headers=auth_headers)
    assert usage_response.status_code == 200
    assert isinstance(usage_response.json()['items'], list)

    history_response = client.get('/api/billing/history', headers=auth_headers)
    assert history_response.status_code == 200
    assert len(history_response.json()['events']) >= 1


def test_billing_checkout_and_portal_real_endpoints(client, auth_headers, monkeypatch):
    _enable_fake_stripe_config()

    monkeypatch.setattr(
        'app.services.billing_service.stripe.checkout.Session.create',
        lambda **_: _FakeCheckoutSession('cs_test_123', 'https://checkout.stripe.com/pay/cs_test_123'),
    )
    monkeypatch.setattr(
        'app.services.billing_service.stripe.Customer.create',
        lambda **_: SimpleNamespace(id='cus_test_123'),
    )
    monkeypatch.setattr(
        'app.services.billing_service.stripe.billing_portal.Session.create',
        lambda **_: SimpleNamespace(url='https://billing.stripe.com/p/session_123'),
    )

    checkout_response = client.post(
        '/api/billing/checkout',
        headers=auth_headers,
        json={'plan_id': 'pro', 'billing_cycle': 'monthly'},
    )
    assert checkout_response.status_code == 200
    assert checkout_response.json()['session_id'] == 'cs_test_123'
    assert 'checkout.stripe.com' in checkout_response.json()['checkout_url']

    portal_response = client.post('/api/billing/portal', headers=auth_headers)
    assert portal_response.status_code == 200
    assert 'billing.stripe.com' in portal_response.json()['portal_url']


def test_billing_cancel_and_resume(client, auth_headers, monkeypatch):
    _enable_fake_stripe_config()
    monkeypatch.setattr('app.services.billing_service.stripe.Subscription.modify', lambda *_, **__: {'id': 'sub_test_123'})

    current_response = client.get('/api/billing/current', headers=auth_headers)
    assert current_response.status_code == 200

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == 'ana@example.com').first()
        subscription = db.query(Subscription).filter(Subscription.user_id == user.id).first()
        subscription.stripe_subscription_id = 'sub_test_123'
        subscription.stripe_customer_id = 'cus_test_123'
        db.commit()
    finally:
        db.close()

    cancel_response = client.post('/api/billing/cancel', headers=auth_headers)
    assert cancel_response.status_code == 200
    assert cancel_response.json()['subscription']['cancel_at_period_end'] is True

    resume_response = client.post('/api/billing/resume', headers=auth_headers)
    assert resume_response.status_code == 200
    assert resume_response.json()['subscription']['cancel_at_period_end'] is False


def test_billing_webhook_valid_and_invalid_signature(client, auth_headers, monkeypatch):
    _enable_fake_stripe_config()

    current_response = client.get('/api/billing/current', headers=auth_headers)
    assert current_response.status_code == 200

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == 'ana@example.com').first()
        user_id = user.id
    finally:
        db.close()

    event = {
        'id': 'evt_test_123',
        'type': 'checkout.session.completed',
        'data': {
            'object': {
                'id': 'cs_test_123',
                'customer': 'cus_test_123',
                'subscription': 'sub_test_123',
                'metadata': {'user_id': str(user_id), 'plan_id': 'pro'},
            }
        },
    }

    stripe_sub = {
        'id': 'sub_test_123',
        'status': 'active',
        'cancel_at_period_end': False,
        'current_period_start': 1712500000,
        'current_period_end': 1715100000,
        'metadata': {'plan_id': 'pro'},
        'items': {'data': [{'price': {'id': 'price_pro_m'}}]},
    }

    monkeypatch.setattr('app.services.billing_service.stripe.Webhook.construct_event', lambda *_: event)
    monkeypatch.setattr('app.services.billing_service.stripe.Subscription.retrieve', lambda *_: stripe_sub)

    ok_response = client.post(
        '/api/billing/webhook',
        data=b'{}',
        headers={'stripe-signature': 'valid-signature'},
    )
    assert ok_response.status_code == 200
    assert ok_response.json()['status'] == 'processed'

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == 'ana@example.com').first()
        subscription = db.query(Subscription).filter(Subscription.user_id == user.id).first()
        assert subscription.plan_id == 'pro'
        assert subscription.stripe_customer_id == 'cus_test_123'
    finally:
        db.close()

    def _raise_invalid_signature(*_):
        from stripe import SignatureVerificationError
        raise SignatureVerificationError('invalid', 'sig', 'payload')

    monkeypatch.setattr('app.services.billing_service.stripe.Webhook.construct_event', _raise_invalid_signature)
    invalid_response = client.post(
        '/api/billing/webhook',
        data=b'{}',
        headers={'stripe-signature': 'invalid-signature'},
    )
    assert invalid_response.status_code == 400


def test_billing_enforcement_messages_limit(client, auth_headers):
    current_response = client.get('/api/billing/current', headers=auth_headers)
    assert current_response.status_code == 200

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == 'ana@example.com').first()
        db.add(UsageLog(user_id=user.id, metric='messages', quantity=500, source='test'))
        db.commit()
    finally:
        db.close()

    send_response = client.post('/api/chat/send', headers=auth_headers, json={'text': 'Mensagem que excede limite'})
    assert send_response.status_code == 403


def test_billing_enforcement_agents_limit(client, auth_headers):
    first = client.post('/api/agents', headers=auth_headers, json=_agent_payload('Agente 1'))
    assert first.status_code == 200

    second = client.post('/api/agents', headers=auth_headers, json=_agent_payload('Agente 2'))
    assert second.status_code == 200

    third = client.post('/api/agents', headers=auth_headers, json=_agent_payload('Agente 3'))
    assert third.status_code == 403


def test_billing_health_endpoint(client):
    response = client.get('/api/billing/health')
    assert response.status_code == 200
    body = response.json()
    assert 'stripe_configured' in body
    assert 'prices_loaded' in body
    assert 'webhook_ready' in body
    assert isinstance(body['stripe_configured'], bool)
    assert isinstance(body['prices_loaded'], bool)
    assert isinstance(body['webhook_ready'], bool)

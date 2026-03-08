"""Billing webhook integration tests."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import create_tables
from main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def _register_user(client: AsyncClient) -> tuple[str, str]:
    create_tables()
    email = f"wh_{uuid.uuid4().hex[:10]}@alici.ai"
    org_name = f"Webhook Org {uuid.uuid4().hex[:8]}"

    register = await client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "StrongPass123!",
            "full_name": "Webhook User",
            "organization_name": org_name,
        },
    )
    assert register.status_code == 200

    token = register.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    user = await client.get("/api/user", headers=headers)
    assert user.status_code == 200
    organization_id = user.json()["organization_id"]
    return token, organization_id


@pytest.mark.anyio
async def test_webhook_checkout_completed_activates_subscription_plan():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token, organization_id = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        checkout = await client.post("/api/billing/checkout", json={"plan": "pro"}, headers=headers)
        assert checkout.status_code == 200
        checkout_payload = checkout.json()

        webhook_event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "object": "checkout.session",
                    "id": checkout_payload["checkout_id"],
                    "customer": "cus_test_webhook",
                    "subscription": "sub_test_webhook",
                    "metadata": {
                        "organization_id": organization_id,
                        "plan": "pro",
                    },
                }
            },
        }

        webhook = await client.post("/api/billing/webhook", json=webhook_event)
        assert webhook.status_code == 200
        assert webhook.json()["processed"] is True

        subscription = await client.get("/api/billing/subscription", headers=headers)
        assert subscription.status_code == 200
        payload = subscription.json()
        assert payload["status"] == "active"
        assert payload["plan"] == "pro"
        assert payload["organization_plan"] == "pro"


@pytest.mark.anyio
async def test_webhook_subscription_deleted_downgrades_to_free():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token, organization_id = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        checkout = await client.post("/api/billing/checkout", json={"plan": "pro"}, headers=headers)
        assert checkout.status_code == 200
        checkout_id = checkout.json()["checkout_id"]

        activate_event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "object": "checkout.session",
                    "id": checkout_id,
                    "customer": "cus_test_webhook2",
                    "subscription": "sub_test_webhook2",
                    "metadata": {
                        "organization_id": organization_id,
                        "plan": "pro",
                    },
                }
            },
        }
        activated = await client.post("/api/billing/webhook", json=activate_event)
        assert activated.status_code == 200
        assert activated.json()["processed"] is True

        deleted_event = {
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "object": "subscription",
                    "id": "sub_test_webhook2",
                    "customer": "cus_test_webhook2",
                    "metadata": {
                        "organization_id": organization_id,
                        "plan": "pro",
                    },
                }
            },
        }

        deleted = await client.post("/api/billing/webhook", json=deleted_event)
        assert deleted.status_code == 200
        assert deleted.json()["processed"] is True

        subscription = await client.get("/api/billing/subscription", headers=headers)
        assert subscription.status_code == 200
        payload = subscription.json()
        assert payload["status"] == "canceled"
        assert payload["plan"] == "free"
        assert payload["organization_plan"] == "free"
        assert payload["monthly_request_limit"] == 1000

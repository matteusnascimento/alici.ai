"""Billing subscription E2E tests for phase progression."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import create_tables
from main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def _register_user(client: AsyncClient) -> str:
    create_tables()
    email = f"billing_{uuid.uuid4().hex[:10]}@alici.ai"
    org_name = f"Billing Org {uuid.uuid4().hex[:8]}"

    response = await client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "StrongPass123!",
            "full_name": "Billing User",
            "organization_name": org_name,
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.mark.anyio
async def test_billing_plans_and_default_subscription_state():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        plans = await client.get("/api/billing/plans", headers=headers)
        assert plans.status_code == 200
        plans_payload = plans.json()
        assert plans_payload["current_plan"] == "free"
        assert "pro" in plans_payload["plans"]

        subscription = await client.get("/api/billing/subscription", headers=headers)
        assert subscription.status_code == 200
        sub_payload = subscription.json()
        assert sub_payload["plan"] == "free"
        assert sub_payload["organization_plan"] == "free"


@pytest.mark.anyio
async def test_billing_checkout_confirm_and_cancel_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await _register_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        checkout = await client.post(
            "/api/billing/checkout",
            json={"plan": "pro"},
            headers=headers,
        )
        assert checkout.status_code == 200
        checkout_payload = checkout.json()
        assert checkout_payload["plan"] == "pro"
        assert checkout_payload["checkout_id"]

        confirm = await client.post(
            "/api/billing/subscription/confirm",
            json={"checkout_id": checkout_payload["checkout_id"], "plan": "pro"},
            headers=headers,
        )
        assert confirm.status_code == 200

        active = await client.get("/api/billing/subscription", headers=headers)
        assert active.status_code == 200
        active_payload = active.json()
        assert active_payload["status"] == "active"
        assert active_payload["plan"] == "pro"
        assert active_payload["organization_plan"] == "pro"
        assert active_payload["monthly_request_limit"] == 10000

        cancel = await client.post(
            "/api/billing/subscription/cancel",
            json={"immediate": True},
            headers=headers,
        )
        assert cancel.status_code == 200

        free_state = await client.get("/api/billing/subscription", headers=headers)
        assert free_state.status_code == 200
        free_payload = free_state.json()
        assert free_payload["status"] == "canceled"
        assert free_payload["plan"] == "free"
        assert free_payload["organization_plan"] == "free"
        assert free_payload["monthly_request_limit"] == 1000

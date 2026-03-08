"""Billing and subscription lifecycle routes."""

import uuid
from datetime import datetime, timedelta, timezone
import json

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models import Organization, Subscription, User
from app.services.auth_service import AuthService
from app.services.billing_service import BillingService

router = APIRouter()

VALID_PLANS = {"free", "pro", "enterprise"}
PLAN_LIMITS = {
    "free": 1000,
    "pro": 10000,
    "enterprise": 1000000,
}


class CheckoutRequest(BaseModel):
    plan: str
    success_url: str | None = None
    cancel_url: str | None = None


class ConfirmCheckoutRequest(BaseModel):
    checkout_id: str
    plan: str


class CancelSubscriptionRequest(BaseModel):
    immediate: bool = True


def _ensure_plan(plan: str) -> str:
    normalized = (plan or "").strip().lower()
    if normalized not in VALID_PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")
    return normalized


def _apply_plan_to_organization(org: Organization, plan: str) -> None:
    org.plan = plan
    org.monthly_request_limit = PLAN_LIMITS[plan]


def _from_unix_timestamp(value: int | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromtimestamp(value, tz=timezone.utc)


def _activate_subscription(
    subscription: Subscription,
    organization: Organization,
    plan: str,
    stripe_customer_id: str | None = None,
    stripe_subscription_id: str | None = None,
) -> None:
    now = datetime.now(timezone.utc)
    subscription.status = "active"
    subscription.plan = plan
    subscription.current_period_start = now
    subscription.current_period_end = now + timedelta(days=30)
    subscription.cancel_at_period_end = False
    subscription.stripe_customer_id = stripe_customer_id or subscription.stripe_customer_id
    subscription.stripe_subscription_id = stripe_subscription_id or subscription.stripe_subscription_id
    _apply_plan_to_organization(organization, plan)


def _find_subscription_for_webhook(db: Session, stripe_object: dict) -> Subscription | None:
    stripe_subscription_id = stripe_object.get("subscription") or stripe_object.get("id")
    checkout_id = stripe_object.get("id") if stripe_object.get("object") == "checkout.session" else None

    metadata = stripe_object.get("metadata") or {}
    organization_id = metadata.get("organization_id")

    # Checkout session IDs are globally unique and the safest first match.
    if checkout_id:
        subscription = db.query(Subscription).filter(Subscription.checkout_id == checkout_id).first()
        if subscription:
            return subscription

    if stripe_subscription_id:
        query = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == stripe_subscription_id
        )
        if organization_id:
            query = query.filter(Subscription.organization_id == organization_id)
        subscription = query.first()
        if subscription:
            return subscription

    if organization_id:
        return (
            db.query(Subscription)
            .filter(Subscription.organization_id == organization_id)
            .order_by(Subscription.created_at.desc())
            .first()
        )

    return None


def _process_webhook_event(db: Session, event: dict) -> bool:
    event_type = event.get("type", "")
    stripe_object = event.get("data", {}).get("object", {})
    if not event_type or not stripe_object:
        return False

    subscription = _find_subscription_for_webhook(db, stripe_object)
    if not subscription:
        return False

    organization = db.query(Organization).filter(Organization.id == subscription.organization_id).first()
    if not organization:
        return False

    metadata = stripe_object.get("metadata") or {}

    if event_type == "checkout.session.completed":
        plan = _ensure_plan(metadata.get("plan") or subscription.plan)
        _activate_subscription(
            subscription,
            organization,
            plan,
            stripe_customer_id=stripe_object.get("customer"),
            stripe_subscription_id=stripe_object.get("subscription"),
        )
        db.commit()
        return True

    if event_type == "customer.subscription.updated":
        plan = metadata.get("plan") or subscription.plan
        plan = _ensure_plan(plan if plan in VALID_PLANS else subscription.plan)
        status = (stripe_object.get("status") or "active").lower()

        subscription.stripe_subscription_id = stripe_object.get("id") or subscription.stripe_subscription_id
        subscription.stripe_customer_id = stripe_object.get("customer") or subscription.stripe_customer_id
        subscription.current_period_start = _from_unix_timestamp(stripe_object.get("current_period_start"))
        subscription.current_period_end = _from_unix_timestamp(stripe_object.get("current_period_end"))
        subscription.cancel_at_period_end = bool(stripe_object.get("cancel_at_period_end", False))

        if status in {"active", "trialing"}:
            _activate_subscription(subscription, organization, plan)
        elif status in {"past_due", "unpaid"}:
            subscription.status = status
            subscription.plan = plan
        elif status in {"canceled", "incomplete_expired"}:
            subscription.status = "canceled"
            subscription.plan = "free"
            subscription.cancel_at_period_end = False
            _apply_plan_to_organization(organization, "free")
        else:
            subscription.status = status

        db.commit()
        return True

    if event_type == "customer.subscription.deleted":
        subscription.status = "canceled"
        subscription.plan = "free"
        subscription.cancel_at_period_end = False
        subscription.current_period_end = datetime.now(timezone.utc)
        subscription.stripe_subscription_id = stripe_object.get("id") or subscription.stripe_subscription_id
        subscription.stripe_customer_id = stripe_object.get("customer") or subscription.stripe_customer_id
        _apply_plan_to_organization(organization, "free")
        db.commit()
        return True

    return False


def _get_or_create_subscription(db: Session, user: User) -> Subscription:
    subscription = (
        db.query(Subscription)
        .filter(Subscription.organization_id == user.organization_id)
        .order_by(Subscription.created_at.desc())
        .first()
    )
    if subscription:
        return subscription

    subscription = Subscription(
        id=str(uuid.uuid4()),
        organization_id=user.organization_id,
        initiated_by_user_id=user.id,
        plan=user.organization.plan or "free",
        status="active",
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription


@router.get("/plans")
def get_plans(current_user: User = Depends(AuthService.get_current_user)):
    billing_service = BillingService()
    plans = billing_service.get_plans()
    return {
        "current_plan": current_user.organization.plan,
        "plans": plans,
        "stripe_enabled": bool(settings.stripe_secret_key),
    }


@router.get("/subscription")
def get_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    subscription = _get_or_create_subscription(db, current_user)
    return {
        "id": subscription.id,
        "plan": subscription.plan,
        "status": subscription.status,
        "cancel_at_period_end": subscription.cancel_at_period_end,
        "current_period_start": subscription.current_period_start,
        "current_period_end": subscription.current_period_end,
        "checkout_id": subscription.checkout_id,
        "organization_plan": current_user.organization.plan,
        "monthly_request_limit": current_user.organization.monthly_request_limit,
    }


@router.post("/checkout")
def create_checkout(
    payload: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    target_plan = _ensure_plan(payload.plan)
    if target_plan == "free":
        raise HTTPException(status_code=400, detail="Free plan does not require checkout")

    subscription = _get_or_create_subscription(db, current_user)

    success_url = payload.success_url or "https://alici.ai/billing/success"
    cancel_url = payload.cancel_url or "https://alici.ai/billing/cancel"

    price_id = settings.stripe_price_pro if target_plan == "pro" else settings.stripe_price_enterprise

    billing_service = BillingService()
    checkout = None
    if settings.stripe_secret_key and price_id:
        checkout = billing_service.create_checkout_session(
            organization_id=current_user.organization_id,
            price_id=price_id,
            success_url=success_url,
            cancel_url=cancel_url,
        )

    checkout_id = (checkout or {}).get("session_id") or f"chk_{uuid.uuid4().hex[:18]}"
    checkout_url = (checkout or {}).get("url") or f"/api/billing/mock-checkout/{checkout_id}"

    subscription.plan = target_plan
    subscription.status = "pending_checkout"
    subscription.checkout_id = checkout_id
    subscription.cancel_at_period_end = False
    db.commit()

    return {
        "checkout_id": checkout_id,
        "checkout_url": checkout_url,
        "plan": target_plan,
        "stripe_checkout": bool(checkout),
    }


@router.post("/subscription/confirm")
def confirm_subscription_checkout(
    payload: ConfirmCheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    target_plan = _ensure_plan(payload.plan)
    if target_plan == "free":
        raise HTTPException(status_code=400, detail="Use cancel endpoint to return to free plan")

    subscription = _get_or_create_subscription(db, current_user)
    if subscription.checkout_id != payload.checkout_id:
        raise HTTPException(status_code=404, detail="Checkout not found")

    now = datetime.now(timezone.utc)
    subscription.status = "active"
    subscription.plan = target_plan
    subscription.current_period_start = now
    subscription.current_period_end = now + timedelta(days=30)
    subscription.cancel_at_period_end = False

    _apply_plan_to_organization(current_user.organization, target_plan)

    db.commit()
    db.refresh(subscription)

    return {
        "message": "Subscription activated",
        "plan": subscription.plan,
        "status": subscription.status,
        "current_period_end": subscription.current_period_end,
    }


@router.post("/subscription/cancel")
def cancel_subscription(
    payload: CancelSubscriptionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    subscription = _get_or_create_subscription(db, current_user)

    if payload.immediate:
        subscription.status = "canceled"
        subscription.cancel_at_period_end = False
        _apply_plan_to_organization(current_user.organization, "free")
        subscription.plan = "free"
    else:
        subscription.status = "canceling"
        subscription.cancel_at_period_end = True

    db.commit()
    db.refresh(subscription)

    return {
        "message": "Subscription canceled" if payload.immediate else "Subscription scheduled for cancellation",
        "status": subscription.status,
        "plan": current_user.organization.plan,
    }


@router.post("/webhook")
async def billing_webhook(request: Request, db: Session = Depends(get_db)):
    payload_bytes = await request.body()
    signature = request.headers.get("stripe-signature")
    event: dict | None = None

    if settings.stripe_secret_key and settings.stripe_webhook_secret and signature:
        try:
            import stripe  # type: ignore

            stripe.api_key = settings.stripe_secret_key
            event = stripe.Webhook.construct_event(
                payload_bytes,
                signature,
                settings.stripe_webhook_secret,
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Invalid webhook signature: {exc}")

    if event is None:
        try:
            event = json.loads(payload_bytes.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid webhook payload")

    processed = _process_webhook_event(db, event)
    return {
        "received": True,
        "processed": processed,
        "event_type": event.get("type"),
    }

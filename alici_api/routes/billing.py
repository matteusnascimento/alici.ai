"""Billing routes backed by Stripe."""

from fastapi import APIRouter, Depends, Request

from alici_api.dependencies import get_current_user
from alici_api.responses import Codes, success
from alici_api.schemas import BillingCheckoutRequest
from alici_api.services.billing_service import BillingService
from alici_api.services.credit_service import CreditService
from database import buscar_assinatura_usuario

router = APIRouter(prefix="/billing", tags=["billing"])
billing_service = BillingService()
credit_service = CreditService()


@router.get("/plans")
def list_plans(user=Depends(get_current_user)):
    return success(
        Codes.BILLING_PLANS_OK,
        data=billing_service.plan_list(),
        plans=billing_service.plan_list(),
        current_plan=(user.get("plano") or "free").lower(),
        stripe_ready=bool(billing_service.settings.stripe_secret_key),
    )


@router.post("/create-checkout")
@router.post("/checkout")
def create_checkout(req: BillingCheckoutRequest, request: Request, user=Depends(get_current_user)):
    session = billing_service.create_checkout_session(
        user=user,
        plan=req.plano,
        idempotency_key=request.headers.get("Idempotency-Key"),
    )
    return success(
        Codes.BILLING_CHECKOUT_OK,
        message="Checkout criado",
        checkout_id=session["checkout_id"],
        session_id=session["checkout_id"],
        checkout_url=session["checkout_url"],
        plano=session["plan"],
        plan_id=session["plan"],
        price_id=session["price_id"],
        user_id=user["id"],
        stripe_ready=True,
    )


@router.post("/customer-portal")
@router.post("/portal")
def customer_portal(request: Request, user=Depends(get_current_user)):
    session = billing_service.create_customer_portal_session(
        user=user,
        idempotency_key=request.headers.get("Idempotency-Key"),
    )
    return success(Codes.BILLING_PORTAL_OK, **session)


@router.get("/current")
def current_subscription(user=Depends(get_current_user)):
    plan_id = (user.get("plano") or "free").lower()
    plan = billing_service.plan_catalog().get(plan_id) or billing_service.plan_catalog()["free"]
    subscription = buscar_assinatura_usuario(user["id"]) or {}
    return {
        "plan_id": plan_id,
        "plan_name": plan["name"],
        "status": subscription.get("status") or ("active" if plan_id != "free" else "free"),
        "billing_cycle": "monthly",
        "monthly_price": int(plan.get("price_brl") or 0),
        "yearly_price": None,
        "auto_renew": bool(subscription.get("status") in {"active", "trialing"}),
        "cancel_at_period_end": False,
        "started_at": str(subscription.get("criado_em")) if subscription.get("criado_em") else None,
        "next_renewal_at": str(subscription.get("current_period_end")) if subscription.get("current_period_end") else None,
        "provider": "stripe" if subscription.get("stripe_customer_id") else None,
        "stripe_customer_id": subscription.get("stripe_customer_id"),
    }


@router.get("/usage")
def billing_usage(user=Depends(get_current_user)):
    plan_id = (user.get("plano") or "free").lower()
    plan = billing_service.plan_catalog().get(plan_id) or billing_service.plan_catalog()["free"]
    limit = int(plan.get("monthly_credits") or 0)
    balance = credit_service.get_balance(int(user["id"]))
    used = max(0, limit - balance) if limit else 0
    return {"items": [{"metric": "creditos", "used": used, "limit": limit}]}


@router.get("/history")
def billing_history(user=Depends(get_current_user)):
    transactions = credit_service.get_history(int(user["id"]), limit=50)
    events = []
    for item in transactions:
        events.append(
            {
                "id": item.get("id"),
                "event_type": item.get("reason") or item.get("type"),
                "amount": item.get("amount") or 0,
                "currency": "credits",
                "description": item.get("model") or item.get("provider") or item.get("reason"),
                "stripe_event_id": (item.get("metadata") or {}).get("stripe_event_id") if isinstance(item.get("metadata"), dict) else None,
                "status": item.get("type"),
                "created_at": str(item.get("created_at")),
            }
        )
    return {"events": events}

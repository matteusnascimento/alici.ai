"""Billing routes (Stripe-ready with webhook support)."""

import os
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request

from alici_api.dependencies import get_current_user
from alici_api.responses import Codes, raise_api_error, success
from alici_api.schemas import BillingCheckoutRequest
from database import atualizar_plano_usuario, upsert_subscription
from logger import get_logger

router = APIRouter(prefix="/billing", tags=["billing"])
logger_billing = get_logger("route_billing")

PLAN_CATALOG = {
    "free": {"name": "Free", "price_brl": 0},
    "pro": {"name": "Pro", "price_brl": 49},
    "ultra": {"name": "Ultra", "price_brl": 99},
    "enterprise": {"name": "Enterprise", "price_brl": None},
}

_STRIPE_PRICE_MAP = {
    "pro": os.getenv("STRIPE_PRICE_PRO", ""),
    "ultra": os.getenv("STRIPE_PRICE_ULTRA", ""),
    "enterprise": os.getenv("STRIPE_PRICE_ENTERPRISE", ""),
}


@router.get("/plans")
def list_plans(user=Depends(get_current_user)):
    return success(
        Codes.BILLING_PLANS_OK,
        plans=PLAN_CATALOG,
        current_plan=(user.get("plano") or "free").lower(),
        stripe_ready=bool(os.getenv("STRIPE_SECRET_KEY")),
    )


@router.post("/create-checkout")
def create_checkout(req: BillingCheckoutRequest, user=Depends(get_current_user)):
    plano = (req.plano or "").strip().lower()
    if plano not in PLAN_CATALOG or plano == "free":
        raise_api_error(400, Codes.BAD_REQUEST, "Plano inválido para checkout")

    stripe_key = os.getenv("STRIPE_SECRET_KEY")
    success_url = os.getenv("STRIPE_SUCCESS_URL", os.getenv("BASE_URL", "") + "/billing/success")
    cancel_url = os.getenv("STRIPE_CANCEL_URL", os.getenv("BASE_URL", "") + "/billing/cancel")
    price_id = _STRIPE_PRICE_MAP.get(plano, "")

    if stripe_key and price_id:
        try:
            import stripe  # type: ignore

            stripe.api_key = stripe_key
            session = stripe.checkout.Session.create(
                mode="subscription",
                line_items=[{"price": price_id, "quantity": 1}],
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={"user_id": str(user["id"]), "plano": plano},
            )
            return success(
                Codes.BILLING_CHECKOUT_OK,
                message="Checkout criado via Stripe",
                checkout_id=session.id,
                checkout_url=session.url,
                plano=plano,
                user_id=user["id"],
                stripe_ready=True,
            )
        except Exception as exc:
            logger_billing.warning(f"Stripe checkout falhou, usando fallback: {exc}")

    # Fallback mock when Stripe SDK or price IDs are not configured
    checkout_id = f"chk_{uuid4().hex[:18]}"
    checkout_url = f"/billing/mock-checkout/{checkout_id}"

    return success(
        Codes.BILLING_CHECKOUT_OK,
        message="Checkout criado (modo base Stripe-ready)",
        checkout_id=checkout_id,
        checkout_url=checkout_url,
        plano=plano,
        user_id=user["id"],
        stripe_ready=False,
    )


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Stripe webhook endpoint — verifies signature and processes events."""
    stripe_key = os.getenv("STRIPE_SECRET_KEY")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    if not stripe_key or not webhook_secret:
        logger_billing.warning("Stripe não configurado — webhook ignorado")
        return {"received": True}

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        import stripe  # type: ignore

        stripe.api_key = stripe_key
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except Exception as exc:
        logger_billing.warning(f"Assinatura Stripe inválida: {exc}")
        raise HTTPException(status_code=400, detail={"code": Codes.BAD_REQUEST, "message": "Assinatura inválida"})

    event_type = event.get("type", "")
    data = event.get("data", {}).get("object", {})
    logger_billing.info(f"Stripe webhook recebido: {event_type}")

    try:
        if event_type == "checkout.session.completed":
            user_id = int(data.get("metadata", {}).get("user_id", 0))
            plano = data.get("metadata", {}).get("plano", "pro")
            stripe_sub_id = data.get("subscription", "")
            if not user_id:
                logger_billing.warning(f"Webhook {event_type}: user_id ausente nos metadados")
            else:
                atualizar_plano_usuario(user_id, plano)
                upsert_subscription(user_id, stripe_sub_id, "active", plano)

        elif event_type == "customer.subscription.updated":
            stripe_sub_id = data.get("id", "")
            status = data.get("status", "")
            plano = data.get("metadata", {}).get("plano", "")
            user_id = int(data.get("metadata", {}).get("user_id", 0))
            if not user_id or not plano:
                logger_billing.warning(f"Webhook {event_type}: user_id ou plano ausente nos metadados")
            else:
                atualizar_plano_usuario(user_id, plano)
                upsert_subscription(user_id, stripe_sub_id, status, plano)

        elif event_type == "customer.subscription.deleted":
            stripe_sub_id = data.get("id", "")
            user_id = int(data.get("metadata", {}).get("user_id", 0))
            if not user_id:
                logger_billing.warning(f"Webhook {event_type}: user_id ausente nos metadados")
            else:
                atualizar_plano_usuario(user_id, "free")
                upsert_subscription(user_id, stripe_sub_id, "canceled", "free")

    except Exception as exc:
        logger_billing.error(f"Erro ao processar evento Stripe {event_type}: {exc}")

    return {"received": True}

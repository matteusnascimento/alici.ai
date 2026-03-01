"""Billing routes (Stripe-ready base)."""

import os
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from alici_api.dependencies import get_current_user
from alici_api.responses import Codes, raise_api_error, success
from alici_api.schemas import BillingCheckoutRequest
from database import contar_mensagens_hoje, salvar_subscription
from logger import get_logger

router = APIRouter(prefix="/billing", tags=["billing"])
logger_billing = get_logger("route_billing")

PLAN_CATALOG = {
    "free": {"name": "Free", "price_brl": 0},
    "pro": {"name": "Pro", "price_brl": 49},
    "ultra": {"name": "Ultra", "price_brl": 99},
    "enterprise": {"name": "Enterprise", "price_brl": None},
}

DAILY_LIMITS = {"free": 20, "pro": 300, "ultra": 2000, "enterprise": None}


@router.get("/plans")
def list_plans(user=Depends(get_current_user)):
    return success(
        Codes.BILLING_PLANS_OK,
        plans=PLAN_CATALOG,
        current_plan=(user.get("plano") or "free").lower(),
        stripe_ready=bool(os.getenv("STRIPE_SECRET_KEY")),
    )


@router.get("/usage")
def get_usage(user=Depends(get_current_user)):
    plano = (user.get("plano") or "free").lower()
    mensagens_hoje = contar_mensagens_hoje(user["id"])
    limite = DAILY_LIMITS.get(plano, 20)
    return success(
        Codes.BILLING_USAGE_OK,
        plano=plano,
        mensagens_hoje=mensagens_hoje,
        limite_diario=limite,
        porcentagem_uso=round((mensagens_hoje / limite * 100), 1) if limite else 0,
    )


@router.post("/create-checkout")
def create_checkout(req: BillingCheckoutRequest, user=Depends(get_current_user)):
    plano = (req.plano or "").strip().lower()
    if plano not in PLAN_CATALOG or plano == "free":
        raise_api_error(400, Codes.BAD_REQUEST, "Plano inválido para checkout")

    stripe_secret = os.getenv("STRIPE_SECRET_KEY")

    if stripe_secret:
        try:
            import stripe

            stripe.api_key = stripe_secret
            price_ids = {
                "pro": os.getenv("STRIPE_PRICE_PRO"),
                "ultra": os.getenv("STRIPE_PRICE_ULTRA"),
                "enterprise": os.getenv("STRIPE_PRICE_ENTERPRISE"),
            }
            price_id = price_ids.get(plano)
            if not price_id:
                raise_api_error(400, Codes.BAD_REQUEST, f"Price ID não configurado para o plano {plano}")

            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{"price": price_id, "quantity": 1}],
                mode="subscription",
                success_url=os.getenv("STRIPE_SUCCESS_URL", "/chat?checkout=success"),
                cancel_url=os.getenv("STRIPE_CANCEL_URL", "/billing/plans"),
                metadata={"user_id": str(user["id"]), "plano": plano},
            )
            return success(
                Codes.BILLING_CHECKOUT_OK,
                message="Checkout Stripe criado",
                checkout_id=session.id,
                checkout_url=session.url,
                plano=plano,
                user_id=user["id"],
                stripe_ready=True,
            )
        except Exception as exc:
            logger_billing.exception("Erro ao criar checkout Stripe", exc_info=exc)

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
async def stripe_webhook(request: Request, stripe_signature: str = Header(None, alias="stripe-signature")):
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    body = await request.body()

    if webhook_secret and stripe_signature:
        try:
            import stripe

            stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
            event = stripe.Webhook.construct_event(body, stripe_signature, webhook_secret)
        except Exception as exc:
            logger_billing.warning(f"Webhook signature inválida: {exc}")
            raise HTTPException(status_code=400, detail="Webhook signature inválida")
    else:
        import json

        try:
            event = json.loads(body)
        except Exception:
            raise HTTPException(status_code=400, detail="Payload inválido")

    event_type = event.get("type") if isinstance(event, dict) else getattr(event, "type", None)
    data_obj = event.get("data", {}).get("object", {}) if isinstance(event, dict) else {}

    if event_type == "checkout.session.completed":
        user_id = data_obj.get("metadata", {}).get("user_id")
        plano = data_obj.get("metadata", {}).get("plano")
        stripe_id = data_obj.get("subscription") or data_obj.get("id")
        if user_id and plano:
            salvar_subscription(int(user_id), stripe_id, "active", plano)
            logger_billing.info(f"Subscription criada: user_id={user_id}, plano={plano}")

    elif event_type in ("customer.subscription.deleted", "customer.subscription.updated"):
        stripe_id = data_obj.get("id")
        status = data_obj.get("status", "inactive")
        plano = data_obj.get("metadata", {}).get("plano", "free")
        user_id = data_obj.get("metadata", {}).get("user_id")
        if user_id:
            # user_id available in metadata — update directly
            salvar_subscription(int(user_id), stripe_id, status, plano if status == "active" else "free")
        else:
            # user_id not in metadata — log for manual reconciliation
            # Full reconciliation requires querying subscriptions by stripe_id (not implemented here)
            logger_billing.warning(
                f"Webhook {event_type}: user_id não encontrado nos metadados para stripe_id={stripe_id}"
            )

    return success(Codes.BILLING_WEBHOOK_OK, message="Webhook processado")


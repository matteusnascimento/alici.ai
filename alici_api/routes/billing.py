"""Billing routes (Stripe-ready base)."""

import hashlib
import hmac
import os
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request

from alici_api.dependencies import get_current_user
from alici_api.responses import Codes, raise_api_error, success
from alici_api.schemas import BillingCheckoutRequest
from logger import get_logger

router = APIRouter(prefix="/billing", tags=["billing"])
logger_billing = get_logger("route_billing")

PLAN_CATALOG = {
    "free": {"name": "Free", "price_brl": 0},
    "pro": {"name": "Pro", "price_brl": 49},
    "ultra": {"name": "Ultra", "price_brl": 99},
    "enterprise": {"name": "Enterprise", "price_brl": None},
}

PLAN_LIMITS = {
    "free": {"mensagens_dia": 20, "mensagens_minuto": 20},
    "pro": {"mensagens_dia": 300, "mensagens_minuto": 120},
    "ultra": {"mensagens_dia": 2000, "mensagens_minuto": 300},
    "enterprise": {"mensagens_dia": None, "mensagens_minuto": None},
}


@router.get("/plans")
def list_plans(user=Depends(get_current_user)):
    plano = (user.get("plano") or "free").lower()
    limits = PLAN_LIMITS.get(plano, PLAN_LIMITS["free"])
    return success(
        Codes.BILLING_PLANS_OK,
        plans=PLAN_CATALOG,
        current_plan=plano,
        limits=limits,
        stripe_ready=bool(os.getenv("STRIPE_SECRET_KEY")),
    )


@router.post("/create-checkout")
def create_checkout(req: BillingCheckoutRequest, user=Depends(get_current_user)):
    plano = (req.plano or "").strip().lower()
    if plano not in PLAN_CATALOG or plano == "free":
        raise_api_error(400, Codes.BAD_REQUEST, "Plano inválido para checkout")

    stripe_key = os.getenv("STRIPE_SECRET_KEY")

    if stripe_key:
        try:
            import stripe  # type: ignore

            stripe.api_key = stripe_key
            price_id = os.getenv(f"STRIPE_PRICE_{plano.upper()}")
            if not price_id:
                raise_api_error(
                    400,
                    Codes.BAD_REQUEST,
                    f"STRIPE_PRICE_{plano.upper()} não configurado",
                )

            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                mode="subscription",
                line_items=[{"price": price_id, "quantity": 1}],
                success_url=os.getenv("STRIPE_SUCCESS_URL", f"{os.getenv('BASE_URL', '')}/billing/success"),
                cancel_url=os.getenv("STRIPE_CANCEL_URL", f"{os.getenv('BASE_URL', '')}/billing/cancel"),
                metadata={"user_id": str(user["id"]), "plano": plano},
            )

            return success(
                Codes.BILLING_CHECKOUT_OK,
                checkout_id=session.id,
                checkout_url=session.url,
                plano=plano,
                user_id=user["id"],
                stripe_ready=True,
            )
        except ImportError:
            logger_billing.warning("Biblioteca stripe não instalada; usando modo mock")
        except Exception as exc:
            logger_billing.error(f"Erro ao criar Stripe checkout: {exc}")
            raise HTTPException(
                status_code=500,
                detail={"code": Codes.INTERNAL, "message": "Erro ao criar sessão de pagamento"},
            )

    # Fallback mock mode
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
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    if webhook_secret:
        # Verify Stripe signature
        try:
            import stripe  # type: ignore

            stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except ImportError:
            # Stripe not installed; verify manually
            event = _verify_webhook_manual(payload, sig_header, webhook_secret)
        except Exception as exc:
            logger_billing.warning(f"Webhook signature inválida: {exc}")
            raise HTTPException(status_code=400, detail="Assinatura inválida")
    else:
        # No secret configured; accept all (dev mode only)
        import json

        try:
            event = json.loads(payload)
        except Exception:
            raise HTTPException(status_code=400, detail="Payload inválido")

    event_type = event.get("type", "")
    logger_billing.info(f"Stripe webhook recebido: {event_type}")

    if event_type in ("customer.subscription.created", "customer.subscription.updated"):
        _handle_subscription_event(event)
    elif event_type == "customer.subscription.deleted":
        _handle_subscription_deleted(event)
    elif event_type == "checkout.session.completed":
        _handle_checkout_completed(event)

    return {"received": True}


def _verify_webhook_manual(payload: bytes, sig_header: str, secret: str) -> dict:
    """Manually verify Stripe webhook signature without the stripe library."""
    import json
    import time as _time

    parts = {k: v for item in sig_header.split(",") for k, _, v in [item.partition("=")]}
    ts = parts.get("t", "")
    v1 = parts.get("v1", "")

    if not ts or not v1:
        raise ValueError("Cabeçalho stripe-signature malformado")

    signed_payload = f"{ts}.{payload.decode('utf-8')}"
    expected = hmac.new(secret.encode("utf-8"), signed_payload.encode("utf-8"), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected, v1):
        raise ValueError("Assinatura inválida")

    tolerance = 300  # seconds; rejects webhooks older than this window
    if abs(_time.time() - int(ts)) > tolerance:
        raise ValueError("Timestamp expirado")

    return json.loads(payload)


def _handle_subscription_event(event: dict) -> None:
    try:
        from database import get_db_connection, USE_POSTGRES, USE_SQLITE, DATABASE_ENABLED

        subscription = event.get("data", {}).get("object", {})
        stripe_id = subscription.get("id", "")
        status = subscription.get("status", "inactive")
        metadata = subscription.get("metadata", {})
        user_id = metadata.get("user_id")
        plano = metadata.get("plano", "free")

        if not user_id or not DATABASE_ENABLED:
            return

        placeholder = "?" if USE_SQLITE else "%s"
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                f"UPDATE users SET plano = {placeholder} WHERE id = {placeholder}",
                (plano, int(user_id)),
            )
            # Upsert subscription record
            if USE_POSTGRES:
                cur.execute(
                    f"""
                    INSERT INTO subscriptions (user_id, stripe_id, status, plano)
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})
                    ON CONFLICT (stripe_id) DO UPDATE
                    SET status = EXCLUDED.status, plano = EXCLUDED.plano
                    """,
                    (int(user_id), stripe_id, status, plano),
                )
            else:
                cur.execute(
                    f"""
                    INSERT OR REPLACE INTO subscriptions (user_id, stripe_id, status, plano)
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})
                    """,
                    (int(user_id), stripe_id, status, plano),
                )
            cur.close()
        logger_billing.info(f"Assinatura atualizada: user={user_id} plano={plano} status={status}")
    except Exception as exc:
        logger_billing.error(f"Erro ao processar evento de assinatura: {exc}")


def _handle_subscription_deleted(event: dict) -> None:
    try:
        from database import get_db_connection, USE_POSTGRES, USE_SQLITE, DATABASE_ENABLED

        subscription = event.get("data", {}).get("object", {})
        metadata = subscription.get("metadata", {})
        user_id = metadata.get("user_id")

        if not user_id or not DATABASE_ENABLED:
            return

        placeholder = "?" if USE_SQLITE else "%s"
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                f"UPDATE users SET plano = {placeholder} WHERE id = {placeholder}",
                ("free", int(user_id)),
            )
            cur.close()
        logger_billing.info(f"Assinatura cancelada: user={user_id} → plano=free")
    except Exception as exc:
        logger_billing.error(f"Erro ao processar cancelamento: {exc}")


def _handle_checkout_completed(event: dict) -> None:
    session = event.get("data", {}).get("object", {})
    metadata = session.get("metadata", {})
    user_id = metadata.get("user_id")
    plano = metadata.get("plano")
    logger_billing.info(f"Checkout concluído: user={user_id} plano={plano}")

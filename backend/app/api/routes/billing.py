import os

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.billing import (
    BillingHistoryResponse,
    BillingUsageResponse,
    CheckoutRequest,
    CheckoutResponse,
    CurrentSubscriptionResponse,
    PlanRead,
    PortalResponse,
    SubscriptionActionResponse,
    UpgradeRequest,
    UpgradeResponse,
)
from app.services.billing_service import BillingService

router = APIRouter(prefix="/billing", tags=["billing"])


def _require_billing_admin(user: User) -> None:
    allowed_emails = {email.strip().lower() for email in settings.billing_admin_emails if email.strip()}
    user_email = (user.email or "").strip().lower()
    if not allowed_emails or user_email not in allowed_emails:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Upgrade manual restrito a administradores de billing. Use /billing/checkout para cobranca.",
        )


# ── Endpoints existentes preservados ────────────────────────────────


@router.get("/plans", response_model=list[PlanRead])
def billing_plans(_: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[PlanRead]:
    return BillingService(db).list_plans()


@router.get("/current", response_model=CurrentSubscriptionResponse)
def billing_current(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CurrentSubscriptionResponse:
    return BillingService(db).current_subscription(current_user)


@router.post("/upgrade", response_model=UpgradeResponse)
def billing_upgrade(
    payload: UpgradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UpgradeResponse:
    """[LEGADO/ADMIN] Upgrade manual sem pagamento real. Fluxo principal: POST /billing/checkout."""
    _require_billing_admin(current_user)
    return BillingService(db).upgrade(current_user, payload)


@router.get("/usage", response_model=BillingUsageResponse)
def billing_usage(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> BillingUsageResponse:
    return BillingService(db).usage(current_user)


@router.get("/history", response_model=BillingHistoryResponse)
def billing_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> BillingHistoryResponse:
    return BillingService(db).history(current_user)


# ── Endpoints Stripe novos ───────────────────────────────────────────


@router.post("/checkout", response_model=CheckoutResponse)
def billing_checkout(
    payload: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CheckoutResponse:
    """Cria uma Stripe Checkout Session e retorna a URL de redirect."""
    return BillingService(db).create_checkout_session(current_user, payload)


@router.post("/portal", response_model=PortalResponse)
def billing_portal(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PortalResponse:
    """Cria uma Stripe Billing Portal Session e retorna a URL de redirect."""
    return BillingService(db).create_billing_portal_session(current_user)


@router.post("/cancel", response_model=SubscriptionActionResponse)
def billing_cancel(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SubscriptionActionResponse:
    """Agenda cancelamento da assinatura ao fim do período atual."""
    return BillingService(db).cancel_subscription(current_user)


@router.post("/resume", response_model=SubscriptionActionResponse)
def billing_resume(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SubscriptionActionResponse:
    """Reverte cancelamento agendado e mantém assinatura ativa."""
    return BillingService(db).resume_subscription(current_user)


@router.post("/webhook")
async def billing_webhook(request: Request, db: Session = Depends(get_db)) -> dict:
    """Endpoint de webhook Stripe — validação de assinatura obrigatória."""
    payload = await request.body()
    stripe_signature = request.headers.get("stripe-signature", "")
    return BillingService(db).process_webhook_event(payload, stripe_signature)


@router.get("/health")
def billing_health() -> dict:
    """Verifica o estado da integração Stripe (para monitoramento em produção)."""
    stripe_key = os.getenv("STRIPE_SECRET_KEY", "")
    prices_configured = all([
        os.getenv("STRIPE_PRICE_PRO_MONTHLY"),
        os.getenv("STRIPE_PRICE_PRO_YEARLY"),
        os.getenv("STRIPE_PRICE_BUSINESS_MONTHLY"),
        os.getenv("STRIPE_PRICE_BUSINESS_YEARLY"),
    ])
    return {
        "stripe_configured": bool(stripe_key),
        "prices_loaded": prices_configured,
        "webhook_ready": bool(os.getenv("STRIPE_WEBHOOK_SECRET")),
    }

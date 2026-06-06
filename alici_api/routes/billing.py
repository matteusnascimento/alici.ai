"""Billing routes backed by Stripe."""

from fastapi import APIRouter, Depends, Request

from alici_api.dependencies import get_current_user
from alici_api.responses import Codes, success
from alici_api.schemas import BillingCheckoutRequest
from alici_api.services.billing_service import BillingService

router = APIRouter(prefix="/billing", tags=["billing"])
billing_service = BillingService()


@router.get("/plans")
def list_plans(user=Depends(get_current_user)):
    return success(
        Codes.BILLING_PLANS_OK,
        plans=billing_service.plan_catalog(),
        current_plan=(user.get("plano") or "free").lower(),
        stripe_ready=bool(billing_service.settings.stripe_secret_key),
    )


@router.post("/create-checkout")
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
        checkout_url=session["checkout_url"],
        plano=session["plan"],
        price_id=session["price_id"],
        user_id=user["id"],
        stripe_ready=True,
    )


@router.post("/customer-portal")
def customer_portal(request: Request, user=Depends(get_current_user)):
    session = billing_service.create_customer_portal_session(
        user=user,
        idempotency_key=request.headers.get("Idempotency-Key"),
    )
    return success(Codes.BILLING_PORTAL_OK, **session)

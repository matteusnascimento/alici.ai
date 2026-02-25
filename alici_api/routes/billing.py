"""Billing routes (Stripe-ready base)."""

import os
from uuid import uuid4

from fastapi import APIRouter, Depends

from alici_api.dependencies import get_current_user
from alici_api.responses import Codes, raise_api_error, success
from alici_api.schemas import BillingCheckoutRequest

router = APIRouter(prefix="/billing", tags=["billing"])

PLAN_CATALOG = {
    "free": {"name": "Free", "price_brl": 0},
    "pro": {"name": "Pro", "price_brl": 49},
    "ultra": {"name": "Ultra", "price_brl": 99},
    "enterprise": {"name": "Enterprise", "price_brl": None},
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

    checkout_id = f"chk_{uuid4().hex[:18]}"
    checkout_url = f"/billing/mock-checkout/{checkout_id}"

    return success(
        Codes.BILLING_CHECKOUT_OK,
        message="Checkout criado (modo base Stripe-ready)",
        checkout_id=checkout_id,
        checkout_url=checkout_url,
        plano=plano,
        user_id=user["id"],
        stripe_ready=bool(os.getenv("STRIPE_SECRET_KEY")),
    )

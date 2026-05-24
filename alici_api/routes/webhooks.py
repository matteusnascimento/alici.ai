"""External provider webhooks."""

from fastapi import APIRouter, Request

from alici_api.responses import Codes, success
from alici_api.services.billing_service import BillingService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
billing_service = BillingService()


@router.post("/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    event = billing_service.construct_webhook_event(payload, signature)
    result = billing_service.handle_webhook_event(event)
    return success(Codes.SUCCESS_DEFAULT, **result)

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.agent_runtime import InboundWebhookResponse
from app.services.channel_integration_service import ChannelIntegrationService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/meta/whatsapp", response_model=InboundWebhookResponse)
async def meta_whatsapp_webhook(request: Request, db: Session = Depends(get_db)) -> InboundWebhookResponse:
    payload = await request.json()
    ChannelIntegrationService(db).process_meta_webhook("whatsapp", payload)
    return InboundWebhookResponse(ok=True, detail="whatsapp processed")


@router.post("/meta/instagram", response_model=InboundWebhookResponse)
async def meta_instagram_webhook(request: Request, db: Session = Depends(get_db)) -> InboundWebhookResponse:
    payload = await request.json()
    ChannelIntegrationService(db).process_meta_webhook("instagram", payload)
    return InboundWebhookResponse(ok=True, detail="instagram processed")
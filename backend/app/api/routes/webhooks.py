import json

from fastapi import APIRouter, Depends, HTTPException, Header, Query, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.schemas.agent_runtime import InboundWebhookResponse
from app.services.agent_runtime_service import AgentRuntimeService
from app.services.channel_integration_service import ChannelIntegrationService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def _get_meta_verify_token() -> str:
    return getattr(settings, "meta_webhook_verify_token", "") or ""


def _get_meta_app_secret() -> str:
    return getattr(settings, "meta_app_secret", "") or ""


def _extract_signature(signature_header: str | None) -> str:
    if not signature_header:
        return ""
    raw = signature_header.strip()
    if raw.startswith("sha256="):
        return raw.split("=", 1)[1].strip()
    return raw


def _verify_meta_signature_or_401(raw_body: bytes, signature_header: str | None) -> None:
    app_secret = _get_meta_app_secret()
    if not app_secret:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Webhook signature secret not configured")
    signature = _extract_signature(signature_header)
    if not signature:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing webhook signature")
    if not AgentRuntimeService.verify_webhook_signature(raw_body, signature, app_secret):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook signature")


def _verify_meta_handshake_or_403(mode: str | None, token: str | None, challenge: str | None) -> str:
    if mode != "subscribe" or not challenge:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook verification params")

    configured_token = _get_meta_verify_token()
    if not configured_token:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Webhook verify token not configured")

    if token != configured_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Webhook verification failed")
    return challenge


async def _handle_meta_post(provider: str, request: Request, db: Session, signature_header: str | None) -> InboundWebhookResponse:
    raw_body = await request.body()
    _verify_meta_signature_or_401(raw_body, signature_header)
    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook payload") from exc
    if not isinstance(payload, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook payload")

    ChannelIntegrationService(db).process_meta_webhook(provider, payload)
    return InboundWebhookResponse(ok=True, detail=f"{provider} processed")


@router.get("/meta/whatsapp")
def meta_whatsapp_handshake(
    mode: str | None = Query(default=None, alias="hub.mode"),
    token: str | None = Query(default=None, alias="hub.verify_token"),
    challenge: str | None = Query(default=None, alias="hub.challenge"),
) -> str:
    return _verify_meta_handshake_or_403(mode, token, challenge)


@router.get("/meta/instagram")
def meta_instagram_handshake(
    mode: str | None = Query(default=None, alias="hub.mode"),
    token: str | None = Query(default=None, alias="hub.verify_token"),
    challenge: str | None = Query(default=None, alias="hub.challenge"),
) -> str:
    return _verify_meta_handshake_or_403(mode, token, challenge)


@router.post("/meta/whatsapp", response_model=InboundWebhookResponse)
async def meta_whatsapp_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_hub_signature_256: str | None = Header(default=None),
) -> InboundWebhookResponse:
    return await _handle_meta_post("whatsapp", request, db, x_hub_signature_256)


@router.post("/meta/instagram", response_model=InboundWebhookResponse)
async def meta_instagram_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_hub_signature_256: str | None = Header(default=None),
) -> InboundWebhookResponse:
    return await _handle_meta_post("instagram", request, db, x_hub_signature_256)

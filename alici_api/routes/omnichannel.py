from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from alici_api.config import get_settings
from alici_api.services.omnichannel_service import OmnichannelService, normalize_provider

router = APIRouter(prefix="/omnichannel", tags=["omnichannel"])
service = OmnichannelService()


def _secret_value(secret) -> str | None:
    if secret is None:
        return None
    return secret.get_secret_value() if hasattr(secret, "get_secret_value") else str(secret)


@router.get("/webhook/meta")
def verify_meta_webhook(
    mode: str | None = Query(default=None, alias="hub.mode"),
    token: str | None = Query(default=None, alias="hub.verify_token"),
    challenge: str | None = Query(default=None, alias="hub.challenge"),
):
    settings = get_settings()
    expected = _secret_value(settings.meta_webhook_verify_token)
    if mode == "subscribe" and expected and token == expected and challenge:
        return PlainTextResponse(challenge)
    raise HTTPException(status_code=403, detail="Webhook Meta nao verificado")


@router.post("/webhook/meta")
async def receive_meta_webhook(request: Request):
    payload = await request.json()
    processed = 0
    ignored = 0

    for entry in payload.get("entry", []):
        entry_object = str(payload.get("object") or "").lower()

        for change in entry.get("changes", []):
            value = change.get("value") or {}
            if value.get("messaging_product") == "whatsapp":
                account_id = (value.get("metadata") or {}).get("phone_number_id")
                contacts = {c.get("wa_id"): c for c in value.get("contacts", [])}
                for message in value.get("messages", []):
                    text = _extract_text(message)
                    contact_id = message.get("from")
                    if not account_id or not contact_id or not text:
                        ignored += 1
                        continue
                    contact = contacts.get(contact_id) or {}
                    contact_name = ((contact.get("profile") or {}).get("name")) or contact_id
                    if service.ingest_inbound("whatsapp", account_id, contact_id, text, contact_name, message.get("id"), payload):
                        processed += 1
                    else:
                        ignored += 1

        for event in entry.get("messaging", []):
            provider = "instagram" if "instagram" in entry_object else "messenger"
            account_id = (event.get("recipient") or {}).get("id") or entry.get("id")
            contact_id = (event.get("sender") or {}).get("id")
            message = event.get("message") or {}
            text = message.get("text")
            if not account_id or not contact_id or not text:
                ignored += 1
                continue
            if service.ingest_inbound(provider, account_id, contact_id, text, contact_id, message.get("mid"), payload):
                processed += 1
            else:
                ignored += 1

    return {"ok": True, "processed": processed, "ignored": ignored}


@router.post("/webhook/{provider}")
async def receive_generic_webhook(provider: str, request: Request):
    payload = await request.json()
    try:
        provider = normalize_provider(provider)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    items = payload.get("messages") if isinstance(payload, dict) else None
    if not isinstance(items, list):
        items = [payload]

    processed = 0
    ignored = 0
    for item in items:
        account_id = _first(item, "account_id", "business_account_id", "recipient_id", "page_id")
        contact_id = _first(item, "contact_id", "sender_id", "from", "user_id")
        text = _first(item, "text", "message", "body")
        external_message_id = _first(item, "message_id", "id", "mid")
        if not account_id or not contact_id or not text:
            ignored += 1
            continue
        if service.ingest_inbound(provider, account_id, contact_id, text, str(contact_id), external_message_id, item):
            processed += 1
        else:
            ignored += 1
    return {"ok": True, "provider": provider, "processed": processed, "ignored": ignored}


def _extract_text(message: dict[str, Any]) -> str | None:
    if message.get("type") == "text":
        return (message.get("text") or {}).get("body")
    if message.get("button"):
        return (message.get("button") or {}).get("text")
    if message.get("interactive"):
        interactive = message.get("interactive") or {}
        return ((interactive.get("button_reply") or {}).get("title")) or ((interactive.get("list_reply") or {}).get("title"))
    return None


def _first(item: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = item.get(key)
        if value:
            return value
    return None

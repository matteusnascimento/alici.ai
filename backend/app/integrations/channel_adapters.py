from __future__ import annotations

from typing import Any


class AdapterError(Exception):
    pass


class ChannelAdapters:
    @staticmethod
    def normalize_whatsapp(payload: dict[str, Any]) -> dict[str, Any]:
        channel_id = str(payload.get("channel_id") or payload.get("phone_number_id") or "")
        sender = str(payload.get("from") or payload.get("sender") or "unknown")
        text = str(payload.get("text") or payload.get("message") or "")
        conversation_id = str(payload.get("conversation_id") or payload.get("wamid") or f"wa:{sender}")
        return {
            "channel_type": "whatsapp",
            "channel_id": channel_id,
            "external_user_id": sender,
            "external_conversation_id": conversation_id,
            "text": text,
            "metadata": payload,
        }

    @staticmethod
    def normalize_instagram(payload: dict[str, Any]) -> dict[str, Any]:
        channel_id = str(payload.get("channel_id") or payload.get("ig_account_id") or "")
        sender = str(payload.get("from") or payload.get("sender") or "unknown")
        text = str(payload.get("text") or payload.get("message") or "")
        conversation_id = str(payload.get("conversation_id") or payload.get("thread_id") or f"ig:{sender}")
        return {
            "channel_type": "instagram",
            "channel_id": channel_id,
            "external_user_id": sender,
            "external_conversation_id": conversation_id,
            "text": text,
            "metadata": payload,
        }

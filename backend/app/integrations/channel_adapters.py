from __future__ import annotations

from typing import Any


class AdapterError(Exception):
    pass


class ChannelAdapters:
    @staticmethod
    def _extract_meta_value(payload: dict[str, Any]) -> dict[str, Any]:
        entries = payload.get("entry")
        if not isinstance(entries, list) or not entries:
            return payload
        first_entry = entries[0] if isinstance(entries[0], dict) else {}
        changes = first_entry.get("changes")
        if not isinstance(changes, list) or not changes:
            return payload
        first_change = changes[0] if isinstance(changes[0], dict) else {}
        value = first_change.get("value")
        if isinstance(value, dict):
            return value
        return payload

    @staticmethod
    def _extract_text_from_meta_message(message: dict[str, Any]) -> str:
        if not isinstance(message, dict):
            return ""
        text_block = message.get("text")
        if isinstance(text_block, dict) and text_block.get("body"):
            return str(text_block.get("body"))
        if message.get("message"):
            return str(message.get("message"))
        return ""

    @staticmethod
    def normalize_whatsapp(payload: dict[str, Any]) -> dict[str, Any]:
        value = ChannelAdapters._extract_meta_value(payload)
        metadata = value.get("metadata") if isinstance(value.get("metadata"), dict) else {}
        messages = value.get("messages") if isinstance(value.get("messages"), list) else []
        statuses = value.get("statuses") if isinstance(value.get("statuses"), list) else []
        message = messages[0] if messages and isinstance(messages[0], dict) else {}
        status_event = statuses[0] if statuses and isinstance(statuses[0], dict) else {}

        channel_id = str(
            metadata.get("phone_number_id")
            or value.get("phone_number_id")
            or payload.get("channel_id")
            or ""
        )
        sender = str(
            message.get("from")
            or status_event.get("recipient_id")
            or payload.get("from")
            or payload.get("sender")
            or "unknown"
        )
        text = ChannelAdapters._extract_text_from_meta_message(message) or str(payload.get("text") or payload.get("message") or "")
        conversation_id = str(
            message.get("id")
            or status_event.get("id")
            or payload.get("conversation_id")
            or payload.get("wamid")
            or f"wa:{sender}"
        )
        event_type = "status_update" if status_event else "message_received"

        return {
            "channel_type": "whatsapp",
            "channel_id": channel_id,
            "external_user_id": sender,
            "external_conversation_id": conversation_id,
            "text": text,
            "external_message_id": str(message.get("id") or status_event.get("id") or ""),
            "event_type": event_type,
            "metadata": payload,
        }

    @staticmethod
    def normalize_instagram(payload: dict[str, Any]) -> dict[str, Any]:
        value = ChannelAdapters._extract_meta_value(payload)
        messages = value.get("messaging") if isinstance(value.get("messaging"), list) else []
        first_message = messages[0] if messages and isinstance(messages[0], dict) else {}
        message_data = first_message.get("message") if isinstance(first_message.get("message"), dict) else {}

        channel_id = str(value.get("id") or payload.get("channel_id") or payload.get("ig_account_id") or "")
        sender_obj = first_message.get("sender") if isinstance(first_message.get("sender"), dict) else {}
        recipient_obj = first_message.get("recipient") if isinstance(first_message.get("recipient"), dict) else {}
        sender = str(sender_obj.get("id") or payload.get("from") or payload.get("sender") or "unknown")
        text = str(message_data.get("text") or payload.get("text") or payload.get("message") or "")
        conversation_id = str(first_message.get("mid") or payload.get("conversation_id") or payload.get("thread_id") or f"ig:{sender}")

        return {
            "channel_type": "instagram",
            "channel_id": channel_id,
            "external_user_id": sender,
            "external_conversation_id": conversation_id,
            "text": text,
            "external_message_id": str(first_message.get("mid") or ""),
            "event_type": "message_received",
            "metadata": {
                **payload,
                "recipient_id": recipient_obj.get("id"),
            },
        }

"""Helpers de respostas padronizadas com códigos de saída."""

from typing import Any

from fastapi import HTTPException


class Codes:
    SUCCESS_DEFAULT = "OK-0000"
    HEALTH_OK = "OK-HEALTH-200"
    AUTH_REGISTER_OK = "OK-AUTH-201"
    AUTH_LOGIN_OK = "OK-AUTH-200"
    AUTH_LOGOUT_OK = "OK-AUTH-204"
    CHAT_REPLY_OK = "OK-CHAT-200"
    CHAT_IMAGE_OK = "OK-CHAT-IMG-200"
    HISTORY_LIST_OK = "OK-HIST-200"
    HISTORY_CLEAR_OK = "OK-HIST-204"
    MEDIA_IMAGE_OK = "OK-MEDIA-IMG-200"
    MEDIA_AUDIO_OK = "OK-MEDIA-AUD-200"
    MEDIA_VIDEO_OK = "OK-MEDIA-VID-200"
    MEDIA_ANALYZE_OK = "OK-MEDIA-ANL-200"
    BILLING_CHECKOUT_OK = "OK-BILLING-CHK-200"
    BILLING_PLANS_OK = "OK-BILLING-PLANS-200"
    BILLING_WEBHOOK_OK = "OK-BILLING-WH-200"
    BILLING_USAGE_OK = "OK-BILLING-USG-200"
    CONV_LIST_OK = "OK-CONV-200"
    CONV_CREATE_OK = "OK-CONV-201"
    CONV_GET_OK = "OK-CONV-200"
    CONV_DELETE_OK = "OK-CONV-204"
    PROFILE_GET_OK = "OK-PROFILE-200"
    PROFILE_UPDATE_OK = "OK-PROFILE-200"

    BAD_REQUEST = "ERR-REQ-400"
    UNAUTHORIZED = "ERR-AUTH-401"
    FORBIDDEN = "ERR-AUTH-403"
    NOT_FOUND = "ERR-REQ-404"
    VALIDATION = "ERR-REQ-422"
    RATE_LIMIT = "ERR-RATE-429"
    SERVICE_UNAVAILABLE = "ERR-SVC-503"
    INTERNAL = "ERR-SYS-500"


def success(code: str, message: str | None = None, **data: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "status": "sucesso",
        "code": code,
    }
    if message:
        payload["message"] = message
    payload.update(data)
    return payload


def error_payload(code: str, message: str, **data: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "status": "erro",
        "code": code,
        "message": message,
    }
    payload.update(data)
    return payload


def raise_api_error(status_code: int, code: str, message: str, **data: Any) -> None:
    raise HTTPException(status_code=status_code, detail=error_payload(code, message, **data))

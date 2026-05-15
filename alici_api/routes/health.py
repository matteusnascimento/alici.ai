"""Health and status routes."""

from __future__ import annotations

import asyncio
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from alici_api.dependencies import get_current_user
from alici_api.responses import Codes, error_payload, success
from alici_api.services.ai import AIManager, VISAO_DISPONIVEL
from alici_api.services.credit_service import CreditService
from alici_api.services.media_service import MediaProviderUnavailableError, available_media_providers
from alici_api.services.media_storage import R2MediaStorage
from alici_api.services.redis_client import ping_redis
from database import get_db_connection

router = APIRouter(tags=["health"])
credit_service = CreditService()


def _run_async(coro):
    try:
        return asyncio.run(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()


def _text_model_statuses() -> tuple[dict, dict]:
    try:
        from alici_api.services.text_model_r2 import get_text_model_status

        r2_status = get_text_model_status()
    except Exception as exc:
        r2_status = {"disponivel": False, "inicializado": False, "erro": str(exc)}

    try:
        from alici_api.services.text_model_hf import get_hf_model_status

        hf_status = get_hf_model_status()
    except Exception as exc:
        hf_status = {"disponivel": False, "inicializado": False, "erro": str(exc)}

    return r2_status, hf_status


def _database_status() -> dict:
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.fetchone()
            cur.close()
        return {"ok": True}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _redis_status() -> dict:
    try:
        return {"ok": bool(_run_async(ping_redis()))}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _media_provider_statuses() -> dict:
    result = {}
    for media_type in ("image", "audio", "video", "image_analysis"):
        try:
            providers = available_media_providers(media_type)
            result[media_type] = [
                {"provider": provider.provider_name, "model": provider.model_name}
                for provider in providers
            ]
        except MediaProviderUnavailableError as exc:
            result[media_type] = {"available": False, "error": str(exc)}
        except Exception as exc:
            result[media_type] = {"available": False, "error": str(exc)}
    return result


def _storage_status(*, include_probe: bool = False) -> dict:
    try:
        return R2MediaStorage().status(include_probe=include_probe)
    except Exception as exc:
        return {"configured": False, "missing": [], "probe_ok": False, "error": str(exc)}


def _health_payload(*, include_probe: bool = False) -> dict:
    manager = AIManager()
    r2_status, hf_status = _text_model_statuses()
    ai_providers = manager.available_providers()
    redis = _redis_status()
    storage = _storage_status(include_probe=include_probe)
    database = _database_status()
    return {
        "ia_disponivel": bool(ai_providers),
        "ai_providers": ai_providers,
        "ai_provider_status": manager.provider_statuses(include_probe=include_probe),
        "media_provider_status": _media_provider_statuses(),
        "media_storage": storage,
        "visao_disponivel": VISAO_DISPONIVEL,
        "modelo_texto_r2": r2_status,
        "modelo_texto_hf": hf_status,
        "database": database,
        "redis": redis,
        "timestamp": datetime.now().isoformat(),
    }


def _ready_from_payload(payload: dict) -> tuple[bool, list[str]]:
    blockers: list[str] = []
    if not payload["database"].get("ok"):
        blockers.append("database")
    if not payload["redis"].get("ok"):
        blockers.append("redis")
    if not payload["ai_providers"]:
        blockers.append("ai_provider")
    storage = payload.get("media_storage") or {}
    if R2MediaStorage().settings.media_storage_required and not storage.get("configured"):
        blockers.append("r2_storage")
    return not blockers, blockers


@router.get("/health")
@router.get("/health.")
@router.get("/api/health")
@router.get("/v1/health")
def health():
    return success(Codes.HEALTH_OK, **_health_payload(include_probe=False))


@router.get("/health/live")
def health_live():
    return success(Codes.HEALTH_OK, status="live", timestamp=datetime.now().isoformat())


@router.get("/health/ready")
def health_ready():
    payload = _health_payload(include_probe=False)
    payload["ready"], payload["blockers"] = _ready_from_payload(payload)
    if not payload["ready"]:
        return JSONResponse(
            status_code=503,
            content=error_payload(Codes.SERVICE_UNAVAILABLE, "Servico ainda nao esta pronto", **payload),
        )
    return success(Codes.HEALTH_OK, **payload)


@router.get("/health/deep")
def health_deep():
    payload = _health_payload(include_probe=True)
    payload["ready"], payload["blockers"] = _ready_from_payload(payload)
    if payload["media_storage"].get("configured") and payload["media_storage"].get("probe_ok") is False:
        payload["ready"] = False
        payload["blockers"].append("r2_storage_probe")
    if not payload["ready"]:
        return JSONResponse(
            status_code=503,
            content=error_payload(Codes.SERVICE_UNAVAILABLE, "Servico ainda nao esta pronto", **payload),
        )
    return success(Codes.HEALTH_OK, **payload)


@router.get("/api/status")
def api_status(user=Depends(get_current_user)):
    credit_balance = credit_service.get_balance(int(user["id"]))
    health_payload = _health_payload(include_probe=False)
    return success(
        Codes.SUCCESS_DEFAULT,
        usuario={
            "id": user["id"],
            "nome": user["nome"],
            "email": user["email"],
            "plano": user.get("plano", "free"),
        },
        plano=user.get("plano", "free"),
        credit_balance=credit_balance,
        **health_payload,
    )

"""Multimodal media routes backed by durable Arq jobs."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from alici_api.dependencies import get_current_user
from alici_api.responses import Codes, success
from alici_api.schemas import AudioRequest, ImageRequest, VideoRequest
from alici_api.services.ai_cache import AICache
from alici_api.services.credit_service import CreditService, InsufficientCreditsError
from alici_api.services.generation_job_service import GenerationJobService
from alici_api.services.media_service import MediaProviderUnavailableError, ensure_media_provider_available
from alici_api.services.media_uploads import save_upload_for_job
from alici_api.services.prompt_security import PromptSecurityError, validate_prompt
from logger import get_logger

router = APIRouter(tags=["media"])
logger_media = get_logger("route_media")
credit_service = CreditService()
job_service = GenerationJobService(credit_service=credit_service)
ai_cache = AICache()

ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/gif", "image/bmp", "image/webp"}


def _raise_insufficient_credits(exc: InsufficientCreditsError) -> None:
    raise HTTPException(
        status_code=402,
        detail={
            "code": Codes.PAYMENT_REQUIRED,
            "message": "Creditos insuficientes para concluir esta operacao",
            "balance": exc.balance,
            "required": exc.required,
        },
    )


def _sanitize_prompt_or_400(prompt: str, *, purpose: str) -> str:
    try:
        return validate_prompt(prompt, purpose=purpose)
    except PromptSecurityError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "code": Codes.PROMPT_BLOCKED,
                "message": str(exc),
                "risk_score": exc.risk_score,
                "findings": exc.findings,
            },
        )


def _ensure_media_or_503(media_type: str) -> None:
    try:
        ensure_media_provider_available(media_type)
    except MediaProviderUnavailableError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "code": Codes.SERVICE_UNAVAILABLE,
                "message": str(exc),
                "media_type": exc.media_type,
                "charged": False,
            },
        )


def _queued_payload(result: dict, *, user: dict, message: str) -> dict:
    job = result["job"]
    return success(
        Codes.JOB_QUEUED_OK,
        message=message,
        job_id=job["id"],
        status=job["status"],
        job_type=job["job_type"],
        progress=job["progress"],
        queue_name=result["queue_name"],
        priority=result["priority"],
        usuario=user["nome"],
        credit_cost=job["cost"],
        credit_balance=result["credit_balance"],
        status_url=f"/jobs/{job['id']}",
    )


def _cache_system_prompt(**parts: object) -> str:
    return ";".join(f"{key}={value}" for key, value in sorted(parts.items()) if value is not None)


async def _cached_media_payload(
    *,
    operation: str,
    prompt: str,
    system_prompt: str = "",
    user: dict,
    media_code: str,
) -> dict | None:
    cached = await ai_cache.get_payload(operation=operation, prompt=prompt, system_prompt=system_prompt)
    if not cached:
        return None

    credit_balance = credit_service.get_balance(int(user["id"]))
    return success(
        media_code,
        message="Resultado reutilizado do cache",
        cached=True,
        status="completed",
        progress=100,
        result_url=cached.get("result_url"),
        result_payload=cached.get("result_payload") or {},
        provider=cached.get("provider"),
        model=cached.get("model"),
        usuario=user["nome"],
        credit_cost=0,
        credit_balance=credit_balance,
        cost_saved_credits=int(cached.get("original_cost") or 0),
    )


async def _create_job_or_http_error(**kwargs) -> dict:
    try:
        return await job_service.create_paid_job(**kwargs)
    except InsufficientCreditsError as exc:
        _raise_insufficient_credits(exc)
        raise
    except HTTPException:
        raise
    except Exception:
        logger_media.exception("Falha ao criar/enfileirar job de midia")
        raise HTTPException(
            status_code=503,
            detail={
                "code": Codes.SERVICE_UNAVAILABLE,
                "message": "Nao foi possivel enfileirar a geracao agora. Tente novamente em instantes.",
            },
        )


@router.post("/generate-image", status_code=status.HTTP_202_ACCEPTED)
async def generate_image_endpoint(req: ImageRequest, user=Depends(get_current_user)):
    prompt = _sanitize_prompt_or_400((req.prompt or "").strip(), purpose="image")
    _ensure_media_or_503("image")
    cache_key = _cache_system_prompt(resolution="1024x1024")
    cached = await _cached_media_payload(
        operation="media:image",
        prompt=prompt,
        system_prompt=cache_key,
        user=user,
        media_code=Codes.MEDIA_IMAGE_OK,
    )
    if cached:
        return cached

    cost = credit_service.calculate_cost(job_type="image", model="default-image", resolution="1024x1024")
    result = await _create_job_or_http_error(
        user=user,
        job_type="image",
        prompt=prompt,
        cost=cost,
        model="default-image",
        reason="image_generation",
        metadata={"endpoint": "/generate-image", "prompt_chars": len(prompt), "resolution": "1024x1024"},
    )
    return _queued_payload(result, user=user, message="Geracao de imagem enfileirada")


@router.post("/generate-audio", status_code=status.HTTP_202_ACCEPTED)
async def generate_audio_endpoint(req: AudioRequest, user=Depends(get_current_user)):
    texto = _sanitize_prompt_or_400((req.texto or "").strip(), purpose="audio")
    _ensure_media_or_503("audio")
    cached = await _cached_media_payload(
        operation="media:audio",
        prompt=texto,
        user=user,
        media_code=Codes.MEDIA_AUDIO_OK,
    )
    if cached:
        return cached

    cost = credit_service.calculate_cost(job_type="audio", model="default-audio")
    result = await _create_job_or_http_error(
        user=user,
        job_type="audio",
        prompt=texto,
        cost=cost,
        model="default-audio",
        reason="audio_generation",
        metadata={"endpoint": "/generate-audio", "prompt_chars": len(texto)},
    )
    return _queued_payload(result, user=user, message="Geracao de audio enfileirada")


@router.post("/generate-video", status_code=status.HTTP_202_ACCEPTED)
async def generate_video_endpoint(req: VideoRequest, user=Depends(get_current_user)):
    prompt = _sanitize_prompt_or_400((req.prompt or "").strip(), purpose="video")
    _ensure_media_or_503("video")
    cache_key = _cache_system_prompt(resolution="720p", duration_seconds=5)
    cached = await _cached_media_payload(
        operation="media:video",
        prompt=prompt,
        system_prompt=cache_key,
        user=user,
        media_code=Codes.MEDIA_VIDEO_OK,
    )
    if cached:
        return cached

    cost = credit_service.calculate_cost(
        job_type="video",
        model="default-video",
        resolution="720p",
        duration_seconds=5,
    )
    result = await _create_job_or_http_error(
        user=user,
        job_type="video",
        prompt=prompt,
        cost=cost,
        model="default-video",
        reason="video_generation",
        metadata={"endpoint": "/generate-video", "prompt_chars": len(prompt), "resolution": "720p", "duration_seconds": 5},
    )
    return _queued_payload(result, user=user, message="Geracao de video enfileirada")


@router.post("/analyze-image", status_code=status.HTTP_202_ACCEPTED)
async def analyze_image_endpoint(file: UploadFile = File(...), user=Depends(get_current_user)):
    _ensure_media_or_503("image_analysis")
    job_id = job_service.new_job_id("image_analysis")
    saved = await save_upload_for_job(file, job_id=job_id, allowed_types=ALLOWED_IMAGE_TYPES)
    cost = credit_service.calculate_cost(job_type="image", model="default-image", resolution="1024x1024")
    result = await _create_job_or_http_error(
        user=user,
        job_type="image_analysis",
        prompt=f"[image-analysis] {saved.filename}",
        cost=cost,
        model="default-image",
        reason="image_analysis",
        input_path=saved.path,
        job_id=job_id,
        metadata={
            "endpoint": "/analyze-image",
            "filename": saved.filename,
            "content_type": saved.content_type,
            "size_bytes": saved.size_bytes,
        },
    )
    return _queued_payload(result, user=user, message="Analise de imagem enfileirada")

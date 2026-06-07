"""Arq worker functions for media generation jobs."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from alici_api.config import get_settings
from alici_api.monitoring import capture_critical_event
from alici_api.repositories.generation_job_repository import GenerationJobRepository
from alici_api.services.ai_cache import AICache
from alici_api.services.credit_service import CreditService
from alici_api.services.media_service import MediaProviderUnavailableError, generate_audio, generate_image, generate_video, unavailable_message
from logger import get_logger


logger_jobs = get_logger("generation_worker")


def _should_dead_letter(ctx: dict[str, Any], job: dict[str, Any]) -> bool:
    job_try = int(ctx.get("job_try") or 1)
    max_retries = int(job.get("max_retries") or get_settings().arq_max_retries)
    return job_try >= max_retries


def _remove_input_file(job: dict[str, Any]) -> None:
    input_path = job.get("input_path")
    if not input_path:
        return
    try:
        Path(str(input_path)).unlink(missing_ok=True)
    except Exception:
        logger_jobs.warning("generation_input_cleanup_failed", extra={"job_id": job.get("id"), "input_path": input_path})


def _refund_job_if_needed(job: dict[str, Any], *, error_message: str | None = None) -> None:
    if not job or job.get("refunded_at") or int(job.get("cost") or 0) <= 0:
        return

    credit_service = CreditService()
    repo = GenerationJobRepository()
    try:
        credit_service.refund_credits(
            user_id=int(job["user_id"]),
            amount=int(job["cost"]),
            reason="generation_failed_refund",
            provider=job.get("provider"),
            model=job.get("model"),
            job_id=str(job["id"]),
            metadata={
                "job_type": job.get("job_type"),
                "error_message": error_message or job.get("error_message"),
            },
        )
    except Exception as exc:
        if "uq_credit_refund_job_reason" not in str(exc):
            logger_jobs.exception("generation_refund_failed", extra={"job_id": job.get("id")})
            raise

    repo.mark_refunded(str(job["id"]))
    logger_jobs.info("generation_refunded", extra={"job_id": job.get("id"), "cost": job.get("cost")})


def _charge_job_if_needed(job: dict[str, Any]) -> None:
    metadata = job.get("metadata") or {}
    if not metadata.get("charge_on_success") or int(job.get("cost") or 0) <= 0:
        return

    reason = str(metadata.get("charge_reason") or "generation_success_charge")
    job_id = str(job["id"])
    credit_service = CreditService()
    if credit_service.transaction_exists(job_id=job_id, reason=reason, transaction_type="spend"):
        return

    credit_service.spend_credits(
        user_id=int(job["user_id"]),
        amount=int(job["cost"]),
        reason=reason,
        provider=job.get("provider"),
        model=job.get("model"),
        job_id=job_id,
        metadata={
            "job_type": job.get("job_type"),
            "result_url": job.get("result_url"),
        },
    )
    logger_jobs.info("generation_charged", extra={"job_id": job_id, "cost": job.get("cost"), "reason": reason})


def _media_cache_system_prompt(job: dict[str, Any]) -> str:
    metadata = job.get("metadata") or {}
    if job.get("job_type") == "image":
        return "resolution=1024x1024"
    if job.get("job_type") == "video":
        return f"duration_seconds={metadata.get('duration_seconds') or 5};resolution={metadata.get('resolution') or '720p'}"
    return ""


async def _store_media_cache(job: dict[str, Any], *, result_url: str | None, payload: dict[str, Any]) -> None:
    job_type = job.get("job_type")
    if job_type not in {"image", "audio", "video"}:
        return
    await AICache().set_payload(
        operation=f"media:{job_type}",
        prompt=str(job.get("prompt") or ""),
        system_prompt=_media_cache_system_prompt(job),
        payload={
            "job_type": job_type,
            "provider": job.get("provider"),
            "model": job.get("model"),
            "result_url": result_url,
            "result_payload": payload,
            "original_cost": int(job.get("cost") or 0),
        },
    )


async def _run_image_job(repo: GenerationJobRepository, job: dict[str, Any]) -> tuple[str | None, dict[str, Any]]:
    repo.update_progress(job["id"], 35)
    url = await asyncio.to_thread(generate_image, job["prompt"])
    repo.update_progress(job["id"], 90)
    return url, {"url": url}


async def _run_audio_job(repo: GenerationJobRepository, job: dict[str, Any]) -> tuple[str | None, dict[str, Any]]:
    repo.update_progress(job["id"], 35)
    url = await asyncio.to_thread(generate_audio, job["prompt"])
    repo.update_progress(job["id"], 90)
    return url, {"audio_url": url}


async def _run_video_job(repo: GenerationJobRepository, job: dict[str, Any]) -> tuple[str | None, dict[str, Any]]:
    repo.update_progress(job["id"], 35)
    payload = await asyncio.to_thread(generate_video, job["prompt"])
    repo.update_progress(job["id"], 90)
    return payload.get("video_url"), payload


async def _run_image_analysis_job(repo: GenerationJobRepository, job: dict[str, Any]) -> tuple[str | None, dict[str, Any]]:
    input_path = job.get("input_path")
    if not input_path or not Path(str(input_path)).exists():
        raise RuntimeError("Arquivo de entrada nao encontrado para analise")

    metadata = job.get("metadata") or {}
    filename = metadata.get("filename") or Path(str(input_path)).name
    content_type = metadata.get("content_type") or "image/unknown"

    repo.update_progress(job["id"], 25)
    try:
        from alici_api.services.ai import VISAO_DISPONIVEL, fazer_predicao, gerar_resposta_predicao

        if VISAO_DISPONIVEL:
            prediction = await asyncio.to_thread(fazer_predicao, str(input_path), 3)
            if prediction.get("status") == "erro":
                raise RuntimeError(prediction.get("erro") or "Falha no modelo de visao")
            repo.update_progress(job["id"], 80)
            payload: dict[str, Any] = {"resultado": prediction}
            if job.get("job_type") == "chat_image_analysis":
                resposta = gerar_resposta_predicao(prediction)
                payload["resposta"] = resposta
                payload["classe"] = prediction.get("classe")
                payload["confianca"] = prediction.get("confianca")
                try:
                    from alici_api.repositories.history_repository import HistoryRepository

                    HistoryRepository().save(
                        int(job["user_id"]),
                        f"[Analise de imagem] {prediction.get('classe')}",
                        resposta,
                    )
                except Exception:
                    logger_jobs.warning("chat_image_history_save_failed", extra={"job_id": job.get("id")})
            return None, payload
    except RuntimeError:
        raise
    except Exception:
        logger_jobs.exception("vision_model_failed", extra={"job_id": job.get("id")})

    raise MediaProviderUnavailableError(str(job.get("job_type") or "image_analysis"), unavailable_message("image_analysis"))


async def run_generation_job(ctx: dict[str, Any], job_id: str) -> dict[str, Any]:
    repo = GenerationJobRepository()
    job = repo.mark_processing(job_id)
    if not job:
        raise RuntimeError(f"Job {job_id} nao encontrado")

    logger_jobs.info(
        "generation_job_started",
        extra={"job_id": job_id, "job_type": job.get("job_type"), "attempt": ctx.get("job_try")},
    )

    try:
        job_type = job.get("job_type")
        if job_type == "image":
            result_url, payload = await _run_image_job(repo, job)
        elif job_type == "audio":
            result_url, payload = await _run_audio_job(repo, job)
        elif job_type == "video":
            result_url, payload = await _run_video_job(repo, job)
        elif job_type in {"image_analysis", "chat_image_analysis"}:
            result_url, payload = await _run_image_analysis_job(repo, job)
        else:
            raise RuntimeError(f"Tipo de job nao suportado: {job_type}")

        completed = repo.complete_job(job_id, result_url=result_url, result_payload=payload)
        _charge_job_if_needed(completed or job)
        await _store_media_cache(completed or job, result_url=result_url, payload=payload)
        _remove_input_file(completed or job)
        logger_jobs.info("generation_job_completed", extra={"job_id": job_id, "job_type": job_type})
        return {"job_id": job_id, "status": "completed", **payload}

    except Exception as exc:
        final_try = _should_dead_letter(ctx, job)
        failed = repo.fail_job(job_id, error_message=str(exc), dead_letter=final_try)
        if final_try:
            _refund_job_if_needed(failed or job, error_message=str(exc))
            _remove_input_file(failed or job)
            capture_critical_event(
                "generation_dead_letter",
                level="error",
                tags={"job_type": str(job.get("job_type")), "job_id": job_id},
                extra={"error": str(exc), "attempt": ctx.get("job_try")},
            )
            redis = ctx.get("redis")
            if redis is not None:
                try:
                    await redis.enqueue_job(
                        "record_dead_letter_job",
                        job_id,
                        str(exc),
                        _queue_name=get_settings().arq_queue_dlq,
                    )
                except Exception:
                    logger_jobs.warning("dead_letter_enqueue_failed", extra={"job_id": job_id})
        logger_jobs.exception(
            "generation_job_failed",
            extra={"job_id": job_id, "final_try": final_try, "attempt": ctx.get("job_try")},
        )
        raise


async def record_dead_letter_job(ctx: dict[str, Any], job_id: str, error_message: str) -> dict[str, Any]:
    repo = GenerationJobRepository()
    job = repo.fail_job(job_id, error_message=error_message, dead_letter=True)
    _refund_job_if_needed(job or repo.get_job(job_id), error_message=error_message)
    logger_jobs.error("generation_dead_letter", extra={"job_id": job_id, "error_message": error_message[:500]})
    return {"job_id": job_id, "status": "dead_letter_recorded"}

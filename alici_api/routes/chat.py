"""Chat routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from alici_api.dependencies import get_current_user
from alici_api.repositories.history_repository import HistoryRepository
from alici_api.responses import Codes, success
from alici_api.schemas import ChatRequest
from alici_api.services.ai import IA_DISPONIVEL
from alici_api.services.ai_service import actual_chat_cost, estimate_chat_cost, generate_chat_response, get_cached_chat_response
from alici_api.services.credit_service import CreditService, InsufficientCreditsError
from alici_api.services.generation_job_service import GenerationJobService
from alici_api.services.media_service import MediaProviderUnavailableError, ensure_media_provider_available
from alici_api.services.media_uploads import save_upload_for_job
from alici_api.services.prompt_security import PromptSecurityError, validate_prompt
from database import contar_mensagens_hoje
from logger import get_logger
from sistema_emocoes import adicionar_metadados_resposta

router = APIRouter(tags=["chat"])
logger_chat = get_logger("route_chat")
history_repository = HistoryRepository()
credit_service = CreditService()
job_service = GenerationJobService(credit_service=credit_service)

ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/gif", "image/bmp", "image/webp"}


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


def _spend_or_402(
    *,
    user_id: int,
    amount: int,
    reason: str,
    provider: str | None = None,
    model: str | None = None,
    metadata: dict | None = None,
) -> int:
    try:
        return credit_service.spend_credits(
            user_id=user_id,
            amount=amount,
            reason=reason,
            provider=provider,
            model=model,
            metadata=metadata,
        )
    except InsufficientCreditsError as exc:
        _raise_insufficient_credits(exc)
        raise


def _prompt_or_400(prompt: str, *, purpose: str) -> str:
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


def _ensure_chat_image_or_503() -> None:
    try:
        ensure_media_provider_available("chat_image_analysis")
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


@router.post("/chat")
async def chat(req: ChatRequest, user=Depends(get_current_user)):
    if not IA_DISPONIVEL:
        raise HTTPException(
            status_code=503,
            detail={"code": Codes.SERVICE_UNAVAILABLE, "message": "Servico de IA nao disponivel"},
        )

    safe_prompt = _prompt_or_400((req.pergunta or "").strip(), purpose="chat")
    plano = (user.get("plano") or "free").lower()

    limite_por_plano = {
        "free": 20,
        "pro": 300,
        "ultra": 2000,
        "enterprise": None,
    }
    limite = limite_por_plano.get(plano, 20)

    if limite is not None:
        mensagens_hoje = contar_mensagens_hoje(user["id"])
        if mensagens_hoje >= limite:
            raise HTTPException(
                status_code=403,
                detail={
                    "code": Codes.FORBIDDEN,
                    "message": f"Limite diario do plano {plano} atingido ({limite} mensagens)",
                    "plano": plano,
                    "limite_diario": limite,
                    "mensagens_hoje": mensagens_hoje,
                },
            )

    try:
        cached_response = await get_cached_chat_response(safe_prompt)
        cost_estimate = None
        chat_cost = 0
        credit_balance = credit_service.get_balance(user["id"])
        provider = cached_response.provider if cached_response else None
        model = cached_response.model if cached_response else None

        if cached_response:
            ai_response = await generate_chat_response(safe_prompt)
        else:
            cost_estimate = estimate_chat_cost(safe_prompt)
            provider = cost_estimate.provider
            model = cost_estimate.model
            chat_cost = cost_estimate.cost_credits
            if chat_cost > 0:
                credit_balance = _spend_or_402(
                    user_id=user["id"],
                    amount=chat_cost,
                    reason="chat_generation",
                    provider=provider,
                    model=model,
                    metadata={
                        "endpoint": "/chat",
                        "plano": plano,
                        "prompt_chars": len(safe_prompt),
                        "fallback_order": cost_estimate.fallback_order,
                    },
                )

            ai_response = await generate_chat_response(safe_prompt)
            credit_balance = credit_service.get_balance(user["id"])

            actual_cost = actual_chat_cost(ai_response)
            if chat_cost > actual_cost:
                adjustment = chat_cost - actual_cost
                credit_balance = credit_service.refund_credits(
                    user_id=user["id"],
                    amount=adjustment,
                    reason="chat_generation_cost_adjustment_refund",
                    provider=ai_response.provider,
                    model=ai_response.model,
                    metadata={
                        "endpoint": "/chat",
                        "reserved_cost": chat_cost,
                        "actual_cost": actual_cost,
                    },
                )
                chat_cost = actual_cost

        resposta = ai_response.content
        resultado_emocao = adicionar_metadados_resposta(resposta) if req.incluir_emocao else None
        history_repository.save(user["id"], safe_prompt, resposta)

        payload = {
            "resposta": resposta,
            "provider": ai_response.provider,
            "modelo": ai_response.model,
            "tempo_resposta_ms": ai_response.response_time_ms,
            "tokens_estimados": ai_response.estimated_tokens,
            "cached": ai_response.cached,
            "credit_cost": chat_cost,
            "credit_balance": credit_balance,
            "usuario": user["nome"],
            "plano": plano,
            "limite_diario": limite,
            "mensagens_hoje": contar_mensagens_hoje(user["id"]),
        }

        if resultado_emocao:
            payload["emocao"] = resultado_emocao.get("emocao")
            payload["intensidade"] = resultado_emocao.get("intensidade")

        return success(Codes.CHAT_REPLY_OK, **payload)
    except HTTPException:
        raise
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
    except RuntimeError as exc:
        if "chat_cost" in locals() and chat_cost > 0:
            try:
                credit_balance = credit_service.refund_credits(
                    user_id=user["id"],
                    amount=chat_cost,
                    reason="chat_generation_failed_refund",
                    provider=provider,
                    model=model,
                    metadata={
                        "endpoint": "/chat",
                        "plano": plano,
                        "prompt_chars": len(safe_prompt),
                        "error": str(exc)[:500],
                    },
                )
                logger_chat.info(
                    "chat_credit_refunded",
                    extra={"user_id": user["id"], "amount": chat_cost, "balance": credit_balance},
                )
            except Exception:
                logger_chat.exception("Falha ao reembolsar creditos do chat")
        logger_chat.warning(f"IA indisponivel ao processar /chat: {exc}")
        raise HTTPException(
            status_code=503,
            detail={"code": Codes.SERVICE_UNAVAILABLE, "message": "Servico de IA nao disponivel"},
        )
    except Exception:
        if "chat_cost" in locals() and chat_cost > 0:
            try:
                credit_service.refund_credits(
                    user_id=user["id"],
                    amount=chat_cost,
                    reason="chat_generation_failed_refund",
                    provider=provider,
                    model=model,
                    metadata={
                        "endpoint": "/chat",
                        "plano": plano,
                        "prompt_chars": len(safe_prompt),
                        "error": "internal_error",
                    },
                )
                logger_chat.info("chat_credit_refunded", extra={"user_id": user["id"], "amount": chat_cost})
            except Exception:
                logger_chat.exception("Falha ao reembolsar creditos do chat")
        logger_chat.exception("Erro interno ao processar /chat")
        raise HTTPException(
            status_code=500,
            detail={"code": Codes.INTERNAL, "message": "Erro interno do servidor"},
        )


@router.post("/chat/image", status_code=status.HTTP_202_ACCEPTED)
async def chat_image(user=Depends(get_current_user), imagem: UploadFile = File(...)):
    _ensure_chat_image_or_503()

    if imagem.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail={"code": Codes.BAD_REQUEST, "message": "Tipo de arquivo nao suportado"},
        )

    plano = (user.get("plano") or "free").lower()

    try:
        job_id = job_service.new_job_id("chat_image_analysis")
        saved = await save_upload_for_job(imagem, job_id=job_id, allowed_types=ALLOWED_IMAGE_TYPES)
        analysis_cost = credit_service.calculate_cost(
            job_type="image",
            provider=None,
            model="default-image",
            resolution="1024x1024",
        )
        result = await job_service.create_paid_job(
            user=user,
            job_id=job_id,
            job_type="chat_image_analysis",
            prompt=f"[chat-image-analysis] {saved.filename}",
            cost=analysis_cost,
            model="default-image",
            reason="image_analysis",
            input_path=saved.path,
            metadata={
                "endpoint": "/chat/image",
                "filename": saved.filename,
                "content_type": saved.content_type,
                "size_bytes": saved.size_bytes,
            },
        )
        job = result["job"]
        return success(
            Codes.JOB_QUEUED_OK,
            message="Analise de imagem enfileirada",
            job_id=job["id"],
            status=job["status"],
            job_type=job["job_type"],
            progress=job["progress"],
            credit_cost=analysis_cost,
            credit_balance=result["credit_balance"],
            status_url=f"/jobs/{job['id']}",
        )
    except HTTPException:
        raise
    except InsufficientCreditsError as exc:
        _raise_insufficient_credits(exc)
        raise
    except Exception:
        logger_chat.exception("Erro interno ao enfileirar /chat/image")
        raise HTTPException(
            status_code=503,
            detail={"code": Codes.SERVICE_UNAVAILABLE, "message": "Nao foi possivel enfileirar a analise agora"},
        )

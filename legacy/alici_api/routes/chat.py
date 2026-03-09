"""Chat routes."""

import os
import tempfile
import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from alici_api.dependencies import get_current_user
from alici_api.repositories.history_repository import HistoryRepository
from alici_api.responses import Codes, success
from alici_api.schemas import ChatRequest
from alici_api.services.ai import (
    IA_DISPONIVEL,
    VISAO_DISPONIVEL,
    fazer_predicao,
    gerar_resposta,
    gerar_resposta_com_emocao,
    gerar_resposta_predicao,
)
from database import contar_mensagens_hoje
from logger import get_logger

router = APIRouter(tags=["chat"])
logger_chat = get_logger("route_chat")
history_repository = HistoryRepository()
_rate_lock = Lock()
_chat_rate_bucket: dict[str, deque[float]] = defaultdict(deque)


def _enforce_chat_rate_limit(user_id: int, plano: str) -> None:
    limits_per_minute = {
        "free": 20,
        "pro": 120,
        "ultra": 300,
        "enterprise": None,
    }
    max_requests = limits_per_minute.get(plano, 20)
    if max_requests is None:
        return

    now = time.time()
    window_seconds = 60
    key = f"user:{user_id}:chat"

    with _rate_lock:
        dq = _chat_rate_bucket[key]
        while dq and now - dq[0] > window_seconds:
            dq.popleft()

        if len(dq) >= max_requests:
            raise HTTPException(
                status_code=429,
                detail={
                    "code": Codes.RATE_LIMIT,
                    "message": f"Limite de requisições por minuto atingido para o plano {plano}",
                    "plano": plano,
                    "limite_por_minuto": max_requests,
                },
            )

        dq.append(now)


@router.post("/chat")
def chat(req: ChatRequest, user=Depends(get_current_user)):
    if not IA_DISPONIVEL:
        raise HTTPException(
            status_code=503,
            detail={"code": Codes.SERVICE_UNAVAILABLE, "message": "Serviço de IA não disponível"},
        )

    if not req.pergunta or not req.pergunta.strip():
        raise HTTPException(
            status_code=400,
            detail={"code": Codes.BAD_REQUEST, "message": "Pergunta vazia"},
        )

    plano = (user.get("plano") or "free").lower()
    _enforce_chat_rate_limit(user["id"], plano)

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
                    "message": f"Limite diário do plano {plano} atingido ({limite} mensagens)",
                    "plano": plano,
                    "limite_diario": limite,
                    "mensagens_hoje": mensagens_hoje,
                },
            )

    try:
        if req.incluir_emocao:
            resultado_emocao = gerar_resposta_com_emocao(req.pergunta)
            resposta = resultado_emocao.get("resposta", "")
        else:
            resultado_emocao = None
            resposta = gerar_resposta(req.pergunta)

        history_repository.save(user["id"], req.pergunta, resposta)

        payload = {
            "resposta": resposta,
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
    except Exception:
        logger_chat.exception("Erro interno ao processar /chat")
        raise HTTPException(
            status_code=500,
            detail={"code": Codes.INTERNAL, "message": "Erro interno do servidor"},
        )


@router.post("/chat/image")
def chat_image(user=Depends(get_current_user), imagem: UploadFile = File(...)):
    if not IA_DISPONIVEL or not VISAO_DISPONIVEL:
        raise HTTPException(
            status_code=503,
            detail={"code": Codes.SERVICE_UNAVAILABLE, "message": "Modelo não disponível"},
        )

    if imagem.content_type not in ["image/png", "image/jpeg", "image/gif", "image/bmp", "image/webp"]:
        raise HTTPException(
            status_code=400,
            detail={"code": Codes.BAD_REQUEST, "message": "Tipo de arquivo não suportado"},
        )

    plano = (user.get("plano") or "free").lower()
    _enforce_chat_rate_limit(user["id"], plano)

    ext_map = {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/gif": ".gif",
        "image/bmp": ".bmp",
        "image/webp": ".webp",
    }
    suffix = ext_map.get(imagem.content_type or "", ".png")
    tmp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(imagem.file.read())
            tmp_path = tmp.name

        resultado = fazer_predicao(tmp_path, top_k=3)
        if resultado.get("status") == "erro":
            raise HTTPException(
                status_code=400,
                detail={"code": Codes.BAD_REQUEST, "message": resultado.get("erro") or "Erro na análise da imagem"},
            )

        resposta = gerar_resposta_predicao(resultado)
        pergunta = f"[Análise de imagem] {resultado.get('classe')}"
        history_repository.save(user["id"], pergunta, resposta)

        return success(
            Codes.CHAT_IMAGE_OK,
            classe=resultado["classe"],
            confianca=resultado["confianca"],
            resposta=resposta,
            alternativas=resultado.get("top_k", [])[1:],
        )
    except HTTPException:
        raise
    except Exception:
        logger_chat.exception("Erro interno ao processar /chat/image")
        raise HTTPException(
            status_code=500,
            detail={"code": Codes.INTERNAL, "message": "Erro interno do servidor"},
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                logger_chat.warning("Falha ao remover arquivo temporário", extra={"tmp_path": tmp_path})

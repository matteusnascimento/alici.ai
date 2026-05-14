"""Health and status routes."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends

from alici_api.dependencies import get_current_user
from alici_api.responses import Codes, success
from alici_api.services.ai import AIManager, IA_DISPONIVEL, VISAO_DISPONIVEL
from alici_api.services.credit_service import CreditService

router = APIRouter(tags=["health"])
credit_service = CreditService()


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


@router.get("/health")
@router.get("/health.")
@router.get("/api/health")
@router.get("/v1/health")
def health():
    r2_status, hf_status = _text_model_statuses()
    return success(
        Codes.HEALTH_OK,
        ia_disponivel=IA_DISPONIVEL,
        ai_providers=AIManager().available_providers(),
        visao_disponivel=VISAO_DISPONIVEL,
        modelo_texto_r2=r2_status,
        modelo_texto_hf=hf_status,
        timestamp=datetime.now().isoformat(),
    )


@router.get("/api/status")
def api_status(user=Depends(get_current_user)):
    r2_status, hf_status = _text_model_statuses()
    credit_balance = credit_service.get_balance(int(user["id"]))
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
        ia_disponivel=IA_DISPONIVEL,
        ai_providers=AIManager().available_providers(),
        visao_disponivel=VISAO_DISPONIVEL,
        modelo_texto_r2=r2_status,
        modelo_texto_hf=hf_status,
        timestamp=datetime.now().isoformat(),
    )

"""Health and status routes."""

from datetime import datetime

from fastapi import APIRouter, Depends

from alici_api.dependencies import get_current_user
from alici_api.services.ai import IA_DISPONIVEL, VISAO_DISPONIVEL
from alici_api.services.text_model_r2 import get_text_model_status

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    text_model_status = get_text_model_status()
    return {
        "status": "ok",
        "ia_disponivel": IA_DISPONIVEL,
        "visao_disponivel": VISAO_DISPONIVEL,
        "modelo_texto_r2": text_model_status,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/api/status")
def api_status(user=Depends(get_current_user)):
    text_model_status = get_text_model_status()
    return {
        "usuario": {
            "id": user["id"],
            "nome": user["nome"],
            "email": user["email"],
            "plano": user["plano"],
        },
        "plano": user["plano"],
        "ia_disponivel": IA_DISPONIVEL,
        "visao_disponivel": VISAO_DISPONIVEL,
        "modelo_texto_r2": text_model_status,
        "timestamp": datetime.now().isoformat(),
    }

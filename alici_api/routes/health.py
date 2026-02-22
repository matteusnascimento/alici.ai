"""Health and status routes."""

from datetime import datetime

from fastapi import APIRouter, Depends

from alici_api.dependencies import get_current_user
from alici_api.services.ai import IA_DISPONIVEL, VISAO_DISPONIVEL

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {
        "status": "ok",
        "ia_disponivel": IA_DISPONIVEL,
        "visao_disponivel": VISAO_DISPONIVEL,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/api/status")
def api_status(user=Depends(get_current_user)):
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
        "timestamp": datetime.now().isoformat(),
    }

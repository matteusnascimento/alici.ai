"""User history routes."""

from fastapi import APIRouter, Depends, HTTPException

from alici_api.dependencies import get_current_user
from database import buscar_historico, limpar_historico

router = APIRouter(prefix="/history", tags=["history"])


@router.get("")
def get_history(limit: int = 50, user=Depends(get_current_user)):
    limit = max(1, min(limit, 200))
    historico = buscar_historico(user["id"], limit)

    return {
        "status": "sucesso",
        "total": len(historico),
        "historico": historico,
    }


@router.delete("")
def delete_history(user=Depends(get_current_user)):
    try:
        limpar_historico(user["id"])
        return {"status": "sucesso", "mensagem": "Histórico limpo"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

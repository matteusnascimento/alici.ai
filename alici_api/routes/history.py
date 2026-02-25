"""User history routes."""

from fastapi import APIRouter, Depends, HTTPException

from alici_api.dependencies import get_current_user
from alici_api.repositories.history_repository import HistoryRepository
from alici_api.responses import Codes, success
from logger import get_logger

router = APIRouter(prefix="/history", tags=["history"])
logger_history = get_logger("route_history")
history_repository = HistoryRepository()


@router.get("")
def get_history(limit: int = 50, user=Depends(get_current_user)):
    limit = max(1, min(limit, 200))
    historico = history_repository.list(user["id"], limit)
    return success(Codes.HISTORY_LIST_OK, total=len(historico), historico=historico)


@router.delete("")
def delete_history(user=Depends(get_current_user)):
    try:
        history_repository.clear(user["id"])
        return success(Codes.HISTORY_CLEAR_OK, message="Histórico limpo")
    except Exception:
        logger_history.exception("Erro interno ao limpar histórico")
        raise HTTPException(
            status_code=500,
            detail={"code": Codes.INTERNAL, "message": "Erro interno do servidor"},
        )

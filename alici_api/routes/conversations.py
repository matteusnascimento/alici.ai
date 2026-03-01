"""Conversation management routes (multi-chat)."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from alici_api.dependencies import get_current_user
from alici_api.repositories.conversation_repository import ConversationRepository
from alici_api.responses import Codes, success
from logger import get_logger

router = APIRouter(prefix="/conversations", tags=["conversations"])
logger_conv = get_logger("route_conversations")
conv_repo = ConversationRepository()


class ConvCreateRequest(BaseModel):
    titulo: str = "Nova conversa"


class ConvRenameRequest(BaseModel):
    titulo: str


@router.get("")
def list_conversations(limit: int = 50, user=Depends(get_current_user)):
    limit = max(1, min(limit, 100))
    convs = conv_repo.list(user["id"], limit)
    return success(Codes.CONV_LIST_OK, total=len(convs), conversations=convs)


@router.post("")
def create_conversation(req: ConvCreateRequest, user=Depends(get_current_user)):
    conv = conv_repo.create(user["id"], req.titulo)
    if not conv:
        raise HTTPException(
            status_code=500,
            detail={"code": Codes.INTERNAL, "message": "Erro ao criar conversa"},
        )
    return success(Codes.CONV_CREATE_OK, conversation=conv)


@router.get("/{conv_id}")
def get_conversation(conv_id: int, user=Depends(get_current_user)):
    conv = conv_repo.get(conv_id, user["id"])
    if not conv:
        raise HTTPException(
            status_code=404,
            detail={"code": Codes.NOT_FOUND, "message": "Conversa não encontrada"},
        )
    messages = conv_repo.list_messages(conv_id)
    return success(Codes.CONV_GET_OK, conversation=conv, messages=messages)


@router.patch("/{conv_id}")
def rename_conversation(conv_id: int, req: ConvRenameRequest, user=Depends(get_current_user)):
    conv = conv_repo.get(conv_id, user["id"])
    if not conv:
        raise HTTPException(
            status_code=404,
            detail={"code": Codes.NOT_FOUND, "message": "Conversa não encontrada"},
        )
    titulo = req.titulo.strip()
    if not titulo:
        raise HTTPException(
            status_code=400,
            detail={"code": Codes.BAD_REQUEST, "message": "Título não pode ser vazio"},
        )
    conv_repo.rename(conv_id, user["id"], titulo)
    return success(Codes.CONV_GET_OK, message="Conversa renomeada")


@router.delete("/{conv_id}")
def delete_conversation(conv_id: int, user=Depends(get_current_user)):
    conv = conv_repo.get(conv_id, user["id"])
    if not conv:
        raise HTTPException(
            status_code=404,
            detail={"code": Codes.NOT_FOUND, "message": "Conversa não encontrada"},
        )
    conv_repo.delete(conv_id, user["id"])
    return success(Codes.CONV_DELETE_OK, message="Conversa excluída")

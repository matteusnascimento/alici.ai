"""Conversations routes — multi-conversation chat management."""

from fastapi import APIRouter, Depends, HTTPException

from alici_api.dependencies import get_current_user
from alici_api.responses import Codes, success
from alici_api.schemas import ConversationCreateRequest, MessageCreateRequest
from alici_api.services.huggingface_service import query_huggingface
from database import (
    adicionar_mensagem,
    atualizar_titulo_conversa,
    buscar_conversa,
    criar_conversa,
    deletar_conversa,
    listar_conversas,
    listar_mensagens,
)
from logger import get_logger

router = APIRouter(prefix="/conversations", tags=["conversations"])
logger_conv = get_logger("route_conversations")
_MAX_TITLE_LENGTH = 60


def _check_ownership(conversa_id: int, user_id: int):
    """Raise 404 if conversation not found, 403 if not owned by user."""
    conv = buscar_conversa(conversa_id)
    if not conv:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "Conversa não encontrada"},
        )
    if int(conv["user_id"]) != int(user_id):
        raise HTTPException(
            status_code=403,
            detail={"code": Codes.FORBIDDEN, "message": "Acesso negado"},
        )
    return conv


@router.get("")
def list_conversations(user=Depends(get_current_user)):
    """Lista as 50 conversas mais recentes do usuário."""
    conversations = listar_conversas(user["id"], limite=50)
    return success(Codes.SUCCESS_DEFAULT, conversations=conversations, total=len(conversations))


@router.post("")
def create_conversation(req: ConversationCreateRequest = ConversationCreateRequest(), user=Depends(get_current_user)):
    """Cria uma nova conversa."""
    conv = criar_conversa(user["id"], titulo=req.titulo)
    if not conv:
        raise HTTPException(
            status_code=500,
            detail={"code": Codes.INTERNAL, "message": "Erro ao criar conversa"},
        )
    return success(Codes.SUCCESS_DEFAULT, conversation=conv)


@router.get("/{conversa_id}/messages")
def get_messages(conversa_id: int, user=Depends(get_current_user)):
    """Retorna as mensagens de uma conversa (com verificação de ownership)."""
    _check_ownership(conversa_id, user["id"])
    msgs = listar_mensagens(conversa_id)
    return success(Codes.SUCCESS_DEFAULT, messages=msgs, total=len(msgs))


@router.post("/{conversa_id}/messages")
def add_message(conversa_id: int, req: MessageCreateRequest, user=Depends(get_current_user)):
    """Adiciona uma mensagem do usuário e retorna a resposta da IA."""
    conv = _check_ownership(conversa_id, user["id"])

    content = (req.content or "").strip()
    if not content:
        raise HTTPException(
            status_code=400,
            detail={"code": Codes.BAD_REQUEST, "message": "Mensagem vazia"},
        )

    # Save user message
    adicionar_mensagem(conversa_id, "user", content)

    # Get AI response via HuggingFace service
    try:
        ai_text = query_huggingface(content)
    except Exception as exc:
        logger_conv.warning(f"HuggingFace indisponível, usando fallback: {exc}")
        ai_text = "Desculpe, o serviço de IA está temporariamente indisponível."

    # Save AI response
    ai_msg = adicionar_mensagem(conversa_id, "assistant", ai_text)

    # Auto-title on first exchange (when conversation has no title yet)
    if not conv.get("titulo"):
        titulo = content[:_MAX_TITLE_LENGTH] + ("..." if len(content) > _MAX_TITLE_LENGTH else "")
        atualizar_titulo_conversa(conversa_id, titulo)

    return success(
        Codes.CHAT_REPLY_OK,
        message={"role": "assistant", "content": ai_text},
        conversa_id=conversa_id,
    )


@router.delete("/{conversa_id}")
def delete_conversation(conversa_id: int, user=Depends(get_current_user)):
    """Remove uma conversa e todas as suas mensagens."""
    _check_ownership(conversa_id, user["id"])
    deletar_conversa(conversa_id)
    return success(Codes.SUCCESS_DEFAULT, message="Conversa removida com sucesso")

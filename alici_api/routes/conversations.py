"""Conversations routes for multi-chat support."""

from fastapi import APIRouter, Depends, HTTPException

from alici_api.dependencies import get_current_user
from alici_api.responses import Codes, success
from alici_api.schemas import ConversationChatRequest, CreateConversationRequest
from alici_api.services.ai import IA_DISPONIVEL, gerar_resposta, gerar_resposta_com_emocao
from database import (
    atualizar_titulo_conversa,
    buscar_mensagens_conversa,
    criar_conversa,
    excluir_conversa,
    listar_conversas,
    salvar_mensagem_conversa,
)
from logger import get_logger

router = APIRouter(prefix="/conversations", tags=["conversations"])
logger_conv = get_logger("route_conversations")


@router.get("")
def list_conversations(user=Depends(get_current_user)):
    conversations = listar_conversas(user["id"])
    return success(Codes.SUCCESS_DEFAULT, conversations=conversations, total=len(conversations))


@router.post("")
def create_conversation(req: CreateConversationRequest, user=Depends(get_current_user)):
    titulo = (req.titulo or "Nova Conversa").strip()[:120]
    conv = criar_conversa(user["id"], titulo)
    if not conv:
        raise HTTPException(
            status_code=500,
            detail={"code": Codes.INTERNAL, "message": "Erro ao criar conversa"},
        )
    return success(Codes.SUCCESS_DEFAULT, conversation=conv)


@router.get("/{conversation_id}/messages")
def get_messages(conversation_id: int, user=Depends(get_current_user)):
    messages = buscar_mensagens_conversa(conversation_id, user["id"])
    if messages is None:
        raise HTTPException(
            status_code=404,
            detail={"code": Codes.NOT_FOUND, "message": "Conversa não encontrada"},
        )
    return success(Codes.SUCCESS_DEFAULT, messages=messages, total=len(messages))


@router.post("/{conversation_id}/messages")
def send_message(conversation_id: int, req: ConversationChatRequest, user=Depends(get_current_user)):
    if not req.content or not req.content.strip():
        raise HTTPException(
            status_code=400,
            detail={"code": Codes.BAD_REQUEST, "message": "Mensagem vazia"},
        )

    # Check ownership
    existing = buscar_mensagens_conversa(conversation_id, user["id"])
    if existing is None:
        raise HTTPException(
            status_code=404,
            detail={"code": Codes.NOT_FOUND, "message": "Conversa não encontrada"},
        )

    pergunta = req.content.strip()
    salvar_mensagem_conversa(conversation_id, "user", pergunta)

    resposta = ""
    novo_titulo = None

    if not IA_DISPONIVEL:
        resposta = "Serviço de IA temporariamente indisponível. Tente novamente mais tarde."
    else:
        try:
            if req.incluir_emocao:
                resultado = gerar_resposta_com_emocao(pergunta)
                resposta = resultado.get("resposta", "")
            else:
                resposta = gerar_resposta(pergunta)
        except Exception:
            logger_conv.exception("Erro ao gerar resposta da IA")
            resposta = "Não foi possível gerar uma resposta no momento."

    salvar_mensagem_conversa(conversation_id, "assistant", resposta)

    # Update conversation title on first message exchange
    if not existing:
        titulo = pergunta[:60]
        atualizar_titulo_conversa(conversation_id, user["id"], titulo)
        novo_titulo = titulo

    payload = {
        "resposta": resposta,
        "conversation_id": conversation_id,
    }
    if novo_titulo:
        payload["novo_titulo"] = novo_titulo

    return success(Codes.CHAT_REPLY_OK, **payload)


@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: int, user=Depends(get_current_user)):
    deleted = excluir_conversa(conversation_id, user["id"])
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail={"code": Codes.NOT_FOUND, "message": "Conversa não encontrada"},
        )
    return success(Codes.SUCCESS_DEFAULT, message="Conversa excluída")

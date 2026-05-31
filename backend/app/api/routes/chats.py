from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.agent import Agent
from app.models.agent_channel import AgentChannel
from app.models.agent_conversation import AgentConversation
from app.models.agent_message import AgentMessage
from app.models.reservation import Reservation
from app.models.user import User
from app.services.ai.manager import AIManager
from app.services.ai.providers.base import ProviderError

router = APIRouter(prefix="/chats", tags=["chats"])

SUPPORTED_CHANNELS = [
    {"key": "whatsapp", "label": "WhatsApp"},
    {"key": "instagram", "label": "Instagram"},
    {"key": "messenger", "label": "Messenger"},
    {"key": "website_chat", "label": "Website Chat"},
]

MODE_TO_STATUS = {"ia": "active_ai", "ai": "active_ai", "humano": "human", "human": "human", "hibrido": "hybrid", "hybrid": "hybrid"}
STATUS_TO_MODE = {"active_ai": "ia", "human": "humano", "hybrid": "hibrido", "awaiting_human": "humano"}


def _user_agents(db: Session, user: User) -> list[Agent]:
    return db.query(Agent).filter(Agent.user_id == user.id).all()


def _user_agent_ids(db: Session, user: User) -> list[int]:
    return [agent.id for agent in _user_agents(db, user)]


def _conversation_or_404(db: Session, user: User, conversation_id: int) -> AgentConversation:
    agent_ids = _user_agent_ids(db, user)
    if not agent_ids:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa nao encontrada")
    conversation = (
        db.query(AgentConversation)
        .filter(AgentConversation.id == conversation_id, AgentConversation.agent_id.in_(agent_ids))
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa nao encontrada")
    return conversation


def _channel_key(value: str | None) -> str:
    raw = (value or "").strip().lower()
    aliases = {
        "website": "website_chat",
        "site": "website_chat",
        "web": "website_chat",
        "facebook": "messenger",
        "facebook_messenger": "messenger",
    }
    return aliases.get(raw, raw)


def _conversation_name(conversation: AgentConversation) -> str:
    return conversation.external_user_id or f"Cliente #{conversation.id}"


def _connected_channel(db: Session, conversation: AgentConversation) -> AgentChannel | None:
    channel = _channel_key(conversation.channel_type)
    return (
        db.query(AgentChannel)
        .filter(
            AgentChannel.agent_id == conversation.agent_id,
            AgentChannel.channel_type == channel,
            AgentChannel.enabled.is_(True),
            AgentChannel.status == "connected",
        )
        .first()
    )


def _serialize_conversation(conversation: AgentConversation, last_message: AgentMessage | None = None) -> dict[str, Any]:
    mode = STATUS_TO_MODE.get(conversation.status, "ia")
    return {
        "id": conversation.id,
        "customer_id": conversation.id,
        "customer_name": _conversation_name(conversation),
        "channel": _channel_key(conversation.channel_type),
        "status": conversation.status,
        "ai_mode": mode,
        "assigned_to": conversation.assigned_to_human,
        "sales_stage": conversation.sales_stage,
        "source": conversation.lead_source,
        "campaign_id": None,
        "last_message_at": conversation.updated_at,
        "last_message_preview": last_message.content[:140] if last_message else "",
        "unread_count": 0,
        "city": None,
        "state": None,
        "phone": conversation.external_user_id if _channel_key(conversation.channel_type) == "whatsapp" else None,
        "email": None,
        "is_ai_active": mode == "ia",
        "is_waiting_human": conversation.status == "awaiting_human",
    }


def _last_message_map(db: Session, conversation_ids: list[int]) -> dict[int, AgentMessage]:
    if not conversation_ids:
        return {}
    rows = (
        db.query(AgentMessage)
        .filter(AgentMessage.conversation_id.in_(conversation_ids))
        .order_by(AgentMessage.created_at.desc())
        .all()
    )
    result: dict[int, AgentMessage] = {}
    for row in rows:
        result.setdefault(row.conversation_id, row)
    return result


def _conversation_query(db: Session, user: User):
    agent_ids = _user_agent_ids(db, user)
    if not agent_ids:
        return None
    return db.query(AgentConversation).filter(AgentConversation.agent_id.in_(agent_ids))


@router.get("/summary", response_model=dict[str, Any])
def get_chat_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    query = _conversation_query(db, current_user)
    total = query.count() if query is not None else 0
    waiting_human = query.filter(AgentConversation.status == "awaiting_human").count() if query is not None else 0
    with_ai = query.filter(AgentConversation.status == "active_ai").count() if query is not None else 0
    closed = query.filter(AgentConversation.status == "closed").count() if query is not None else 0
    return {
        "total": total,
        "waiting_human": waiting_human,
        "with_ai": with_ai,
        "closed": closed,
        "provider_status": "connected" if AIManager().get_active_provider() else "not_configured",
    }


@router.get("/channels", response_model=list[dict[str, Any]])
def get_chat_channels(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    query = _conversation_query(db, current_user)
    agents = _user_agents(db, current_user)
    agent_ids = [agent.id for agent in agents]
    result = []
    for channel in SUPPORTED_CHANNELS:
        count = query.filter(AgentConversation.channel_type == channel["key"]).count() if query is not None else 0
        configured = False
        last_sync_at = None
        last_error = None
        if agent_ids:
            row = (
                db.query(AgentChannel)
                .filter(AgentChannel.agent_id.in_(agent_ids), AgentChannel.channel_type == channel["key"], AgentChannel.enabled.is_(True))
                .order_by(AgentChannel.updated_at.desc())
                .first()
            )
            configured = bool(row and row.status == "connected")
            last_sync_at = row.last_sync_at if row else None
            last_error = row.last_error if row else None
        result.append(
            {
                **channel,
                "open_count": count,
                "status": "connected" if configured else "not_configured",
                "credentials_configured": configured,
                "last_sync_at": last_sync_at,
                "last_error": last_error,
            }
        )
    return result


@router.get("/conversations", response_model=list[dict[str, Any]])
def list_chat_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    query = _conversation_query(db, current_user)
    if query is None:
        return []
    rows = query.order_by(AgentConversation.updated_at.desc()).limit(100).all()
    last_messages = _last_message_map(db, [row.id for row in rows])
    return [_serialize_conversation(row, last_messages.get(row.id)) for row in rows]


@router.get("/conversations/{conversation_id}", response_model=dict[str, Any])
def get_chat_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    conversation = _conversation_or_404(db, current_user, conversation_id)
    messages = (
        db.query(AgentMessage)
        .filter(AgentMessage.conversation_id == conversation.id)
        .order_by(AgentMessage.created_at.asc())
        .all()
    )
    return {
        "conversation": _serialize_conversation(conversation, messages[-1] if messages else None),
        "messages": [
            {
                "id": item.id,
                "conversation_id": item.conversation_id,
                "sender_type": item.role,
                "channel": _channel_key(conversation.channel_type),
                "message_type": item.message_type,
                "content": item.content,
                "delivery_status": "stored",
                "created_at": item.created_at,
            }
            for item in messages
        ],
    }


@router.patch("/conversations/{conversation_id}/ai-mode", response_model=dict[str, Any])
def update_chat_ai_mode(
    conversation_id: int,
    payload: dict[str, str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    mode = (payload.get("mode") or "").strip().lower()
    if mode not in MODE_TO_STATUS:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="mode deve ser ia, humano ou hibrido")
    conversation = _conversation_or_404(db, current_user, conversation_id)
    conversation.status = MODE_TO_STATUS[mode]
    db.commit()
    db.refresh(conversation)
    return _serialize_conversation(conversation)


@router.post("/conversations/{conversation_id}/request-human", response_model=dict[str, Any])
def request_human_chat(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    conversation = _conversation_or_404(db, current_user, conversation_id)
    conversation.status = "awaiting_human"
    db.commit()
    db.refresh(conversation)
    return _serialize_conversation(conversation)


@router.post("/conversations/{conversation_id}/messages", response_model=dict[str, Any])
def send_chat_message(
    conversation_id: int,
    payload: dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    conversation = _conversation_or_404(db, current_user, conversation_id)
    content = str(payload.get("content") or "").strip()
    if not content:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Mensagem vazia")
    if _connected_channel(db, conversation) is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Provider do canal nao configurado. A mensagem nao foi enviada.",
        )
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Envio externo ainda nao implementado para este provider.",
    )


@router.post("/conversations/{conversation_id}/ai-suggestions", response_model=dict[str, Any])
def create_ai_suggestions(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    conversation = _conversation_or_404(db, current_user, conversation_id)
    messages = (
        db.query(AgentMessage)
        .filter(AgentMessage.conversation_id == conversation.id)
        .order_by(AgentMessage.created_at.desc())
        .limit(8)
        .all()
    )
    context = "\n".join(f"{item.role}: {item.content[:500]}" for item in reversed(messages))
    try:
        result = AIManager().chat(
            messages=[
                {
                    "role": "system",
                    "content": "Gere exatamente 3 sugestoes curtas de resposta para atendimento comercial. Nao invente disponibilidade, preco ou reserva.",
                },
                {"role": "user", "content": context or "Sem mensagens suficientes."},
            ],
            max_tokens=220,
            temperature=0.2,
        )
    except ProviderError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    text = str(result.get("text") or result.get("content") or "").strip()
    suggestions = [line.strip(" -0123456789.") for line in text.splitlines() if line.strip()]
    suggestions = [item for item in suggestions if item][:3]
    if not suggestions:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Provider de IA retornou sugestoes vazias.")
    return {"items": suggestions, "provider": result.get("provider"), "source": "backend/app/services/ai"}


@router.get("/team", response_model=list[dict[str, Any]])
def get_chat_team(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    query = _conversation_query(db, current_user)
    assigned_count = query.filter(AgentConversation.assigned_to_human.isnot(None)).count() if query is not None else 0
    return [
        {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "status": "unknown",
            "assigned_count": assigned_count,
        }
    ]


@router.get("/tags", response_model=list[dict[str, Any]])
def get_chat_tags(_: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    return [
        {"id": "reserva", "label": "Reserva", "color": "violet"},
        {"id": "informacoes", "label": "Informacoes", "color": "cyan"},
        {"id": "reclamacao", "label": "Reclamacao", "color": "amber"},
        {"id": "orcamento", "label": "Orcamento", "color": "rose"},
    ]


@router.get("/customers/{customer_id}/reservations", response_model=dict[str, Any])
def get_customer_reservations(
    customer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    conversation = _conversation_or_404(db, current_user, customer_id)
    customer_name = _conversation_name(conversation)
    rows = db.query(Reservation).filter(Reservation.guest_name == customer_name).order_by(Reservation.created_at.desc()).limit(20).all()
    return {
        "items": [
            {
                "id": item.id,
                "check_in": item.check_in,
                "check_out": item.check_out,
                "value": item.total_price,
                "status": item.status,
            }
            for item in rows
        ],
        "source": "reservations",
    }


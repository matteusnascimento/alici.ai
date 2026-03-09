"""Conversation history routes."""

import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Agent, Conversation, Message, User
from app.services.auth_service import AuthService

router = APIRouter()


def _ok(data):
    return {"status": "success", "data": data, "error": None}


class ConversationCreateRequest(BaseModel):
    title: str | None = None
    agent_id: str | None = None


@router.get("")
def list_conversations(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    limit = max(1, min(limit, 100))
    offset = max(0, offset)

    latest_message_ts = (
        db.query(
            Message.conversation_id.label("conversation_id"),
            func.max(Message.created_at).label("last_message_at"),
        )
        .group_by(Message.conversation_id)
        .subquery()
    )

    latest_message = (
        db.query(
            Message.conversation_id.label("conversation_id"),
            Message.content.label("last_message"),
            Message.created_at.label("last_message_at"),
        )
        .join(
            latest_message_ts,
            and_(
                Message.conversation_id == latest_message_ts.c.conversation_id,
                Message.created_at == latest_message_ts.c.last_message_at,
            ),
        )
        .subquery()
    )

    rows = (
        db.query(
            Conversation,
            latest_message.c.last_message,
            latest_message.c.last_message_at,
        )
        .filter(
            Conversation.organization_id == current_user.organization_id,
            Conversation.user_id == current_user.id,
            Conversation.is_active.is_(True),
        )
        .outerjoin(latest_message, latest_message.c.conversation_id == Conversation.id)
        .order_by(Conversation.updated_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    response = []
    for conversation, last_message, last_message_at in rows:
        response.append(
            {
                "id": conversation.id,
                "title": conversation.title,
                "created_at": conversation.created_at,
                "updated_at": conversation.updated_at,
                "last_message": last_message,
                "last_message_at": last_message_at,
            }
        )
    return _ok({"history": response})


@router.post("")
def create_conversation(
    payload: ConversationCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    agent_id = payload.agent_id
    if not agent_id:
        default_agent = (
            db.query(Agent)
            .filter(Agent.organization_id == current_user.organization_id, Agent.is_active.is_(True))
            .first()
        )
        if not default_agent:
            raise HTTPException(status_code=400, detail="No active agent available")
        agent_id = default_agent.id

    conversation = Conversation(
        id=str(uuid.uuid4()),
        title=(payload.title or "Nova conversa").strip(),
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        agent_id=agent_id,
        is_active=True,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return _ok(
        {
            "conversation": {
                "id": conversation.id,
                "title": conversation.title,
                "created_at": conversation.created_at,
            }
        }
    )


@router.get("/{conversation_id}")
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.organization_id == current_user.organization_id,
            Conversation.user_id == current_user.id,
            Conversation.is_active.is_(True),
        )
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.asc())
        .all()
    )

    return _ok(
        {
            "conversation": {
                "id": conversation.id,
                "title": conversation.title,
                "created_at": conversation.created_at,
                "messages": [
                    {
                        "id": msg.id,
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.created_at,
                    }
                    for msg in messages
                ],
            }
        }
    )


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.organization_id == current_user.organization_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    db.query(Message).filter(Message.conversation_id == conversation.id).delete()
    db.delete(conversation)
    db.commit()

    return _ok({"message": "Conversation deleted", "conversation_id": conversation_id})

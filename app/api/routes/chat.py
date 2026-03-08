"""
Chat routes for the platform
"""
import asyncio
import json
from typing import AsyncGenerator, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.services.ai_orchestrator import AIOrchestrator
from app.services.auth_service import AuthService
from app.services.billing_service import BillingService
from app.services.user_memory_service import UserMemoryService
from app.models import User, Agent, Conversation, Message

router = APIRouter()
orchestrator = AIOrchestrator()
billing_service = BillingService()
user_memory_service = UserMemoryService()


class ChatMessageRequest(BaseModel):
    """Request schema compatible with both new and legacy frontends."""
    message: Optional[str] = None
    pergunta: Optional[str] = None
    conversation_id: Optional[str] = None
    agent_id: Optional[str] = None


async def streamResponse(content: str) -> AsyncGenerator[str, None]:
    """Emit response chunks in SSE format for chat streaming clients."""
    words = content.split()
    if not words:
        yield "data: {\"status\":\"success\",\"data\":{\"chunk\":\"\"},\"error\":null}\n\n"
        yield "data: [DONE]\n\n"
        return

    for word in words:
        payload = {
            "status": "success",
            "data": {"chunk": f"{word} "},
            "error": None,
        }
        yield f"data: {json.dumps(payload, ensure_ascii=True)}\n\n"
        await asyncio.sleep(0.02)

    yield "data: [DONE]\n\n"


@router.post("/message")
async def send_message(
    payload: ChatMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Send a chat message"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    message = (payload.message or payload.pergunta or "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    conversation_id = payload.conversation_id
    agent_id = payload.agent_id

    # Validate conversation ownership when conversation_id is provided.
    if conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.organization_id == current_user.organization_id,
            Conversation.user_id == current_user.id,
            Conversation.is_active == True,
        ).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

    # Check usage limits
    if billing_service.check_usage_limit(current_user.organization):
        raise HTTPException(
            status_code=429,
            detail="Monthly usage limit exceeded. Upgrade your plan."
        )

    # Use default agent if not specified
    if not agent_id:
        # Get first active agent from organization
        agent = db.query(Agent).filter(
            Agent.organization_id == current_user.organization_id,
            Agent.is_active == True
        ).first()
        if not agent:
            raise HTTPException(status_code=400, detail="No active agents available")
        agent_id = agent.id

    try:
        # Capture long-term user facts without blocking chat flow.
        captured_memories = user_memory_service.capture_from_message(
            db=db,
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            message=message,
        )
        if captured_memories:
            db.commit()

        # Process message through orchestrator
        result = await orchestrator.process_chat(
            message=message,
            conversation_id=conversation_id,
            agent_id=agent_id,
            user_id=current_user.id,
            organization_id=current_user.organization_id
        )

        # Increment usage
        billing_service.increment_usage(current_user.organization_id)

        # Keep compatibility with multiple frontend payload contracts.
        content = result.get("content", "")
        return {
            **result,
            "message": content,
            "response": content,
            "resposta": content,
            "status": "success",
            "data": result,
            "error": None,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations")
def get_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Get user's conversations"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    conversations = db.query(Conversation).filter(
        Conversation.organization_id == current_user.organization_id,
        Conversation.user_id == current_user.id
    ).order_by(Conversation.updated_at.desc()).all()

    return [
        {
            "id": conv.id,
            "title": conv.title,
            "agent_id": conv.agent_id,
            "last_message_at": conv.last_message_at,
            "created_at": conv.created_at
        }
        for conv in conversations
    ]


@router.get("/conversations/{conversation_id}/messages")
def get_conversation_messages(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Get messages from a conversation"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Verify conversation belongs to user's organization
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.organization_id == current_user.organization_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()

    return [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at,
            "tokens_used": msg.tokens_used
        }
        for msg in messages
    ]


@router.post("/stream")
async def stream_message(
    payload: ChatMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Stream chat response chunks as Server-Sent Events."""
    result = await send_message(payload=payload, db=db, current_user=current_user)
    content = result.get("content") or result.get("message") or ""
    return StreamingResponse(streamResponse(content), media_type="text/event-stream")
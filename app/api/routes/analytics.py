"""Analytics routes for platform dashboard metrics."""

from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from app.core.database import get_db
from app.models import Agent, Conversation, Integration, Message, UsageLog, User
from app.services.auth_service import AuthService

router = APIRouter()


@router.get("")
def get_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    org_id = current_user.organization_id

    total_conversations = db.query(Conversation).filter(Conversation.organization_id == org_id).count()
    total_messages = (
        db.query(func.count(Message.id))
        .join(Conversation, Conversation.id == Message.conversation_id)
        .filter(Conversation.organization_id == org_id)
        .scalar()
        or 0
    )
    active_agents = (
        db.query(Agent)
        .filter(Agent.organization_id == org_id, Agent.is_active.is_(True))
        .count()
    )

    token_usage = (
        db.query(func.sum(UsageLog.tokens_used))
        .filter(UsageLog.organization_id == org_id)
        .scalar()
        or 0
    )

    total_cost = (
        db.query(func.sum(UsageLog.cost))
        .filter(UsageLog.organization_id == org_id)
        .scalar()
        or 0.0
    )

    connected_integrations = (
        db.query(Integration)
        .filter(
            Integration.user_id == current_user.id,
            Integration.organization_id == org_id,
            Integration.is_active.is_(True),
            Integration.status == "connected",
        )
        .count()
    )

    return {
        "messages_sent": int(total_messages),
        "conversations": int(total_conversations),
        "ai_usage_tokens": int(token_usage),
        "active_agents": int(active_agents),
        "integrations_connected": int(connected_integrations),
        "cost": float(total_cost),
        "organization_plan": current_user.organization.plan,
    }

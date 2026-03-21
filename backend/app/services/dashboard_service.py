from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.conversation import Message
from app.models.user import User
from app.schemas.dashboard import DashboardStats, UsageBar


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_stats(self, user: User) -> DashboardStats:
        total_messages = (
            self.db.query(func.count(Message.id))
            .join(Message.conversation)
            .filter_by(user_id=user.id)
            .scalar()
            or 0
        )
        total_agents = self.db.query(func.count(Agent.id)).filter(Agent.user_id == user.id).scalar() or 0
        usage_seed = max(total_messages, 1)
        usage_bars = [
            UsageBar(label="Seg", value=usage_seed),
            UsageBar(label="Ter", value=usage_seed + total_agents),
            UsageBar(label="Qua", value=max(1, usage_seed - 1)),
            UsageBar(label="Qui", value=usage_seed + 2),
            UsageBar(label="Sex", value=usage_seed + 1),
            UsageBar(label="Sab", value=max(1, total_agents)),
            UsageBar(label="Dom", value=max(1, total_messages // 2 + 1)),
        ]
        return DashboardStats(
            total_messages=total_messages,
            total_agents=total_agents,
            revenue=float(total_agents * 197 + total_messages * 3),
            conversions=total_agents * 2 + max(1, total_messages // 3),
            clicks=total_messages * 4 + 12,
            quotes=total_agents + max(1, total_messages // 2),
            usage_bars=usage_bars,
        )

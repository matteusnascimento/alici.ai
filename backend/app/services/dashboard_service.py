from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.conversation import Message
from app.models.subscription import Subscription
from app.models.usage_log import UsageLog
from app.models.user import User
from app.schemas.dashboard import DashboardMetricItem, DashboardMetrics, DashboardOverview, DashboardStats, DashboardUsage, UsageBar


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

    def get_overview(self, user: User) -> DashboardOverview:
        total_agents = self.db.query(func.count(Agent.id)).filter(Agent.user_id == user.id).scalar() or 0
        active_agents = (
            self.db.query(func.count(Agent.id))
            .filter(Agent.user_id == user.id, Agent.ativo.is_(True))
            .scalar()
            or 0
        )
        total_messages = (
            self.db.query(func.count(Message.id))
            .join(Message.conversation)
            .filter_by(user_id=user.id)
            .scalar()
            or 0
        )
        return DashboardOverview(
            total_messages=total_messages,
            total_agents=total_agents,
            active_agents=active_agents,
            current_plan=user.plan,
        )

    def get_usage(self, user: User) -> DashboardUsage:
        messages_used = (
            self.db.query(func.coalesce(func.sum(UsageLog.quantity), 0))
            .filter(UsageLog.user_id == user.id, UsageLog.metric == "messages")
            .scalar()
            or 0
        )
        agents_used = self.db.query(func.count(Agent.id)).filter(Agent.user_id == user.id).scalar() or 0

        subscription = self.db.query(Subscription).filter(Subscription.user_id == user.id).first()
        if user.plan == "pro":
            messages_limit = 5000
            agents_limit = 10
        elif user.plan in {"business", "enterprise"}:
            messages_limit = 50000
            agents_limit = 100
        else:
            messages_limit = 500
            agents_limit = 2

        if subscription and subscription.plan_id in {"pro", "business", "enterprise"}:
            if subscription.plan_id == "pro":
                messages_limit = 5000
                agents_limit = 10
            else:
                messages_limit = 50000
                agents_limit = 100

        return DashboardUsage(
            messages_used=messages_used,
            messages_limit=messages_limit,
            agents_used=agents_used,
            agents_limit=agents_limit,
        )

    def get_metrics(self, user: User) -> DashboardMetrics:
        stats = self.get_stats(user)
        items = [
            DashboardMetricItem(key="revenue", value=stats.revenue),
            DashboardMetricItem(key="conversions", value=float(stats.conversions)),
            DashboardMetricItem(key="clicks", value=float(stats.clicks)),
            DashboardMetricItem(key="quotes", value=float(stats.quotes)),
        ]
        return DashboardMetrics(items=items)

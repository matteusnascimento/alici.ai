from datetime import UTC, datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.ai_request_log import AIRequestLog
from app.models.conversation import Message
from app.models.subscription import Subscription
from app.models.usage_log import UsageLog
from app.models.user import User
from app.schemas.dashboard import (
    DashboardAIHealth,
    DashboardAIMetrics,
    DashboardMetricItem,
    DashboardMetrics,
    DashboardOverview,
    DashboardStats,
    DashboardUsage,
    UsageBar,
)
from app.services.openai_service import OpenAIService


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

    def get_ai_health(self, user: User) -> DashboardAIHealth:
        result = OpenAIService().healthcheck()
        status = str(result.get("status") or "error")
        model = str(result.get("model") or "gpt-4o-mini")
        return DashboardAIHealth(
            provider="openai",
            status=status,
            model=model,
            latency_ms=float(result.get("latency_ms") or 0.0),
            error_type=result.get("error_type"),
            status_code=result.get("status_code"),
        )

    @staticmethod
    def _window_to_timedelta(window: str) -> timedelta:
        normalized = (window or "24h").strip().lower()
        if normalized == "7d":
            return timedelta(days=7)
        if normalized == "30d":
            return timedelta(days=30)
        return timedelta(hours=24)

    @staticmethod
    def _window_label(window: str) -> str:
        normalized = (window or "24h").strip().lower()
        return normalized if normalized in {"24h", "7d", "30d"} else "24h"

    def get_ai_metrics(self, user: User, window: str = "24h") -> DashboardAIMetrics:
        window_label = self._window_label(window)
        start = datetime.now(UTC) - self._window_to_timedelta(window_label)
        base_query = self.db.query(AIRequestLog).filter(
            AIRequestLog.created_at >= start,
            (AIRequestLog.user_id == user.id) | (AIRequestLog.user_id.is_(None)),
        )

        total_requests = base_query.count()
        success_requests = base_query.filter(AIRequestLog.status == "success").count()
        error_requests = base_query.filter(AIRequestLog.status == "error").count()
        rate_limit_requests = base_query.filter(AIRequestLog.status_code == 429).count()

        avg_latency = (
            self.db.query(func.avg(AIRequestLog.latency_ms))
            .filter(
                AIRequestLog.created_at >= start,
                (AIRequestLog.user_id == user.id) | (AIRequestLog.user_id.is_(None)),
            )
            .scalar()
            or 0
        )

        # Tendência diária de erros e 429 no período selecionado.
        trend_errors_by_day: dict[str, int] = {}
        trend_429_by_day: dict[str, int] = {}

        rows = (
            self.db.query(AIRequestLog.created_at, AIRequestLog.status, AIRequestLog.status_code)
            .filter(
                AIRequestLog.created_at >= start,
                (AIRequestLog.user_id == user.id) | (AIRequestLog.user_id.is_(None)),
            )
            .all()
        )
        for created_at, status, status_code in rows:
            if created_at is None:
                continue
            day_key = created_at.date().isoformat()
            if status == "error":
                trend_errors_by_day[day_key] = trend_errors_by_day.get(day_key, 0) + 1
            if status_code == 429:
                trend_429_by_day[day_key] = trend_429_by_day.get(day_key, 0) + 1

        if window_label == "24h":
            day_range = [datetime.now(UTC).date()]
        else:
            total_days = 7 if window_label == "7d" else 30
            base_date = datetime.now(UTC).date()
            day_range = [base_date - timedelta(days=i) for i in range(total_days - 1, -1, -1)]

        trend = []
        trend_429 = []
        for day in day_range:
            key = day.isoformat()
            trend.append(UsageBar(label=day.strftime("%d/%m"), value=int(trend_errors_by_day.get(key, 0))))
            trend_429.append(UsageBar(label=day.strftime("%d/%m"), value=int(trend_429_by_day.get(key, 0))))

        return DashboardAIMetrics(
            window=window_label,
            total_requests=int(total_requests),
            success_requests=int(success_requests),
            error_requests=int(error_requests),
            rate_limit_429=int(rate_limit_requests),
            avg_latency_ms=float(avg_latency),
            trend=trend,
            trend_429=trend_429,
        )

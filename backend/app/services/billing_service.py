from datetime import UTC

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.billing_event import BillingEvent
from app.models.subscription import Subscription
from app.models.usage_log import UsageLog
from app.models.user import User
from app.schemas.billing import (
    BillingHistoryItem,
    BillingHistoryResponse,
    BillingUsageItem,
    BillingUsageResponse,
    CurrentSubscriptionResponse,
    PlanLimit,
    PlanRead,
    UpgradeRequest,
    UpgradeResponse,
)


class BillingService:
    PLAN_CATALOG = {
        "free": {
            "name": "Free",
            "monthly_price": 0.0,
            "yearly_price": 0.0,
            "features": ["Alici Chat basico", "1 workspace", "Suporte comunitario"],
            "limits": {"messages": 500, "agents": 2},
        },
        "pro": {
            "name": "Pro",
            "monthly_price": 197.0,
            "yearly_price": 1970.0,
            "features": ["Automacao multiagente", "Marketing Studio completo", "Prioridade de suporte"],
            "limits": {"messages": 5000, "agents": 10},
        },
        "business": {
            "name": "Business",
            "monthly_price": 597.0,
            "yearly_price": 5970.0,
            "features": ["Multiusuarios", "Integracoes avancadas", "SLAs empresariais"],
            "limits": {"messages": 50000, "agents": 100},
        },
    }

    def __init__(self, db: Session):
        self.db = db

    def list_plans(self) -> list[PlanRead]:
        plans: list[PlanRead] = []
        for plan_id, config in self.PLAN_CATALOG.items():
            plans.append(
                PlanRead(
                    id=plan_id,
                    name=config["name"],
                    monthly_price=config["monthly_price"],
                    yearly_price=config["yearly_price"],
                    features=config["features"],
                    limits=[PlanLimit(key=key, value=value) for key, value in config["limits"].items()],
                    active=True,
                )
            )
        return plans

    def current_subscription(self, user: User) -> CurrentSubscriptionResponse:
        subscription = self._get_or_create_subscription(user)
        plan = self.PLAN_CATALOG.get(subscription.plan_id, self.PLAN_CATALOG["free"])
        return CurrentSubscriptionResponse(
            plan_id=subscription.plan_id,
            plan_name=plan["name"],
            status=subscription.status,
            billing_cycle=subscription.billing_cycle,
            monthly_price=subscription.monthly_price,
            yearly_price=subscription.yearly_price,
            auto_renew=subscription.auto_renew,
            started_at=subscription.current_period_start,
        )

    def upgrade(self, user: User, payload: UpgradeRequest) -> UpgradeResponse:
        if payload.plan_id not in self.PLAN_CATALOG:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid plan")

        subscription = self._get_or_create_subscription(user)
        plan = self.PLAN_CATALOG[payload.plan_id]
        subscription.plan_id = payload.plan_id
        subscription.billing_cycle = payload.billing_cycle
        subscription.monthly_price = float(plan["monthly_price"])
        subscription.yearly_price = float(plan["yearly_price"])
        subscription.status = "active"
        user.plan = payload.plan_id

        event = BillingEvent(
            user_id=user.id,
            event_type="upgrade",
            amount=subscription.monthly_price if payload.billing_cycle == "monthly" else subscription.yearly_price or 0.0,
            currency="BRL",
            description=f"Upgrade para plano {plan['name']}",
            provider="pending-provider",
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(subscription)

        return UpgradeResponse(
            message=f"Plano alterado para {plan['name']} com sucesso.",
            subscription=self.current_subscription(user),
        )

    def usage(self, user: User) -> BillingUsageResponse:
        subscription = self._get_or_create_subscription(user)
        plan = self.PLAN_CATALOG.get(subscription.plan_id, self.PLAN_CATALOG["free"])
        usage_map = {
            metric: (
                self.db.query(func.coalesce(func.sum(UsageLog.quantity), 0))
                .filter(UsageLog.user_id == user.id, UsageLog.metric == metric)
                .scalar()
                or 0
            )
            for metric in plan["limits"].keys()
        }
        items = [
            BillingUsageItem(metric=metric, used=int(usage_map.get(metric, 0)), limit=int(limit))
            for metric, limit in plan["limits"].items()
        ]
        return BillingUsageResponse(items=items)

    def history(self, user: User) -> BillingHistoryResponse:
        events = (
            self.db.query(BillingEvent)
            .filter(BillingEvent.user_id == user.id)
            .order_by(BillingEvent.created_at.desc())
            .limit(50)
            .all()
        )
        return BillingHistoryResponse(
            events=[
                BillingHistoryItem(
                    id=item.id,
                    event_type=item.event_type,
                    amount=item.amount,
                    currency=item.currency,
                    description=item.description,
                    created_at=item.created_at.astimezone(UTC) if item.created_at else item.created_at,
                )
                for item in events
            ]
        )

    def _get_or_create_subscription(self, user: User) -> Subscription:
        subscription = self.db.query(Subscription).filter(Subscription.user_id == user.id).first()
        if subscription:
            return subscription

        initial_plan_id = user.plan if user.plan in self.PLAN_CATALOG else "free"
        config = self.PLAN_CATALOG[initial_plan_id]
        subscription = Subscription(
            user_id=user.id,
            plan_id=initial_plan_id,
            monthly_price=config["monthly_price"],
            yearly_price=config["yearly_price"],
            billing_cycle="monthly",
            status="active",
        )
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

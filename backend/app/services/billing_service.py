import json
import logging
from datetime import UTC, datetime, timedelta

import stripe
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.agent import Agent
from app.models.billing_event import BillingEvent
from app.models.subscription import Subscription
from app.models.usage_log import UsageLog
from app.models.user import User
from app.schemas.billing import (
    BillingHistoryItem,
    BillingHistoryResponse,
    BillingUsageItem,
    BillingUsageResponse,
    CheckoutRequest,
    CheckoutResponse,
    CurrentSubscriptionResponse,
    PlanLimit,
    PlanRead,
    PlanStripePrices,
    PortalResponse,
    SubscriptionActionResponse,
    UpgradeRequest,
    UpgradeResponse,
)

logger = logging.getLogger(__name__)


class BillingService:
    PLAN_CATALOG: dict = {
        "free": {
            "name": "Free",
            "monthly_price": 0.0,
            "yearly_price": 0.0,
            "features": ["Alici Chat basico", "1 workspace", "Suporte comunitario"],
            "limits": {"messages": 500, "agents": 2},
            "stripe_price_monthly_env": "",
            "stripe_price_yearly_env": "",
        },
        "pro": {
            "name": "Pro",
            "monthly_price": 397.0,
            "yearly_price": 3970.0,
            "features": ["Automacao multiagente", "Marketing Studio completo", "Prioridade de suporte"],
            "limits": {"messages": 5000, "agents": 10},
            "stripe_price_monthly_env": "stripe_price_pro_monthly",
            "stripe_price_yearly_env": "stripe_price_pro_yearly",
        },
        "business": {
            "name": "Business",
            "monthly_price": 697.0,
            "yearly_price": 6970.0,
            "features": ["Multiusuarios", "Integracoes avancadas", "SLAs empresariais"],
            "limits": {"messages": 50000, "agents": 100},
            "stripe_price_monthly_env": "stripe_price_business_monthly",
            "stripe_price_yearly_env": "stripe_price_business_yearly",
        },
    }

    def __init__(self, db: Session):
        self.db = db
        self._settings = get_settings()

    # ─────────────────────────────────────────────────────────────────
    # MÉTODOS EXISTENTES PRESERVADOS
    # ─────────────────────────────────────────────────────────────────

    def list_plans(self) -> list[PlanRead]:
        plans: list[PlanRead] = []
        for plan_id, config in self.PLAN_CATALOG.items():
            stripe_prices = PlanStripePrices(
                monthly=bool(self._resolve_price_id(plan_id, "monthly")),
                yearly=bool(self._resolve_price_id(plan_id, "yearly")),
            )
            plans.append(
                PlanRead(
                    id=plan_id,
                    name=config["name"],
                    monthly_price=config["monthly_price"],
                    yearly_price=config["yearly_price"],
                    features=config["features"],
                    limits=[PlanLimit(key=key, value=value) for key, value in config["limits"].items()],
                    active=True,
                    checkout_available=plan_id != "free" and (stripe_prices.monthly or stripe_prices.yearly),
                    stripe_prices=stripe_prices,
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
            cancel_at_period_end=subscription.cancel_at_period_end,
            started_at=subscription.current_period_start,
            next_renewal_at=subscription.current_period_end,
            provider=subscription.provider,
            stripe_customer_id=subscription.stripe_customer_id,
        )

    def upgrade(self, user: User, payload: UpgradeRequest) -> UpgradeResponse:
        """[LEGADO/ADMIN] Upgrade manual sem pagamento. Use /billing/checkout para fluxo real."""
        if payload.plan_id not in self.PLAN_CATALOG:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Plano inválido")

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
            event_type="upgrade_manual",
            amount=subscription.monthly_price if payload.billing_cycle == "monthly" else subscription.yearly_price or 0.0,
            currency="BRL",
            description=f"Upgrade manual para plano {plan['name']}",
            provider="manual",
            status="succeeded",
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
        items: list[BillingUsageItem] = []

        for metric, limit in plan["limits"].items():
            if metric == "agents":
                # Agentes: contagem de agentes não arquivados do usuário.
                used = (
                    self.db.query(func.count(Agent.id))
                    .filter(Agent.user_id == user.id, Agent.archived.is_(False))
                    .scalar()
                    or 0
                )
            else:
                # Demais métricas: soma de UsageLog
                used = self._usage_total_for_period(user.id, metric, subscription)
            items.append(BillingUsageItem(metric=metric, used=int(used), limit=int(limit)))

        return BillingUsageResponse(items=items)

    def assert_can_use(self, user: User, metric: str, quantity: int = 1) -> None:
        subscription = self._get_or_create_subscription(user)
        plan = self.PLAN_CATALOG.get(subscription.plan_id, self.PLAN_CATALOG["free"])
        limit = int(plan["limits"].get(metric, 0) or 0)
        if limit <= 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Seu plano nao permite uso de {metric}.")
        used = int(self._usage_total_for_period(user.id, metric, subscription))
        if used + quantity > limit:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Limite de {metric} do plano atingido. Atualize o plano para continuar.",
            )

    def record_usage(self, user: User, metric: str, quantity: int = 1, source: str | None = None) -> UsageLog:
        row = UsageLog(user_id=user.id, metric=metric, quantity=quantity, source=source)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

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
                    stripe_event_id=item.stripe_event_id,
                    status=item.status,
                    created_at=item.created_at.astimezone(UTC) if item.created_at else item.created_at,
                )
                for item in events
            ]
        )

    # ─────────────────────────────────────────────────────────────────
    # MÉTODOS STRIPE NOVOS
    # ─────────────────────────────────────────────────────────────────

    def create_checkout_session(self, user: User, payload: CheckoutRequest) -> CheckoutResponse:
        if payload.plan_id not in self.PLAN_CATALOG or payload.plan_id == "free":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Plano inválido para checkout")

        if not self._settings.stripe_secret_key:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Stripe não configurado")

        stripe.api_key = self._settings.stripe_secret_key
        subscription = self._get_or_create_subscription(user)
        price_id = self._resolve_price_id(payload.plan_id, payload.billing_cycle)

        if not price_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Price ID do Stripe não configurado para plano {payload.plan_id}",
            )

        customer_id = self._ensure_stripe_customer(user, subscription)

        success_url = self._settings.stripe_success_url or f"{self._settings.app_base_url}/app/billing/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = self._settings.stripe_cancel_url or f"{self._settings.app_base_url}/app/billing/cancel"

        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[{"price": price_id, "quantity": 1}],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={"user_id": str(user.id), "plan_id": payload.plan_id, "billing_cycle": payload.billing_cycle},
                subscription_data={"metadata": {"user_id": str(user.id), "plan_id": payload.plan_id, "billing_cycle": payload.billing_cycle}},
            )
        except stripe.StripeError as exc:
            logger.error("Erro ao criar checkout session Stripe: %s", exc)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Erro ao criar sessão de checkout") from exc

        subscription.last_checkout_session_id = session.id
        self.db.commit()

        return CheckoutResponse(checkout_url=session.url, session_id=session.id)

    def create_billing_portal_session(self, user: User) -> PortalResponse:
        if not self._settings.stripe_secret_key:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Stripe não configurado")

        stripe.api_key = self._settings.stripe_secret_key
        subscription = self._get_or_create_subscription(user)

        if not subscription.stripe_customer_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Nenhuma assinatura Stripe ativa encontrada",
            )

        return_url = self._settings.stripe_billing_portal_return_url or f"{self._settings.frontend_base_url}/app/account/overview"
        try:
            session = stripe.billing_portal.Session.create(
                customer=subscription.stripe_customer_id,
                return_url=return_url,
            )
        except stripe.StripeError as exc:
            logger.error("Erro ao criar portal session Stripe: %s", exc)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Erro ao criar portal") from exc

        return PortalResponse(portal_url=session.url)

    def cancel_subscription(self, user: User) -> SubscriptionActionResponse:
        if not self._settings.stripe_secret_key:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Stripe não configurado")

        stripe.api_key = self._settings.stripe_secret_key
        subscription = self._get_or_create_subscription(user)

        if not subscription.stripe_subscription_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Nenhuma assinatura Stripe ativa para cancelar",
            )

        try:
            stripe.Subscription.modify(subscription.stripe_subscription_id, cancel_at_period_end=True)
        except stripe.StripeError as exc:
            logger.error("Erro ao cancelar assinatura Stripe: %s", exc)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Erro ao cancelar assinatura") from exc

        subscription.cancel_at_period_end = True
        self.db.commit()

        self._record_event(user.id, "subscription_cancel_scheduled", 0.0, "Cancelamento agendado ao fim do período")
        return SubscriptionActionResponse(
            message="Cancelamento agendado. Sua assinatura continua ativa até o fim do período.",
            subscription=self.current_subscription(user),
        )

    def resume_subscription(self, user: User) -> SubscriptionActionResponse:
        if not self._settings.stripe_secret_key:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Stripe não configurado")

        stripe.api_key = self._settings.stripe_secret_key
        subscription = self._get_or_create_subscription(user)

        if not subscription.stripe_subscription_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Nenhuma assinatura Stripe para reativar",
            )

        try:
            stripe.Subscription.modify(subscription.stripe_subscription_id, cancel_at_period_end=False)
        except stripe.StripeError as exc:
            logger.error("Erro ao reativar assinatura Stripe: %s", exc)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Erro ao reativar assinatura") from exc

        subscription.cancel_at_period_end = False
        self.db.commit()

        self._record_event(user.id, "subscription_resumed", 0.0, "Cancelamento revertido — assinatura reativada")
        return SubscriptionActionResponse(
            message="Assinatura reativada com sucesso.",
            subscription=self.current_subscription(user),
        )

    def process_webhook_event(self, payload: bytes, stripe_signature: str) -> dict:
        if not self._settings.stripe_webhook_secret:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Webhook secret não configurado")
        if not self._settings.stripe_secret_key:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Stripe não configurado")

        stripe.api_key = self._settings.stripe_secret_key

        try:
            event = stripe.Webhook.construct_event(payload, stripe_signature, self._settings.stripe_webhook_secret)
        except stripe.SignatureVerificationError as exc:
            logger.warning("Assinatura de webhook Stripe inválida: %s", exc)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assinatura inválida") from exc

        event_id: str = event["id"]

        # Idempotência — ignorar evento já processado
        existing = self.db.query(BillingEvent).filter(BillingEvent.stripe_event_id == event_id).first()
        if existing:
            logger.info("Evento Stripe já processado: %s", event_id)
            return {"status": "already_processed"}

        event_type: str = event["type"]
        event_data = event["data"]["object"]

        handlers = {
            "checkout.session.completed": self._handle_checkout_completed,
            "customer.subscription.created": self._handle_subscription_upsert,
            "customer.subscription.updated": self._handle_subscription_upsert,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "invoice.paid": self._handle_invoice_paid,
            "invoice.payment_failed": self._handle_invoice_failed,
        }

        handler = handlers.get(event_type)
        if handler:
            handler(event_data, event_id)
        else:
            logger.debug("Evento Stripe ignorado (sem handler): %s", event_type)

        return {"status": "processed", "event_type": event_type}

    # ─────────────────────────────────────────────────────────────────
    # ENFORCEMENT DE LIMITES
    # ─────────────────────────────────────────────────────────────────

    def check_limit(self, user: User, metric: str) -> None:
        """Levanta HTTP 403 se o usuário atingiu o limite do plano para a métrica."""
        subscription = self._get_or_create_subscription(user)
        plan = self.PLAN_CATALOG.get(subscription.plan_id, self.PLAN_CATALOG["free"])
        limit = plan["limits"].get(metric)
        if limit is None:
            return

        if metric == "agents":
            used = (
                self.db.query(func.count(Agent.id))
                .filter(Agent.user_id == user.id, Agent.archived.is_(False))
                .scalar()
                or 0
            )
        else:
            used = self._usage_total_for_period(user.id, metric, subscription)

        if used >= limit:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "PLAN_LIMIT_REACHED",
                    "metric": metric,
                    "used": int(used),
                    "limit": int(limit),
                    "plan": subscription.plan_id,
                    "message": f"Limite de {metric} atingido ({used}/{limit}). Faça upgrade para continuar.",
                },
            )

    def log_usage(self, user_id: int, metric: str, quantity: int = 1, source: str | None = None) -> None:
        """Registra uso no UsageLog."""
        log = UsageLog(user_id=user_id, metric=metric, quantity=quantity, source=source)
        self.db.add(log)
        self.db.commit()

    # ─────────────────────────────────────────────────────────────────
    # HELPERS INTERNOS
    # ─────────────────────────────────────────────────────────────────

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
            currency="BRL",
            provider="stripe",
        )
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def _usage_total_for_period(self, user_id: int, metric: str, subscription: Subscription) -> int:
        query = (
            self.db.query(func.coalesce(func.sum(UsageLog.quantity), 0))
            .filter(UsageLog.user_id == user_id, UsageLog.metric == metric)
        )
        if subscription.current_period_start:
            period_start = subscription.current_period_start
            if self._settings.sqlalchemy_database_url.startswith("sqlite"):
                period_start = period_start - timedelta(seconds=1)
            query = query.filter(UsageLog.created_at >= period_start)
        if subscription.current_period_end:
            query = query.filter(UsageLog.created_at < subscription.current_period_end)
        return int(query.scalar() or 0)

    def _resolve_price_id(self, plan_id: str, billing_cycle: str) -> str:
        if billing_cycle == "monthly":
            if plan_id == "pro" and self._settings.stripe_price_pro:
                return self._settings.stripe_price_pro
            if plan_id == "business" and self._settings.stripe_price_business:
                return self._settings.stripe_price_business
        plan = self.PLAN_CATALOG.get(plan_id, {})
        env_key = plan.get("stripe_price_monthly_env") if billing_cycle == "monthly" else plan.get("stripe_price_yearly_env")
        if not env_key:
            return ""
        return getattr(self._settings, env_key, "") or ""

    def _ensure_stripe_customer(self, user: User, subscription: Subscription) -> str:
        if subscription.stripe_customer_id:
            return subscription.stripe_customer_id

        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.name,
                metadata={"user_id": str(user.id), "username": user.username},
            )
        except stripe.StripeError as exc:
            logger.error("Erro ao criar customer Stripe: %s", exc)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Erro ao criar cliente no Stripe") from exc

        subscription.stripe_customer_id = customer.id
        self.db.commit()
        return customer.id

    def _sync_subscription_from_stripe(self, subscription: Subscription, stripe_sub: dict) -> None:
        plan_id = self._plan_id_from_stripe_sub(stripe_sub)
        plan_config = self.PLAN_CATALOG.get(plan_id, self.PLAN_CATALOG["free"])

        subscription.stripe_subscription_id = stripe_sub["id"]
        subscription.stripe_price_id = stripe_sub["items"]["data"][0]["price"]["id"] if stripe_sub.get("items") else None
        subscription.external_status = stripe_sub.get("status")
        subscription.cancel_at_period_end = stripe_sub.get("cancel_at_period_end", False)
        subscription.plan_id = plan_id
        subscription.billing_cycle = self._billing_cycle_from_stripe_sub(stripe_sub)
        subscription.status = "active" if stripe_sub.get("status") in ("active", "trialing") else stripe_sub.get("status", "active")
        subscription.provider = "stripe"

        period_start = stripe_sub.get("current_period_start")
        period_end = stripe_sub.get("current_period_end")
        if period_start:
            subscription.current_period_start = datetime.fromtimestamp(period_start, tz=UTC)
        if period_end:
            subscription.current_period_end = datetime.fromtimestamp(period_end, tz=UTC)

        subscription.monthly_price = float(plan_config["monthly_price"])
        subscription.yearly_price = float(plan_config["yearly_price"])

    def _plan_id_from_stripe_sub(self, stripe_sub: dict) -> str:
        """Resolve plan_id local a partir dos metadados ou price_id da assinatura Stripe."""
        metadata = stripe_sub.get("metadata") or {}
        if metadata.get("plan_id") and metadata["plan_id"] in self.PLAN_CATALOG:
            return metadata["plan_id"]

        price_id = None
        items = stripe_sub.get("items", {}).get("data", [])
        if items:
            price_id = items[0].get("price", {}).get("id")

        if price_id:
            for plan_id, config in self.PLAN_CATALOG.items():
                if getattr(self._settings, config.get("stripe_price_monthly_env") or "", None) == price_id:
                    return plan_id
                if getattr(self._settings, config.get("stripe_price_yearly_env") or "", None) == price_id:
                    return plan_id

        return "free"

    def _billing_cycle_from_stripe_sub(self, stripe_sub: dict) -> str:
        """Resolve ciclo local sem expor IDs de preco ao frontend."""
        metadata = stripe_sub.get("metadata") or {}
        if metadata.get("billing_cycle") in {"monthly", "yearly"}:
            return metadata["billing_cycle"]

        items = stripe_sub.get("items", {}).get("data", [])
        if not items:
            return "monthly"

        price = items[0].get("price", {})
        recurring = price.get("recurring") or {}
        interval = recurring.get("interval")
        if interval == "year":
            return "yearly"
        if interval == "month":
            return "monthly"

        price_id = price.get("id")
        if price_id:
            for config in self.PLAN_CATALOG.values():
                if getattr(self._settings, config.get("stripe_price_yearly_env") or "", None) == price_id:
                    return "yearly"
                if getattr(self._settings, config.get("stripe_price_monthly_env") or "", None) == price_id:
                    return "monthly"

        return "monthly"

    def _record_event(
        self,
        user_id: int,
        event_type: str,
        amount: float,
        description: str,
        currency: str = "BRL",
        stripe_event_id: str | None = None,
        payload_json: str | None = None,
        event_status: str = "succeeded",
    ) -> None:
        billing_event = BillingEvent(
            user_id=user_id,
            event_type=event_type,
            amount=amount,
            currency=currency,
            description=description,
            provider="stripe",
            stripe_event_id=stripe_event_id,
            status=event_status,
            payload_json=payload_json,
        )
        self.db.add(billing_event)
        self.db.commit()

    # ─────────────────────────────────────────────────────────────────
    # HANDLERS DE WEBHOOK
    # ─────────────────────────────────────────────────────────────────

    def _handle_checkout_completed(self, session: dict, event_id: str) -> None:
        customer_id = session.get("customer")
        stripe_sub_id = session.get("subscription")
        metadata = session.get("metadata") or {}
        user_id_str = metadata.get("user_id")

        if not user_id_str:
            logger.warning("checkout.session.completed sem user_id nos metadados")
            return

        user = self.db.query(User).filter(User.id == int(user_id_str)).first()
        if not user:
            return

        subscription = self._get_or_create_subscription(user)
        subscription.stripe_customer_id = customer_id
        subscription.last_checkout_session_id = session.get("id")

        if stripe_sub_id:
            try:
                stripe.api_key = self._settings.stripe_secret_key
                stripe_sub = stripe.Subscription.retrieve(stripe_sub_id)
                self._sync_subscription_from_stripe(subscription, dict(stripe_sub))
                user.plan = subscription.plan_id
            except stripe.StripeError as exc:
                logger.error("Erro ao recuperar subscription Stripe: %s", exc)

        self.db.commit()
        self._record_event(
            user.id, "checkout_completed", 0.0,
            f"Checkout concluído — sessão {session.get('id')}",
            stripe_event_id=event_id,
            payload_json=json.dumps({"session_id": session.get("id")}),
        )

    def _handle_subscription_upsert(self, stripe_sub: dict, event_id: str) -> None:
        customer_id = stripe_sub.get("customer")
        subscription = self.db.query(Subscription).filter(
            Subscription.stripe_customer_id == customer_id
        ).first()

        if not subscription:
            logger.warning("Subscription Stripe para customer %s não encontrada localmente", customer_id)
            return

        user = self.db.query(User).filter(User.id == subscription.user_id).first()
        if not user:
            return

        self._sync_subscription_from_stripe(subscription, stripe_sub)
        user.plan = subscription.plan_id
        self.db.commit()

        self._record_event(
            user.id, "subscription_updated", 0.0,
            f"Assinatura Stripe atualizada: {stripe_sub.get('id')}",
            stripe_event_id=event_id,
        )

    def _handle_subscription_deleted(self, stripe_sub: dict, event_id: str) -> None:
        customer_id = stripe_sub.get("customer")
        subscription = self.db.query(Subscription).filter(
            Subscription.stripe_customer_id == customer_id
        ).first()

        if not subscription:
            return

        user = self.db.query(User).filter(User.id == subscription.user_id).first()
        subscription.plan_id = "free"
        subscription.status = "canceled"
        subscription.external_status = "canceled"
        subscription.stripe_subscription_id = None
        subscription.stripe_price_id = None
        subscription.cancel_at_period_end = False
        if user:
            user.plan = "free"
        self.db.commit()

        user_id = subscription.user_id
        self._record_event(
            user_id, "subscription_canceled", 0.0,
            "Assinatura cancelada — downgrade para Free",
            stripe_event_id=event_id,
        )

    def _handle_invoice_paid(self, invoice: dict, event_id: str) -> None:
        customer_id = invoice.get("customer")
        subscription = self.db.query(Subscription).filter(
            Subscription.stripe_customer_id == customer_id
        ).first()

        if not subscription:
            return

        amount = (invoice.get("amount_paid") or 0) / 100.0
        currency = (invoice.get("currency") or "brl").upper()
        subscription.last_invoice_id = invoice.get("id")
        subscription.status = "active"
        self.db.commit()

        self._record_event(
            subscription.user_id, "invoice_paid", amount,
            f"Fatura paga: {invoice.get('id')}",
            currency=currency,
            stripe_event_id=event_id,
            event_status="succeeded",
        )

    def _handle_invoice_failed(self, invoice: dict, event_id: str) -> None:
        customer_id = invoice.get("customer")
        subscription = self.db.query(Subscription).filter(
            Subscription.stripe_customer_id == customer_id
        ).first()

        if not subscription:
            return

        subscription.status = "past_due"
        self.db.commit()

        amount = (invoice.get("amount_due") or 0) / 100.0
        currency = (invoice.get("currency") or "brl").upper()
        self._record_event(
            subscription.user_id, "invoice_payment_failed", amount,
            f"Falha no pagamento da fatura: {invoice.get('id')}",
            currency=currency,
            stripe_event_id=event_id,
            event_status="failed",
        )

"""Stripe billing service."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import stripe
from fastapi import HTTPException

from alici_api.config import get_settings
from alici_api.monitoring import capture_critical_event
from alici_api.responses import Codes
from alici_api.services.credit_service import CreditService
from database import (
    buscar_assinatura_usuario,
    iniciar_evento_stripe,
    marcar_evento_stripe_falhou,
    marcar_evento_stripe_processado,
    salvar_assinatura_usuario,
)
from logger import get_logger

logger_billing = get_logger("billing_service")


class BillingService:
    def __init__(self, credit_service: CreditService | None = None):
        self.settings = get_settings()
        self.credit_service = credit_service or CreditService()
        if self.settings.stripe_secret_key:
            stripe.api_key = self.settings.stripe_secret_key.get_secret_value()

    def _require_stripe(self) -> None:
        if not self.settings.stripe_secret_key:
            raise HTTPException(
                status_code=503,
                detail={
                    "code": Codes.SERVICE_UNAVAILABLE,
                    "message": "Stripe nao configurado",
                },
            )

    def plan_catalog(self) -> dict[str, dict[str, Any]]:
        return {
            "free": {
                "name": "Free",
                "price_brl": 0,
                "price_id": None,
                "monthly_credits": self.settings.credits_free_signup,
            },
            "pro": {
                "name": "Pro",
                "price_brl": 49,
                "price_id": self.settings.stripe_price_pro,
                "monthly_credits": self.settings.credits_pro_monthly,
            },
            "ultra": {
                "name": "Ultra",
                "price_brl": 99,
                "price_id": self.settings.stripe_price_ultra,
                "monthly_credits": self.settings.credits_ultra_monthly,
            },
            "enterprise": {
                "name": "Enterprise",
                "price_brl": None,
                "price_id": self.settings.stripe_price_enterprise,
                "monthly_credits": self.settings.credits_enterprise_monthly,
            },
        }

    def price_to_plan(self, price_id: str | None) -> str:
        for plan, data in self.plan_catalog().items():
            if data.get("price_id") and data.get("price_id") == price_id:
                return plan
        return "free"

    def plan_credits(self, plan: str) -> int:
        return int(self.plan_catalog().get(plan, self.plan_catalog()["free"])["monthly_credits"])

    def create_checkout_session(self, user: dict, plan: str, idempotency_key: str | None = None) -> dict:
        self._require_stripe()
        catalog = self.plan_catalog()
        plan = (plan or "").strip().lower()
        if plan not in catalog or plan == "free":
            raise HTTPException(
                status_code=400,
                detail={"code": Codes.BAD_REQUEST, "message": "Plano invalido para checkout"},
            )

        price_id = catalog[plan].get("price_id")
        if not price_id:
            raise HTTPException(
                status_code=503,
                detail={
                    "code": Codes.SERVICE_UNAVAILABLE,
                    "message": f"Preco Stripe nao configurado para o plano {plan}",
                },
            )

        success_url = self.settings.stripe_checkout_success_url or f"{self.settings.public_app_url}/dashboard?checkout=success"
        cancel_url = self.settings.stripe_checkout_cancel_url or f"{self.settings.public_app_url}/dashboard?checkout=cancelled"
        subscription = buscar_assinatura_usuario(user["id"])

        params: dict[str, Any] = {
            "mode": "subscription",
            "line_items": [{"price": price_id, "quantity": 1}],
            "success_url": success_url,
            "cancel_url": cancel_url,
            "client_reference_id": str(user["id"]),
            "customer_email": user["email"],
            "metadata": {
                "user_id": str(user["id"]),
                "plan": plan,
            },
            "subscription_data": {
                "metadata": {
                    "user_id": str(user["id"]),
                    "plan": plan,
                    "price_id": price_id,
                }
            },
            "allow_promotion_codes": True,
        }

        customer_id = subscription.get("stripe_customer_id") if subscription else None
        if customer_id:
            params.pop("customer_email", None)
            params["customer"] = customer_id

        request_options = {}
        if idempotency_key:
            request_options["idempotency_key"] = idempotency_key

        session = stripe.checkout.Session.create(**params, **request_options)
        logger_billing.info(
            "stripe_checkout_created",
            extra={"user_id": user["id"], "plan": plan, "session_id": session.id},
        )
        return {
            "checkout_id": session.id,
            "checkout_url": session.url,
            "plan": plan,
            "price_id": price_id,
        }

    def create_customer_portal_session(self, user: dict, idempotency_key: str | None = None) -> dict:
        self._require_stripe()
        subscription = buscar_assinatura_usuario(user["id"])
        customer_id = subscription.get("stripe_customer_id") if subscription else None
        if not customer_id:
            raise HTTPException(
                status_code=404,
                detail={"code": Codes.NOT_FOUND, "message": "Cliente Stripe nao encontrado para este usuario"},
            )

        return_url = self.settings.stripe_portal_return_url or f"{self.settings.public_app_url}/dashboard"
        request_options = {}
        if idempotency_key:
            request_options["idempotency_key"] = idempotency_key

        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
            **request_options,
        )
        return {"portal_url": session.url}

    def construct_webhook_event(self, payload: bytes, signature: str | None):
        self._require_stripe()
        if not self.settings.stripe_webhook_secret:
            raise HTTPException(
                status_code=503,
                detail={"code": Codes.SERVICE_UNAVAILABLE, "message": "Stripe webhook secret nao configurado"},
            )
        if not signature:
            raise HTTPException(
                status_code=400,
                detail={"code": Codes.BAD_REQUEST, "message": "Assinatura Stripe ausente"},
            )
        try:
            return stripe.Webhook.construct_event(
                payload=payload,
                sig_header=signature,
                secret=self.settings.stripe_webhook_secret.get_secret_value(),
            )
        except ValueError:
            raise HTTPException(status_code=400, detail={"code": Codes.BAD_REQUEST, "message": "Payload Stripe invalido"})
        except stripe.SignatureVerificationError:
            raise HTTPException(status_code=400, detail={"code": Codes.BAD_REQUEST, "message": "Assinatura Stripe invalida"})

    def handle_webhook_event(self, event) -> dict:
        event_id = event["id"]
        event_type = event["type"]
        payload = event.to_dict_recursive() if hasattr(event, "to_dict_recursive") else dict(event)

        should_process = iniciar_evento_stripe(event_id, event_type, payload)
        if not should_process:
            return {"processed": False, "duplicate": True, "event_id": event_id, "event_type": event_type}

        try:
            if event_type == "checkout.session.completed":
                self._handle_checkout_completed(event["data"]["object"])
            elif event_type == "invoice.payment_succeeded":
                self._handle_invoice_payment_succeeded(event["data"]["object"], event_id)
            elif event_type in {
                "customer.subscription.created",
                "customer.subscription.updated",
                "customer.subscription.deleted",
            }:
                self._handle_subscription_event(event["data"]["object"])
            else:
                marcar_evento_stripe_processado(event_id, status="ignored")
                return {"processed": True, "ignored": True, "event_id": event_id, "event_type": event_type}

            marcar_evento_stripe_processado(event_id)
            return {"processed": True, "event_id": event_id, "event_type": event_type}
        except Exception as exc:
            marcar_evento_stripe_falhou(event_id, str(exc))
            logger_billing.exception(
                "stripe_webhook_failed",
                extra={"event_id": event_id, "event_type": event_type},
            )
            capture_critical_event(
                "billing_webhook_failed",
                tags={"event_id": str(event_id), "event_type": str(event_type)},
                extra={"error": str(exc)},
            )
            raise

    def _timestamp_to_datetime(self, value) -> datetime | None:
        if not value:
            return None
        return datetime.fromtimestamp(int(value), tz=timezone.utc)

    def _extract_subscription_fields(self, subscription) -> dict[str, Any]:
        subscription_id = subscription.get("id")
        customer_id = subscription.get("customer")
        status = subscription.get("status", "inactive")
        metadata = subscription.get("metadata") or {}
        plan = (metadata.get("plan") or "").strip().lower()
        price_id = metadata.get("price_id")

        items = subscription.get("items", {}).get("data", [])
        if items:
            price = items[0].get("price") or {}
            price_id = price_id or price.get("id")

        if not plan:
            plan = self.price_to_plan(price_id)
        if status in {"canceled", "incomplete_expired", "unpaid"}:
            plan = "free"

        return {
            "user_id": int(metadata.get("user_id") or 0),
            "stripe_customer_id": customer_id,
            "stripe_subscription_id": subscription_id,
            "stripe_price_id": price_id,
            "status": status,
            "plan": plan,
            "current_period_end": self._timestamp_to_datetime(subscription.get("current_period_end")),
        }

    def _sync_subscription(self, subscription) -> dict[str, Any]:
        data = self._extract_subscription_fields(subscription)
        if not data["user_id"]:
            raise RuntimeError("Assinatura Stripe sem metadata user_id")

        salvar_assinatura_usuario(
            data["user_id"],
            stripe_customer_id=data["stripe_customer_id"],
            stripe_subscription_id=data["stripe_subscription_id"],
            stripe_price_id=data["stripe_price_id"],
            status=data["status"],
            plano=data["plan"],
            current_period_end=data["current_period_end"],
        )
        return data

    def _handle_checkout_completed(self, session) -> None:
        user_id = int((session.get("metadata") or {}).get("user_id") or session.get("client_reference_id") or 0)
        plan = ((session.get("metadata") or {}).get("plan") or "free").strip().lower()
        subscription_id = session.get("subscription")
        customer_id = session.get("customer")
        if not user_id:
            raise RuntimeError("Checkout Stripe sem user_id")

        if subscription_id:
            subscription = stripe.Subscription.retrieve(subscription_id, expand=["items.data.price"])
            self._sync_subscription(subscription)
        else:
            salvar_assinatura_usuario(
                user_id,
                stripe_customer_id=customer_id,
                status="active" if session.get("payment_status") == "paid" else "incomplete",
                plano=plan,
            )

    def _handle_invoice_payment_succeeded(self, invoice, event_id: str) -> None:
        subscription_id = invoice.get("subscription")
        if not subscription_id:
            return

        subscription = stripe.Subscription.retrieve(subscription_id, expand=["items.data.price"])
        data = self._sync_subscription(subscription)
        plan = data["plan"]
        credits = self.plan_credits(plan)
        if credits <= 0:
            return

        self.credit_service.add_credits(
            user_id=data["user_id"],
            amount=credits,
            reason="stripe_invoice_payment_succeeded",
            provider="stripe",
            model=plan,
            job_id=invoice.get("id"),
            metadata={
                "stripe_event_id": event_id,
                "invoice_id": invoice.get("id"),
                "subscription_id": subscription_id,
                "plan": plan,
                "price_id": data["stripe_price_id"],
            },
        )

    def _handle_subscription_event(self, subscription) -> None:
        self._sync_subscription(subscription)

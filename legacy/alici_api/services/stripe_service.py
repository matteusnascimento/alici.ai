"""
Stripe Payment Service for ALICI
Handles subscriptions, webhooks, invoicing
"""

import stripe
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from enum import Enum

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class PlanType(str, Enum):
    """Available subscription plans"""
    FREE = "free"
    PRO = "pro"
    ULTRA = "ultra"
    ENTERPRISE = "enterprise"


class StripeService:
    """Manage Stripe payments and subscriptions"""
    
    PLANS = {
        "free": {
            "name": "Free",
            "price_usd": 0,
            "price_brl": 0,
            "stripe_price_id": None,
            "features": ["20 messages/day", "100MB storage", "7-day history"],
        },
        "pro": {
            "name": "Pro",
            "price_usd": 9,
            "price_brl": 49,
            "stripe_price_id": os.getenv("STRIPE_PRICE_PRO", "price_pro_monthly"),
            "features": ["100 messages/day", "3GB storage", "365-day history", "basic analytics"],
        },
        "ultra": {
            "name": "Ultra",
            "price_usd": 19,
            "price_brl": 99,
            "stripe_price_id": os.getenv("STRIPE_PRICE_ULTRA", "price_ultra_monthly"),
            "features": ["Unlimited messages", "100GB storage", "unlimited history", "advanced analytics", "API access"],
        },
        "enterprise": {
            "name": "Enterprise",
            "price_usd": "Custom",
            "price_brl": "Custom",
            "stripe_price_id": None,
            "features": ["Everything in Ultra", "SSO", "SLA", "dedicated support"],
        },
    }
    
    @staticmethod
    def create_customer(user_email: str, user_name: str, user_id: str) -> str:
        """
        Create Stripe customer linked to ALICI user
        
        Args:
            user_email: Email address
            user_name: Full name
            user_id: ALICI user ID
            
        Returns:
            Stripe customer ID
        """
        try:
            customer = stripe.Customer.create(
                email=user_email,
                name=user_name,
                metadata={
                    "alici_user_id": user_id,
                    "created_at": datetime.utcnow().isoformat()
                }
            )
            return customer.id
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create Stripe customer: {str(e)}")
    
    @staticmethod
    def create_subscription(
        user_id: str,
        stripe_customer_id: str,
        plan: str
    ) -> Dict:
        """
        Create monthly subscription for user
        
        Args:
            user_id: ALICI user ID
            stripe_customer_id: Stripe customer ID
            plan: Plan type ('pro', 'ultra', etc)
            
        Returns:
            Subscription details dict
        """
        if plan == "free":
            return {
                "status": "active",
                "plan": "free",
                "amount": 0,
                "next_billing": None
            }
        
        if plan not in StripeService.PLANS or not StripeService.PLANS[plan]["stripe_price_id"]:
            raise ValueError(f"Invalid plan: {plan}")
        
        try:
            price_id = StripeService.PLANS[plan]["stripe_price_id"]
            
            subscription = stripe.Subscription.create(
                customer=stripe_customer_id,
                items=[{"price": price_id}],
                payment_behavior="default_incomplete",
                collection_method="charge_automatically",
                metadata={
                    "alici_user_id": user_id,
                    "plan": plan
                }
            )
            
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "plan": plan,
                "amount": StripeService.PLANS[plan]["price_brl"],
                "next_billing": subscription.current_period_end,
                "client_secret": subscription.client_secret
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create subscription: {str(e)}")
    
    @staticmethod
    def upgrade_subscription(subscription_id: str, new_plan: str) -> Dict:
        """
        Upgrade/downgrade user plan
        
        Args:
            subscription_id: Stripe subscription ID
            new_plan: New plan type
            
        Returns:
            Updated subscription details
        """
        if new_plan not in StripeService.PLANS or not StripeService.PLANS[new_plan]["stripe_price_id"]:
            raise ValueError(f"Invalid plan: {new_plan}")
        
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            new_price_id = StripeService.PLANS[new_plan]["stripe_price_id"]
            
            updated_subscription = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    "id": subscription.items.data[0].id,
                    "price": new_price_id
                }],
                proration_behavior="always_invoice"
            )
            
            return {
                "subscription_id": updated_subscription.id,
                "new_plan": new_plan,
                "status": updated_subscription.status,
                "prorated_amount": updated_subscription.latest_invoice
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to upgrade subscription: {str(e)}")
    
    @staticmethod
    def cancel_subscription(subscription_id: str, immediate: bool = False) -> Dict:
        """
        Cancel subscription (at end of period or immediately)
        
        Args:
            subscription_id: Stripe subscription ID
            immediate: If True, cancel immediately; else at period end
            
        Returns:
            Cancellation details
        """
        try:
            if immediate:
                deleted = stripe.Subscription.delete(subscription_id)
                return {
                    "status": "canceled",
                    "deleted_at": deleted.canceled_at
                }
            else:
                cancelled = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
                return {
                    "status": cancelled.status,
                    "final_billing": cancelled.current_period_end
                }
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to cancel subscription: {str(e)}")
    
    @staticmethod
    def list_invoices(stripe_customer_id: str, limit: int = 20) -> List[Dict]:
        """
        Get all invoices for a customer
        
        Args:
            stripe_customer_id: Stripe customer ID
            limit: Number of invoices to return
            
        Returns:
            List of invoice dicts
        """
        try:
            invoices = stripe.Invoice.list(customer=stripe_customer_id, limit=limit)
            return [
                {
                    "invoice_id": inv.id,
                    "amount": inv.total / 100,
                    "date": inv.created,
                    "status": inv.status,
                    "pdf_url": inv.invoice_pdf
                }
                for inv in invoices.data
            ]
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to list invoices: {str(e)}")
    
    @staticmethod
    def handle_webhook(event: Dict) -> bool:
        """
        Process Stripe webhook events
        
        Args:
            event: Stripe event dict
            
        Returns:
            True if handled successfully
        """
        event_type = event.get("type")
        data = event.get("data", {}).get("object", {})
        
        try:
            if event_type == "invoice.payment_succeeded":
                user_id = data.get("metadata", {}).get("alici_user_id")
                amount = data.get("amount_paid", 0) / 100
                StripeService._record_payment(user_id, amount)
                
            elif event_type == "customer.subscription.updated":
                user_id = data.get("metadata", {}).get("alici_user_id")
                new_plan = data.get("metadata", {}).get("plan")
                StripeService._update_user_plan(user_id, new_plan)
                
            elif event_type == "customer.subscription.deleted":
                user_id = data.get("metadata", {}).get("alici_user_id")
                StripeService._downgrade_user_to_free(user_id)
            
            return True
        except Exception as e:
            print(f"Webhook error: {str(e)}")
            return False
    
    @staticmethod
    def _record_payment(user_id: str, amount: float):
        """Log payment in database"""
        # TODO: Implement with database connection
        print(f"[PAYMENT] user={user_id}, amount={amount}")
    
    @staticmethod
    def _update_user_plan(user_id: str, plan: str):
        """Update user's plan in database"""
        # TODO: Implement with database connection
        print(f"[PLAN UPDATE] user={user_id}, plan={plan}")
    
    @staticmethod
    def _downgrade_user_to_free(user_id: str):
        """Downgrade user after cancellation"""
        # TODO: Implement with database connection
        StripeService._update_user_plan(user_id, "free")
    
    @staticmethod
    def get_plan_info(plan: str) -> Dict:
        """Get plan information"""
        return StripeService.PLANS.get(plan, {})

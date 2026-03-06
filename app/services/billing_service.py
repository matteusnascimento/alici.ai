"""
Billing service for Stripe integration
"""
import os
from typing import Dict, Any, Optional
import stripe

from app.core.config import settings
from app.models import Organization
from app.core.database import SessionLocal


class BillingService:
    """Stripe billing integration"""

    def __init__(self):
        self.stripe_secret = settings.stripe_secret_key
        if self.stripe_secret:
            stripe.api_key = self.stripe_secret

    def create_customer(self, organization: Organization) -> Optional[str]:
        """Create Stripe customer for organization"""
        if not self.stripe_secret:
            return None

        try:
            customer = stripe.Customer.create(
                email=organization.users[0].email if organization.users else None,
                name=organization.name,
                metadata={
                    "organization_id": organization.id
                }
            )
            return customer.id
        except Exception as e:
            print(f"Error creating Stripe customer: {e}")
            return None

    def create_checkout_session(
        self,
        organization_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str
    ) -> Optional[Dict[str, Any]]:
        """Create Stripe checkout session"""
        if not self.stripe_secret:
            return None

        db = SessionLocal()
        try:
            organization = db.query(Organization).filter(
                Organization.id == organization_id
            ).first()

            if not organization:
                return None

            # Create customer if not exists
            customer_id = organization.stripe_customer_id
            if not customer_id:
                customer_id = self.create_customer(organization)
                if customer_id:
                    organization.stripe_customer_id = customer_id
                    db.commit()

            if not customer_id:
                return None

            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "organization_id": organization_id
                }
            )

            return {
                "session_id": session.id,
                "url": session.url
            }

        except Exception as e:
            print(f"Error creating checkout session: {e}")
            return None
        finally:
            db.close()

    def get_plans(self) -> Dict[str, Any]:
        """Get available plans"""
        return {
            "free": {
                "name": "Free",
                "price": 0,
                "features": ["100 requests/month", "1 agent", "Basic support"]
            },
            "pro": {
                "name": "Professional",
                "price": 299,
                "stripe_price_id": settings.stripe_price_pro,
                "features": ["10K requests/month", "5 agents", "Priority support", "API access"]
            },
            "enterprise": {
                "name": "Enterprise",
                "price": "Custom",
                "stripe_price_id": settings.stripe_price_enterprise,
                "features": ["Unlimited requests", "Unlimited agents", "Dedicated support", "Custom integrations"]
            }
        }

    def update_organization_plan(self, organization_id: str, plan: str):
        """Update organization plan"""
        db = SessionLocal()
        try:
            organization = db.query(Organization).filter(
                Organization.id == organization_id
            ).first()

            if organization:
                organization.plan = plan

                # Update limits based on plan
                limits = {
                    "free": 100,
                    "pro": 10000,
                    "enterprise": 1000000
                }
                organization.monthly_request_limit = limits.get(plan, 100)

                db.commit()
                return True

        except Exception as e:
            print(f"Error updating plan: {e}")
            return False
        finally:
            db.close()

    def check_usage_limit(self, organization: Organization) -> bool:
        """Check if organization has exceeded usage limit"""
        return organization.current_month_requests >= organization.monthly_request_limit

    def increment_usage(self, organization_id: str):
        """Increment usage counter"""
        db = SessionLocal()
        try:
            organization = db.query(Organization).filter(
                Organization.id == organization_id
            ).first()

            if organization:
                organization.current_month_requests += 1
                db.commit()

        except Exception as e:
            print(f"Error incrementing usage: {e}")
        finally:
            db.close()
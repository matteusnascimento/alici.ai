"""Subscription model for organization billing lifecycle."""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.sql import func

from app.core.database import Base


class Subscription(Base):
    __tablename__ = "platform_subscriptions"

    id = Column(String, primary_key=True, index=True)
    organization_id = Column(String, ForeignKey("platform_organizations.id"), nullable=False, index=True)
    initiated_by_user_id = Column(String, ForeignKey("platform_users.id"), nullable=False, index=True)

    plan = Column(String, nullable=False, default="free")
    status = Column(String, nullable=False, default="active")

    stripe_customer_id = Column(String)
    stripe_subscription_id = Column(String)
    checkout_id = Column(String)

    cancel_at_period_end = Column(Boolean, default=False)
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return (
            f"<Subscription(id={self.id}, organization_id={self.organization_id}, "
            f"plan={self.plan}, status={self.status})>"
        )

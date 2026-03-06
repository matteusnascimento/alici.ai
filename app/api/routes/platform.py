"""
Platform management routes (dashboard)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.services.billing_service import BillingService
from app.models import User, Organization, Agent, APIKey, UsageLog

router = APIRouter()
billing_service = BillingService()


@router.get("/overview")
def get_platform_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Get platform overview for organization"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    org = current_user.organization

    # Get stats
    total_users = db.query(User).filter(User.organization_id == org.id).count()
    total_agents = db.query(Agent).filter(Agent.organization_id == org.id).count()
    total_api_keys = db.query(APIKey).filter(APIKey.organization_id == org.id).count()

    # Usage this month
    current_month_usage = db.query(func.sum(UsageLog.tokens_used)).filter(
        UsageLog.organization_id == org.id,
        func.extract('month', UsageLog.created_at) == func.extract('month', func.now()),
        func.extract('year', UsageLog.created_at) == func.extract('year', func.now())
    ).scalar() or 0

    # Recent usage logs
    recent_logs = db.query(UsageLog).filter(
        UsageLog.organization_id == org.id
    ).order_by(UsageLog.created_at.desc()).limit(10).all()

    return {
        "organization": {
            "id": org.id,
            "name": org.name,
            "plan": org.plan,
            "monthly_limit": org.monthly_request_limit,
            "current_usage": org.current_month_requests
        },
        "stats": {
            "total_users": total_users,
            "total_agents": total_agents,
            "total_api_keys": total_api_keys,
            "current_month_tokens": current_month_usage
        },
        "recent_activity": [
            {
                "id": log.id,
                "endpoint": log.endpoint,
                "tokens_used": log.tokens_used,
                "cost": log.cost,
                "created_at": log.created_at
            }
            for log in recent_logs
        ]
    }


@router.get("/api-keys")
def list_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """List API keys for organization"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    api_keys = db.query(APIKey).filter(
        APIKey.organization_id == current_user.organization_id
    ).all()

    return [
        {
            "id": key.id,
            "name": key.name,
            "key": key.key[:20] + "..." if len(key.key) > 20 else key.key,
            "is_active": key.is_active,
            "can_chat": key.can_chat,
            "can_generate": key.can_generate,
            "total_requests": key.total_requests,
            "last_used_at": key.last_used_at,
            "created_at": key.created_at
        }
        for key in api_keys
    ]


@router.post("/api-keys")
def create_api_key(
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Create new API key"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    api_key = AuthService.create_api_key(
        db=db,
        organization_id=current_user.organization_id,
        name=name
    )

    return {
        "id": api_key.id,
        "name": api_key.name,
        "key": api_key.key,  # Show full key on creation
        "created_at": api_key.created_at
    }


@router.delete("/api-keys/{key_id}")
def delete_api_key(
    key_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Delete API key"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.organization_id == current_user.organization_id
    ).first()

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    db.delete(api_key)
    db.commit()

    return {"message": "API key deleted successfully"}


@router.get("/billing")
def get_billing_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Get billing information"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    org = current_user.organization
    plans = billing_service.get_plans()

    return {
        "current_plan": org.plan,
        "monthly_limit": org.monthly_request_limit,
        "current_usage": org.current_month_requests,
        "stripe_customer_id": org.stripe_customer_id,
        "available_plans": plans
    }


@router.post("/billing/checkout")
def create_checkout(
    plan: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Create Stripe checkout session"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    plans = billing_service.get_plans()
    if plan not in plans or plan == "free":
        raise HTTPException(status_code=400, detail="Invalid plan")

    price_id = plans[plan].get("stripe_price_id")
    if not price_id:
        raise HTTPException(status_code=400, detail="Plan not available for purchase")

    session = billing_service.create_checkout_session(
        organization_id=current_user.organization_id,
        price_id=price_id,
        success_url="http://localhost:8000/platform?success=true",
        cancel_url="http://localhost:8000/platform?canceled=true"
    )

    if not session:
        raise HTTPException(status_code=500, detail="Failed to create checkout session")

    return session
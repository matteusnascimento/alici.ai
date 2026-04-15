from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.dashboard import DashboardMetrics, DashboardOverview, DashboardStats, DashboardUsage
from app.schemas.revenue import RevenueIntelligenceSnapshot, RevenueSeriesResponse
from app.services.ai_service import AIService, AIServiceError
from app.services.dashboard_service import DashboardService
from app.services.revenue_service import RevenueService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> DashboardStats:
    return DashboardService(db).get_stats(current_user)


@router.get("/overview", response_model=DashboardOverview)
def get_overview(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> DashboardOverview:
    return DashboardService(db).get_overview(current_user)


@router.get("/usage", response_model=DashboardUsage)
def get_usage(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> DashboardUsage:
    return DashboardService(db).get_usage(current_user)


@router.get("/metrics", response_model=DashboardMetrics)
def get_metrics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> DashboardMetrics:
    return DashboardService(db).get_metrics(current_user)


@router.get("/revenue-intelligence", response_model=RevenueIntelligenceSnapshot)
def get_revenue_intelligence(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RevenueIntelligenceSnapshot:
    return RevenueService(db).get_snapshot(current_user, days=days)


@router.get("/revenue-series", response_model=RevenueSeriesResponse)
def get_revenue_series(
    days: int = 30,
    granularity: str = "daily",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RevenueSeriesResponse:
    return RevenueService(db).get_revenue_series(current_user, days=days, granularity=granularity)


@router.get("/insights", response_model=dict[str, Any])
def get_insights(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    dashboard = DashboardService(db)
    stats = dashboard.get_stats(current_user)
    overview = dashboard.get_overview(current_user)
    usage = dashboard.get_usage(current_user)

    payload = {
        "overview": overview.model_dump(),
        "stats": stats.model_dump(),
        "usage": usage.model_dump(),
    }

    try:
        return AIService().run_task(
            task_name="analytics_insights",
            context=str(payload),
            endpoint="/api/dashboard/insights",
            user_id=current_user.id,
            structured_schema={
                "type": "object",
                "properties": {
                    "executive_summary": {"type": "string"},
                    "warnings": {"type": "array", "items": {"type": "string"}},
                    "opportunities": {"type": "array", "items": {"type": "string"}},
                    "recommendations": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["executive_summary", "warnings", "opportunities", "recommendations"],
                "additionalProperties": False,
            },
        )
    except AIServiceError:
        return {
            "success": False,
            "provider": "openai",
            "model": "gpt-4o-mini",
            "task": "analytics_insights",
            "content": "Insights indisponiveis no momento.",
            "structured_data": {
                "executive_summary": "Insights indisponiveis no momento.",
                "warnings": [],
                "opportunities": [],
                "recommendations": [],
            },
            "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
            "meta": {"latency_ms": 0, "error": "ai_unavailable"},
        }

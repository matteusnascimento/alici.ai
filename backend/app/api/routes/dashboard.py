from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.dashboard import DashboardMetrics, DashboardOverview, DashboardStats, DashboardUsage
from app.services.dashboard_service import DashboardService

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

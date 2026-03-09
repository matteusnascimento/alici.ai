"""Workflow routes for frontend compatibility."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.services.auth_service import AuthService

router = APIRouter()


def _ok(data):
    return {"status": "success", "data": data, "error": None}


@router.get("")
def list_workflows(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    """Return placeholder workflows until full workflow engine is implemented."""
    workflows = [
        {
            "id": "wf-onboarding",
            "name": "Onboarding Sequence",
            "trigger": "Webhook",
            "runsToday": 0,
            "successRate": 100.0,
        },
        {
            "id": "wf-followup",
            "name": "Lead Follow-up",
            "trigger": "Schedule",
            "runsToday": 0,
            "successRate": 100.0,
        },
    ]
    return _ok({"workflows": workflows})

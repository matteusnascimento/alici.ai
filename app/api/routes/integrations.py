"""Integration routes for connecting external channels."""

import json
import uuid
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Integration
from app.models import User
from app.services.auth_service import AuthService

router = APIRouter()


class IntegrationUpsertRequest(BaseModel):
    type: str
    credentials: dict | None = None
    status: str = "connected"


@router.get("")
def list_integrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    rows = (
        db.query(Integration)
        .filter(
            Integration.user_id == current_user.id,
            Integration.organization_id == current_user.organization_id,
            Integration.is_active.is_(True),
        )
        .all()
    )

    return [
        {
            "id": row.id,
            "type": row.type,
            "status": row.status,
            "credentials": json.loads(row.credentials or "{}"),
            "updated_at": row.updated_at,
        }
        for row in rows
    ]


@router.post("")
def create_or_update_integration(
    payload: IntegrationUpsertRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    integration_type = payload.type.strip().lower()
    if not integration_type:
        raise HTTPException(status_code=400, detail="Integration type is required")

    item = (
        db.query(Integration)
        .filter(
            Integration.user_id == current_user.id,
            Integration.organization_id == current_user.organization_id,
            Integration.type == integration_type,
        )
        .first()
    )

    if not item:
        item = Integration(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            type=integration_type,
            is_active=True,
        )
        db.add(item)

    item.status = payload.status
    item.credentials = json.dumps(payload.credentials or {})
    db.commit()
    db.refresh(item)

    return {
        "id": item.id,
        "type": integration_type,
        "status": item.status,
        "updated_at": item.updated_at,
    }


@router.delete("/{integration_type}")
def delete_integration(
    integration_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    row = (
        db.query(Integration)
        .filter(
            Integration.user_id == current_user.id,
            Integration.organization_id == current_user.organization_id,
            Integration.type == integration_type.strip().lower(),
            Integration.is_active.is_(True),
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Integration not found")

    row.is_active = False
    db.commit()
    return {"message": "Integration deleted"}

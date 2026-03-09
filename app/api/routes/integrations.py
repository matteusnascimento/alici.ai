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


def _ok(data):
    # /**
    #  * Function: _ok
    #  * Description: Wrap successful responses in the standard envelope.
    #  * Parameters:
    #  *   data: response payload.
    #  * Returns:
    #  *   dict status envelope.
    #  */
    return {"status": "success", "data": data, "error": None}


class IntegrationUpsertRequest(BaseModel):
    type: str
    credentials: dict | None = None
    status: str = "connected"


@router.get("")
def list_integrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    # /**
    #  * Function: list_integrations
    #  * Description: List active integrations for the authenticated organization.
    #  * Parameters:
    #  *   db: active SQLAlchemy session.
    #  *   current_user: authenticated user context.
    #  * Returns:
    #  *   Standard API envelope with integrations list.
    #  */
    rows = (
        db.query(Integration)
        .filter(
            Integration.user_id == current_user.id,
            Integration.organization_id == current_user.organization_id,
            Integration.is_active.is_(True),
        )
        .all()
    )

    integrations = [
        {
            "id": row.id,
            "provider": row.type,
            "status": row.status,
            "lastSync": row.updated_at.isoformat() if row.updated_at else "never",
        }
        for row in rows
    ]
    return _ok({"integrations": integrations})


@router.post("")
def create_or_update_integration(
    payload: IntegrationUpsertRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    # /**
    #  * Function: create_or_update_integration
    #  * Description: Create or update one integration configuration by provider type.
    #  * Parameters:
    #  *   payload: provider and credentials.
    #  *   db: active SQLAlchemy session.
    #  *   current_user: authenticated user context.
    #  * Returns:
    #  *   Standard API envelope with integration summary.
    #  */
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

    return _ok({
        "id": item.id,
        "provider": integration_type,
        "status": item.status,
        "lastSync": item.updated_at.isoformat() if item.updated_at else "never",
    })


@router.delete("/{integration_type}")
def delete_integration(
    integration_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    # /**
    #  * Function: delete_integration
    #  * Description: Soft-delete an integration by provider type.
    #  * Parameters:
    #  *   integration_type: provider identifier in route.
    #  *   db: active SQLAlchemy session.
    #  *   current_user: authenticated user context.
    #  * Returns:
    #  *   Standard API envelope with deletion status.
    #  */
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
    return _ok({"message": "Integration deleted", "provider": integration_type.strip().lower()})

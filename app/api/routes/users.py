"""User profile routes."""

import uuid
import re

from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password
from app.models import UsageLog, User, UserSetting
from app.services.auth_service import AuthService
from app.services.user_memory_service import UserMemoryService

router = APIRouter()
user_memory_service = UserMemoryService()


class UserUpdateRequest(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None


class PasswordUpdateRequest(BaseModel):
    current_password: str
    new_password: str


class UserSettingsUpdateRequest(BaseModel):
    language: str | None = None
    theme: str | None = None
    notifications_enabled: bool | None = None
    api_key_alias: str | None = None


class UserMemoryUpsertRequest(BaseModel):
    key: str
    value: str


def _get_or_create_settings(db: Session, user_id: str) -> UserSetting:
    settings = db.query(UserSetting).filter(UserSetting.user_id == user_id).first()
    if settings:
        return settings

    settings = UserSetting(id=str(uuid.uuid4()), user_id=user_id)
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


def _validate_password_strength(password: str) -> bool:
    rules = [
        len(password) >= 8,
        bool(re.search(r"[a-z]", password)),
        bool(re.search(r"[A-Z]", password)),
        bool(re.search(r"\d", password)),
        bool(re.search(r"[^A-Za-z0-9]", password)),
    ]
    return all(rules)


def _log_user_action(db: Session, current_user: User, endpoint: str, method: str = "PUT") -> None:
    log = UsageLog(
        id=str(uuid.uuid4()),
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        endpoint=endpoint,
        method=method,
        status_code=200,
        model="system",
        tokens_used=0,
        cost=0.0,
    )
    db.add(log)


@router.get("")
def get_user(current_user: User = Depends(AuthService.get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "plan": current_user.organization.plan,
        "organization_id": current_user.organization_id,
        "created_at": current_user.created_at,
    }


@router.put("")
def update_user(
    payload: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    if payload.email and payload.email != current_user.email:
        exists = db.query(User).filter(User.email == payload.email, User.id != current_user.id).first()
        if exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")
        current_user.email = payload.email

    if payload.full_name is not None:
        full_name = payload.full_name.strip()
        if not full_name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Full name cannot be empty")
        if len(full_name) > 120:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Full name is too long")
        current_user.full_name = full_name

    _log_user_action(db, current_user, "/api/user", method="PUT")

    db.commit()
    db.refresh(current_user)
    return {"message": "User profile updated"}


@router.put("/password")
def update_password(
    payload: PasswordUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    if payload.current_password == payload.new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password must be different")

    if not _validate_password_strength(payload.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain upper, lower, number and symbol with at least 8 chars",
        )

    current_user.hashed_password = get_password_hash(payload.new_password)
    _log_user_action(db, current_user, "/api/user/password", method="PUT")
    db.commit()
    return {"message": "Password updated"}


@router.get("/settings")
def get_user_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    settings = _get_or_create_settings(db, current_user.id)
    return {
        "language": settings.language,
        "theme": settings.theme,
        "notifications_enabled": settings.notifications_enabled,
        "api_key_alias": settings.api_key_alias,
    }


@router.put("/settings")
def update_user_settings(
    payload: UserSettingsUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    settings = _get_or_create_settings(db, current_user.id)
    values = payload.model_dump(exclude_unset=True)
    for key, value in values.items():
        setattr(settings, key, value)

    _log_user_action(db, current_user, "/api/user/settings", method="PUT")

    db.commit()
    db.refresh(settings)
    return {"message": "User settings updated"}


@router.get("/memory")
def list_user_memory(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    rows = user_memory_service.list_memory(db, current_user.id, limit=limit)
    return [
        {
            "key": row.key,
            "value": row.value,
            "timestamp": row.timestamp,
        }
        for row in rows
    ]


@router.post("/memory")
def upsert_user_memory(
    payload: UserMemoryUpsertRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    key = payload.key.strip()
    value = payload.value.strip()
    if not key or not value:
        raise HTTPException(status_code=400, detail="Key and value are required")

    row = user_memory_service.upsert_memory(
        db,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        key=key,
        value=value,
    )
    db.commit()
    db.refresh(row)
    return {
        "key": row.key,
        "value": row.value,
        "timestamp": row.timestamp,
    }

"""
User profile and settings routes.
"""
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.services.auth_service import AuthService

router = APIRouter()

# In-memory settings store for fields not present in SQL models yet.
SETTINGS_STORE: Dict[str, Dict[str, Any]] = {}


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class ThemeLanguageRequest(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    accent: Optional[str] = None


class NotificationSettingsRequest(BaseModel):
    chat_notifications: Optional[bool] = None
    agent_activity_notifications: Optional[bool] = None
    system_updates_notifications: Optional[bool] = None
    marketing_notifications: Optional[bool] = None


class IntegrationConnectRequest(BaseModel):
    platform: str
    token: Optional[str] = None


class AISettingsRequest(BaseModel):
    default_model: Optional[str] = None
    temperature: Optional[float] = None
    memory_enabled: Optional[bool] = None
    web_search_enabled: Optional[bool] = None


def _default_settings(user: User) -> Dict[str, Any]:
    return {
        "theme": "dark",
        "language": "pt-BR",
        "accent": "blue",
        "phone": "",
        "notifications": {
            "chat_notifications": True,
            "agent_activity_notifications": True,
            "system_updates_notifications": True,
            "marketing_notifications": False,
        },
        "ai": {
            "default_model": "ALICI Core",
            "temperature": 0.7,
            "memory_enabled": True,
            "web_search_enabled": True,
        },
        "integrations": {
            "whatsapp": "disconnected",
            "instagram": "disconnected",
            "facebook": "disconnected",
            "telegram": "disconnected",
            "api": "disconnected",
        },
        "archived_chats": [],
        "avatar_url": "/static/avatars/default.svg",
    }


def _get_user_settings(user: User) -> Dict[str, Any]:
    if user.id not in SETTINGS_STORE:
        SETTINGS_STORE[user.id] = _default_settings(user)
    return SETTINGS_STORE[user.id]


@router.get("/user/profile")
def get_user_profile(
    current_user: User = Depends(AuthService.get_current_user),
):
    profile = _get_user_settings(current_user)
    return {
        "id": current_user.id,
        "full_name": current_user.full_name or "",
        "email": current_user.email,
        "phone": profile.get("phone", ""),
        "plan": "Free",
        "avatar_url": profile.get("avatar_url", "/static/avatars/default.svg"),
    }


@router.put("/user/update")
def update_user_profile(
    payload: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    profile = _get_user_settings(current_user)

    if payload.full_name is not None:
        current_user.full_name = payload.full_name.strip()

    if payload.email is not None:
        email = payload.email.strip().lower()
        existing = db.query(User).filter(User.email == email, User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=409, detail="Email already in use")
        current_user.email = email

    if payload.phone is not None:
        profile["phone"] = payload.phone.strip()

    db.commit()
    db.refresh(current_user)

    return {"message": "Profile updated successfully"}


@router.post("/user/avatar")
async def upload_user_avatar(
    avatar: UploadFile = File(...),
    current_user: User = Depends(AuthService.get_current_user),
):
    # Placeholder response. Persisting files can be added in a dedicated media service.
    profile = _get_user_settings(current_user)
    profile["avatar_url"] = f"/static/avatars/{current_user.id}_{avatar.filename}"
    return {
        "message": "Avatar upload accepted",
        "avatar_url": profile["avatar_url"],
    }


@router.get("/settings/theme")
def get_theme_language(
    current_user: User = Depends(AuthService.get_current_user),
):
    profile = _get_user_settings(current_user)
    return {
        "theme": profile.get("theme", "dark"),
        "language": profile.get("language", "pt-BR"),
        "accent": profile.get("accent", "blue"),
    }


@router.put("/settings/theme")
def update_theme_language(
    payload: ThemeLanguageRequest,
    current_user: User = Depends(AuthService.get_current_user),
):
    profile = _get_user_settings(current_user)
    if payload.theme is not None:
        profile["theme"] = payload.theme
    if payload.language is not None:
        profile["language"] = payload.language
    if payload.accent is not None:
        profile["accent"] = payload.accent
    return {"message": "Theme and language settings saved"}


@router.get("/settings/notifications")
def get_notifications(
    current_user: User = Depends(AuthService.get_current_user),
):
    profile = _get_user_settings(current_user)
    return profile.get("notifications", {})


@router.put("/settings/notifications")
def update_notifications(
    payload: NotificationSettingsRequest,
    current_user: User = Depends(AuthService.get_current_user),
):
    profile = _get_user_settings(current_user)
    notifications = profile.setdefault("notifications", {})

    values = payload.model_dump(exclude_unset=True)
    for key, value in values.items():
        notifications[key] = bool(value)

    return {"message": "Notification settings saved"}


@router.get("/settings/ai")
def get_ai_settings(
    current_user: User = Depends(AuthService.get_current_user),
):
    profile = _get_user_settings(current_user)
    return profile.get("ai", {})


@router.put("/settings/ai")
def update_ai_settings(
    payload: AISettingsRequest,
    current_user: User = Depends(AuthService.get_current_user),
):
    profile = _get_user_settings(current_user)
    ai = profile.setdefault("ai", {})
    values = payload.model_dump(exclude_unset=True)
    for key, value in values.items():
        ai[key] = value
    return {"message": "AI settings saved"}


@router.post("/integrations/connect")
def connect_integration(
    payload: IntegrationConnectRequest,
    current_user: User = Depends(AuthService.get_current_user),
):
    profile = _get_user_settings(current_user)
    integrations = profile.setdefault("integrations", {})
    platform = payload.platform.strip().lower()
    integrations[platform] = "connected"
    return {
        "message": f"{platform} connected",
        "platform": platform,
        "status": integrations[platform],
    }


@router.post("/data/export")
def export_data(
    current_user: User = Depends(AuthService.get_current_user),
):
    profile = _get_user_settings(current_user)
    return {
        "message": "Data export generated",
        "download_url": f"/downloads/{current_user.id}/export.json",
        "preview": {
            "profile": {
                "id": current_user.id,
                "email": current_user.email,
                "full_name": current_user.full_name,
            },
            "settings": {
                "theme": profile.get("theme"),
                "language": profile.get("language"),
                "notifications": profile.get("notifications"),
            },
        },
    }


@router.delete("/data/delete")
def delete_all_data(
    current_user: User = Depends(AuthService.get_current_user),
):
    SETTINGS_STORE[current_user.id] = _default_settings(current_user)
    return {"message": "All user settings reset"}

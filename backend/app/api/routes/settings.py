from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.settings import AccountResponse, ProfileRead, ProfileUpdate, SettingsRead, SettingsUpdate
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/me", response_model=AccountResponse)
def get_account(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> AccountResponse:
    user, settings = SettingsService(db).get_account(current_user)
    return AccountResponse(profile=ProfileRead.model_validate(user), settings=SettingsRead.model_validate(settings))


@router.put("/profile", response_model=ProfileRead)
def update_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfileRead:
    user = SettingsService(db).update_profile(current_user, payload)
    return ProfileRead.model_validate(user)


@router.put("/me", response_model=SettingsRead)
def update_settings(
    payload: SettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SettingsRead:
    settings = SettingsService(db).update_settings(current_user, payload)
    return SettingsRead.model_validate(settings)

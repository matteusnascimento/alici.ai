from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.setting import UserSettings
from app.models.user import User
from app.schemas.settings import ProfileUpdate, SettingsUpdate


class SettingsService:
    def __init__(self, db: Session):
        self.db = db

    def get_account(self, user: User) -> tuple[User, UserSettings]:
        settings = self._get_settings(user)
        return user, settings

    def update_profile(self, user: User, payload: ProfileUpdate) -> User:
        conflict = (
            self.db.query(User)
            .filter((User.email == payload.email) | (User.username == payload.username), User.id != user.id)
            .first()
        )
        if conflict:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or username already in use")
        user.name = payload.name
        user.username = payload.username
        user.email = payload.email
        user.phone = payload.phone
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_settings(self, user: User, payload: SettingsUpdate) -> UserSettings:
        settings = self._get_settings(user)
        for key, value in payload.model_dump().items():
            setattr(settings, key, value)
        self.db.commit()
        self.db.refresh(settings)
        return settings

    def _get_settings(self, user: User) -> UserSettings:
        settings = self.db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
        if not settings:
            settings = UserSettings(user_id=user.id)
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
        return settings

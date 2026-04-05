from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.integration import Integration
from app.models.setting import UserSettings
from app.models.user import User
from app.schemas.account import (
    AccountActionResponse,
    AccountArchivedChatList,
    AccountIntegrationRead,
    AccountIntegrationUpdate,
    AccountNotificationRead,
    AccountNotificationUpdate,
    AccountPreferencesRead,
    AccountPreferencesUpdate,
    AccountPrivacyRead,
    AccountProfileRead,
    AccountProfileUpdate,
    AccountSecurityChangePassword,
    AccountSecuritySummary,
)


class AccountService:
    def __init__(self, db: Session):
        self.db = db

    def get_profile(self, user: User) -> AccountProfileRead:
        return AccountProfileRead.model_validate(user)

    def update_profile(self, user: User, payload: AccountProfileUpdate) -> AccountProfileRead:
        conflict = (
            self.db.query(User)
            .filter((User.email == payload.email) | (User.username == payload.username), User.id != user.id)
            .first()
        )
        if conflict:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or username already in use")

        phone = payload.phone.strip() if payload.phone else None
        if phone and len(phone) < 8:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Phone must contain at least 8 digits")

        user.name = payload.name
        user.username = payload.username
        user.email = payload.email
        user.phone = phone
        user.avatar_url = payload.avatar_url
        user.bio = payload.bio
        self.db.commit()
        self.db.refresh(user)
        return AccountProfileRead.model_validate(user)

    def get_preferences(self, user: User) -> AccountPreferencesRead:
        settings = self._get_settings(user)
        return AccountPreferencesRead.model_validate(settings)

    def update_preferences(self, user: User, payload: AccountPreferencesUpdate) -> AccountPreferencesRead:
        settings = self._get_settings(user)
        for key, value in payload.model_dump().items():
            setattr(settings, key, value)
        self.db.commit()
        self.db.refresh(settings)
        return AccountPreferencesRead.model_validate(settings)

    def get_notifications(self, user: User) -> AccountNotificationRead:
        settings = self._get_settings(user)
        return AccountNotificationRead.model_validate(settings)

    def update_notifications(self, user: User, payload: AccountNotificationUpdate) -> AccountNotificationRead:
        settings = self._get_settings(user)
        for key, value in payload.model_dump().items():
            setattr(settings, key, value)
        self.db.commit()
        self.db.refresh(settings)
        return AccountNotificationRead.model_validate(settings)

    def list_integrations(self, user: User) -> list[AccountIntegrationRead]:
        self._seed_integrations(user)
        rows = self.db.query(Integration).filter(Integration.user_id == user.id).order_by(Integration.provider.asc()).all()
        return [
            AccountIntegrationRead(
                id=item.id,
                provider=item.provider,
                name=item.name,
                enabled=item.is_active,
                status="connected" if item.is_active else "disconnected",
                updated_at=item.updated_at,
            )
            for item in rows
        ]

    def update_integration(self, user: User, provider: str, payload: AccountIntegrationUpdate) -> AccountIntegrationRead:
        row = (
            self.db.query(Integration)
            .filter(Integration.user_id == user.id, Integration.provider == provider)
            .first()
        )
        if not row:
            row = Integration(user_id=user.id, provider=provider, name=provider.title(), is_active=payload.enabled)
            self.db.add(row)
        else:
            row.is_active = payload.enabled

        self.db.commit()
        self.db.refresh(row)
        return AccountIntegrationRead(
            id=row.id,
            provider=row.provider,
            name=row.name,
            enabled=row.is_active,
            status="connected" if row.is_active else "disconnected",
            updated_at=row.updated_at,
        )

    def change_password(self, user: User, payload: AccountSecurityChangePassword) -> AccountActionResponse:
        if payload.new_password != payload.confirm_password:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password confirmation does not match")
        if payload.current_password == payload.new_password:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="New password must be different")
        if not verify_password(payload.current_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is invalid")

        user.password_hash = get_password_hash(payload.new_password)
        self.db.commit()
        self.db.refresh(user)
        return AccountActionResponse(message="Password updated successfully")

    def security_summary(self, user: User) -> AccountSecuritySummary:
        settings = self._get_settings(user)
        return AccountSecuritySummary(
            password_last_changed=user.updated_at,
            session_count=1,
            security_alerts=settings.security_alerts,
        )

    def archived_chats(self, _: User) -> AccountArchivedChatList:
        # Archived flow is backend-ready and returns empty list until archive support is implemented.
        return AccountArchivedChatList(items=[])

    def privacy_info(self, user: User) -> AccountPrivacyRead:
        settings = self._get_settings(user)
        return AccountPrivacyRead(
            archived_chat_visibility=settings.archived_chat_visibility,
            notes=[
                "Voce pode solicitar exportacao de dados a qualquer momento.",
                "Solicitacoes de exclusao passam por confirmacao de seguranca.",
                "Preferencias de conversa ficam salvas por usuario.",
            ],
        )

    def request_data_export(self, user: User) -> AccountActionResponse:
        return AccountActionResponse(message=f"Export request queued for {user.email}")

    def request_account_deletion(self, user: User) -> AccountActionResponse:
        return AccountActionResponse(message=f"Deletion request received for {user.email}. We will contact you for confirmation.")

    def logout(self) -> AccountActionResponse:
        return AccountActionResponse(message="Logged out successfully")

    def _get_settings(self, user: User) -> UserSettings:
        settings = self.db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
        if settings:
            return settings

        settings = UserSettings(user_id=user.id)
        self.db.add(settings)
        self.db.commit()
        self.db.refresh(settings)
        return settings

    def _seed_integrations(self, user: User) -> None:
        defaults = [("openai", "OpenAI"), ("whatsapp", "WhatsApp"), ("instagram", "Instagram"), ("website", "Website Widget")]
        existing = {row.provider for row in self.db.query(Integration).filter(Integration.user_id == user.id).all()}
        created = False
        for provider, name in defaults:
            if provider in existing:
                continue
            self.db.add(Integration(user_id=user.id, provider=provider, name=name, is_active=False))
            created = True
        if created:
            self.db.commit()

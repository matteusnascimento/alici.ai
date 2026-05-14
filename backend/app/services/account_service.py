from datetime import datetime, timedelta, timezone
from secrets import randbelow

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
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
    AccountVerificationChallenge,
    AccountVerificationConfirm,
    AccountSecurityChangePassword,
    AccountSecuritySummary,
)


class AccountService:
    def __init__(self, db: Session):
        self.db = db

    def get_profile(self, user: User) -> AccountProfileRead:
        settings = self._get_settings(user)
        return AccountProfileRead(
            id=user.id,
            name=user.name,
            username=user.username,
            email=user.email,
            phone=user.phone,
            avatar_url=user.avatar_url,
            bio=user.bio,
            company=user.company,
            job_title=user.job_title,
            timezone=user.timezone,
            language=settings.language,
            email_verified=user.email_verified,
            phone_verified=user.phone_verified,
            status="ativa",
            plan=user.plan,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at,
        )

    def update_profile(self, user: User, payload: AccountProfileUpdate) -> AccountProfileRead:
        settings = self._get_settings(user)
        email_changed = user.email != payload.email
        conflict = (
            self.db.query(User)
            .filter((User.email == payload.email) | (User.username == payload.username), User.id != user.id)
            .first()
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este email ou nome de usuario ja esta em uso.",
            )

        phone = payload.phone.strip() if payload.phone else None
        phone_changed = (user.phone or None) != phone
        if phone and len(phone) < 8:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Telefone deve ter pelo menos 8 digitos")

        user.name = payload.name
        user.username = payload.username
        user.email = payload.email
        user.phone = phone
        user.avatar_url = payload.avatar_url
        user.bio = payload.bio
        user.company = payload.company.strip() if payload.company else None
        user.job_title = payload.job_title.strip() if payload.job_title else None
        user.timezone = payload.timezone.strip() if payload.timezone else None
        if email_changed:
            user.email_verified = False
            user.email_verification_code = None
            user.email_verification_expires_at = None
        if phone_changed:
            user.phone_verified = False
            user.phone_verification_code = None
            user.phone_verification_expires_at = None
        if payload.language:
            settings.language = payload.language
        self.db.commit()
        self.db.refresh(user)
        self.db.refresh(settings)
        return self.get_profile(user)

    def request_email_verification(self, user: User) -> AccountVerificationChallenge:
        if not user.email:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Nenhum email cadastrado para verificar")

        code = self._generate_code()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        user.email_verification_code = code
        user.email_verification_expires_at = expires_at
        self.db.commit()
        self.db.refresh(user)
        return AccountVerificationChallenge(
            channel="email",
            destination=self._mask_email(user.email),
            expires_at=expires_at,
            message="Código de verificação de email gerado com sucesso.",
            preview_code=code if settings.app_env.lower() != "production" else None,
        )

    def confirm_email_verification(self, user: User, payload: AccountVerificationConfirm) -> AccountActionResponse:
        self._validate_verification_code(
            submitted_code=payload.code,
            expected_code=user.email_verification_code,
            expires_at=user.email_verification_expires_at,
            missing_message="Solicite um código de verificação de email antes de confirmar.",
        )
        user.email_verified = True
        user.email_verification_code = None
        user.email_verification_expires_at = None
        self.db.commit()
        self.db.refresh(user)
        return AccountActionResponse(message="Email verificado com sucesso")

    def request_phone_verification(self, user: User) -> AccountVerificationChallenge:
        if not user.phone:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Cadastre um telefone antes de solicitar verificação")

        code = self._generate_code()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        user.phone_verification_code = code
        user.phone_verification_expires_at = expires_at
        self.db.commit()
        self.db.refresh(user)
        return AccountVerificationChallenge(
            channel="phone",
            destination=self._mask_phone(user.phone),
            expires_at=expires_at,
            message="Código de verificação de telefone gerado com sucesso.",
            preview_code=code if settings.app_env.lower() != "production" else None,
        )

    def confirm_phone_verification(self, user: User, payload: AccountVerificationConfirm) -> AccountActionResponse:
        self._validate_verification_code(
            submitted_code=payload.code,
            expected_code=user.phone_verification_code,
            expires_at=user.phone_verification_expires_at,
            missing_message="Solicite um código de verificação de telefone antes de confirmar.",
        )
        user.phone_verified = True
        user.phone_verification_code = None
        user.phone_verification_expires_at = None
        self.db.commit()
        self.db.refresh(user)
        return AccountActionResponse(message="Telefone verificado com sucesso")

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
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Confirmacao de senha nao confere")
        if payload.current_password == payload.new_password:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="A nova senha deve ser diferente da atual")
        if not verify_password(payload.current_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Senha atual invalida")

        user.password_hash = get_password_hash(payload.new_password)
        self.db.commit()
        self.db.refresh(user)
        return AccountActionResponse(message="Senha atualizada com sucesso")

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
        return AccountActionResponse(message=f"Solicitacao de exportacao registrada para {user.email}")

    def request_account_deletion(self, user: User) -> AccountActionResponse:
        return AccountActionResponse(
            message=f"Solicitacao de exclusao recebida para {user.email}. Entraremos em contato para confirmacao."
        )

    def logout(self) -> AccountActionResponse:
        return AccountActionResponse(message="Sessao encerrada com sucesso")

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

    def _generate_code(self) -> str:
        return f"{randbelow(900000) + 100000}"

    def _validate_verification_code(
        self,
        *,
        submitted_code: str,
        expected_code: str | None,
        expires_at: datetime | None,
        missing_message: str,
    ) -> None:
        if not expected_code or not expires_at:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=missing_message)

        now = datetime.now(timezone.utc)
        normalized_expires_at = expires_at if expires_at.tzinfo else expires_at.replace(tzinfo=timezone.utc)
        if normalized_expires_at < now:
            raise HTTPException(status_code=status.HTTP_410_GONE, detail="O código de verificação expirou. Solicite um novo código.")

        if submitted_code.strip() != expected_code:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Código de verificação inválido")

    def _mask_email(self, email: str) -> str:
        local_part, _, domain = email.partition("@")
        if len(local_part) <= 2:
            masked_local = local_part[0] + "*" if local_part else "*"
        else:
            masked_local = local_part[:2] + "*" * max(1, len(local_part) - 2)
        return f"{masked_local}@{domain}"

    def _mask_phone(self, phone: str) -> str:
        digits = ''.join(char for char in phone if char.isdigit())
        if len(digits) <= 4:
            return '*' * len(digits)
        return '*' * (len(digits) - 4) + digits[-4:]

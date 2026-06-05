from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.admin_audit_event import AdminAuditEvent
from app.models.auth_token import AuthToken
from app.models.subscription import Subscription
from app.models.setting import UserSettings
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest


def _validate_password(password: str) -> None:
    if len(password) < 8:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="A senha deve ter no mínimo 8 caracteres")
    if not any(c.isalpha() for c in password):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="A senha deve conter ao menos uma letra")
    if not any(c.isdigit() for c in password):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="A senha deve conter ao menos um número")


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def _issue_token(self, user: User, token_type: str, expires_delta: timedelta) -> str:
        raw_token = secrets.token_urlsafe(48)
        self.db.add(
            AuthToken(
                user_id=user.id,
                token_hash=self._hash_token(raw_token),
                token_type=token_type,
                expires_at=datetime.now(timezone.utc) + expires_delta,
            )
        )
        return raw_token

    def _consume_token(self, token: str, token_type: str, *, revoke: bool = True) -> AuthToken:
        token_hash = self._hash_token(token)
        row = self.db.query(AuthToken).filter(AuthToken.token_hash == token_hash, AuthToken.token_type == token_type).first()
        now = datetime.now(timezone.utc)
        expires_at = row.expires_at if row and row.expires_at.tzinfo else row.expires_at.replace(tzinfo=timezone.utc) if row else now
        if not row or row.revoked_at or expires_at < now:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido ou expirado")
        if revoke:
            row.revoked_at = now
            row.used_at = now
        return row

    def register(self, payload: RegisterRequest) -> tuple[str, str, User]:
        _validate_password(payload.password)
        existing_user = self.db.query(User).filter((User.email == payload.email) | (User.username == payload.username)).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este email ou nome de usuario ja esta em uso. Tente outro ou faca login.",
            )

        user = User(
            name=payload.name,
            username=payload.username,
            email=payload.email,
            phone=payload.phone,
            password_hash=get_password_hash(payload.password),
            plan="free",
            last_login_at=datetime.now(timezone.utc),
        )
        self.db.add(user)
        self.db.flush()

        defaults = UserSettings(user_id=user.id)
        self.db.add(defaults)
        self.db.add(
            Subscription(
                user_id=user.id,
                plan_id="free",
                status="active",
                monthly_price=0.0,
                yearly_price=0.0,
                billing_cycle="monthly",
                currency="BRL",
                provider="stripe",
            )
        )
        token = create_access_token(str(user.id))
        refresh_token = self._issue_token(user, "refresh", timedelta(minutes=settings.refresh_token_expire_minutes))
        self._issue_token(user, "email_verification", timedelta(minutes=settings.email_verification_expire_minutes))
        self.db.commit()
        self.db.refresh(user)
        return token, refresh_token, user

    def login(self, payload: LoginRequest) -> tuple[str, str, User]:
        user = self.db.query(User).filter(User.email == payload.email).first()

        if not user:
            can_auto_seed = (
                settings.app_env == "development"
                and settings.database_url.startswith("sqlite")
                and payload.email == settings.dev_seed_email
                and payload.password == settings.dev_seed_password
            )
            if can_auto_seed:
                user = User(
                    name=settings.dev_seed_name,
                    username=settings.dev_seed_username,
                    email=settings.dev_seed_email,
                    phone=settings.dev_seed_phone,
                    password_hash=get_password_hash(settings.dev_seed_password),
                    plan="free",
                    last_login_at=datetime.now(timezone.utc),
                )
                self.db.add(user)
                self.db.flush()
                self.db.add(UserSettings(user_id=user.id))
                self.db.add(
                    Subscription(
                        user_id=user.id,
                        plan_id="free",
                        status="active",
                        monthly_price=0.0,
                        yearly_price=0.0,
                        billing_cycle="monthly",
                        currency="BRL",
                        provider="stripe",
                    )
                )
                self.db.commit()
                self.db.refresh(user)

        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha invalidos. Confira os dados e tente novamente.",
            )
        if user.disabled_at is not None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario desativado.")
        user.last_login_at = datetime.now(timezone.utc)
        token = create_access_token(str(user.id))
        refresh_token = self._issue_token(user, "refresh", timedelta(minutes=settings.refresh_token_expire_minutes))
        self.db.add(
            AdminAuditEvent(
                actor_user_id=user.id,
                target_user_id=user.id,
                action="login",
                origin="auth",
                details_json=None,
            )
        )
        self.db.commit()
        self.db.refresh(user)
        return token, refresh_token, user

    def refresh(self, refresh_token: str) -> tuple[str, str, User]:
        row = self._consume_token(refresh_token, "refresh")
        user = self.db.query(User).filter(User.id == row.user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario nao encontrado")
        if user.disabled_at is not None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario desativado.")
        access_token = create_access_token(str(user.id))
        new_refresh = self._issue_token(user, "refresh", timedelta(minutes=settings.refresh_token_expire_minutes))
        self.db.commit()
        self.db.refresh(user)
        return access_token, new_refresh, user

    def request_password_reset(self, email: str) -> str | None:
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            return None
        token = self._issue_token(user, "password_reset", timedelta(minutes=settings.password_reset_expire_minutes))
        self.db.commit()
        return token if settings.app_env == "development" else None

    def reset_password(self, token: str, password: str) -> None:
        _validate_password(password)
        row = self._consume_token(token, "password_reset")
        user = self.db.query(User).filter(User.id == row.user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario nao encontrado")
        user.password_hash = get_password_hash(password)
        now = datetime.now(timezone.utc)
        self.db.query(AuthToken).filter(AuthToken.user_id == user.id, AuthToken.token_type == "refresh").update({"revoked_at": now})
        self.db.commit()

    def request_email_verification(self, user: User) -> str | None:
        if user.email_verified:
            return None
        token = self._issue_token(user, "email_verification", timedelta(minutes=settings.email_verification_expire_minutes))
        self.db.commit()
        return token if settings.app_env == "development" else None

    def verify_email(self, token: str) -> User:
        row = self._consume_token(token, "email_verification")
        user = self.db.query(User).filter(User.id == row.user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario nao encontrado")
        user.email_verified = True
        self.db.commit()
        self.db.refresh(user)
        return user

from datetime import datetime, timedelta, timezone
import json
import secrets

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.admin_audit_event import AdminAuditEvent
from app.models.admin_permission import AdminPermission
from app.models.auth_token import AuthToken
from app.models.billing_event import BillingEvent
from app.models.setting import UserSettings
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.admin import (
    ADMIN_PERMISSION_MODULES,
    AdminAuditEventRead,
    AdminAuditResponse,
    AdminBillingResponse,
    AdminCompanyCreate,
    AdminCompanyRead,
    AdminMetric,
    AdminOverviewResponse,
    AdminPermissionsResponse,
    AdminPermissionsUpdateRequest,
    AdminSecurityEvent,
    AdminSecurityResponse,
    AdminUserActionResponse,
    AdminUserInviteRequest,
    AdminUserInviteResponse,
    AdminUserRead,
    AdminUserUpdateRequest,
)
from app.schemas.billing import PlanLimit
from app.services.auth_service import AuthService
from app.services.billing_service import BillingService


class AdminService:
    permission_modules = ADMIN_PERMISSION_MODULES
    permission_levels = {"none", "read", "write", "admin"}

    def __init__(self, db: Session):
        self.db = db

    def overview(self, current_user: User) -> AdminOverviewResponse:
        users = self.list_users(current_user)
        companies = self.company_rows(current_user)
        subscription_count = db_count(self.db.query(func.count(Subscription.id)).scalar())
        billing_event_count = db_count(self.db.query(func.count(BillingEvent.id)).scalar())
        audit_count = db_count(self.db.query(func.count(AdminAuditEvent.id)).scalar())
        active_sessions = self._active_token_count(current_user)

        return AdminOverviewResponse(
            empresas=companies,
            usuarios=users[:50],
            permissoes=list(self.permission_modules.values()),
            billing=[
                AdminMetric(label="Assinaturas", value=subscription_count),
                AdminMetric(label="Eventos Stripe", value=billing_event_count),
            ],
            seguranca=[
                AdminMetric(label="Sessoes ativas", value=active_sessions),
                AdminMetric(label="Tokens revogados", value=self._revoked_token_count(current_user)),
            ],
            auditoria=[
                AdminMetric(label="Eventos registrados", value=audit_count),
                AdminMetric(label="Usuarios cadastrados", value=len(users)),
            ],
        )

    def company_rows(self, current_user: User) -> list[AdminCompanyRead]:
        query = self.db.query(User).order_by(User.created_at.desc()).limit(500)
        if current_user.company and current_user.role != "owner":
            query = query.filter(User.company == current_user.company)
        users = query.all()

        companies_by_name: dict[str, list[User]] = {}
        for user in users:
            if user.company:
                companies_by_name.setdefault(user.company, []).append(user)

        companies = []
        for name, company_users in sorted(companies_by_name.items()):
            owner = sorted(company_users, key=lambda item: item.created_at or datetime.min)[0]
            companies.append(
                AdminCompanyRead(
                    name=name,
                    email=owner.email,
                    plan=owner.plan,
                    status="Ativa" if any(not item.disabled_at for item in company_users) else "Inativa",
                    users_count=len(company_users),
                    created_at=owner.created_at.date().isoformat() if owner.created_at else None,
                )
            )
        return companies

    def create_company(self, payload: AdminCompanyCreate, actor: User) -> AdminCompanyRead:
        existing_email = self.db.query(User).filter(User.email == str(payload.email)).first()
        if existing_email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail institucional ja cadastrado.")

        existing_company = self.db.query(User).filter(User.company == payload.nome).first()
        if existing_company:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Empresa ja cadastrada.")

        username = self._unique_username(str(payload.email))
        admin_metadata = {
            "admin_company": {
                "razao_social": payload.razao_social,
                "cnpj": payload.cnpj,
                "modules": payload.modules,
            }
        }
        user = User(
            name=payload.nome,
            username=username,
            email=str(payload.email),
            phone=payload.telefone,
            company=payload.nome,
            job_title="Proprietario",
            plan=payload.plano,
            bio=json.dumps(admin_metadata, ensure_ascii=False),
            password_hash=get_password_hash(secrets.token_urlsafe(18)),
            email_verified=False,
        )
        self.db.add(user)
        self.db.flush()
        self._ensure_user_defaults(user)
        self._record_audit(actor, "empresa_criada", target_user=user, details={"company": payload.nome})
        self.db.commit()
        self.db.refresh(user)

        return AdminCompanyRead(
            name=payload.nome,
            email=user.email,
            plan=user.plan,
            status="Ativa",
            users_count=1,
            created_at=user.created_at.date().isoformat() if user.created_at else None,
        )

    def list_users(self, current_user: User) -> list[AdminUserRead]:
        return [self._serialize_user(user) for user in self._user_query(current_user).order_by(User.created_at.desc()).all()]

    def invite_user(self, payload: AdminUserInviteRequest, actor: User) -> AdminUserInviteResponse:
        email = str(payload.email).strip().lower()
        if self.db.query(User).filter(User.email == email).first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Usuario ja cadastrado com este e-mail.")

        user = User(
            name=payload.name.strip(),
            username=self._unique_username(email),
            email=email,
            phone=payload.phone,
            company=actor.company,
            job_title=payload.job_title,
            plan=actor.plan or "free",
            password_hash=get_password_hash(secrets.token_urlsafe(32)),
            email_verified=False,
        )
        self.db.add(user)
        self.db.flush()
        self._ensure_user_defaults(user)

        permissions = self._normalize_permissions(payload.permissions)
        self._upsert_permissions(user, permissions, actor)

        auth_service = AuthService(self.db)
        invite_token = auth_service._issue_token(user, "password_reset", timedelta(minutes=settings.password_reset_expire_minutes))
        self._record_audit(actor, "usuario_convidado", target_user=user, details={"email": email})
        self.db.commit()
        self.db.refresh(user)

        message = "Convite criado, mas envio de email indisponivel."
        token = invite_token if settings.app_env.lower() == "development" else None
        return AdminUserInviteResponse(
            user=self._serialize_user(user),
            email_delivery="unavailable",
            message=message,
            invite_token=token,
        )

    def get_user(self, user_id: int, actor: User) -> AdminUserRead:
        return self._serialize_user(self._user_or_404(user_id, actor))

    def update_user(self, user_id: int, payload: AdminUserUpdateRequest, actor: User) -> AdminUserRead:
        user = self._user_or_404(user_id, actor)
        if payload.email and str(payload.email).lower() != user.email.lower():
            existing = self.db.query(User).filter(User.email == str(payload.email).lower(), User.id != user.id).first()
            if existing:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail ja cadastrado por outro usuario.")
            user.email = str(payload.email).lower()
        if payload.name is not None:
            user.name = payload.name.strip()
        if payload.job_title is not None:
            user.job_title = payload.job_title
        if payload.phone is not None:
            user.phone = payload.phone
        if payload.plan is not None:
            user.plan = payload.plan
        self._record_audit(actor, "usuario_atualizado", target_user=user, details={"user_id": user.id})
        self.db.commit()
        self.db.refresh(user)
        return self._serialize_user(user)

    def disable_user(self, user_id: int, actor: User) -> AdminUserActionResponse:
        if user_id == actor.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nao e possivel desativar o proprio usuario.")
        user = self._user_or_404(user_id, actor)
        user.disabled_at = datetime.now(timezone.utc)
        self.db.query(AuthToken).filter(AuthToken.user_id == user.id, AuthToken.revoked_at.is_(None)).update(
            {"revoked_at": user.disabled_at}
        )
        self._record_audit(actor, "usuario_desativado", target_user=user, details={"user_id": user.id})
        self.db.commit()
        self.db.refresh(user)
        return AdminUserActionResponse(message="Usuario desativado.", user=self._serialize_user(user))

    def enable_user(self, user_id: int, actor: User) -> AdminUserActionResponse:
        user = self._user_or_404(user_id, actor)
        user.disabled_at = None
        self._record_audit(actor, "usuario_reativado", target_user=user, details={"user_id": user.id})
        self.db.commit()
        self.db.refresh(user)
        return AdminUserActionResponse(message="Usuario reativado.", user=self._serialize_user(user))

    def reset_password(self, user_id: int, actor: User) -> AdminUserActionResponse:
        user = self._user_or_404(user_id, actor)
        token = AuthService(self.db)._issue_token(user, "password_reset", timedelta(minutes=settings.password_reset_expire_minutes))
        self._record_audit(actor, "redefinicao_senha_solicitada", target_user=user, details={"user_id": user.id})
        self.db.commit()
        self.db.refresh(user)
        dev_token = token if settings.app_env.lower() == "development" else None
        return AdminUserActionResponse(
            message="Token de redefinicao criado; envio de email indisponivel.",
            user=self._serialize_user(user),
            reset_token=dev_token,
        )

    def get_permissions(self, user_id: int, actor: User) -> AdminPermissionsResponse:
        user = self._user_or_404(user_id, actor)
        return AdminPermissionsResponse(user_id=user.id, permissions=self._permissions_for_edit(user))

    def update_permissions(
        self,
        user_id: int,
        payload: AdminPermissionsUpdateRequest,
        actor: User,
    ) -> AdminPermissionsResponse:
        user = self._user_or_404(user_id, actor)
        permissions = self._normalize_permissions(payload.permissions)
        self._upsert_permissions(user, permissions, actor)
        self._record_audit(actor, "permissoes_alteradas", target_user=user, details={"permissions": permissions})
        self.db.commit()
        return AdminPermissionsResponse(user_id=user.id, permissions=permissions)

    def security(self, current_user: User) -> AdminSecurityResponse:
        users = self._user_query(current_user).all()
        user_ids = [user.id for user in users]
        users_by_id = {user.id: user for user in users}
        now = datetime.now(timezone.utc)

        last_logins = [
            AdminSecurityEvent(
                id=user.id,
                user_id=user.id,
                user_name=user.name,
                user_email=user.email,
                event_type="login",
                status="success",
                created_at=user.last_login_at,
            )
            for user in sorted(
                [item for item in users if item.last_login_at],
                key=lambda item: item.last_login_at or datetime.min,
                reverse=True,
            )[:20]
        ]

        token_query = self.db.query(AuthToken)
        if user_ids:
            token_query = token_query.filter(AuthToken.user_id.in_(user_ids))
        else:
            token_query = token_query.filter(False)
        tokens = token_query.order_by(AuthToken.created_at.desc()).limit(100).all()

        active_tokens = [
            token
            for token in tokens
            if token.revoked_at is None and self._as_aware(token.expires_at) >= now
        ]
        revoked_tokens = [token for token in tokens if token.revoked_at is not None]

        return AdminSecurityResponse(
            last_logins=last_logins,
            active_sessions=[self._serialize_token(token, users_by_id) for token in active_tokens if token.token_type == "refresh"],
            open_sessions=[self._serialize_token(token, users_by_id) for token in active_tokens],
            login_attempts=[],
            revoked_tokens=[self._serialize_token(token, users_by_id) for token in revoked_tokens],
        )

    def audit(self, current_user: User) -> AdminAuditResponse:
        query = self.db.query(AdminAuditEvent).order_by(AdminAuditEvent.created_at.desc()).limit(200)
        if current_user.company and current_user.role != "owner":
            scoped_ids = [user.id for user in self._user_query(current_user).all()]
            if scoped_ids:
                query = query.filter(
                    (AdminAuditEvent.actor_user_id.in_(scoped_ids))
                    | (AdminAuditEvent.target_user_id.in_(scoped_ids))
                )
            else:
                query = query.filter(False)
        events = query.all()
        user_ids = {
            item.actor_user_id
            for item in events
            if item.actor_user_id is not None
        }
        user_ids.update(item.target_user_id for item in events if item.target_user_id is not None)
        users_by_id = {
            user.id: user
            for user in self.db.query(User).filter(User.id.in_(user_ids)).all()
        } if user_ids else {}

        return AdminAuditResponse(
            events=[
                AdminAuditEventRead(
                    id=item.id,
                    data=item.created_at,
                    usuario=users_by_id.get(item.actor_user_id).name if item.actor_user_id in users_by_id else None,
                    acao=item.action,
                    origem=item.origin,
                    detalhes=self._parse_json(item.details_json),
                )
                for item in events
            ]
        )

    def billing(self, current_user: User) -> AdminBillingResponse:
        billing_service = BillingService(self.db)
        current = billing_service.current_subscription(current_user)
        usage = billing_service.usage(current_user).items
        history = billing_service.history(current_user).events
        plan = BillingService.PLAN_CATALOG.get(current.plan_id, BillingService.PLAN_CATALOG["free"])
        limits = [PlanLimit(key=key, value=int(value)) for key, value in plan["limits"].items()]
        message = None
        if not settings.is_stripe_configured():
            message = "Stripe nao configurado. Billing administrativo exibido em modo somente leitura local."
        return AdminBillingResponse(
            current=current,
            usage=usage,
            limits=limits,
            events=history,
            stripe_configured=settings.is_stripe_configured(),
            message=message,
        )

    def _user_query(self, current_user: User):
        query = self.db.query(User)
        if current_user.company and current_user.role != "owner":
            query = query.filter(User.company == current_user.company)
        return query

    def _user_or_404(self, user_id: int, actor: User) -> User:
        user = self._user_query(actor).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario nao encontrado.")
        return user

    def _ensure_user_defaults(self, user: User) -> None:
        if not self.db.query(UserSettings).filter(UserSettings.user_id == user.id).first():
            self.db.add(UserSettings(user_id=user.id))
        if not self.db.query(Subscription).filter(Subscription.user_id == user.id).first():
            plan_id = user.plan if user.plan in BillingService.PLAN_CATALOG else "free"
            config = BillingService.PLAN_CATALOG[plan_id]
            self.db.add(
                Subscription(
                    user_id=user.id,
                    plan_id=plan_id,
                    status="active",
                    monthly_price=float(config["monthly_price"]),
                    yearly_price=float(config["yearly_price"]),
                    billing_cycle="monthly",
                    currency="BRL",
                    provider="stripe",
                )
            )

    def _unique_username(self, email: str) -> str:
        username_base = email.split("@", 1)[0].lower().replace(".", "_").replace("+", "_")[:40] or "user"
        username = username_base
        suffix = 1
        while self.db.query(User).filter(User.username == username).first():
            suffix += 1
            username = f"{username_base}_{suffix}"[:50]
        return username

    def _serialize_user(self, user: User) -> AdminUserRead:
        return AdminUserRead(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            plan=user.plan,
            job_title=user.job_title,
            phone=user.phone,
            company=user.company,
            status=self._status_for_user(user),
            last_login_at=user.last_login_at,
            created_at=user.created_at,
            disabled_at=user.disabled_at,
            email_verified=user.email_verified,
            permissions=user.permissions,
        )

    def _status_for_user(self, user: User) -> str:
        if user.disabled_at is not None:
            return "inactive"
        if not user.email_verified and user.last_login_at is None:
            return "pending"
        return "active"

    def _permissions_for_edit(self, user: User) -> dict[str, str]:
        defaults = {module: "none" for module in self.permission_modules}
        defaults.update(user.permissions)
        return defaults

    def _normalize_permissions(self, permissions: dict[str, str]) -> dict[str, str]:
        normalized = {module: "none" for module in self.permission_modules}
        for module, level in permissions.items():
            if module not in self.permission_modules:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Modulo invalido: {module}")
            if level not in self.permission_levels:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Nivel invalido: {level}")
            normalized[module] = level
        return normalized

    def _upsert_permissions(self, user: User, permissions: dict[str, str], actor: User) -> AdminPermission:
        row = self.db.query(AdminPermission).filter(AdminPermission.user_id == user.id).first()
        if not row:
            row = AdminPermission(user_id=user.id)
            self.db.add(row)
        row.permissions_json = json.dumps(permissions, ensure_ascii=False)
        row.updated_by_user_id = actor.id
        return row

    def _record_audit(self, actor: User, action: str, *, target_user: User | None = None, details: dict | None = None) -> None:
        self.db.add(
            AdminAuditEvent(
                actor_user_id=actor.id if actor else None,
                target_user_id=target_user.id if target_user else None,
                action=action,
                origin="admin",
                details_json=json.dumps(details or {}, ensure_ascii=False),
            )
        )

    def _active_token_count(self, current_user: User) -> int:
        users = self._user_query(current_user).with_entities(User.id).all()
        user_ids = [item[0] for item in users]
        if not user_ids:
            return 0
        now = datetime.now(timezone.utc)
        return db_count(
            self.db.query(func.count(AuthToken.id))
            .filter(AuthToken.user_id.in_(user_ids), AuthToken.revoked_at.is_(None), AuthToken.expires_at >= now)
            .scalar()
        )

    def _revoked_token_count(self, current_user: User) -> int:
        users = self._user_query(current_user).with_entities(User.id).all()
        user_ids = [item[0] for item in users]
        if not user_ids:
            return 0
        return db_count(
            self.db.query(func.count(AuthToken.id))
            .filter(AuthToken.user_id.in_(user_ids), AuthToken.revoked_at.is_not(None))
            .scalar()
        )

    def _serialize_token(self, token: AuthToken, users_by_id: dict[int, User]) -> AdminSecurityEvent:
        user = users_by_id.get(token.user_id)
        token_status = "revogado" if token.revoked_at else "ativo"
        return AdminSecurityEvent(
            id=token.id,
            user_id=token.user_id,
            user_name=user.name if user else None,
            user_email=user.email if user else None,
            event_type=token.token_type,
            status=token_status,
            created_at=token.created_at,
            expires_at=token.expires_at,
            revoked_at=token.revoked_at,
        )

    def _parse_json(self, raw: str | None) -> dict | None:
        if not raw:
            return None
        try:
            parsed = json.loads(raw)
        except (TypeError, ValueError):
            return None
        return parsed if isinstance(parsed, dict) else None

    def _as_aware(self, value: datetime) -> datetime:
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def db_count(value: int | None) -> int:
    return int(value or 0)

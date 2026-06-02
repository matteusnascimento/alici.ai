from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.billing_event import BillingEvent
from app.models.subscription import Subscription
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


class AdminMetric(BaseModel):
    label: str
    value: int


class AdminUserRead(BaseModel):
    id: int
    name: str
    email: str
    role: str
    plan: str


class AdminCompanyRead(BaseModel):
    name: str
    email: str | None = None
    plan: str
    status: str
    users_count: int
    created_at: str | None = None


class AdminOverviewResponse(BaseModel):
    empresas: list[AdminCompanyRead]
    usuarios: list[AdminUserRead]
    permissoes: list[str]
    billing: list[AdminMetric]
    seguranca: list[AdminMetric]
    auditoria: list[AdminMetric]


def require_owner(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administracao restrita ao owner.")
    return current_user


@router.get("/overview", response_model=AdminOverviewResponse)
def admin_overview(_: User = Depends(require_owner), db: Session = Depends(get_db)) -> AdminOverviewResponse:
    users = db.query(User).order_by(User.created_at.desc()).limit(50).all()
    companies_by_name: dict[str, list[User]] = {}
    for user in users:
        if user.company:
            companies_by_name.setdefault(user.company, []).append(user)

    companies = []
    for name, company_users in sorted(companies_by_name.items()):
        owner = sorted(company_users, key=lambda item: item.created_at)[0]
        companies.append(
            AdminCompanyRead(
                name=name,
                email=owner.email,
                plan=owner.plan,
                status="Ativa" if company_users else "Pendente",
                users_count=len(company_users),
                created_at=owner.created_at.date().isoformat() if owner.created_at else None,
            )
        )
    subscription_count = db.query(func.count(Subscription.id)).scalar() or 0
    billing_event_count = db.query(func.count(BillingEvent.id)).scalar() or 0

    return AdminOverviewResponse(
        empresas=companies,
        usuarios=[
            AdminUserRead(id=user.id, name=user.name, email=user.email, role=user.role, plan=user.plan)
            for user in users
        ],
        permissoes=["owner", "member"],
        billing=[
            AdminMetric(label="Assinaturas", value=int(subscription_count)),
            AdminMetric(label="Eventos Stripe", value=int(billing_event_count)),
        ],
        seguranca=[
            AdminMetric(label="Usuarios com email verificado", value=sum(1 for user in users if user.email_verified)),
            AdminMetric(label="Usuarios com telefone verificado", value=sum(1 for user in users if user.phone_verified)),
        ],
        auditoria=[
            AdminMetric(label="Usuarios cadastrados", value=len(users)),
            AdminMetric(label="Empresas identificadas", value=len(companies)),
        ],
    )

import json
import secrets

from pydantic import BaseModel, EmailStr, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, get_password_hash
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


class AdminCompanyCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=140)
    razao_social: str | None = Field(default=None, max_length=180)
    cnpj: str | None = Field(default=None, max_length=32)
    email: EmailStr
    telefone: str | None = Field(default=None, max_length=30)
    plano: str = Field(default="basic", pattern="^(basic|pro|enterprise)$")
    modules: list[str] = Field(default_factory=list)


def _company_rows(db: Session) -> list[AdminCompanyRead]:
    users = db.query(User).order_by(User.created_at.desc()).limit(500).all()
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
    return companies


def require_admin_access(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in {"owner", "admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administracao restrita ao owner/admin.")
    return current_user


@router.get("/overview", response_model=AdminOverviewResponse)
def admin_overview(_: User = Depends(require_admin_access), db: Session = Depends(get_db)) -> AdminOverviewResponse:
    users = db.query(User).order_by(User.created_at.desc()).limit(50).all()
    companies = _company_rows(db)
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


@router.get("/companies", response_model=list[AdminCompanyRead])
def list_admin_companies(_: User = Depends(require_admin_access), db: Session = Depends(get_db)) -> list[AdminCompanyRead]:
    return _company_rows(db)


@router.post("/companies", response_model=AdminCompanyRead, status_code=status.HTTP_201_CREATED)
def create_admin_company(payload: AdminCompanyCreate, _: User = Depends(require_admin_access), db: Session = Depends(get_db)) -> AdminCompanyRead:
    existing_email = db.query(User).filter(User.email == payload.email).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail institucional ja cadastrado.")

    existing_company = db.query(User).filter(User.company == payload.nome).first()
    if existing_company:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Empresa ja cadastrada.")

    username_base = payload.email.split("@", 1)[0].lower().replace(".", "_")
    username = username_base
    suffix = 1
    while db.query(User).filter(User.username == username).first():
        suffix += 1
        username = f"{username_base}_{suffix}"

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
    db.add(user)
    db.commit()
    db.refresh(user)

    return AdminCompanyRead(
        name=payload.nome,
        email=user.email,
        plan=user.plan,
        status="Ativa",
        users_count=1,
        created_at=user.created_at.date().isoformat() if user.created_at else None,
    )

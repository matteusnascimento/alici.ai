from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.admin import (
    AdminAuditResponse,
    AdminBillingResponse,
    AdminCompanyCreate,
    AdminCompanyRead,
    AdminOverviewResponse,
    AdminPermissionsResponse,
    AdminPermissionsUpdateRequest,
    AdminSecurityResponse,
    AdminUserActionResponse,
    AdminUserInviteRequest,
    AdminUserInviteResponse,
    AdminUserRead,
    AdminUserUpdateRequest,
)
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin_access(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in {"owner", "admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administracao restrita ao owner/admin.")
    return current_user


@router.get("/overview", response_model=AdminOverviewResponse)
def admin_overview(
    current_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db),
) -> AdminOverviewResponse:
    return AdminService(db).overview(current_user)


@router.get("/companies", response_model=list[AdminCompanyRead])
def list_admin_companies(
    current_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db),
) -> list[AdminCompanyRead]:
    return AdminService(db).company_rows(current_user)


@router.post("/companies", response_model=AdminCompanyRead, status_code=status.HTTP_201_CREATED)
def create_admin_company(
    payload: AdminCompanyCreate,
    current_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db),
) -> AdminCompanyRead:
    return AdminService(db).create_company(payload, current_user)


@router.get("/users", response_model=list[AdminUserRead])
def list_admin_users(
    current_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db),
) -> list[AdminUserRead]:
    return AdminService(db).list_users(current_user)


@router.post("/users/invite", response_model=AdminUserInviteResponse, status_code=status.HTTP_201_CREATED)
def invite_admin_user(
    payload: AdminUserInviteRequest,
    current_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db),
) -> AdminUserInviteResponse:
    return AdminService(db).invite_user(payload, current_user)


@router.get("/users/{user_id}", response_model=AdminUserRead)
def get_admin_user(
    user_id: int,
    current_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db),
) -> AdminUserRead:
    return AdminService(db).get_user(user_id, current_user)


@router.patch("/users/{user_id}", response_model=AdminUserRead)
def update_admin_user(
    user_id: int,
    payload: AdminUserUpdateRequest,
    current_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db),
) -> AdminUserRead:
    return AdminService(db).update_user(user_id, payload, current_user)


@router.post("/users/{user_id}/disable", response_model=AdminUserActionResponse)
def disable_admin_user(
    user_id: int,
    current_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db),
) -> AdminUserActionResponse:
    return AdminService(db).disable_user(user_id, current_user)


@router.post("/users/{user_id}/enable", response_model=AdminUserActionResponse)
def enable_admin_user(
    user_id: int,
    current_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db),
) -> AdminUserActionResponse:
    return AdminService(db).enable_user(user_id, current_user)


@router.post("/users/{user_id}/reset-password", response_model=AdminUserActionResponse)
def reset_admin_user_password(
    user_id: int,
    current_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db),
) -> AdminUserActionResponse:
    return AdminService(db).reset_password(user_id, current_user)


@router.get("/users/{user_id}/permissions", response_model=AdminPermissionsResponse)
def get_admin_user_permissions(
    user_id: int,
    current_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db),
) -> AdminPermissionsResponse:
    return AdminService(db).get_permissions(user_id, current_user)


@router.put("/users/{user_id}/permissions", response_model=AdminPermissionsResponse)
def update_admin_user_permissions(
    user_id: int,
    payload: AdminPermissionsUpdateRequest,
    current_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db),
) -> AdminPermissionsResponse:
    return AdminService(db).update_permissions(user_id, payload, current_user)


@router.get("/security", response_model=AdminSecurityResponse)
def admin_security(
    current_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db),
) -> AdminSecurityResponse:
    return AdminService(db).security(current_user)


@router.get("/audit", response_model=AdminAuditResponse)
def admin_audit(
    current_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db),
) -> AdminAuditResponse:
    return AdminService(db).audit(current_user)


@router.get("/billing", response_model=AdminBillingResponse)
def admin_billing(
    current_user: User = Depends(require_admin_access),
    db: Session = Depends(get_db),
) -> AdminBillingResponse:
    return AdminService(db).billing(current_user)

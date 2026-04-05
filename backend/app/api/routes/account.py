from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.account import (
    AccountActionResponse,
    AccountArchivedChatList,
    AccountHelpInfo,
    AccountIntegrationRead,
    AccountIntegrationUpdate,
    AccountLegalInfo,
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
from app.schemas.billing import CurrentSubscriptionResponse
from app.services.account_service import AccountService
from app.services.billing_service import BillingService

router = APIRouter(prefix="/account", tags=["account"])


@router.get("/profile", response_model=AccountProfileRead)
def account_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> AccountProfileRead:
    return AccountService(db).get_profile(current_user)


@router.put("/profile", response_model=AccountProfileRead)
def account_profile_update(
    payload: AccountProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountProfileRead:
    return AccountService(db).update_profile(current_user, payload)


@router.get("/preferences", response_model=AccountPreferencesRead)
def account_preferences(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> AccountPreferencesRead:
    return AccountService(db).get_preferences(current_user)


@router.put("/preferences", response_model=AccountPreferencesRead)
def account_preferences_update(
    payload: AccountPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountPreferencesRead:
    return AccountService(db).update_preferences(current_user, payload)


@router.get("/notifications", response_model=AccountNotificationRead)
def account_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> AccountNotificationRead:
    return AccountService(db).get_notifications(current_user)


@router.put("/notifications", response_model=AccountNotificationRead)
def account_notifications_update(
    payload: AccountNotificationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountNotificationRead:
    return AccountService(db).update_notifications(current_user, payload)


@router.get("/subscription", response_model=CurrentSubscriptionResponse)
def account_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CurrentSubscriptionResponse:
    return BillingService(db).current_subscription(current_user)


@router.get("/integrations", response_model=list[AccountIntegrationRead])
def account_integrations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[AccountIntegrationRead]:
    return AccountService(db).list_integrations(current_user)


@router.put("/integrations/{provider}", response_model=AccountIntegrationRead)
def account_integrations_update(
    provider: str,
    payload: AccountIntegrationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountIntegrationRead:
    return AccountService(db).update_integration(current_user, provider, payload)


@router.get("/privacy", response_model=AccountPrivacyRead)
def account_privacy(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> AccountPrivacyRead:
    return AccountService(db).privacy_info(current_user)


@router.post("/privacy/export", response_model=AccountActionResponse)
def account_privacy_export(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> AccountActionResponse:
    return AccountService(db).request_data_export(current_user)


@router.post("/privacy/delete-request", response_model=AccountActionResponse)
def account_privacy_delete_request(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> AccountActionResponse:
    return AccountService(db).request_account_deletion(current_user)


@router.get("/security", response_model=AccountSecuritySummary)
def account_security_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> AccountSecuritySummary:
    return AccountService(db).security_summary(current_user)


@router.post("/security/change-password", response_model=AccountActionResponse)
def account_change_password(
    payload: AccountSecurityChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountActionResponse:
    return AccountService(db).change_password(current_user, payload)


@router.get("/chats/archived", response_model=AccountArchivedChatList)
def account_archived_chats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> AccountArchivedChatList:
    return AccountService(db).archived_chats(current_user)


@router.get("/help", response_model=AccountHelpInfo)
def account_help(_: User = Depends(get_current_user)) -> AccountHelpInfo:
    return AccountHelpInfo(
        app_version="AXI 1.0.0",
        help_center_url="https://axi.app/help",
        report_bug_url="https://axi.app/support",
    )


@router.get("/legal", response_model=AccountLegalInfo)
def account_legal(_: User = Depends(get_current_user)) -> AccountLegalInfo:
    return AccountLegalInfo(
        terms_url="https://axi.app/terms",
        privacy_url="https://axi.app/privacy",
    )


@router.post("/logout", response_model=AccountActionResponse)
def account_logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> AccountActionResponse:
    _ = current_user
    return AccountService(db).logout()

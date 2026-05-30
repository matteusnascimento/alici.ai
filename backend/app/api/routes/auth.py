from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserRead,
    VerifyEmailRequest,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    token, refresh_token, user = AuthService(db).register(payload)
    return TokenResponse(access_token=token, refresh_token=refresh_token, user=UserRead.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    token, refresh_token, user = AuthService(db).login(payload)
    return TokenResponse(access_token=token, refresh_token=refresh_token, user=UserRead.model_validate(user))


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    token, refresh_token, user = AuthService(db).refresh(payload.refresh_token)
    return TokenResponse(access_token=token, refresh_token=refresh_token, user=UserRead.model_validate(user))


@router.post("/password/forgot", response_model=MessageResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)) -> MessageResponse:
    dev_token = AuthService(db).request_password_reset(str(payload.email))
    message = "Se o email existir, enviaremos instrucoes para redefinir a senha."
    if dev_token:
        message = f"{message} Token dev: {dev_token}"
    return MessageResponse(message=message)


@router.post("/password/reset", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> MessageResponse:
    AuthService(db).reset_password(payload.token, payload.password)
    return MessageResponse(message="Senha redefinida com sucesso.")


@router.post("/email/request-verification", response_model=MessageResponse)
def request_email_verification(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MessageResponse:
    dev_token = AuthService(db).request_email_verification(current_user)
    message = "Se o email ainda nao foi verificado, enviaremos um link de verificacao."
    if dev_token:
        message = f"{message} Token dev: {dev_token}"
    return MessageResponse(message=message)


@router.post("/email/verify", response_model=UserRead)
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)) -> UserRead:
    user = AuthService(db).verify_email(payload.token)
    return UserRead.model_validate(user)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)

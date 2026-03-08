"""Authentication routes for platform backend."""

from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.services.auth_service import AuthService

router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    organization_name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = AuthService.create_user(
        db=db,
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
        organization_name=payload.organization_name,
    )

    access_token = AuthService.create_access_token_for_user(user)
    refresh_token = AuthService.create_refresh_token_for_user(user)

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "organization_id": user.organization_id,
        },
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = AuthService.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return {
        "access_token": AuthService.create_access_token_for_user(user),
        "refresh_token": AuthService.create_refresh_token_for_user(user),
        "token_type": "bearer",
    }


@router.post("/refresh")
def refresh_token(payload: RefreshRequest):
    access_token = AuthService.refresh_access_token(payload.refresh_token)
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(current_user: User = Depends(AuthService.get_current_user)):
    # JWT is stateless here; clients should discard tokens.
    return {"message": "Logged out successfully", "user_id": current_user.id}

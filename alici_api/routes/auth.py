"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException

from alici_api.dependencies import get_current_user
from alici_api.responses import Codes, success
from alici_api.schemas import LoginRequest, RefreshRequest, RegisterRequest
from alici_api.services.auth_service import AuthService
from logger import get_logger

router = APIRouter(prefix="/auth", tags=["auth"])
logger_auth = get_logger("route_auth")
auth_service = AuthService()


@router.post("/register")
def register(req: RegisterRequest):
    usuario = auth_service.register(req.nome, req.email, req.senha)
    return success(
        Codes.AUTH_REGISTER_OK,
        message="Usuário criado com sucesso",
        usuario={
            "id": usuario["id"],
            "nome": usuario["nome"],
            "email": usuario["email"],
        },
    )


@router.post("/login")
def login(req: LoginRequest):
    payload = auth_service.login(req.email, req.senha)
    return success(Codes.AUTH_LOGIN_OK, **payload)


@router.post("/refresh")
def refresh_token(req: RefreshRequest):
    try:
        payload = auth_service.refresh_access_token(req.refresh_token)
        return success(Codes.AUTH_LOGIN_OK, **payload)
    except HTTPException:
        raise
    except Exception:
        logger_auth.exception("Falha inesperada no refresh token")
        raise HTTPException(
            status_code=500,
            detail={"code": Codes.INTERNAL, "message": "Erro interno do servidor"},
        )


@router.post("/logout")
def logout(user=Depends(get_current_user)):
    auth_service.logout(user["id"])
    return success(Codes.AUTH_LOGOUT_OK, message="Logout realizado")

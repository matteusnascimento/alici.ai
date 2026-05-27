"""Authentication routes."""

from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse

from alici_api.config import get_settings
from alici_api.dependencies import get_current_user
from alici_api.responses import Codes, success
from alici_api.schemas import LoginRequest, RefreshRequest, RegisterRequest
from alici_api.services.auth_service import AuthService
from logger import get_logger

router = APIRouter(prefix="/auth", tags=["auth"])
logger_auth = get_logger("route_auth")
auth_service = AuthService()
settings = get_settings()


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


@router.get("/google/start")
def google_start():
    return RedirectResponse(url=auth_service.google_authorization_url(), status_code=302)


@router.get("/google/callback")
async def google_callback(code: str | None = Query(default=None), error: str | None = Query(default=None)):
    frontend_url = settings.frontend_app_url.rstrip("/")
    if error or not code:
        params = urlencode({"error": error or "missing_code"})
        return RedirectResponse(url=f"{frontend_url}/auth/google/callback?{params}", status_code=302)

    payload = await auth_service.login_with_google_code(code)
    params = urlencode({
        "access_token": payload["access_token"],
        "refresh_token": payload.get("refresh_token", ""),
        "token_type": payload.get("token_type", "bearer"),
    })
    return RedirectResponse(url=f"{frontend_url}/auth/google/callback?{params}", status_code=302)


@router.get("/me")
def me(user=Depends(get_current_user)):
    return success(
        Codes.AUTH_LOGIN_OK,
        usuario={
            "id": user["id"],
            "nome": user["nome"],
            "email": user["email"],
            "plano": user.get("plano", "free"),
        },
    )


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

"""Authentication service with business rules."""

from __future__ import annotations

import secrets
from datetime import datetime, timezone
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException

from alici_api.config import get_settings
from alici_api.repositories.refresh_token_repository import RefreshTokenRepository
from alici_api.repositories.user_repository import UserRepository
from alici_api.responses import Codes
from auth import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)
from logger import get_logger

logger_auth_service = get_logger("auth_service")


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository | None = None,
        refresh_repository: RefreshTokenRepository | None = None,
    ) -> None:
        self.user_repository = user_repository or UserRepository()
        self.refresh_repository = refresh_repository or RefreshTokenRepository()
        self.settings = get_settings()

    @staticmethod
    def _exp_to_datetime(exp: int) -> datetime:
        return datetime.fromtimestamp(int(exp), tz=timezone.utc)

    def register(self, nome: str, email: str, senha: str):
        if len(senha) < 8:
            raise HTTPException(status_code=400, detail={"code": Codes.BAD_REQUEST, "message": "Senha deve ter pelo menos 8 caracteres"})

        if len(senha.encode("utf-8")) > 72:
            raise HTTPException(status_code=400, detail={"code": Codes.BAD_REQUEST, "message": "Senha muito longa (max 72 bytes)"})

        if len(nome.strip()) < 2:
            raise HTTPException(status_code=400, detail={"code": Codes.BAD_REQUEST, "message": "Nome deve ter pelo menos 2 caracteres"})

        if self.user_repository.find_by_email(email):
            raise HTTPException(status_code=400, detail={"code": Codes.BAD_REQUEST, "message": "Email ja esta registrado"})

        senha_hash = hash_password(senha)
        usuario = self.user_repository.create(nome.strip(), email, senha_hash)
        if not usuario:
            logger_auth_service.error("Falha ao criar usuario", extra={"email": email})
            raise HTTPException(status_code=500, detail={"code": Codes.INTERNAL, "message": "Erro interno do servidor"})

        return usuario

    def _issue_session(self, usuario: dict) -> dict:
        access_token = create_access_token(usuario["id"], usuario["email"])
        refresh_token = create_refresh_token(usuario["id"], usuario["email"])
        refresh_payload = verify_token(refresh_token, expected_type="refresh")
        jti = refresh_payload.get("jti")
        exp = refresh_payload.get("exp")

        if not jti or not exp:
            raise HTTPException(status_code=500, detail={"code": Codes.INTERNAL, "message": "Erro interno do servidor"})

        self.refresh_repository.create(usuario["id"], str(jti), self._exp_to_datetime(int(exp)))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "usuario": {
                "id": usuario["id"],
                "nome": usuario["nome"],
                "email": usuario["email"],
                "plano": usuario.get("plano", "free"),
            },
        }

    def login(self, email: str, senha: str) -> dict:
        usuario = self.user_repository.find_by_email(email)
        if not usuario or not verify_password(senha, usuario["senha_hash"]):
            raise HTTPException(status_code=401, detail={"code": Codes.UNAUTHORIZED, "message": "Email ou senha invalidos"})

        return self._issue_session(usuario)

    def google_authorization_url(self) -> str:
        if not self.settings.google_oauth_client_id:
            raise HTTPException(
                status_code=503,
                detail={"code": Codes.BAD_REQUEST, "message": "Login com Google ainda nao foi configurado."},
            )

        redirect_uri = self.settings.google_oauth_redirect_uri or f"{self.settings.api_base_url.rstrip('/')}/auth/google/callback"
        params = {
            "client_id": self.settings.google_oauth_client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "select_account",
        }
        return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

    async def login_with_google_code(self, code: str) -> dict:
        if not self.settings.google_oauth_client_id or not self.settings.google_oauth_client_secret:
            raise HTTPException(
                status_code=503,
                detail={"code": Codes.BAD_REQUEST, "message": "Login com Google ainda nao foi configurado."},
            )

        redirect_uri = self.settings.google_oauth_redirect_uri or f"{self.settings.api_base_url.rstrip('/')}/auth/google/callback"
        client_secret = self.settings.google_oauth_client_secret.get_secret_value()

        async with httpx.AsyncClient(timeout=15.0) as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": self.settings.google_oauth_client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            if token_response.status_code >= 400:
                logger_auth_service.warning("Google OAuth token exchange failed", extra={"status": token_response.status_code})
                raise HTTPException(status_code=401, detail={"code": Codes.UNAUTHORIZED, "message": "Falha ao autenticar com Google"})

            google_access_token = token_response.json().get("access_token")
            if not google_access_token:
                raise HTTPException(status_code=401, detail={"code": Codes.UNAUTHORIZED, "message": "Resposta invalida do Google"})

            userinfo_response = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {google_access_token}"},
            )
            if userinfo_response.status_code >= 400:
                raise HTTPException(status_code=401, detail={"code": Codes.UNAUTHORIZED, "message": "Nao foi possivel ler o perfil Google"})

        profile = userinfo_response.json()
        email = str(profile.get("email") or "").strip().lower()
        email_verified = bool(profile.get("email_verified"))
        name = str(profile.get("name") or email).strip()

        if not email or not email_verified:
            raise HTTPException(status_code=401, detail={"code": Codes.UNAUTHORIZED, "message": "Email Google nao verificado"})

        usuario = self.user_repository.find_by_email(email)
        if not usuario:
            random_password = secrets.token_urlsafe(48)[:72]
            usuario = self.user_repository.create(name or email, email, hash_password(random_password))
            if not usuario:
                raise HTTPException(status_code=500, detail={"code": Codes.INTERNAL, "message": "Erro interno do servidor"})

        return self._issue_session(usuario)

    def refresh_access_token(self, refresh_token: str) -> dict:
        payload = verify_token(refresh_token, expected_type="refresh")
        user_id = int(payload.get("sub"))
        email = str(payload.get("email"))
        jti = str(payload.get("jti") or "")

        if not jti:
            raise HTTPException(status_code=401, detail={"code": Codes.UNAUTHORIZED, "message": "Token invalido"})

        token_entry = self.refresh_repository.find_by_jti(jti)
        if not token_entry or token_entry.get("revoked"):
            raise HTTPException(status_code=401, detail={"code": Codes.UNAUTHORIZED, "message": "Token invalido ou revogado"})

        expires_at = token_entry.get("expires_at")
        if not expires_at or expires_at <= datetime.now(timezone.utc):
            self.refresh_repository.revoke_by_jti(jti)
            raise HTTPException(status_code=401, detail={"code": Codes.UNAUTHORIZED, "message": "Token expirado"})

        usuario = self.user_repository.find_by_id(user_id)
        if not usuario or usuario.get("email") != email:
            raise HTTPException(status_code=401, detail={"code": Codes.UNAUTHORIZED, "message": "Token invalido"})

        self.refresh_repository.revoke_by_jti(jti)

        new_access = create_access_token(user_id, email)
        new_refresh = create_refresh_token(user_id, email)
        new_refresh_payload = verify_token(new_refresh, expected_type="refresh")
        new_jti = str(new_refresh_payload.get("jti"))
        new_exp = int(new_refresh_payload.get("exp"))
        self.refresh_repository.create(user_id, new_jti, self._exp_to_datetime(new_exp))

        return {
            "access_token": new_access,
            "refresh_token": new_refresh,
            "token_type": "bearer",
        }

    def logout(self, user_id: int) -> None:
        self.refresh_repository.revoke_all_by_user(user_id)

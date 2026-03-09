"""Authentication service with business rules."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException

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
            raise HTTPException(status_code=400, detail={"code": Codes.BAD_REQUEST, "message": "Email já está registrado"})

        senha_hash = hash_password(senha)
        usuario = self.user_repository.create(nome.strip(), email, senha_hash)
        if not usuario:
            logger_auth_service.error("Falha ao criar usuário", extra={"email": email})
            raise HTTPException(status_code=500, detail={"code": Codes.INTERNAL, "message": "Erro interno do servidor"})

        return usuario

    def login(self, email: str, senha: str) -> dict:
        usuario = self.user_repository.find_by_email(email)
        if not usuario or not verify_password(senha, usuario["senha_hash"]):
            raise HTTPException(status_code=401, detail={"code": Codes.UNAUTHORIZED, "message": "Email ou senha inválidos"})

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

    def refresh_access_token(self, refresh_token: str) -> dict:
        payload = verify_token(refresh_token, expected_type="refresh")
        user_id = int(payload.get("sub"))
        email = str(payload.get("email"))
        jti = str(payload.get("jti") or "")

        if not jti:
            raise HTTPException(status_code=401, detail={"code": Codes.UNAUTHORIZED, "message": "Token inválido"})

        token_entry = self.refresh_repository.find_by_jti(jti)
        if not token_entry or token_entry.get("revoked"):
            raise HTTPException(status_code=401, detail={"code": Codes.UNAUTHORIZED, "message": "Token inválido ou revogado"})

        expires_at = token_entry.get("expires_at")
        if not expires_at or expires_at <= datetime.now(timezone.utc):
            self.refresh_repository.revoke_by_jti(jti)
            raise HTTPException(status_code=401, detail={"code": Codes.UNAUTHORIZED, "message": "Token expirado"})

        usuario = self.user_repository.find_by_id(user_id)
        if not usuario or usuario.get("email") != email:
            raise HTTPException(status_code=401, detail={"code": Codes.UNAUTHORIZED, "message": "Token inválido"})

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

"""Refresh token repository."""

from database import (
    buscar_refresh_token_por_jti,
    revogar_refresh_token_por_jti,
    revogar_refresh_tokens_usuario,
    salvar_refresh_token,
)


class RefreshTokenRepository:
    def create(self, user_id: int, jti: str, expires_at, created_ip: str | None = None, user_agent: str | None = None) -> bool:
        return salvar_refresh_token(user_id, jti, expires_at, created_ip, user_agent)

    def find_by_jti(self, jti: str):
        return buscar_refresh_token_por_jti(jti)

    def revoke_by_jti(self, jti: str) -> bool:
        return revogar_refresh_token_por_jti(jti)

    def revoke_all_by_user(self, user_id: int) -> bool:
        return revogar_refresh_tokens_usuario(user_id)

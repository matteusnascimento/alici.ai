"""Shared dependencies for route handlers."""

from fastapi import HTTPException, Request

from auth import verify_token
from database import buscar_usuario_por_id


def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise HTTPException(status_code=401, detail="Token não fornecido")

    try:
        if not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Formato de token inválido")

        token = auth_header.replace("Bearer ", "", 1)
        payload = verify_token(token)
        user_id = int(payload.get("sub"))

        user = buscar_usuario_por_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")

        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")

"""Shared dependencies for route handlers."""

from fastapi import HTTPException, Request

from alici_api.middleware.monitoring import user_id_ctx
from alici_api.monitoring import set_monitoring_user
from alici_api.repositories.user_repository import UserRepository
from alici_api.responses import Codes
from auth import verify_token

user_repository = UserRepository()


def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise HTTPException(
            status_code=401,
            detail={"code": Codes.UNAUTHORIZED, "message": "Token nao fornecido"},
        )

    try:
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail={"code": Codes.UNAUTHORIZED, "message": "Formato de token invalido"},
            )

        token = auth_header.replace("Bearer ", "", 1)
        payload = verify_token(token, expected_type="access")
        user_id = int(payload.get("sub"))

        user = user_repository.find_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=401,
                detail={"code": Codes.UNAUTHORIZED, "message": "Usuario nao encontrado"},
            )

        user_id_ctx.set(str(user["id"]))
        set_monitoring_user(user)
        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=401,
            detail={"code": Codes.UNAUTHORIZED, "message": "Token invalido"},
        )

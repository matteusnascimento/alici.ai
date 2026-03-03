"""Authentication routes."""

import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from alici_api.dependencies import get_current_user
from alici_api.repositories.user_repository import UserRepository
from alici_api.responses import Codes, success
from alici_api.schemas import LoginRequest, RefreshRequest, RegisterRequest, UpdateProfileRequest
from alici_api.services.auth_service import AuthService
from auth import hash_password, verify_password
from logger import get_logger

router = APIRouter(prefix="/auth", tags=["auth"])
logger_auth = get_logger("route_auth")
auth_service = AuthService()
user_repository = UserRepository()

_GENERATED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "generated", "avatars")


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


@router.get("/profile")
def get_profile(user=Depends(get_current_user)):
    return success(
        Codes.SUCCESS_DEFAULT,
        usuario={
            "id": user["id"],
            "nome": user["nome"],
            "email": user["email"],
            "plano": user.get("plano", "free"),
            "foto_url": user.get("foto_url"),
            "tema": user.get("tema", "dark"),
        },
    )


@router.put("/profile")
def update_profile(req: UpdateProfileRequest, user=Depends(get_current_user)):
    nome = req.nome.strip() if req.nome else None
    senha_hash = None
    tema = req.tema

    if nome is not None and len(nome) < 2:
        raise HTTPException(
            status_code=400,
            detail={"code": Codes.BAD_REQUEST, "message": "Nome deve ter pelo menos 2 caracteres"},
        )

    if req.nova_senha:
        if not req.senha_atual:
            raise HTTPException(
                status_code=400,
                detail={"code": Codes.BAD_REQUEST, "message": "Senha atual é obrigatória para alterar a senha"},
            )
        if len(req.nova_senha) < 8:
            raise HTTPException(
                status_code=400,
                detail={"code": Codes.BAD_REQUEST, "message": "Nova senha deve ter pelo menos 8 caracteres"},
            )
        if len(req.nova_senha.encode("utf-8")) > 72:
            raise HTTPException(
                status_code=400,
                detail={"code": Codes.BAD_REQUEST, "message": "Senha muito longa (max 72 bytes)"},
            )
        current_user_data = user_repository.find_by_id(user["id"])
        if not current_user_data or not verify_password(req.senha_atual, current_user_data.get("senha_hash", "")):
            raise HTTPException(
                status_code=400,
                detail={"code": Codes.BAD_REQUEST, "message": "Senha atual incorreta"},
            )
        senha_hash = hash_password(req.nova_senha)

    updated = user_repository.update_profile(
        user["id"],
        nome=nome,
        senha_hash=senha_hash,
        tema=tema,
    )
    if not updated:
        raise HTTPException(
            status_code=500,
            detail={"code": Codes.INTERNAL, "message": "Erro ao atualizar perfil"},
        )

    updated_user = user_repository.find_by_id(user["id"])
    return success(
        Codes.SUCCESS_DEFAULT,
        message="Perfil atualizado",
        usuario={
            "id": updated_user["id"],
            "nome": updated_user["nome"],
            "email": updated_user["email"],
            "plano": updated_user.get("plano", "free"),
            "foto_url": updated_user.get("foto_url"),
            "tema": updated_user.get("tema", "dark"),
        },
    )


@router.post("/profile/photo")
async def upload_profile_photo(user=Depends(get_current_user), file: UploadFile = File(...)):
    allowed_types = {"image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail={"code": Codes.BAD_REQUEST, "message": "Tipo de arquivo não suportado"},
        )

    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=400,
            detail={"code": Codes.BAD_REQUEST, "message": "Arquivo vazio"},
        )
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail={"code": Codes.BAD_REQUEST, "message": "Arquivo muito grande (max 5MB)"},
        )

    ext_map = {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/gif": ".gif",
        "image/webp": ".webp",
    }
    ext = ext_map.get(file.content_type or "", ".png")
    filename = f"avatar_{user['id']}_{uuid.uuid4().hex[:8]}{ext}"

    avatars_dir = _GENERATED_DIR
    os.makedirs(avatars_dir, exist_ok=True)
    file_path = os.path.join(avatars_dir, filename)

    with open(file_path, "wb") as f:
        f.write(content)

    foto_url = f"/generated/avatars/{filename}"
    user_repository.update_profile(user["id"], foto_url=foto_url)

    return success(Codes.SUCCESS_DEFAULT, message="Foto atualizada", foto_url=foto_url)

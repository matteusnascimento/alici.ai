"""Authentication routes."""

import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from alici_api.dependencies import get_current_user
from alici_api.repositories.user_repository import UserRepository
from alici_api.responses import Codes, success
from alici_api.schemas import LoginRequest, ProfileUpdateRequest, RefreshRequest, RegisterRequest
from alici_api.services.auth_service import AuthService
from auth import hash_password, verify_password
from logger import get_logger

router = APIRouter(prefix="/auth", tags=["auth"])
logger_auth = get_logger("route_auth")
auth_service = AuthService()
user_repository = UserRepository()

_AVATAR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "generated", "avatars")
_MAX_PHOTO_BYTES = 5 * 1024 * 1024  # 5 MB


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
    full = user_repository.find_full(user["id"]) or user
    return success(
        Codes.SUCCESS_DEFAULT,
        nome=full.get("nome"),
        email=full.get("email"),
        foto_url=full.get("foto_url"),
        tema=full.get("tema", "dark"),
        plano=full.get("plano", "free"),
    )


@router.put("/profile")
def update_profile(req: ProfileUpdateRequest, user=Depends(get_current_user)):
    updates: dict = {}

    if req.nome is not None:
        nome = req.nome.strip()
        if len(nome) < 2:
            raise HTTPException(
                status_code=400,
                detail={"code": Codes.BAD_REQUEST, "message": "Nome deve ter pelo menos 2 caracteres"},
            )
        updates["nome"] = nome

    if req.tema is not None:
        if req.tema not in ("dark", "light"):
            raise HTTPException(
                status_code=400,
                detail={"code": Codes.BAD_REQUEST, "message": "Tema inválido. Use 'dark' ou 'light'"},
            )
        updates["tema"] = req.tema

    if req.nova_senha is not None:
        if not req.senha_atual:
            raise HTTPException(
                status_code=400,
                detail={"code": Codes.BAD_REQUEST, "message": "Senha atual é obrigatória para alterar a senha"},
            )
        full = user_repository.find_full(user["id"])
        if not full or not verify_password(req.senha_atual, full["senha_hash"]):
            raise HTTPException(
                status_code=400,
                detail={"code": Codes.BAD_REQUEST, "message": "Senha atual incorreta"},
            )
        if len(req.nova_senha) < 8:
            raise HTTPException(
                status_code=400,
                detail={"code": Codes.BAD_REQUEST, "message": "Nova senha deve ter pelo menos 8 caracteres"},
            )
        updates["senha_hash"] = hash_password(req.nova_senha)

    if updates:
        user_repository.update(user["id"], updates)

    return success(Codes.SUCCESS_DEFAULT, message="Perfil atualizado com sucesso")


@router.post("/profile/photo")
async def upload_photo(user=Depends(get_current_user), foto: UploadFile = File(...)):
    allowed_types = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
    if foto.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail={"code": Codes.BAD_REQUEST, "message": "Tipo de arquivo não suportado. Use PNG, JPEG ou WebP"},
        )

    content = await foto.read()
    if len(content) > _MAX_PHOTO_BYTES:
        raise HTTPException(
            status_code=400,
            detail={"code": Codes.BAD_REQUEST, "message": "Foto deve ter no máximo 5MB"},
        )

    os.makedirs(_AVATAR_DIR, exist_ok=True)
    ext = os.path.splitext(foto.filename or "foto.png")[1].lower()
    if ext not in {".png", ".jpg", ".jpeg", ".webp"}:
        ext = ".png"
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(_AVATAR_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(content)

    foto_url = f"/generated/avatars/{filename}"
    user_repository.update(user["id"], {"foto_url": foto_url})

    return success(Codes.SUCCESS_DEFAULT, foto_url=foto_url, message="Foto atualizada com sucesso")

"""Profile management routes."""

import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from alici_api.dependencies import get_current_user
from alici_api.repositories.user_repository import UserRepository
from alici_api.responses import Codes, success
from auth import hash_password, verify_password
from database import contar_mensagens_hoje
from logger import get_logger

router = APIRouter(prefix="/profile", tags=["profile"])
logger_profile = get_logger("route_profile")
user_repo = UserRepository()

ALLOWED_AVATAR_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif"}
MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2 MB
# bcrypt truncates input at 72 bytes — enforce this limit explicitly
MAX_PASSWORD_BYTES = 72


class ProfileUpdateRequest(BaseModel):
    nome: str | None = None
    tema: str | None = None


class PasswordChangeRequest(BaseModel):
    senha_atual: str
    nova_senha: str


@router.get("")
def get_profile(user=Depends(get_current_user)):
    mensagens_hoje = contar_mensagens_hoje(user["id"])
    plano = (user.get("plano") or "free").lower()
    limites = {"free": 20, "pro": 300, "ultra": 2000, "enterprise": None}
    limite = limites.get(plano, 20)
    return success(
        Codes.PROFILE_GET_OK,
        profile={
            "id": user["id"],
            "nome": user["nome"],
            "email": user["email"],
            "plano": plano,
            "tema": user.get("tema") or "dark",
            "foto_url": user.get("foto_url"),
            "mensagens_hoje": mensagens_hoje,
            "limite_diario": limite,
        },
    )


@router.put("")
def update_profile(req: ProfileUpdateRequest, user=Depends(get_current_user)):
    updates = {}
    if req.nome is not None:
        nome = req.nome.strip()
        if len(nome) < 2:
            raise HTTPException(
                status_code=400,
                detail={"code": Codes.BAD_REQUEST, "message": "Nome deve ter ao menos 2 caracteres"},
            )
        updates["nome"] = nome
    if req.tema is not None:
        if req.tema not in {"dark", "light"}:
            raise HTTPException(
                status_code=400,
                detail={"code": Codes.BAD_REQUEST, "message": "Tema inválido (dark ou light)"},
            )
        updates["tema"] = req.tema
    if updates:
        user_repo.update(user["id"], **updates)
    return success(Codes.PROFILE_UPDATE_OK, message="Perfil atualizado")


@router.put("/password")
def change_password(req: PasswordChangeRequest, user=Depends(get_current_user)):
    full_user = user_repo.find_by_id(user["id"])
    if not full_user or not verify_password(req.senha_atual, full_user["senha_hash"]):
        raise HTTPException(
            status_code=400,
            detail={"code": Codes.BAD_REQUEST, "message": "Senha atual incorreta"},
        )
    if len(req.nova_senha) < 8:
        raise HTTPException(
            status_code=400,
            detail={"code": Codes.BAD_REQUEST, "message": "Nova senha deve ter ao menos 8 caracteres"},
        )
    if len(req.nova_senha.encode("utf-8")) > MAX_PASSWORD_BYTES:
        raise HTTPException(
            status_code=400,
            detail={"code": Codes.BAD_REQUEST, "message": f"Senha muito longa (máx {MAX_PASSWORD_BYTES} bytes)"},
        )
    new_hash = hash_password(req.nova_senha)
    user_repo.update(user["id"], senha_hash=new_hash)
    return success(Codes.PROFILE_UPDATE_OK, message="Senha alterada com sucesso")


@router.post("/avatar")
def upload_avatar(user=Depends(get_current_user), imagem: UploadFile = File(...)):
    if imagem.content_type not in ALLOWED_AVATAR_TYPES:
        raise HTTPException(
            status_code=400,
            detail={"code": Codes.BAD_REQUEST, "message": "Tipo de arquivo não suportado"},
        )

    data = imagem.file.read(MAX_AVATAR_SIZE + 1)
    if len(data) > MAX_AVATAR_SIZE:
        raise HTTPException(
            status_code=400,
            detail={"code": Codes.BAD_REQUEST, "message": "Imagem muito grande (máx 2 MB)"},
        )

    ext_map = {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }
    ext = ext_map.get(imagem.content_type or "", ".png")
    generated_dir = "generated/avatars"
    os.makedirs(generated_dir, exist_ok=True)
    filename = f"avatar_{user['id']}{ext}"
    filepath = os.path.join(generated_dir, filename)

    with open(filepath, "wb") as f:
        f.write(data)

    foto_url = f"/generated/avatars/{filename}"
    user_repo.update(user["id"], foto_url=foto_url)
    return success(Codes.PROFILE_UPDATE_OK, message="Avatar atualizado", foto_url=foto_url)

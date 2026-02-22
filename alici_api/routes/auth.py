"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException

from alici_api.dependencies import get_current_user
from alici_api.schemas import LoginRequest, RegisterRequest
from auth import create_access_token, hash_password, verify_password
from database import buscar_usuario_por_email, criar_usuario

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(req: RegisterRequest):
    if len(req.senha) < 8:
        raise HTTPException(status_code=400, detail="Senha deve ter pelo menos 8 caracteres")

    if len(req.senha.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Senha muito longa (max 72 bytes)")

    if len(req.nome) < 2:
        raise HTTPException(status_code=400, detail="Nome deve ter pelo menos 2 caracteres")

    if buscar_usuario_por_email(req.email):
        raise HTTPException(status_code=400, detail="Email já está registrado")

    try:
        senha_hash = hash_password(req.senha)
        usuario = criar_usuario(req.nome, req.email, senha_hash)

        if not usuario:
            raise HTTPException(status_code=500, detail="Não foi possível criar usuário")

        return {
            "status": "sucesso",
            "mensagem": "Usuário criado com sucesso",
            "usuario": {
                "id": usuario["id"],
                "nome": usuario["nome"],
                "email": usuario["email"],
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/login")
def login(req: LoginRequest):
    usuario = buscar_usuario_por_email(req.email)

    if not usuario:
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")

    if not verify_password(req.senha, usuario["senha_hash"]):
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")

    token = create_access_token(usuario["id"], usuario["email"])

    return {
        "status": "sucesso",
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "email": usuario["email"],
            "plano": usuario["plano"],
        },
    }


@router.post("/logout")
def logout(user=Depends(get_current_user)):
    return {"status": "sucesso", "mensagem": "Logout realizado"}

"""
ALICI™ API - FastAPI Application
Entrypoint principal da aplicação web
"""

import os
import sys
from typing import Optional

# ==================================================
# BASE DIR (FUNCIONA LOCAL E RENDER)
# ==================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ==================================================

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status, Header
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

# ================================
# IMPORTS INTERNOS
# ================================

from engine import gerar_resposta, gerar_resposta_com_emocao
from auth import (
    create_access_token,
    verify_password,
    hash_password,
    verify_token
)
from database import (
    buscar_usuario_por_email,
    criar_usuario,
    buscar_usuario_por_id,
    salvar_historico,
    buscar_historico,
    criar_tabelas
)
from logger import get_logger

# ================================
# CONFIGURAÇÃO INICIAL
# ================================

load_dotenv()
logger_app = get_logger("api")

app = FastAPI(
    title="ALICI™ API",
    description="Inteligência Artificial com Memória Persistente",
    version="1.0.0"
)

# ================================
# CORS
# ================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================
# STATIC FILES
# ================================

STATIC_DIR = os.path.join(BASE_DIR, "static")

if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ================================
# MODELS
# ================================

class LoginRequest(BaseModel):
    email: str
    senha: str


class RegisterRequest(BaseModel):
    nome: str
    email: str
    senha: str

    @field_validator("senha")
    @classmethod
    def validate_password_length(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Senha muito longa (max 72 bytes)")
        return value


class ChatRequest(BaseModel):
    pergunta: str = Field(..., min_length=1, max_length=1000)
    incluir_emocao: bool = False


class ChatResponse(BaseModel):
    resposta: str
    emocao: Optional[str] = None
    intensidade: Optional[float] = None


# ================================
# FUNÇÕES AUXILIARES
# ================================

def get_current_user(authorization: Optional[str]):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não fornecido"
        )

    try:
        scheme, token = authorization.split()

        if scheme.lower() != "bearer":
            raise ValueError("Schema inválido")

        payload = verify_token(token)
        user_id = int(payload.get("sub"))

        user = buscar_usuario_por_id(user_id)

        if not user:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")

        return user

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )


# ================================
# ROTAS - AUTENTICAÇÃO
# ================================

@app.post("/auth/login")
async def login(request: LoginRequest):
    user = buscar_usuario_por_email(request.email)

    if not user or not verify_password(request.senha, user.get("senha_hash")):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")

    access_token = create_access_token(user["id"], user["email"])

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": {
            "id": user["id"],
            "nome": user["nome"],
            "email": user["email"],
            "plano": user.get("plano", "free")
        }
    }


@app.post("/auth/register")
async def register(request: RegisterRequest):
    if buscar_usuario_por_email(request.email):
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    senha_hash = hash_password(request.senha)
    user = criar_usuario(request.nome, request.email, senha_hash)

    access_token = create_access_token(user["id"], user["email"])

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": user
    }


# ================================
# CHAT (CORRIGIDO)
# ================================

@app.get("/chat", include_in_schema=False)
async def chat_html():
    return serve_html("chat.html")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, authorization: Optional[str] = Header(None)):

    user = None

    if authorization:
        try:
            user = get_current_user(authorization)
        except:
            pass

    if request.incluir_emocao:
        resultado = gerar_resposta_com_emocao(request.pergunta)
        resposta = resultado.get("resposta")
        emocao = resultado.get("emocao")
        intensidade = resultado.get("intensidade")
    else:
        resposta = gerar_resposta(request.pergunta)
        emocao = None
        intensidade = None

    if user:
        salvar_historico(user["id"], request.pergunta, resposta)

    return {
        "resposta": resposta,
        "emocao": emocao,
        "intensidade": intensidade
    }


# ================================
# STATUS
# ================================

@app.get("/api/status")
async def api_status():
    return {
        "status": "operacional",
        "version": "1.0.0"
    }


# ================================
# HTML
# ================================

TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

def serve_html(file_name: str):
    file_path = os.path.join(TEMPLATES_DIR, file_name)

    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"{file_name} não encontrado no servidor"
        )

    return FileResponse(file_path)


@app.get("/", include_in_schema=False)
@app.get("/login", include_in_schema=False)
async def login_page():
    return serve_html("login.html")


@app.get("/chat-page", include_in_schema=False)
async def chat_page():
    return serve_html("chat.html")


# ================================
# STARTUP
# ================================

@app.on_event("startup")
async def startup_event():
    logger_app.info("🚀 Inicializando ALICI API...")
    try:
        criar_tabelas()
        logger_app.info("✓ Banco verificado")
    except Exception as e:
        logger_app.warning(f"⚠ Aviso BD: {e}")
    logger_app.info("✓ ALICI pronta!")


@app.on_event("shutdown")
async def shutdown_event():
    logger_app.info("🛑 ALICI desligando...")


# ================================
# EXECUÇÃO LOCAL
# ================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "alici_api.app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENV", "development") == "development"
    )

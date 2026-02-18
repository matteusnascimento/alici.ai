"""
ALICI™ API - FastAPI Application
Entrypoint principal da aplicação web
"""

import os
import sys
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

# Adicionar diretório pai para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar módulos ALICI
from engine import gerar_resposta, gerar_resposta_com_emocao
from auth import create_access_token, verify_password, hash_password
from database import (
    buscar_usuario_por_email, criar_usuario, buscar_usuario_por_id,
    salvar_historico, buscar_historico, criar_tabelas
)
from logger import get_logger

# Carregar variáveis de ambiente
load_dotenv()

# Logger
logger_app = get_logger("api")

# ================================
# APP & CORS
# ================================
app = FastAPI(
    title="ALICI™ API",
    description="Inteligência Artificial com Memória Persistente",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos
STATIC_DIR = "static"
if os.path.exists(STATIC_DIR):
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

def get_current_user(authorization: Optional[str] = None):
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token não fornecido")
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Schema inválido")
        from auth import verify_token
        payload = verify_token(token)
        user_id = int(payload.get("sub"))
        user = buscar_usuario_por_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")
        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token inválido: {str(e)}")

# ================================
# ROTAS - AUTENTICAÇÃO
# ================================

@app.post("/auth/login")
async def login(request: LoginRequest):
    try:
        logger_app.info(f"Login attempt: {request.email}")
        user = buscar_usuario_por_email(request.email)
        if not user or not verify_password(request.senha, user.get("senha_hash")):
            logger_app.warning(f"Login failed for {request.email}")
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
    except HTTPException:
        raise
    except Exception as e:
        logger_app.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.post("/auth/register")
async def register(request: RegisterRequest):
    try:
        logger_app.info(f"Register attempt: {request.email}")
        if buscar_usuario_por_email(request.email):
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        senha_hash = hash_password(request.senha)
        user = criar_usuario(request.nome, request.email, senha_hash)
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
    except HTTPException:
        raise
    except Exception as e:
        logger_app.error(f"Register error: {e}")
        raise HTTPException(status_code=500, detail="Erro ao registrar usuário")

# ================================
# ROTAS - CHAT
# ================================

@app.post("/chat")
async def chat(request: ChatRequest, authorization: Optional[str] = None):
    try:
        user = None
        if authorization:
            try:
                user = get_current_user(authorization)
            except:
                pass
        if request.incluir_emocao:
            resultado = gerar_resposta_com_emocao(request.pergunta)
            resposta, emocao, intensidade = resultado.values()
        else:
            resposta = gerar_resposta(request.pergunta)
            emocao = None
            intensidade = None
        if user:
            salvar_historico(user["id"], request.pergunta, resposta)
        return {"resposta": resposta, "emocao": emocao, "intensidade": intensidade}
    except Exception as e:
        logger_app.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar pergunta")

@app.get("/history")
async def get_history(authorization: Optional[str] = None):
    user = get_current_user(authorization)
    historico = buscar_historico(user["id"], limite=50)
    return {"usuario": user, "historico": historico}

@app.post("/chat/image")
async def chat_with_image(authorization: Optional[str] = None):
    get_current_user(authorization)
    return {"resposta": "Análise de imagem será disponível em breve"}

# ================================
# ROTAS - STATUS
# ================================

@app.get("/api/status")
async def status(authorization: Optional[str] = None):
    user = None
    if authorization:
        try:
            user = get_current_user(authorization)
        except:
            pass
    return {"status": "operacional", "version": "1.0.0", "usuario": user}

# ================================
# ROTAS DE PÁGINAS
# ================================

def serve_html(file_name: str, fallback_msg: str):
    path = os.path.join("templates", file_name)
    if os.path.exists(path):
        return FileResponse(path)
    return {"message": fallback_msg}

@app.get("/")
@app.get("/login")
def login_page():
    return serve_html("login.html", "Login")

@app.get("/chat")
def chat_page():
    return serve_html("chat.html", "Chat")

# ================================
# STARTUP & SHUTDOWN
# ================================

@app.on_event("startup")
async def startup_event():
    logger_app.info("="*60)
    logger_app.info("🚀 Inicializando ALICI API...")
    try:
        criar_tabelas()
        logger_app.info("✓ Banco de dados verificado")
    except Exception as e:
        logger_app.warning(f"⚠ Aviso ao verificar BD: {e}")
    logger_app.info("✓ ALICI pronta para conversar!")
    logger_app.info("="*60)

@app.on_event("shutdown")
async def shutdown_event():
    logger_app.info("🛑 ALICI desligando...")

# ================================
# HANDLER DE ERROS
# ================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

# ================================
# MAIN
# ================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENV", "development") == "development"
    )

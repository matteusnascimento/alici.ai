"""
ALICI™ API - FastAPI Application
Entrypoint principal da aplicação web
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
import sys

# Adicionar diretório pai ao path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar módulos ALICI
from engine import gerar_resposta, gerar_resposta_com_emocao
from auth import create_access_token, verify_password, hash_password
from database import (
    buscar_usuario_por_email, criar_usuario, buscar_usuario_por_id,
    salvar_historico, buscar_historico, criar_tabelas
)
from logger import get_logger

# Configurar logger
logger_app = get_logger("api")

load_dotenv()

# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

app = FastAPI(
    title="ALICI™ API",
    description="Inteligência Artificial com Memória Persistente",
    version="1.0.0"
)

# CORS - Permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos
if os.path.exists("Static"):
    app.mount("/static", StaticFiles(directory="Static"), name="static")

# ============================================================================
# MODELOS
# ============================================================================

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

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
        # bcrypt suporta no maximo 72 bytes
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

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def get_current_user(authorization: Optional[str] = None):
    """
    Extrai e valida o token JWT do header Authorization
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não fornecido"
        )
    
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}"
        )

# ============================================================================
# ROTAS - AUTENTICAÇÃO
# ============================================================================

@app.post("/auth/login")
async def login(request: LoginRequest):
    """
    Login de usuário existente
    Retorna access_token JWT
    """
    try:
        logger_app.info(f"Login attempt: {request.email}")
        user = buscar_usuario_por_email(request.email)
        
        if not user:
            logger_app.warning(f"Login failed: user not found {request.email}")
            raise HTTPException(
                status_code=401,
                detail="Email ou senha incorretos"
            )
        
        if not verify_password(request.senha, user.get("senha_hash")):
            logger_app.warning(f"Login failed: incorrect password {request.email}")
            raise HTTPException(
                status_code=401,
                detail="Email ou senha incorretos"
            )
        
        logger_app.info(f"Login successful: {request.email}")
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
        logger_app.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.post("/auth/register")
async def register(request: RegisterRequest):
    """
    Registrar novo usuário
    """
    try:
        logger_app.info(f"Register attempt: {request.email}")
        # Verificar se email já existe
        existing = buscar_usuario_por_email(request.email)
        if existing:
            logger_app.warning(f"Register failed: email already exists {request.email}")
            raise HTTPException(
                status_code=400,
                detail="Email já cadastrado"
            )
        
        # Criar novo usuário
        logger_app.info(f"Creating new user: {request.email}")
        senha_hash = hash_password(request.senha)
        user = criar_usuario(request.nome, request.email, senha_hash)
        
        logger_app.info(f"User registered: {request.email}")
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
        logger_app.error(f"Register error: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao registrar usuário")

# ============================================================================
# ROTAS - CHAT
# ============================================================================

@app.post("/chat")
async def chat(request: ChatRequest, authorization: Optional[str] = None):
    """
    Endpoint principal de chat
    Processa pergunta e retorna resposta
    """
    try:
        logger_app.debug(f"Chat request: {request.pergunta[:50]}...")
        # Validar autenticação (opcional por hora)
        user = None
        if authorization:
            try:
                user = get_current_user(authorization)
            except:
                pass
        
        # Gerar resposta
        if request.incluir_emocao:
            resultado = gerar_resposta_com_emocao(request.pergunta)
            resposta = resultado.get("resposta")
            emocao = resultado.get("emocao")
            intensidade = resultado.get("intensidade")
        else:
            resposta = gerar_resposta(request.pergunta)
            emocao = None
            intensidade = None
        
        # Salvar no histórico se autenticado
        if user:
            salvar_historico(user["id"], request.pergunta, resposta)
            logger_app.info(f"Chat saved for user: {user['email']}")
        
        logger_app.debug(f"Chat response generated: {resposta[:50]}...")
        return {
            "resposta": resposta,
            "emocao": emocao,
            "intensidade": intensidade
        }
    except Exception as e:
        logger_app.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao processar pergunta")

@app.get("/history")
async def get_history(authorization: Optional[str] = None):
    """
    Obter histórico de conversas do usuário
    """
    try:
        user = get_current_user(authorization)
        historico = buscar_historico(user["id"], limite=50)
        
        return {
            "usuario": user,
            "historico": historico
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/image")
async def chat_with_image(authorization: Optional[str] = None):
    """
    Analisar imagem e gerar resposta
    (Stub para integração futura com modelo de visão)
    """
    try:
        user = get_current_user(authorization)
        
        return {
            "resposta": "Análise de imagem será disponível em breve"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ROTAS - STATUS
# ============================================================================

@app.get("/api/status")
async def status(authorization: Optional[str] = None):
    """
    Verificar status da aplicação e usuário
    """
    try:
        user = None
        if authorization:
            try:
                user = get_current_user(authorization)
            except:
                pass
        
        return {
            "status": "operacional",
            "version": "1.0.0",
            "usuario": user
        }
    except Exception as e:
        logger_app.error(f"Status error: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno")

@app.get("/")
async def root():
    """
    Página inicial - Login
    """
    if os.path.exists("templates/login.html"):
        return FileResponse("templates/login.html")
    return {"message": "Login"}

@app.get("/login")
async def login_page():
    """
    Página de login
    """
    if os.path.exists("templates/login.html"):
        return FileResponse("templates/login.html")
    return {"message": "Login"}

@app.get("/chat")
async def chat_page():
    """
    Página de chat - requer autenticação
    """
    if os.path.exists("templates/chat.html"):
        return FileResponse("templates/chat.html")
    return {"message": "Chat"}

# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Executar ao iniciar a aplicação
    """
    logger_app.info("="*60)
    logger_app.info("🚀 Inicializando ALICI API...")
    logger_app.info("="*60)
    
    # Criar tabelas se não existirem
    try:
        criar_tabelas()
        logger_app.info("✓ Banco de dados verificado")
    except Exception as e:
        logger_app.warning(f"⚠ Aviso ao verificar BD: {e}")
    
    logger_app.info("✓ ALICI pronta para conversar!")
    logger_app.info("="*60)

@app.on_event("shutdown")
async def shutdown_event():
    """
    Executar ao desligar a aplicação
    """
    logger_app.info("🛑 ALICI desligando...")

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENV", "development") == "development"
    )

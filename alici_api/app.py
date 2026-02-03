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

from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    email: str
    senha: str

class RegisterRequest(BaseModel):
    nome: str
    email: str
    senha: str

class ChatRequest(BaseModel):
    pergunta: str
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
        user = buscar_usuario_por_email(request.email)
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Email ou senha incorretos"
            )
        
        if not verify_password(request.senha, user.get("senha_hash")):
            raise HTTPException(
                status_code=401,
                detail="Email ou senha incorretos"
            )
        
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
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/register")
async def register(request: RegisterRequest):
    """
    Registrar novo usuário
    """
    try:
        # Verificar se email já existe
        existing = buscar_usuario_por_email(request.email)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Email já cadastrado"
            )
        
        # Criar novo usuário
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
        raise HTTPException(status_code=500, detail=str(e))

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
        
        return {
            "resposta": resposta,
            "emocao": emocao,
            "intensidade": intensidade
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        raise HTTPException(status_code=500, detail=str(e))

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
    print("\n" + "="*60)
    print("🚀 Inicializando ALICI API...")
    print("="*60)
    
    # Criar tabelas se não existirem
    try:
        criar_tabelas()
        print("✓ Banco de dados verificado")
    except Exception as e:
        print(f"⚠ Aviso ao verificar BD: {e}")
    
    print("✓ ALICI pronta para conversar!")
    print("="*60 + "\n")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Executar ao desligar a aplicação
    """
    print("\n🛑 ALICI desligando...\n")

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

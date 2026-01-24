"""
main_auth.py
Servidor FastAPI com autenticação JWT, login, registro e integração com ALICI
"""

import os
from fastapi import FastAPI, HTTPException, Depends, Request, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from datetime import datetime
from dotenv import load_dotenv

# Importar módulos da ALICI
from auth import hash_password, verify_password, create_access_token, verify_token
from database_auth import (
    criar_usuario, 
    buscar_usuario_por_email, 
    buscar_usuario_por_id,
    salvar_historico,
    buscar_historico,
    limpar_historico,
    criar_tabelas
)

# Tentar importar módulos de IA (opcionais)
try:
    from engine import gerar_resposta
    from model_inference import fazer_predicao, gerar_resposta_predicao
    IA_DISPONIVEL = True
except ImportError:
    IA_DISPONIVEL = False
    print("[WARNING] Módulos de IA não disponíveis (engine.py, model_inference.py)")

load_dotenv()

# ============================================================================
# INICIALIZAÇÃO DO APP
# ============================================================================

app = FastAPI(
    title="ALICI™ API",
    description="Inteligência Artificial Avançada com Autenticação JWT",
    version="2.0"
)

# CORS - permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# ============================================================================
# MODELOS PYDANTIC
# ============================================================================

class RegisterRequest(BaseModel):
    nome: str
    email: EmailStr
    senha: str


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class ChatRequest(BaseModel):
    pergunta: str
    incluir_emocao: bool = False


class PredictRequest(BaseModel):
    imagem_base64: str


# ============================================================================
# DEPENDÊNCIAS
# ============================================================================

def get_current_user(request: Request):
    """
    Extrai o usuário atual do token JWT
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(status_code=401, detail="Token não fornecido")
    
    try:
        token = auth_header.replace("Bearer ", "")
        payload = verify_token(token)
        user_id = int(payload.get("sub"))
        
        # Verificar se usuário existe
        user = buscar_usuario_por_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")
        
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token inválido")


# ============================================================================
# ROTAS DE AUTENTICAÇÃO
# ============================================================================

@app.post("/auth/register")
def register(req: RegisterRequest):
    """
    Registra novo usuário
    
    - nome: Nome completo
    - email: Email único
    - senha: Mínimo 8 caracteres
    """
    # Validação
    if len(req.senha) < 8:
        raise HTTPException(status_code=400, detail="Senha deve ter pelo menos 8 caracteres")
    
    if len(req.nome) < 2:
        raise HTTPException(status_code=400, detail="Nome deve ter pelo menos 2 caracteres")
    
    # Verificar se email já existe
    if buscar_usuario_por_email(req.email):
        raise HTTPException(status_code=400, detail="Email já está registrado")
    
    try:
        # Criptografar senha
        senha_hash = hash_password(req.senha)
        
        # Criar usuário
        usuario = criar_usuario(req.nome, req.email, senha_hash)
        
        return {
            "status": "sucesso",
            "mensagem": "Usuário criado com sucesso",
            "usuario": {
                "id": usuario["id"],
                "nome": usuario["nome"],
                "email": usuario["email"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/auth/login")
def login(req: LoginRequest):
    """
    Faz login e retorna JWT token
    
    - email: Email registrado
    - senha: Senha
    
    Response: access_token (JWT)
    """
    # Buscar usuário
    usuario = buscar_usuario_por_email(req.email)
    
    if not usuario:
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")
    
    # Verificar senha
    if not verify_password(req.senha, usuario["senha_hash"]):
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")
    
    # Gerar token JWT
    token = create_access_token(usuario["id"], usuario["email"])
    
    return {
        "status": "sucesso",
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "email": usuario["email"],
            "plano": usuario["plano"]
        }
    }


@app.post("/auth/logout")
def logout(user=Depends(get_current_user)):
    """
    Logout do usuário (implementação no frontend)
    """
    return {"status": "sucesso", "mensagem": "Logout realizado"}


# ============================================================================
# ROTAS DE CHAT (COM AUTENTICAÇÃO)
# ============================================================================

@app.post("/chat")
def chat(req: ChatRequest, user=Depends(get_current_user)):
    """
    Endpoint de chat com IA
    
    - pergunta: Pergunta para a ALICI
    - incluir_emocao: Se deve incluir metadata emocional
    
    Requer autenticação via JWT
    """
    if not IA_DISPONIVEL:
        raise HTTPException(status_code=503, detail="Serviço de IA não disponível")
    
    if not req.pergunta or not req.pergunta.strip():
        raise HTTPException(status_code=400, detail="Pergunta vazia")
    
    try:
        # Gerar resposta com IA
        resposta = gerar_resposta(req.pergunta)
        
        # Salvar no histórico
        salvar_historico(user["id"], req.pergunta, resposta)
        
        # Adicionar metadata emocional (opcional)
        resultado = {
            "status": "sucesso",
            "resposta": resposta,
            "usuario": user["nome"]
        }
        
        if req.incluir_emocao:
            # Aqui pode adicionar detecção de emoção
            resultado["emocao"] = "neutra"
        
        return resultado
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/image")
def chat_image(
    user=Depends(get_current_user),
    imagem: UploadFile = File(...)
):
    """
    Análise de imagem com modelo CIFAR-100
    
    Requer: arquivo de imagem (multipart upload)
    Requer autenticação via JWT
    """
    if not IA_DISPONIVEL:
        raise HTTPException(status_code=503, detail="Modelo não disponível")
    
    # Verificar tipo de arquivo
    if imagem.content_type not in ["image/png", "image/jpeg", "image/gif", "image/bmp"]:
        raise HTTPException(status_code=400, detail="Tipo de arquivo não suportado")
    
    try:
        import tempfile
        
        # Salvar temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            conteudo = imagem.file.read()
            tmp.write(conteudo)
            tmp_path = tmp.name
        
        # Fazer predição
        resultado = fazer_predicao(tmp_path, top_k=3)
        
        # Limpar arquivo
        os.remove(tmp_path)
        
        if resultado.get("status") == "erro":
            raise HTTPException(status_code=400, detail=resultado.get("erro"))
        
        # Gerar resposta
        resposta = gerar_resposta_predicao(resultado)
        
        # Salvar no histórico
        pergunta = f"[Análise de imagem] {resultado.get('classe')}"
        salvar_historico(user["id"], pergunta, resposta)
        
        return {
            "status": "sucesso",
            "classe": resultado["classe"],
            "confianca": resultado["confianca"],
            "resposta": resposta,
            "alternativas": resultado.get("top_k", [])[1:]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ROTAS DE HISTÓRICO
# ============================================================================

@app.get("/history")
def get_history(limit: int = 50, user=Depends(get_current_user)):
    """
    Retorna histórico de chat do usuário
    
    Query params:
    - limit: Número máximo de registros (default: 50)
    """
    historico = buscar_historico(user["id"], limit)
    
    return {
        "status": "sucesso",
        "total": len(historico),
        "historico": historico
    }


@app.delete("/history")
def delete_history(user=Depends(get_current_user)):
    """
    Limpa o histórico do usuário
    """
    try:
        limpar_historico(user["id"])
        return {"status": "sucesso", "mensagem": "Histórico limpo"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ROTAS DE PÁGINAS HTML
# ============================================================================

@app.get("/", response_class=HTMLResponse)
def home():
    """
    Página de login
    """
    with open("templates/login.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/chat", response_class=HTMLResponse)
def chat_page(user=Depends(get_current_user)):
    """
    Página de chat (protegida por autenticação)
    """
    with open("templates/chat.html", "r", encoding="utf-8") as f:
        return f.read()


# ============================================================================
# ROTAS DE HEALTH CHECK
# ============================================================================

@app.get("/health")
def health():
    """
    Verificar saúde do serviço
    """
    return {
        "status": "ok",
        "ia_disponivel": IA_DISPONIVEL,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/status")
def api_status(user=Depends(get_current_user)):
    """
    Status da API (requer autenticação)
    """
    return {
        "usuario": user["nome"],
        "plano": user["plano"],
        "ia_disponivel": IA_DISPONIVEL,
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return {
        "status": "erro",
        "status_code": exc.status_code,
        "detail": exc.detail
    }


# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Executado ao iniciar o servidor
    """
    print("🚀 Inicializando ALICI™ API...")
    
    try:
        # Criar tabelas no banco de dados
        criar_tabelas()
        print("✅ Banco de dados pronto")
    except Exception as e:
        print(f"⚠️  Erro ao conectar BD: {e}")
    
    if IA_DISPONIVEL:
        print("✅ Módulos de IA carregados")
    else:
        print("⚠️  Módulos de IA não disponíveis")
    
    print("🤖 ALICI™ pronta para receber requisições!")


# ============================================================================
# PONTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main_auth:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )

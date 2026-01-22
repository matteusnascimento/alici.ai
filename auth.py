"""
auth.py - Sistema de autenticação e gerenciamento de sessões
"""
from fastapi import APIRouter, HTTPException, Depends, Header, status
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
import uuid
from config import get_settings
from database_models import get_db

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()

# Configuração de hash de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==================== MODELOS ====================

class UserRegister(BaseModel):
    nome: str
    email: EmailStr
    senha: str

class UserLogin(BaseModel):
    email: EmailStr
    senha: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    id: str
    nome: str
    email: str
    plano: str
    criado_em: str

# ==================== UTILITÁRIOS ====================

def hash_password(password: str) -> str:
    """Hash de senha com bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha corresponde ao hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: str, expires_in_hours: int = None) -> tuple[str, datetime]:
    """Cria JWT access token"""
    if expires_in_hours is None:
        expires_in_hours = settings.ACCESS_TOKEN_EXPIRE_HOURS
    
    expire = datetime.utcnow() + timedelta(hours=expires_in_hours)
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, expire

def create_refresh_token(user_id: str) -> tuple[str, datetime]:
    """Cria JWT refresh token (válido por mais tempo)"""
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, expire

def verify_token(token: str) -> Optional[str]:
    """Verifica e decodifica o token JWT, retorna user_id"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None

async def get_current_user(authorization: str = Header(None)) -> str:
    """Dependency para pegar o user_id do token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Token não fornecido")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Esquema de autenticação inválido")
    except ValueError:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Token expirado ou inválido")
    
    return user_id

# ==================== ROTAS ====================

@router.post("/register", response_model=UserResponse)
async def register(user: UserRegister):
    """Cria uma nova conta"""
    db = get_db()
    
    # Validações
    if len(user.senha) < 8:
        raise HTTPException(400, "Senha deve ter no mínimo 8 caracteres")
    
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            # Verifica se email já existe
            cur.execute("SELECT id FROM users WHERE email = %s", (user.email,))
            if cur.fetchone():
                raise HTTPException(400, "Email já cadastrado")
            
            # Cria usuário
            user_id = str(uuid.uuid4())
            senha_hash = hash_password(user.senha)
            
            cur.execute(
                """
                INSERT INTO users (id, nome, email, senha_hash, plano)
                VALUES (%s, %s, %s, %s, 'free')
                """,
                (user_id, user.nome, user.email, senha_hash)
            )
            conn.commit()
    
    return UserResponse(
        id=user_id,
        nome=user.nome,
        email=user.email,
        plano="free",
        criado_em=datetime.utcnow().isoformat()
    )

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, user_agent: str = Header(None)):
    """Autentica usuário e retorna tokens"""
    db = get_db()
    
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            # Busca usuário
            cur.execute(
                "SELECT id, senha_hash FROM users WHERE email = %s AND ativo = TRUE",
                (credentials.email,)
            )
            user = cur.fetchone()
            
            if not user or not verify_password(credentials.senha, user[1]):
                raise HTTPException(401, "Credenciais inválidas")
            
            user_id = user[0]
            
            # Cria tokens
            access_token, access_expire = create_access_token(user_id)
            refresh_token, refresh_expire = create_refresh_token(user_id)
            
            # Salva sessão
            session_id = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO sessions 
                (id, user_id, token, token_refresh, expira_em, expira_refresh_em, dispositivo, ativo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
                """,
                (
                    session_id,
                    user_id,
                    access_token,
                    refresh_token,
                    access_expire,
                    refresh_expire,
                    user_agent or "unknown"
                )
            )
            conn.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_HOURS * 3600
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh(refresh_token: str):
    """Renova o access token usando refresh token"""
    db = get_db()
    
    # Valida refresh token
    user_id = verify_token(refresh_token)
    if not user_id:
        raise HTTPException(401, "Refresh token inválido")
    
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            # Verifica se refresh token existe na BD
            cur.execute(
                "SELECT id FROM sessions WHERE user_id = %s AND token_refresh = %s AND ativo = TRUE",
                (user_id, refresh_token)
            )
            if not cur.fetchone():
                raise HTTPException(401, "Refresh token não encontrado ou expirado")
            
            # Cria novo access token
            new_access_token, access_expire = create_access_token(user_id)
            new_refresh_token, refresh_expire = create_refresh_token(user_id)
            
            # Atualiza sessão
            cur.execute(
                """
                UPDATE sessions 
                SET token = %s, token_refresh = %s, expira_em = %s, expira_refresh_em = %s
                WHERE user_id = %s
                """,
                (new_access_token, new_refresh_token, access_expire, refresh_expire, user_id)
            )
            conn.commit()
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_HOURS * 3600
    )

@router.post("/logout")
async def logout(current_user: str = Depends(get_current_user), authorization: str = Header(None)):
    """Faz logout invalidando o token"""
    db = get_db()
    
    try:
        token = authorization.split()[1]
    except:
        raise HTTPException(401, "Token inválido")
    
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE sessions SET ativo = FALSE WHERE user_id = %s AND token = %s",
                (current_user, token)
            )
            conn.commit()
    
    return {"status": "logout realizado com sucesso"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: str = Depends(get_current_user)):
    """Retorna informações do usuário atual"""
    db = get_db()
    
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, nome, email, plano, criado_em 
                FROM users WHERE id = %s
                """,
                (current_user,)
            )
            user = cur.fetchone()
            
            if not user:
                raise HTTPException(404, "Usuário não encontrado")
    
    return UserResponse(
        id=user[0],
        nome=user[1],
        email=user[2],
        plano=user[3],
        criado_em=user[4].isoformat()
    )

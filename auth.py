"""
auth.py
Módulo de autenticação: criptografia de senha, geração de JWT
"""

from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

SECRET_KEY = os.getenv("SECRET_KEY")

# Em produção, SECRET_KEY é obrigatória
if not SECRET_KEY:
    env = os.getenv("ENV", "development")
    if env == "production":
        raise ValueError(
            "⚠️ ERRO CRÍTICO: SECRET_KEY não configurada em produção!\n"
            "Configure a variável de ambiente SECRET_KEY com um valor seguro."
        )
    # Em desenvolvimento, usar um valor padrão (com aviso)
    SECRET_KEY = "ALICI_DEVELOPMENT_KEY_CHANGE_IN_PRODUCTION"
    print("⚠️ AVISO: Usando SECRET_KEY padrão (apenas para desenvolvimento)")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

# Contexto de criptografia bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# ============================================================================
# FUNÇÕES DE SENHA
# ============================================================================

def hash_password(password: str) -> str:
    """
    Criptografa a senha usando bcrypt
    
    Args:
        password: Senha em texto plano
    
    Returns:
        Hash bcrypt seguro
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto plano corresponde ao hash
    
    Args:
        plain_password: Senha em texto plano
        hashed_password: Hash bcrypt armazenado
    
    Returns:
        True se corresponde, False caso contrário
    """
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================================
# FUNÇÕES DE JWT
# ============================================================================

def create_access_token(user_id: int, email: str) -> str:
    """
    Cria um JWT access token
    
    Args:
        user_id: ID do usuário
        email: Email do usuário
    
    Returns:
        String de JWT
    """
    to_encode = {
        "sub": str(user_id),
        "email": email,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Decodifica um JWT token
    
    Args:
        token: String de JWT
    
    Returns:
        Dicionário com payload do token
    
    Raises:
        JWTError: Se o token for inválido
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise JWTError(f"Token inválido: {str(e)}")


def verify_token(token: str) -> dict:
    """
    Verifica e retorna payload do token
    
    Args:
        token: String de JWT (pode incluir "Bearer ")
    
    Returns:
        Payload do token
    
    Raises:
        JWTError: Se inválido
    """
    # Remover "Bearer " se presente
    if token.startswith("Bearer "):
        token = token[7:]
    
    return decode_token(token)

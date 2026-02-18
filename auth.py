"""
auth.py
Módulo de autenticação: criptografia de senha, geração e validação de JWT
"""

from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

SECRET_KEY = os.getenv("SECRET_KEY")
ENV = os.getenv("ENV", "development")

if not SECRET_KEY:
    if ENV == "production":
        raise ValueError(
            "⚠️ ERRO CRÍTICO: SECRET_KEY não configurada em produção!\n"
            "Configure a variável de ambiente SECRET_KEY com um valor seguro."
        )
    SECRET_KEY = "ALICI_DEVELOPMENT_KEY_CHANGE_IN_PRODUCTION"
    print("⚠️ AVISO: Usando SECRET_KEY padrão (apenas para desenvolvimento)")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24h

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# ============================================================================
# SENHAS
# ============================================================================

def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Senha não pode ser vazia")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False

    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


# ============================================================================
# JWT
# ============================================================================

def create_access_token(user_id: int, email: str) -> str:
    """
    Cria um JWT access token
    """

    now = datetime.now(timezone.utc)

    to_encode = {
        "sub": str(user_id),
        "email": email,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decodifica token e valida expiração
    """

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload

    except ExpiredSignatureError:
        raise JWTError("Token expirado")

    except JWTError as e:
        raise JWTError(f"Token inválido: {str(e)}")


def verify_token(token: str) -> dict:
    """
    Verifica token e retorna payload
    """

    if not token:
        raise JWTError("Token não fornecido")

    # Remover prefixo Bearer
    if token.startswith("Bearer "):
        token = token[7:]

    payload = decode_token(token)

    if payload.get("type") != "access":
        raise JWTError("Tipo de token inválido")

    return payload

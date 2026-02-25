"""
auth.py
Módulo de autenticação: criptografia de senha, geração e validação de JWT
"""

import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from dotenv import load_dotenv
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from alici_api.config import get_settings

load_dotenv()

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
settings = get_settings()
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_MINUTES = settings.refresh_token_expire_minutes

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


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


def _create_token(user_id: int, email: str, token_type: str, expire_minutes: int) -> str:
    now = datetime.now(timezone.utc)

    to_encode = {
        "sub": str(user_id),
        "email": email,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expire_minutes)).timestamp()),
    }

    if token_type == "refresh":
        to_encode["jti"] = uuid4().hex

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(user_id: int, email: str) -> str:
    return _create_token(user_id, email, "access", ACCESS_TOKEN_EXPIRE_MINUTES)


def create_refresh_token(user_id: int, email: str) -> str:
    return _create_token(user_id, email, "refresh", REFRESH_TOKEN_EXPIRE_MINUTES)


def decode_token(token: str) -> dict:
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


def verify_token(token: str, expected_type: str = "access") -> dict:
    if not token:
        raise JWTError("Token não fornecido")

    if token.startswith("Bearer "):
        token = token[7:]

    payload = decode_token(token)

    if payload.get("type") != expected_type:
        raise JWTError("Tipo de token inválido")

    return payload

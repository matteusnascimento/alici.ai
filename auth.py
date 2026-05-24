"""Password hashing and JWT helpers."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from dotenv import load_dotenv
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from alici_api.config import get_settings
from logger import get_logger

load_dotenv()
logger_auth = get_logger("auth")
settings = get_settings()

SECRET_KEY = settings.secret_key.get_secret_value()
if not SECRET_KEY or SECRET_KEY == "dev-only-change-me":
    if settings.is_production:
        raise ValueError("SECRET_KEY segura e obrigatoria em producao")
    logger_auth.warning("AVISO: Usando SECRET_KEY padrao (apenas para desenvolvimento)")

ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_MINUTES = settings.refresh_token_expire_minutes

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Senha nao pode ser vazia")
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
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise JWTError("Token expirado")
    except JWTError as exc:
        raise JWTError(f"Token invalido: {exc}")


def verify_token(token: str, expected_type: str = "access") -> dict:
    if not token:
        raise JWTError("Token nao fornecido")

    if token.startswith("Bearer "):
        token = token[7:]

    payload = decode_token(token)
    if payload.get("type") != expected_type:
        raise JWTError("Tipo de token invalido")

    return payload

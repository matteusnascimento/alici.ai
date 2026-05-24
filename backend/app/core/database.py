from collections.abc import Generator
import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

_LOCAL_SQLITE_FALLBACK = "sqlite:///./axi.db"


class Base(DeclarativeBase):
    pass


database_url = settings.sqlalchemy_database_url


def _build_engine(url: str):
    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        return create_engine(url, future=True, connect_args=connect_args)

    # Neon/Postgres can close idle TLS sessions; pre_ping avoids reusing dead pooled connections.
    return create_engine(
        url,
        future=True,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_use_lifo=True,
    )


engine = _build_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)


def ensure_database_connection() -> str:
    global engine, SessionLocal, database_url

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return database_url
    except Exception as exc:
        if settings.app_env.lower() == "production" or database_url.startswith("sqlite"):
            raise

        logger.warning(
            "database.connection_failed db_url=%s fallback=%s reason=%s",
            database_url,
            _LOCAL_SQLITE_FALLBACK,
            exc,
        )
        database_url = _LOCAL_SQLITE_FALLBACK
        object.__setattr__(settings, "database_url", _LOCAL_SQLITE_FALLBACK)
        engine = _build_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)
        return database_url


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

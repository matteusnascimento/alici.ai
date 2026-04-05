from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


database_url = settings.sqlalchemy_database_url

if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(database_url, future=True, connect_args=connect_args)
else:
    # Neon/Postgres can close idle TLS sessions; pre_ping avoids reusing dead pooled connections.
    engine = create_engine(
        database_url,
        future=True,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_use_lifo=True,
    )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

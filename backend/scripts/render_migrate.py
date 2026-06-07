import os
import subprocess
import sys

from sqlalchemy import create_engine, inspect


def run(cmd: list[str]) -> int:
    print("$", " ".join(cmd), flush=True)
    return subprocess.call(cmd)


def normalize_db_url(url: str) -> str:
    if url.startswith("postgresql://") and not url.startswith("postgresql+psycopg://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def is_production() -> bool:
    return os.getenv("APP_ENV", os.getenv("ENV", "")).strip().lower() == "production"


def main() -> int:
    db_url = os.getenv("DATABASE_URL", "").strip()

    if not db_url:
        message = (
            "DATABASE_URL ausente. Abortando migrations para evitar fallback SQLite no deploy. "
            "Configure DATABASE_URL no Render/Neon antes de publicar."
        )
        print(message, flush=True)
        return 1 if is_production() else run(["alembic", "upgrade", "head"])

    normalized_db_url = normalize_db_url(db_url)

    if is_production() and normalized_db_url.startswith("sqlite"):
        print(
            "DATABASE_URL inválida para produção: SQLite não é permitido no Render. "
            "Configure PostgreSQL/Neon.",
            flush=True,
        )
        return 1

    os.environ["DATABASE_URL"] = db_url

    engine = create_engine(normalized_db_url, future=True)
    inspector = inspect(engine)

    tables = set(inspector.get_table_names())
    has_alembic_version = "alembic_version" in tables

    if not has_alembic_version and tables:
        print(
            "Banco existente sem alembic_version detectado. Abortando para evitar drift silencioso de schema. "
            "Execute baseline/migracao manual antes do deploy.",
            flush=True,
        )
        return 1

    print("Executando alembic upgrade head.", flush=True)
    return run(["alembic", "upgrade", "head"])


if __name__ == "__main__":
    sys.exit(main())

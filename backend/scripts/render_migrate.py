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


def main() -> int:
    db_url = os.getenv("DATABASE_URL", "").strip()
    if not db_url:
        try:
            from app.core.config import settings

            db_url = settings.database_url.strip()
        except Exception:
            db_url = ""

    if not db_url:
        print("DATABASE_URL ausente; executando upgrade padrao.", flush=True)
        return run(["alembic", "upgrade", "head"])

    engine = create_engine(normalize_db_url(db_url), future=True)
    inspector = inspect(engine)

    tables = set(inspector.get_table_names())
    has_alembic_version = "alembic_version" in tables

    if not has_alembic_version and tables:
        print("Banco existente sem alembic_version; aplicando stamp head.", flush=True)
        code = run(["alembic", "stamp", "head"])
        if code != 0:
            return code

    print("Executando alembic upgrade head.", flush=True)
    return run(["alembic", "upgrade", "head"])


if __name__ == "__main__":
    sys.exit(main())
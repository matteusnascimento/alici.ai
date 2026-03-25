from sqlalchemy import text
from sqlalchemy.engine import Engine


class SchemaSyncService:
    """Aplica ajustes mínimos de compatibilidade de schema em bancos legados."""

    def __init__(self, engine: Engine):
        self.engine = engine

    def apply_startup_fixes(self) -> None:
        if self.engine.url.get_backend_name() != "postgresql":
            return

        with self.engine.begin() as conn:
            table_exists = conn.execute(text("select to_regclass('public.users')")).scalar()
            if not table_exists:
                return

            self._sync_users_table(conn)

    def _sync_users_table(self, conn) -> None:
        rename_map = {
            "nome": "name",
            "senha_hash": "password_hash",
            "plano": "plan",
            "criado_em": "created_at",
        }

        columns = self._get_users_columns(conn)

        for old_name, new_name in rename_map.items():
            if old_name in columns and new_name not in columns:
                conn.execute(text(f'ALTER TABLE users RENAME COLUMN "{old_name}" TO "{new_name}"'))

        columns = self._get_users_columns(conn)

        if "username" not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN username VARCHAR(50)"))

        if "phone" not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(30)"))

        if "plan" in self._get_users_columns(conn):
            conn.execute(text("UPDATE users SET plan = 'free' WHERE plan IS NULL OR btrim(plan) = ''"))
            conn.execute(text("ALTER TABLE users ALTER COLUMN plan SET DEFAULT 'free'"))

        conn.execute(
            text(
                """
                UPDATE users
                SET username = left(split_part(email, '@', 1), 40) || '_' || id::text
                WHERE username IS NULL OR btrim(username) = ''
                """
            )
        )
        conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users (username)"))

    def _get_users_columns(self, conn) -> set[str]:
        rows = conn.execute(
            text(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'users'
                """
            )
        ).fetchall()
        return {row[0] for row in rows}

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
            self._sync_user_settings_table(conn)
            self._sync_media_tables(conn)

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

        if "avatar_url" not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR(512)"))

        if "bio" not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN bio TEXT"))

        if "updated_at" not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN updated_at TIMESTAMPTZ DEFAULT now()"))

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

    def _sync_user_settings_table(self, conn) -> None:
        table_exists = conn.execute(text("select to_regclass('public.user_settings')")).scalar()
        if not table_exists:
            return

        columns = self._get_table_columns(conn, "user_settings")
        expected_columns = {
            "theme_mode": "VARCHAR(20) DEFAULT 'dark'",
            "accent_color": "VARCHAR(30) DEFAULT 'cyan'",
            "haptic_feedback": "BOOLEAN DEFAULT false",
            "notifications_enabled": "BOOLEAN DEFAULT true",
            "email_notifications": "BOOLEAN DEFAULT true",
            "push_notifications": "BOOLEAN DEFAULT true",
            "product_updates": "BOOLEAN DEFAULT true",
            "marketing_notifications": "BOOLEAN DEFAULT false",
            "security_alerts": "BOOLEAN DEFAULT true",
            "archived_chat_visibility": "BOOLEAN DEFAULT true",
        }

        for column_name, column_type in expected_columns.items():
            if column_name in columns:
                continue
            conn.execute(text(f"ALTER TABLE user_settings ADD COLUMN {column_name} {column_type}"))

    def _get_users_columns(self, conn) -> set[str]:
        return self._get_table_columns(conn, "users")

    def _sync_media_tables(self, conn) -> None:
        media_projects_exists = conn.execute(text("select to_regclass('public.media_projects')")).scalar()
        if not media_projects_exists:
            conn.execute(
                text(
                    """
                    CREATE TABLE media_projects (
                      id SERIAL PRIMARY KEY,
                      user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                      name VARCHAR(140) NOT NULL,
                      timeline_json JSONB NOT NULL DEFAULT '{}'::jsonb,
                      thumbnail VARCHAR(512),
                      duration INTEGER NOT NULL DEFAULT 0,
                      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                      updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                    )
                    """
                )
            )
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_media_projects_user_id ON media_projects (user_id)"))

        media_jobs_exists = conn.execute(text("select to_regclass('public.media_jobs')")).scalar()
        if not media_jobs_exists:
            conn.execute(
                text(
                    """
                    CREATE TABLE media_jobs (
                      id SERIAL PRIMARY KEY,
                      user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                      project_id INTEGER REFERENCES media_projects(id) ON DELETE SET NULL,
                      job_type VARCHAR(40) NOT NULL DEFAULT 'generate',
                      status VARCHAR(40) NOT NULL DEFAULT 'queued',
                      progress INTEGER NOT NULL DEFAULT 0,
                      prompt VARCHAR(1000),
                      result_url VARCHAR(512),
                      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                      updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                    )
                    """
                )
            )
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_media_jobs_user_id ON media_jobs (user_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_media_jobs_project_id ON media_jobs (project_id)"))

    def _get_table_columns(self, conn, table_name: str) -> set[str]:
        rows = conn.execute(
            text(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = :table_name
                """
            ),
            {"table_name": table_name},
        ).fetchall()
        return {row[0] for row in rows}

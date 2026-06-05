from app.core.config import Settings


def test_settings_accepts_release_debug_value():
    settings = Settings(
        app_env="development",
        debug="release",
        database_url="sqlite:///./test.db",
        enable_dev_seed_user=False,
    )

    assert settings.debug is False


def test_settings_ignores_render_extra_env_and_accepts_aliases(monkeypatch):
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("PORT", "10000")
    monkeypatch.setenv("DATABASE_URL", " postgresql://user:pass@example.com:5432/db ")
    monkeypatch.setenv("SECRET_KEY", "render-secret-key-with-more-than-32-characters")
    monkeypatch.setenv("REDIS_URL", "redis://example.com:6379")
    monkeypatch.setenv("GROQ_API_KEY", "groq-key")
    monkeypatch.setenv("R2_ENDPOINT_URL", " https://r2.example.com ")
    monkeypatch.setenv("R2_ACCESS_KEY_ID", "r2-access")
    monkeypatch.setenv("R2_SECRET_ACCESS_KEY", "r2-secret")
    monkeypatch.setenv("R2_BUCKET_UPLOADS", "uploads")
    monkeypatch.setenv("R2_PUBLIC_BASE_URL", "https://cdn.example.com")
    monkeypatch.setenv("PGUSER", "unused")
    monkeypatch.setenv("PGPASSWORD", "unused")
    monkeypatch.setenv("UNDECLARED_RENDER_VAR", "ignored")

    settings = Settings(enable_dev_seed_user=False)

    assert settings.app_env == "production"
    assert settings.port == 10000
    assert settings.redis_url == "redis://example.com:6379"
    assert settings.groq_api_key == "groq-key"
    assert settings.sqlalchemy_database_url == "postgresql+psycopg://user:pass@example.com:5432/db"
    assert settings.effective_r2_endpoint_url == "https://r2.example.com"
    assert settings.effective_r2_bucket_name == "uploads"
    assert settings.is_r2_configured() is True

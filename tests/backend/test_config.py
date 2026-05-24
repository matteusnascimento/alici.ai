from app.core.config import Settings


def test_settings_accepts_release_debug_value():
    settings = Settings(
        app_env="development",
        debug="release",
        database_url="sqlite:///./test.db",
        enable_dev_seed_user=False,
    )

    assert settings.debug is False

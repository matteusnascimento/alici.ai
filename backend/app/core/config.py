import warnings
import json
from urllib.parse import urlparse
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_KEYS = {"change-me", "secret", "changeme", "dev", "development", "troque-esta-chave-por-uma-chave-forte"}
_LOCAL_SQLITE_FALLBACK = "sqlite:///./axi.db"


def _is_valid_database_url(value: str) -> bool:
    raw = (value or "").strip()
    if not raw:
        return False
    if raw.startswith("sqlite"):
        return True

    parsed = urlparse(raw)
    return parsed.scheme in {"postgresql", "postgresql+psycopg"} and bool(parsed.netloc)


class Settings(BaseSettings):
    app_name: str = "AXI Platform"
    app_env: str = "development"
    debug: bool = True
    public_backend_url: str = "http://127.0.0.1:8000"
    public_frontend_url: str = "http://127.0.0.1:5173"
    app_secret_key: str = ""
    database_url: str = _LOCAL_SQLITE_FALLBACK
    enable_dev_seed_user: bool = True
    dev_seed_name: str = "AXI Dev"
    dev_seed_username: str = "devaxi"
    dev_seed_email: str = "dev@axi-platform.com"
    dev_seed_phone: str = "11990000000"
    dev_seed_password: str = ""
    secret_key: str = "change-me-local-dev-secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    refresh_token_expire_minutes: int = 10080
    password_reset_expire_minutes: int = 30
    email_verification_expire_minutes: int = 1440
    default_ai_provider: str = "groq"
    ai_provider_timeout_seconds: float = 30.0
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    groq_model_chat: str = ""
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    gemini_model_chat: str = ""
    ollama_enabled: bool = False
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    ollama_timeout_seconds: float = 8.0
    openai_api_key: str = ""
    openai_api_key_rotated: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_chat_model: str = ""
    openai_timeout_seconds: float = 30.0
    openai_model_chat_general: str = "gpt-4o-mini"
    openai_model_support: str = "gpt-4o-mini"
    openai_model_copy: str = "gpt-4o-mini"
    openai_model_agent_runtime: str = "gpt-4o-mini"
    openai_model_summarization: str = "gpt-4o-mini"
    openai_model_classifier: str = "gpt-4o-mini"
    openai_model_knowledge_qa: str = "gpt-4o-mini"
    openai_model_vision: str = "gpt-4o-mini"
    openai_image_model: str = "gpt-image-1"
    openai_model_transcription: str = "gpt-4o-transcribe"
    openai_model_embeddings: str = "text-embedding-3-small"
    database_url_rotated: str = ""
    cors_allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173", "http://localhost:3000"])
    billing_admin_emails: list[str] = Field(default_factory=list)
    admin_emails: list[str] = Field(default_factory=list)
    owner_emails: list[str] = Field(default_factory=list)

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_publishable_key: str = ""
    stripe_price_pro: str = ""
    stripe_price_business: str = ""
    stripe_price_pro_monthly: str = ""
    stripe_price_pro_yearly: str = ""
    stripe_price_business_monthly: str = ""
    stripe_price_business_yearly: str = ""
    stripe_price_test: str = ""
    app_base_url: str = "http://localhost:5173"
    stripe_success_url: str = ""
    stripe_cancel_url: str = ""
    stripe_billing_portal_return_url: str = "http://127.0.0.1:5173/app/admin/billing"

    # Meta channels (WhatsApp/Instagram)
    meta_client_id: str = ""
    meta_client_secret: str = ""
    meta_redirect_uri: str = ""
    meta_oauth_scopes: str = ""
    meta_graph_api_version: str = "v20.0"
    meta_oauth_client_id: str = ""
    meta_oauth_redirect_uri: str = ""
    meta_app_secret: str = ""
    meta_webhook_verify_token: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = ""
    google_oauth_scopes: str = ""
    google_ads_developer_token: str = ""
    google_ads_customer_id: str = ""
    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""
    google_oauth_redirect_uri: str = ""

    # Website tracker / widget
    axi_tracker_public_url: str = "http://127.0.0.1:8000/api/tracker/script.js"
    axi_widget_public_url: str = "http://127.0.0.1:8000/static/axi-widget.js"
    website_allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"])

    # Hospitality providers
    omnibees_api_base_url: str = ""
    omnibees_client_id: str = ""
    omnibees_client_secret: str = ""
    omnibees_environment: str = "sandbox"
    pms_api_base_url: str = ""
    pms_client_id: str = ""
    pms_client_secret: str = ""
    pms_environment: str = "sandbox"

    # Studio external providers
    freepik_api_key: str = ""
    envato_api_key: str = ""
    removebg_api_key: str = ""
    flux_api_key: str = ""
    shotstack_api_key: str = ""
    shotstack_environment: str = "sandbox"
    creatomate_api_key: str = ""
    elevenlabs_api_key: str = ""

    # Storage / media
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = ""
    r2_public_base_url: str = ""

    redis_url: str = ""
    redis_required: bool = False
    storage_external_required: bool = False
    rate_limit_enabled: bool = True
    rate_limit_window_seconds: int = 60
    rate_limit_max_requests: int = 120
    public_upload_max_age_seconds: int = 300

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_cors(cls, value: str | list[str]) -> list[str]:
        return cls._parse_string_list(value, field_name="CORS_ALLOWED_ORIGINS")

    @field_validator("website_allowed_origins", mode="before")
    @classmethod
    def parse_website_allowed_origins(cls, value: str | list[str]) -> list[str]:
        return cls._parse_string_list(value, field_name="WEBSITE_ALLOWED_ORIGINS")

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value: bool | str) -> bool | str:
        if isinstance(value, str):
            raw = value.strip().lower()
            if raw in {"1", "true", "yes", "on", "debug", "dev", "development"}:
                return True
            if raw in {"0", "false", "no", "off", "release", "prod", "production"}:
                return False
        return value

    @field_validator("billing_admin_emails", mode="before")
    @classmethod
    def parse_billing_admin_emails(cls, value: str | list[str]) -> list[str]:
        return [item.lower() for item in cls._parse_string_list(value, field_name="BILLING_ADMIN_EMAILS")]

    @field_validator("admin_emails", mode="before")
    @classmethod
    def parse_admin_emails(cls, value: str | list[str]) -> list[str]:
        return [item.lower() for item in cls._parse_string_list(value, field_name="ADMIN_EMAILS")]

    @field_validator("owner_emails", mode="before")
    @classmethod
    def parse_owner_emails(cls, value: str | list[str]) -> list[str]:
        return [item.lower() for item in cls._parse_string_list(value, field_name="OWNER_EMAILS")]

    @field_validator("default_ai_provider")
    @classmethod
    def validate_default_ai_provider(cls, value: str) -> str:
        normalized = (value or "").strip().lower()
        if normalized not in {"groq", "gemini", "ollama", "openai"}:
            raise ValueError("DEFAULT_AI_PROVIDER deve ser groq, gemini, ollama ou openai")
        return normalized

    @classmethod
    def _parse_string_list(cls, value: str | list[str], *, field_name: str) -> list[str]:
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return []
            if raw.startswith("["):
                parsed = json.loads(raw)
                if not isinstance(parsed, list):
                    raise ValueError(f"{field_name} JSON deve ser uma lista de strings")
                return [item.strip() for item in parsed if isinstance(item, str) and item.strip()]
            return [item.strip() for item in raw.split(",") if item.strip()]
        return [item.strip() for item in value if isinstance(item, str) and item.strip()]

    def __init__(self, **data):
        super().__init__(**data)

        raw_database_url = (self.database_url or "").strip()
        if not _is_valid_database_url(raw_database_url):
            if self.app_env.lower() == "production":
                raise ValueError("Invalid DATABASE_URL for production environment")
            warnings.warn(
                "Invalid DATABASE_URL detected in local environment. Falling back to SQLite.",
                RuntimeWarning,
            )
            object.__setattr__(self, "database_url", _LOCAL_SQLITE_FALLBACK)
        elif raw_database_url != self.database_url:
            object.__setattr__(self, "database_url", raw_database_url)

        normalized_env = self.app_env.lower()
        normalized_secret = self.secret_key.strip().lower()

        if normalized_env != "development" and (
            normalized_secret in _INSECURE_KEYS
            or normalized_secret.startswith("change-me")
            or len(self.secret_key) < 32
        ):
            raise ValueError(
                "Insecure SECRET_KEY detected for non-development environment. "
                "Set a strong SECRET_KEY via environment variable."
            )

        if normalized_env != "development" and "*" in self.cors_allowed_origins:
            raise ValueError("CORS_ALLOWED_ORIGINS cannot contain '*' outside development")

        if self.should_seed_dev_user and not self.dev_seed_password:
            raise ValueError(
                "ENABLE_DEV_SEED_USER=true requires DEV_SEED_PASSWORD to be set via environment variable."
            )

        if normalized_env != "development":
            object.__setattr__(self, "debug", False)

    @property
    def sqlalchemy_database_url(self) -> str:
        effective_database_url = self.database_url_rotated or self.database_url
        if effective_database_url.startswith("postgresql://") and not effective_database_url.startswith("postgresql+psycopg://"):
            return effective_database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        return effective_database_url

    @property
    def frontend_base_url(self) -> str:
        return (self.public_frontend_url or self.app_base_url or "http://localhost:5173").rstrip("/")

    @property
    def backend_base_url(self) -> str:
        return (self.public_backend_url or "http://127.0.0.1:8000").rstrip("/")

    @property
    def effective_app_secret_key(self) -> str:
        return self.app_secret_key or self.secret_key

    @property
    def effective_meta_client_id(self) -> str:
        return self.meta_client_id or self.meta_oauth_client_id

    @property
    def effective_meta_client_secret(self) -> str:
        return self.meta_client_secret or self.meta_app_secret

    @property
    def effective_meta_redirect_uri(self) -> str:
        return self.meta_redirect_uri or self.meta_oauth_redirect_uri

    @property
    def effective_google_client_id(self) -> str:
        return self.google_client_id or self.google_oauth_client_id

    @property
    def effective_google_client_secret(self) -> str:
        return self.google_client_secret or self.google_oauth_client_secret

    @property
    def effective_google_redirect_uri(self) -> str:
        return self.google_redirect_uri or self.google_oauth_redirect_uri

    @property
    def effective_openai_api_key(self) -> str:
        # During key rotation, OPENAI_API_KEY_ROTATED takes precedence.
        return self.openai_api_key_rotated or self.openai_api_key

    @property
    def effective_openai_chat_model(self) -> str:
        return self.openai_chat_model or self.openai_model or "gpt-4o-mini"

    @property
    def effective_groq_chat_model(self) -> str:
        return self.groq_model_chat or self.groq_model or "llama-3.1-8b-instant"

    @property
    def effective_gemini_chat_model(self) -> str:
        return self.gemini_model_chat or self.gemini_model or "gemini-1.5-flash"

    @property
    def should_seed_dev_user(self) -> bool:
        return (
            self.enable_dev_seed_user
            and self.app_env.lower() != "production"
            and self.sqlalchemy_database_url.startswith("sqlite")
        )

    def is_meta_configured(self) -> bool:
        return all(
            [
                (self.effective_meta_client_id or "").strip(),
                (self.effective_meta_client_secret or "").strip(),
                (self.effective_meta_redirect_uri or "").strip(),
                (self.meta_oauth_scopes or "").strip(),
                (self.effective_app_secret_key or "").strip(),
            ]
        )

    def is_google_configured(self) -> bool:
        return all(
            [
                (self.effective_google_client_id or "").strip(),
                (self.effective_google_client_secret or "").strip(),
                (self.effective_google_redirect_uri or "").strip(),
                (self.google_oauth_scopes or "").strip(),
                (self.effective_app_secret_key or "").strip(),
            ]
        )

    def is_studio_template_provider_configured(self, provider: str | None = None) -> bool:
        normalized = (provider or "").strip().lower()
        providers = {
            "freepik": self.freepik_api_key,
            "envato": self.envato_api_key,
        }
        if normalized:
            return bool((providers.get(normalized) or "").strip())
        return any((value or "").strip() for value in providers.values())

    def is_ai_provider_configured(self, provider: str | None = None) -> bool:
        normalized = (provider or self.default_ai_provider or "").strip().lower()
        if normalized == "groq":
            return bool((self.groq_api_key or "").strip())
        if normalized == "gemini":
            return bool((self.gemini_api_key or "").strip())
        if normalized == "ollama":
            return bool(self.ollama_enabled and (self.ollama_base_url or "").strip())
        if normalized == "openai":
            return bool((self.effective_openai_api_key or "").strip())
        return False

    def is_r2_configured(self) -> bool:
        return all(
            [
                (self.r2_account_id or "").strip(),
                (self.r2_access_key_id or "").strip(),
                (self.r2_secret_access_key or "").strip(),
                (self.r2_bucket_name or "").strip(),
                (self.r2_public_base_url or "").strip(),
            ]
        )

    def is_stripe_configured(self) -> bool:
        return bool((self.stripe_secret_key or "").strip() and (self.stripe_webhook_secret or "").strip())

    def is_omnibees_configured(self) -> bool:
        return all(
            [
                (self.omnibees_api_base_url or "").strip(),
                (self.omnibees_client_id or "").strip(),
                (self.omnibees_client_secret or "").strip(),
            ]
        )

    def is_pms_configured(self) -> bool:
        return all(
            [
                (self.pms_api_base_url or "").strip(),
                (self.pms_client_id or "").strip(),
                (self.pms_client_secret or "").strip(),
            ]
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

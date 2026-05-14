"""Typed application settings.

All runtime configuration must come from environment variables or .env files.
Production validates critical secrets and blocks wildcard CORS.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _split_csv(value: str | list[str] | tuple[str, ...] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value).split(",") if item.strip()]


def _parse_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    normalized = str(value).strip().lower()
    return normalized in {"1", "true", "yes", "on", "debug", "development", "dev"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "ALICI API"
    app_version: str = "2.2"
    env: Literal["development", "staging", "production", "test"] = "development"
    debug: bool = False
    port: int = 8000
    public_app_url: str = "http://localhost:8000"
    api_base_url: str = "http://localhost:8000"
    docs_enabled: bool = True
    openapi_enabled: bool = True
    allowed_hosts: str = ""

    # Security / JWT
    secret_key: SecretStr = Field(default=SecretStr("dev-only-change-me"))
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_minutes: int = 60 * 24 * 7

    # Database
    database_url: str | None = "sqlite:///database.db"
    database_pool_min: int = 1
    database_pool_max: int = 10

    # CORS
    cors_allowed_origins: str = ""
    cors_allow_credentials: bool = True
    cors_allowed_methods: str = "*"
    cors_allowed_headers: str = "*"

    # Security headers
    security_headers_enabled: bool = True
    security_hsts_enabled: bool = True
    security_hsts_max_age: int = 31_536_000
    security_csp_enabled: bool = True
    security_csp: str = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: blob:; "
        "font-src 'self' data:; "
        "connect-src 'self' http://localhost:* ws://localhost:*; "
        "media-src 'self' blob: data:; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    security_referrer_policy: str = "strict-origin-when-cross-origin"
    security_permissions_policy: str = "camera=(), microphone=(), geolocation=(), payment=()"

    # AI prompt protection
    prompt_security_enabled: bool = True
    prompt_max_chars: int = 8_000
    prompt_block_high_risk: bool = True
    prompt_risk_threshold: int = 3

    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_window_seconds: int = 60
    rate_limit_max_requests: int = 60
    rate_limit_user_max_requests: int = 120
    rate_limit_ip_max_requests: int = 180
    rate_limit_endpoint_max_requests: int = 600
    rate_limit_global_max_requests: int = 3_000
    rate_limit_excluded_paths: str = (
        "/health,/health.,/health/live,/health/ready,/health/deep,"
        "/api/health,/v1/health,/static,/generated,/favicon.ico"
    )
    redis_url: str | None = None
    redis_prefix: str = "alici"

    # Redis AI cache
    ai_cache_enabled: bool = True
    ai_cache_ttl_seconds: int = 3_600

    # Arq background jobs
    arq_queue_default: str = "alici:queue:default"
    arq_queue_high: str = "alici:queue:high"
    arq_queue_low: str = "alici:queue:low"
    arq_queue_dlq: str = "alici:queue:dead"
    arq_max_retries: int = 3
    arq_job_timeout_seconds: int = 600
    arq_keep_result_seconds: int = 3600
    media_upload_max_bytes: int = 10_485_760

    # Sentry / observability
    sentry_dsn: str | None = None
    sentry_traces_sample_rate: float = 0.05
    sentry_profiles_sample_rate: float = 0.0
    log_level: str = "INFO"

    # Stripe
    stripe_secret_key: SecretStr | None = None
    stripe_publishable_key: str | None = None
    stripe_webhook_secret: SecretStr | None = None
    stripe_portal_return_url: str | None = None
    stripe_checkout_success_url: str | None = None
    stripe_checkout_cancel_url: str | None = None
    stripe_price_pro: str | None = None
    stripe_price_ultra: str | None = None
    stripe_price_enterprise: str | None = None

    # Credits
    credits_free_signup: int = 20
    credits_pro_monthly: int = 1_000
    credits_ultra_monthly: int = 5_000
    credits_enterprise_monthly: int = 25_000
    credits_chat_default_cost: int = 1
    credits_image_default_cost: int = 10
    credits_audio_default_cost: int = 5
    credits_video_default_cost: int = 100

    # AI providers
    default_ai_provider: Literal["groq", "gemini", "ollama", "openai"] = "groq"
    groq_api_key: SecretStr | None = None
    groq_model_chat: str = "llama-3.1-8b-instant"
    groq_model_agent: str = "llama-3.1-8b-instant"
    groq_model_code: str = "qwen/qwen3-coder"
    gemini_api_key: SecretStr | None = None
    gemini_model: str = "gemini-1.5-flash"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    openai_api_key: SecretStr | None = None
    openai_model_chat_general: str = "gpt-4o-mini"

    # Cloudflare R2 / uploads
    alici_r2_account_id: str | None = None
    alici_r2_access_key: SecretStr | None = None
    alici_r2_secret_key: SecretStr | None = None
    alici_r2_endpoint: str | None = None
    alici_r2_bucket: str | None = None
    alici_r2_model_prefix: str | None = None
    alici_model_cache_dir: str = "/tmp/alici_cpu_simple_r2_cache"
    alici_intents_path: str = "./intents.json"
    r2_endpoint_url: str | None = None
    r2_access_key_id: str | None = None
    r2_secret_access_key: SecretStr | None = None
    r2_bucket_uploads: str = "uploads"
    r2_public_base_url: str | None = None

    # Hugging Face
    huggingface_api_key: SecretStr | None = None
    huggingface_token: SecretStr | None = None
    huggingface_model_url: str | None = None
    huggingface_timeout_seconds: int = 25
    huggingface_max_retries: int = 2
    alici_hf_repo_id: str = "Matteusnascimento/alici.ai"
    alici_hf_repo_type: str = "space"
    alici_hf_subfolder: str | None = None
    alici_hf_cache_dir: str = "/tmp/alici_hf_cache"

    @field_validator(
        "debug",
        "cors_allow_credentials",
        "security_headers_enabled",
        "security_hsts_enabled",
        "security_csp_enabled",
        "rate_limit_enabled",
        "ai_cache_enabled",
        "docs_enabled",
        "openapi_enabled",
        "prompt_security_enabled",
        "prompt_block_high_risk",
        mode="before",
    )
    @classmethod
    def parse_bool_values(cls, value):
        return _parse_bool(value)

    @model_validator(mode="after")
    def validate_production_settings(self):
        cors_origins = self.cors_origins

        if self.env == "production":
            secret_value = self.secret_key.get_secret_value()
            if not secret_value or secret_value == "dev-only-change-me":
                raise ValueError("SECRET_KEY seguro e unico e obrigatorio em producao")
            if not self.database_url or not self.database_url.startswith("postgresql"):
                raise ValueError("DATABASE_URL PostgreSQL/Neon e obrigatorio em producao")
            if not self.public_app_url.startswith("https://"):
                raise ValueError("PUBLIC_APP_URL deve usar HTTPS em producao")
            if not self.api_base_url.startswith("https://"):
                raise ValueError("API_BASE_URL deve usar HTTPS em producao")
            if "*" in cors_origins:
                raise ValueError("CORS_ALLOWED_ORIGINS nao pode conter '*' em producao")
            if not cors_origins:
                raise ValueError("CORS_ALLOWED_ORIGINS deve ser configurado em producao")
            if "*" in self.trusted_hosts:
                raise ValueError("ALLOWED_HOSTS nao pode conter '*' em producao")
            if not self.trusted_hosts:
                raise ValueError("ALLOWED_HOSTS deve ser configurado em producao")
            if not self.redis_url:
                raise ValueError("REDIS_URL e obrigatorio em producao para rate limit, cache e jobs")

        return self

    @property
    def is_production(self) -> bool:
        return self.env == "production"

    @property
    def is_development(self) -> bool:
        return self.env == "development"

    @property
    def api_docs_enabled(self) -> bool:
        return self.env != "production" and self.docs_enabled

    @property
    def api_openapi_enabled(self) -> bool:
        return self.env != "production" and self.openapi_enabled

    @property
    def cors_origins(self) -> list[str]:
        values = _split_csv(self.cors_allowed_origins)
        if values:
            return values
        return ["*"] if self.env != "production" else []

    @property
    def cors_methods(self) -> list[str]:
        return _split_csv(self.cors_allowed_methods) or ["*"]

    @property
    def cors_headers(self) -> list[str]:
        return _split_csv(self.cors_allowed_headers) or ["*"]

    @property
    def trusted_hosts(self) -> list[str]:
        values = _split_csv(self.allowed_hosts)
        if values:
            return values
        return ["*"] if self.env != "production" else []

    @property
    def excluded_rate_limit_paths(self) -> list[str]:
        return _split_csv(self.rate_limit_excluded_paths)

    @property
    def resolved_redis_url(self) -> str:
        if self.redis_url:
            return self.redis_url
        if self.env == "production":
            raise ValueError("REDIS_URL e obrigatorio em producao")
        return "redis://localhost:6379/0"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

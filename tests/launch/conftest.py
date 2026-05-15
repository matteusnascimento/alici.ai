from __future__ import annotations

import os


os.environ.setdefault("ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_launch.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-change-in-prod")
os.environ.setdefault("DEFAULT_AI_PROVIDER", "grok")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("MEDIA_STORAGE_REQUIRED", "false")
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_placeholder")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_placeholder")

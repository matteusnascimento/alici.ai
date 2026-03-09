"""
Development user for bypassing authentication in DEV_MODE.

This module provides a mock user and organization that are returned by
``AuthService.get_current_user`` when the application is running with
``DEV_MODE=true``.  It must **never** be used in a production environment.
"""
from types import SimpleNamespace

DEV_ORGANIZATION = SimpleNamespace(
    id="dev_org",
    name="Dev Organization",
    slug="dev-organization",
    plan="admin",
    monthly_request_limit=999_999,
    current_month_requests=0,
    is_active=True,
    allow_public_api=True,
    users=[],
    agents=[],
    api_keys=[],
    usage_logs=[],
    stripe_customer_id=None,
    description=None,
    created_at=None,
    updated_at=None,
)

DEV_USER = SimpleNamespace(
    id="dev_user",
    email="dev@alici.ai",
    full_name="Developer",
    hashed_password="",
    is_active=True,
    is_superuser=True,
    organization_id="dev_org",
    organization=DEV_ORGANIZATION,
    created_at=None,
    updated_at=None,
)

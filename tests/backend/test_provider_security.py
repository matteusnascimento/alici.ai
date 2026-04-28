import pytest
from fastapi import HTTPException

from app.api.routes.ai import _download_public_image
from app.integrations.providers.api import APIProvider
from app.integrations.providers.crm import CRMProvider
from app.integrations.providers.webhook import WebhookProvider


def test_api_provider_rejects_local_urls():
    result = APIProvider().validate_config({"api_url": "http://127.0.0.1:8000/private"})

    assert result.success is False
    assert "local" in result.message or "privado" in result.message


def test_webhook_provider_rejects_localhost():
    result = WebhookProvider().validate_config({"webhook_url": "http://localhost:3000/hook"})

    assert result.success is False
    assert "localhost" in result.message


def test_crm_provider_rejects_private_custom_url():
    result = CRMProvider().validate_config(
        {
            "crm_type": "custom",
            "api_key": "secret",
            "api_url": "http://10.0.0.5/api",
        }
    )

    assert result.success is False
    assert "privado" in result.message or "local" in result.message


def test_image_analysis_rejects_local_urls():
    with pytest.raises(HTTPException) as exc_info:
        _download_public_image("http://127.0.0.1/internal.png")

    assert exc_info.value.status_code == 400
    assert "local" in exc_info.value.detail or "privado" in exc_info.value.detail

from __future__ import annotations

import pytest
from pydantic import SecretStr

from alici_api.config import get_settings
from alici_api.services.media_service import MediaProviderUnavailableError, available_media_providers
from alici_api.services.media_storage import R2MediaStorage


def test_r2_status_reports_missing_required_configuration(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "r2_endpoint_url", None)
    monkeypatch.setattr(settings, "r2_access_key_id", None)
    monkeypatch.setattr(settings, "r2_secret_access_key", None)
    monkeypatch.setattr(settings, "r2_public_base_url", None)

    status = R2MediaStorage().status()

    assert status["configured"] is False
    assert "R2_ENDPOINT_URL" in status["missing"]
    assert "R2_PUBLIC_BASE_URL" in status["missing"]


def test_paid_image_provider_requires_r2_before_accepting_generation(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "replicate_api_token", SecretStr("replicate-test"))
    monkeypatch.setattr(settings, "r2_endpoint_url", None)
    monkeypatch.setattr(settings, "r2_access_key_id", None)
    monkeypatch.setattr(settings, "r2_secret_access_key", None)
    monkeypatch.setattr(settings, "r2_public_base_url", None)

    with pytest.raises(MediaProviderUnavailableError) as exc:
        available_media_providers("image")

    assert "Storage persistente R2 obrigatorio" in str(exc.value)

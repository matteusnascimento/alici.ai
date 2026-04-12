from __future__ import annotations

import base64
import hashlib

from app.core.config import settings


def _secret_key_bytes() -> bytes:
    return hashlib.sha256(settings.secret_key.encode("utf-8")).digest()


def seal_secret(value: str | None) -> str | None:
    if not value:
        return None

    key = _secret_key_bytes()
    payload = value.encode("utf-8")
    encrypted = bytes(byte ^ key[index % len(key)] for index, byte in enumerate(payload))
    return base64.urlsafe_b64encode(encrypted).decode("ascii")


def open_secret(value: str | None) -> str | None:
    if not value:
        return None

    key = _secret_key_bytes()
    encrypted = base64.urlsafe_b64decode(value.encode("ascii"))
    payload = bytes(byte ^ key[index % len(key)] for index, byte in enumerate(encrypted))
    return payload.decode("utf-8")
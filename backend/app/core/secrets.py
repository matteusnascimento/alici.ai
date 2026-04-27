from __future__ import annotations

import base64
import binascii
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings

_FERNET_PREFIX = "fernet:"


def _secret_key_bytes() -> bytes:
    return hashlib.sha256(settings.secret_key.encode("utf-8")).digest()


def _fernet() -> Fernet:
    return Fernet(base64.urlsafe_b64encode(_secret_key_bytes()))


def _legacy_open_secret(value: str) -> str:
    try:
        encrypted = base64.urlsafe_b64decode(value.encode("ascii"))
    except (binascii.Error, UnicodeEncodeError) as exc:
        raise ValueError("Invalid encrypted secret") from exc

    key = _secret_key_bytes()
    payload = bytes(byte ^ key[index % len(key)] for index, byte in enumerate(encrypted))
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Invalid encrypted secret") from exc


def seal_secret(value: str | None) -> str | None:
    if not value:
        return None

    token = _fernet().encrypt(value.encode("utf-8")).decode("ascii")
    return f"{_FERNET_PREFIX}{token}"


def open_secret(value: str | None) -> str | None:
    if not value:
        return None

    if value.startswith(_FERNET_PREFIX):
        token = value.removeprefix(_FERNET_PREFIX).encode("ascii")
        try:
            return _fernet().decrypt(token).decode("utf-8")
        except (InvalidToken, UnicodeEncodeError, UnicodeDecodeError) as exc:
            raise ValueError("Invalid encrypted secret") from exc

    try:
        return _fernet().decrypt(value.encode("ascii")).decode("utf-8")
    except (InvalidToken, UnicodeEncodeError, UnicodeDecodeError):
        return _legacy_open_secret(value)

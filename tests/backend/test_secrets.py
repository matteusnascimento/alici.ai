import base64
import hashlib

from app.core.config import settings
from app.core.secrets import open_secret, seal_secret


def _legacy_xor_seal(value: str) -> str:
    key = hashlib.sha256(settings.secret_key.encode("utf-8")).digest()
    payload = value.encode("utf-8")
    encrypted = bytes(byte ^ key[index % len(key)] for index, byte in enumerate(payload))
    return base64.urlsafe_b64encode(encrypted).decode("ascii")


def test_secret_encryption_roundtrip_uses_authenticated_envelope():
    encrypted = seal_secret("meta-token-valid")

    assert encrypted is not None
    assert encrypted.startswith("fernet:")
    assert "meta-token-valid" not in encrypted
    assert open_secret(encrypted) == "meta-token-valid"


def test_secret_encryption_reads_legacy_xor_values():
    legacy_value = _legacy_xor_seal("legacy-token")

    assert open_secret(legacy_value) == "legacy-token"

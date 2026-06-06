import logging

logger = logging.getLogger(__name__)


def configure_system_trust_store() -> None:
    try:
        import truststore
    except ImportError:
        return

    try:
        truststore.inject_into_ssl()
    except Exception as exc:
        logger.warning("tls.truststore_unavailable error=%s", exc)

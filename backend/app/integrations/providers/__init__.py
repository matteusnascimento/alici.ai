"""Registry de providers — retorna instância correta por channel_type."""
from __future__ import annotations

from app.integrations.providers.api import APIProvider
from app.integrations.providers.base import BaseProvider
from app.integrations.providers.email import EmailProvider
from app.integrations.providers.instagram import InstagramProvider
from app.integrations.providers.webhook import WebhookProvider
from app.integrations.providers.website_chat import WebsiteChatProvider
from app.integrations.providers.whatsapp import WhatsAppProvider

VALID_PROVIDERS = frozenset({
    "whatsapp",
    "instagram",
    "website_chat",
    "email",
    "api",
    "webhook",
})

_REGISTRY: dict[str, type[BaseProvider]] = {
    "whatsapp": WhatsAppProvider,
    "instagram": InstagramProvider,
    "website_chat": WebsiteChatProvider,
    "email": EmailProvider,
    "api": APIProvider,
    "webhook": WebhookProvider,
}


def get_provider(channel_type: str) -> BaseProvider:
    cls = _REGISTRY.get(channel_type.lower())
    if cls is None:
        raise ValueError(f"Provider desconhecido: '{channel_type}'. Válidos: {sorted(VALID_PROVIDERS)}")
    return cls()

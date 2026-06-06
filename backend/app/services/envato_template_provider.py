from __future__ import annotations

import logging
import ssl
from typing import Any

import httpx

from app.core.config import settings


logger = logging.getLogger(__name__)


class EnvatoTemplateProviderError(RuntimeError):
    pass


class EnvatoTemplateProvider:
    SEARCH_URL = "https://api.envato.com/v1/discovery/search/search/item"
    DEFAULT_QUERIES = (
        {"site": "graphicriver", "term": "marketing template", "category": "graphics"},
        {"site": "videohive", "term": "social media template", "category": "video"},
        {"site": "themeforest", "term": "landing page template", "category": "site-templates"},
    )

    def __init__(self, api_key: str | None = None, timeout_seconds: float = 8.0):
        self.api_key = (api_key or settings.envato_api_key or "").strip()
        self.timeout_seconds = timeout_seconds

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def search_templates(self, limit: int = 18) -> list[dict[str, Any]]:
        if not self.is_configured:
            return []

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "User-Agent": "AXI-Studio/1.0",
        }

        templates: list[dict[str, Any]] = []
        try:
            with httpx.Client(timeout=self.timeout_seconds, verify=self._ssl_context()) as client:
                for query in self.DEFAULT_QUERIES:
                    response = client.get(self.SEARCH_URL, headers=headers, params=query)
                    if response.status_code in {401, 403}:
                        raise EnvatoTemplateProviderError("ENVATO_API_KEY invalida ou sem permissao para buscar templates.")
                    if response.status_code == 429:
                        retry_after = response.headers.get("Retry-After")
                        detail = f"Envato rate limit atingido{f' (Retry-After: {retry_after}s)' if retry_after else ''}."
                        raise EnvatoTemplateProviderError(detail)
                    if response.status_code >= 400:
                        raise EnvatoTemplateProviderError(f"Envato retornou HTTP {response.status_code} ao buscar templates.")

                    payload = response.json()
                    matches = payload.get("matches") if isinstance(payload, dict) else None
                    if not isinstance(matches, list):
                        continue

                    for item in matches:
                        if isinstance(item, dict):
                            normalized = self._normalize_item(item, query)
                            if normalized:
                                templates.append(normalized)
                        if len(templates) >= limit:
                            return templates
        except httpx.HTTPError as exc:
            logger.warning("envato.templates.http_error type=%s", exc.__class__.__name__)
            raise EnvatoTemplateProviderError("Falha de rede ao buscar templates na Envato.") from exc

        return templates

    def _ssl_context(self) -> ssl.SSLContext:
        try:
            import truststore

            return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        except ImportError:
            pass

        try:
            import certifi

            return ssl.create_default_context(cafile=certifi.where())
        except ImportError:
            return ssl.create_default_context()

    def _normalize_item(self, item: dict[str, Any], query: dict[str, str]) -> dict[str, Any] | None:
        envato_id = item.get("id") or item.get("item_id")
        name = item.get("name") or item.get("title")
        if not envato_id or not name:
            return None

        preview_url = self._extract_preview_url(item)
        tags = item.get("tags") if isinstance(item.get("tags"), list) else []
        category = item.get("classification") or item.get("category") or query["category"]
        style_tag = ", ".join(str(tag) for tag in tags[:3]) if tags else query["site"]

        return {
            "source": "envato",
            "source_id": str(envato_id),
            "name": str(name)[:180],
            "category": str(category)[:60],
            "style_tag": style_tag[:120],
            "preview_url": preview_url,
            "template_data": {
                "source": "envato",
                "source_id": str(envato_id),
                "source_site": query["site"],
                "source_url": item.get("url"),
                "classification": item.get("classification"),
                "layout": "envato-template",
                "ratio": self._infer_ratio(query["site"], str(category)),
                "tags": tags,
                "author": item.get("author_username") or item.get("author"),
                "price_cents": item.get("price_cents"),
            },
        }

    def _extract_preview_url(self, item: dict[str, Any]) -> str | None:
        for key in ("thumbnail_url", "preview_url", "image"):
            value = item.get(key)
            if isinstance(value, str) and value:
                return value[:500]

        previews = item.get("previews")
        if isinstance(previews, dict):
            for value in previews.values():
                if isinstance(value, dict):
                    for nested_key in ("url", "src", "image_url", "icon_url"):
                        nested_value = value.get(nested_key)
                        if isinstance(nested_value, str) and nested_value:
                            return nested_value[:500]
                if isinstance(value, str) and value:
                    return value[:500]
        if isinstance(previews, list):
            for value in previews:
                if isinstance(value, dict):
                    nested_value = value.get("url") or value.get("src")
                    if isinstance(nested_value, str) and nested_value:
                        return nested_value[:500]

        return None

    def _infer_ratio(self, site: str, category: str) -> str:
        lowered = f"{site} {category}".lower()
        if "video" in lowered:
            return "9:16"
        if "site" in lowered or "theme" in lowered:
            return "16:9"
        return "1:1"

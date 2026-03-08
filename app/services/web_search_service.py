"""Web search fallback service for current-events and unknown topics."""

from urllib.parse import quote

import requests

from app.core.config import settings


class WebSearchService:
    """Performs lightweight web lookups using DuckDuckGo Instant Answer API."""

    def search(self, query: str) -> dict:
        text = (query or "").strip()
        if not text:
            return {"found": False, "answer": None, "source": "duckduckgo"}

        url = f"https://api.duckduckgo.com/?q={quote(text)}&format=json&no_redirect=1"
        response = requests.get(url, timeout=settings.web_search_timeout_seconds)
        response.raise_for_status()
        data = response.json()

        abstract = (data.get("AbstractText") or "").strip()
        if abstract:
            source_url = data.get("AbstractURL") or data.get("Heading") or "DuckDuckGo"
            return {
                "found": True,
                "answer": abstract,
                "source": source_url,
                "confidence": 0.8,
            }

        related = data.get("RelatedTopics") or []
        for item in related:
            if isinstance(item, dict) and item.get("Text"):
                first = item.get("Text", "").strip()
                if first:
                    return {
                        "found": True,
                        "answer": first,
                        "source": item.get("FirstURL") or "DuckDuckGo",
                        "confidence": 0.6,
                    }

        return {"found": False, "answer": None, "source": "duckduckgo", "confidence": 0.0}

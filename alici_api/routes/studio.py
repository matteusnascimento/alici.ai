"""Axi Studio routes backed by real external services.

This router only returns media from configured external providers. If a provider
is not configured, the endpoint returns a clear 503 so the UI can explain what
is missing instead of inventing assets.
"""

from __future__ import annotations

from typing import Any, Literal

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from alici_api.config import get_settings
from alici_api.dependencies import get_current_user
from database import listar_studio_templates

router = APIRouter(prefix="/studio", tags=["studio"])


class StudioWebImage(BaseModel):
    id: str
    provider: Literal["pexels", "unsplash"]
    title: str
    image_url: str
    thumb_url: str
    author_name: str | None = None
    author_url: str | None = None
    source_url: str


class StudioTemplateCatalogItem(BaseModel):
    id: str
    name: str
    category: str
    type: Literal["photo", "video", "social", "ad"]
    thumbnail_url: str | None = None
    preview_video_url: str | None = None
    premium: bool = False
    template_json: dict[str, Any]


def _secret_value(value) -> str | None:
    if not value:
        return None
    return value.get_secret_value() if hasattr(value, "get_secret_value") else str(value)


@router.get("/templates/catalog", response_model=list[StudioTemplateCatalogItem])
async def list_template_catalog(
    category: str | None = Query(default=None, max_length=80),
    type: Literal["photo", "video", "social", "ad"] | None = Query(default=None),
    current_user=Depends(get_current_user),
):
    del current_user
    try:
        return listar_studio_templates(category=category, template_type=type)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Catalogo de templates indisponivel. Execute alembic upgrade head e cadastre templates reais no banco.",
        ) from exc


def _pexels_photo_to_image(photo: dict[str, Any]) -> StudioWebImage:
    src = photo.get("src") or {}
    photographer = photo.get("photographer")
    return StudioWebImage(
        id=f"pexels:{photo.get('id')}",
        provider="pexels",
        title=photo.get("alt") or "Imagem Pexels",
        image_url=src.get("large2x") or src.get("large") or src.get("original"),
        thumb_url=src.get("medium") or src.get("small") or src.get("tiny"),
        author_name=photographer,
        author_url=photo.get("photographer_url"),
        source_url=photo.get("url") or "https://www.pexels.com",
    )


def _unsplash_photo_to_image(photo: dict[str, Any]) -> StudioWebImage:
    urls = photo.get("urls") or {}
    user = photo.get("user") or {}
    links = photo.get("links") or {}
    return StudioWebImage(
        id=f"unsplash:{photo.get('id')}",
        provider="unsplash",
        title=photo.get("alt_description") or photo.get("description") or "Imagem Unsplash",
        image_url=urls.get("regular") or urls.get("full") or urls.get("raw"),
        thumb_url=urls.get("small") or urls.get("thumb") or urls.get("regular"),
        author_name=user.get("name"),
        author_url=(user.get("links") or {}).get("html"),
        source_url=links.get("html") or "https://unsplash.com",
    )


@router.get("/web-images/search", response_model=list[StudioWebImage])
async def search_web_images(
    query: str = Query(min_length=2, max_length=80),
    limit: int = Query(default=12, ge=1, le=24),
    current_user=Depends(get_current_user),
):
    del current_user
    settings = get_settings()
    pexels_key = _secret_value(settings.pexels_api_key)
    unsplash_key = _secret_value(settings.unsplash_access_key)

    if not pexels_key and not unsplash_key:
        raise HTTPException(
            status_code=503,
            detail=(
                "Busca de imagens reais indisponivel. Configure PEXELS_API_KEY "
                "ou UNSPLASH_ACCESS_KEY no backend."
            ),
        )

    timeout = httpx.Timeout(8.0, connect=3.0)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            if pexels_key:
                response = await client.get(
                    "https://api.pexels.com/v1/search",
                    params={"query": query, "per_page": limit, "orientation": "landscape", "locale": "pt-BR"},
                    headers={"Authorization": pexels_key},
                )
                response.raise_for_status()
                return [_pexels_photo_to_image(photo) for photo in response.json().get("photos", []) if photo.get("src")]

            response = await client.get(
                "https://api.unsplash.com/search/photos",
                params={"query": query, "per_page": limit, "content_filter": "high"},
                headers={"Authorization": f"Client-ID {unsplash_key}"},
            )
            response.raise_for_status()
            return [_unsplash_photo_to_image(photo) for photo in response.json().get("results", []) if photo.get("urls")]
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Provider de imagem recusou a requisicao ({exc.response.status_code}). Verifique a chave configurada.",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Provider de imagem indisponivel no momento.") from exc

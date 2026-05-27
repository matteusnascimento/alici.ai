from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException

from alici_api.config import get_settings
from database import (
    atualizar_conexao_social,
    buscar_conexao_social_por_canal,
    criar_conexao_social,
    desconectar_conexoes_sociais_por_provider,
    listar_conexoes_sociais,
    salvar_mensagem_omnichannel,
    upsert_business_contact_from_channel,
)
from logger import get_logger

logger = get_logger("omnichannel")


SUPPORTED_PROVIDERS = {
    "whatsapp": {
        "title": "WhatsApp",
        "description": "Mensagens via WhatsApp Business API.",
        "helper_text": "Use o Phone Number ID da Meta Business API e o access token da conta.",
    },
    "instagram": {
        "title": "Instagram",
        "description": "DMs do Instagram Messaging.",
        "helper_text": "Use o Instagram Business Account ID ligado a uma pagina Meta.",
    },
    "messenger": {
        "title": "Facebook Messenger",
        "description": "Mensagens do Facebook Messenger.",
        "helper_text": "Use o Page ID da pagina Facebook e o token de pagina.",
    },
    "tiktok": {
        "title": "TikTok",
        "description": "Mensagens e eventos via TikTok Business API.",
        "helper_text": "Use o Business Account ID e credenciais TikTok configuradas.",
    },
    "google_ads": {
        "title": "Google Ads",
        "description": "Métricas de campanhas, cliques e conversões do Google Ads.",
        "helper_text": "Conecte com OAuth Google para a AXI importar dados de marketing autorizados.",
    },
}

PROVIDER_ALIASES = {
    "facebook": "messenger",
    "facebook_messenger": "messenger",
}


def normalize_provider(provider: str) -> str:
    key = (provider or "").strip().lower()
    key = PROVIDER_ALIASES.get(key, key)
    if key not in SUPPORTED_PROVIDERS:
        raise ValueError(f"Canal nao suportado: {provider}")
    return key


def _public_connection(connection: dict[str, Any]) -> dict[str, Any]:
    safe = dict(connection)
    safe.pop("access_token", None)
    return safe


class OmnichannelService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def list_providers(self, user_id: int) -> list[dict[str, Any]]:
        accounts = listar_conexoes_sociais(user_id)
        result = []
        for provider, meta in SUPPORTED_PROVIDERS.items():
            provider_accounts = [a for a in accounts if a["provider"] == provider]
            active = [a for a in provider_accounts if a.get("enabled") and a.get("status") in {"connected", "active"}]
            status = "connected" if active else "disconnected"
            result.append(
                {
                    "provider": provider,
                    "title": meta["title"],
                    "description": meta["description"],
                    "status": status,
                    "helper_text": meta["helper_text"],
                    "connected_accounts": len(active),
                    "active_bindings": len(active),
                    "supports_activation": True,
                }
            )
        return result

    def list_accounts(self, user_id: int) -> list[dict[str, Any]]:
        return [_public_connection(account) for account in listar_conexoes_sociais(user_id)]

    def connect(
        self,
        user_id: int,
        provider: str,
        external_account_id: str,
        external_account_name: str | None = None,
        access_token: str | None = None,
        enabled: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        provider = normalize_provider(provider)
        connection = criar_conexao_social(
            user_id=user_id,
            provider=provider,
            external_account_id=external_account_id.strip(),
            external_account_name=(external_account_name or "").strip() or None,
            access_token=access_token,
            enabled=enabled,
            metadata=metadata or {},
        )
        logger.info("social_connection_created", extra={"user_id": user_id, "provider": provider})
        return _public_connection(connection)

    def _state_secret(self) -> bytes:
        secret = self.settings.secret_key.get_secret_value()
        return secret.encode("utf-8")

    def _sign_state(self, payload: dict[str, Any]) -> str:
        raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        body = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
        signature = hmac.new(self._state_secret(), body.encode("ascii"), hashlib.sha256).hexdigest()
        return f"{body}.{signature}"

    def _verify_state(self, state: str, provider: str) -> dict[str, Any]:
        try:
            body, signature = state.split(".", 1)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Estado OAuth invalido") from exc

        expected = hmac.new(self._state_secret(), body.encode("ascii"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise HTTPException(status_code=400, detail="Estado OAuth invalido")

        padded = body + ("=" * (-len(body) % 4))
        payload = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8"))
        if payload.get("provider") != provider:
            raise HTTPException(status_code=400, detail="Provider OAuth invalido")
        if int(payload.get("exp") or 0) < int(time.time()):
            raise HTTPException(status_code=400, detail="Sessao OAuth expirada")
        return payload

    def oauth_redirect_uri(self, provider: str) -> str:
        provider = normalize_provider(provider)
        if provider == "google_ads" and self.settings.google_ads_oauth_redirect_uri:
            return self.settings.google_ads_oauth_redirect_uri
        return f"{self.settings.public_app_url.rstrip('/')}/integrations/oauth/{provider}/callback"

    def oauth_start_url(self, user_id: int, provider: str) -> dict[str, Any]:
        provider = normalize_provider(provider)
        state = self._sign_state({"user_id": user_id, "provider": provider, "exp": int(time.time()) + 900})

        if provider in {"whatsapp", "instagram", "messenger"}:
            if not self.settings.meta_app_id:
                raise HTTPException(status_code=503, detail="META_APP_ID nao configurado")
            scopes = [
                "pages_show_list",
                "pages_read_engagement",
                "pages_messaging",
                "instagram_basic",
                "instagram_manage_messages",
                "business_management",
                "whatsapp_business_management",
                "whatsapp_business_messaging",
            ]
            params = {
                "client_id": self.settings.meta_app_id,
                "redirect_uri": self.oauth_redirect_uri(provider),
                "state": state,
                "response_type": "code",
                "scope": ",".join(scopes),
            }
            return {
                "provider": provider,
                "authorization_url": f"https://www.facebook.com/{self.settings.meta_graph_api_version}/dialog/oauth?{urlencode(params)}",
            }

        if provider == "tiktok":
            if not self.settings.tiktok_client_key:
                raise HTTPException(status_code=503, detail="TIKTOK_CLIENT_KEY nao configurado")
            params = {
                "app_id": self.settings.tiktok_client_key,
                "state": state,
                "redirect_uri": self.oauth_redirect_uri(provider),
            }
            return {
                "provider": provider,
                "authorization_url": f"https://business-api.tiktok.com/portal/auth?{urlencode(params)}",
            }

        if provider == "google_ads":
            if not self.settings.google_oauth_client_id:
                raise HTTPException(status_code=503, detail="GOOGLE_OAUTH_CLIENT_ID nao configurado")
            params = {
                "client_id": self.settings.google_oauth_client_id,
                "redirect_uri": self.oauth_redirect_uri(provider),
                "state": state,
                "response_type": "code",
                "access_type": "offline",
                "prompt": "consent",
                "scope": " ".join(
                    [
                        "openid",
                        "email",
                        "profile",
                        "https://www.googleapis.com/auth/adwords",
                    ]
                ),
            }
            return {
                "provider": provider,
                "authorization_url": f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}",
            }

        raise HTTPException(status_code=400, detail="Provider sem OAuth configurado")

    async def handle_oauth_callback(self, provider: str, code: str, state: str) -> list[dict[str, Any]]:
        provider = normalize_provider(provider)
        payload = self._verify_state(state, provider)
        user_id = int(payload["user_id"])
        if provider in {"whatsapp", "instagram", "messenger"}:
            return await self._connect_meta_accounts(user_id, provider, code)
        if provider == "tiktok":
            raise HTTPException(status_code=501, detail="OAuth TikTok preparado; troca de token depende da app Business aprovada")
        if provider == "google_ads":
            return await self._connect_google_ads(user_id, provider, code)
        raise HTTPException(status_code=400, detail="Provider sem callback OAuth")

    async def _connect_google_ads(self, user_id: int, provider: str, code: str) -> list[dict[str, Any]]:
        if not self.settings.google_oauth_client_id or not self.settings.google_oauth_client_secret:
            raise HTTPException(status_code=503, detail="Credenciais Google OAuth nao configuradas")

        redirect_uri = self.oauth_redirect_uri(provider)
        async with httpx.AsyncClient(timeout=20) as client:
            token_resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": self.settings.google_oauth_client_id,
                    "client_secret": self.settings.google_oauth_client_secret.get_secret_value(),
                    "redirect_uri": redirect_uri,
                    "code": code,
                    "grant_type": "authorization_code",
                },
            )
            if token_resp.status_code >= 400:
                raise HTTPException(status_code=400, detail="Falha ao autorizar Google Ads")
            token_data = token_resp.json()
            access_token = token_data.get("access_token")
            if not access_token:
                raise HTTPException(status_code=400, detail="Google nao retornou access token")

            userinfo_resp = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            profile = userinfo_resp.json() if userinfo_resp.status_code < 400 else {}
            account_id = profile.get("sub") or profile.get("email") or f"google-{user_id}"
            account_name = profile.get("email") or profile.get("name") or "Google Ads"
            connection = self.connect(
                user_id,
                "google_ads",
                str(account_id),
                external_account_name=account_name,
                access_token=access_token,
                metadata={
                    "source": "google_oauth",
                    "email": profile.get("email"),
                    "refresh_token_available": bool(token_data.get("refresh_token")),
                    "scope": token_data.get("scope"),
                },
            )
            return [connection]

    async def _connect_meta_accounts(self, user_id: int, provider: str, code: str) -> list[dict[str, Any]]:
        if not self.settings.meta_app_id or not self.settings.meta_app_secret:
            raise HTTPException(status_code=503, detail="Credenciais Meta nao configuradas")

        version = self.settings.meta_graph_api_version
        redirect_uri = self.oauth_redirect_uri(provider)
        app_secret = self.settings.meta_app_secret.get_secret_value()
        async with httpx.AsyncClient(timeout=20) as client:
            token_resp = await client.get(
                f"https://graph.facebook.com/{version}/oauth/access_token",
                params={
                    "client_id": self.settings.meta_app_id,
                    "client_secret": app_secret,
                    "redirect_uri": redirect_uri,
                    "code": code,
                },
            )
            if token_resp.status_code >= 400:
                raise HTTPException(status_code=400, detail="Falha ao autorizar conta Meta")
            user_token = token_resp.json().get("access_token")
            if not user_token:
                raise HTTPException(status_code=400, detail="Meta nao retornou access token")

            saved: list[dict[str, Any]] = []
            if provider in {"instagram", "messenger"}:
                pages_resp = await client.get(
                    f"https://graph.facebook.com/{version}/me/accounts",
                    params={
                        "access_token": user_token,
                        "fields": "id,name,access_token,instagram_business_account{id,username,name}",
                    },
                )
                pages_resp.raise_for_status()
                for page in pages_resp.json().get("data", []):
                    page_token = page.get("access_token") or user_token
                    if provider == "messenger":
                        saved.append(
                            self.connect(
                                user_id,
                                "messenger",
                                str(page["id"]),
                                external_account_name=page.get("name"),
                                access_token=page_token,
                                metadata={"source": "meta_oauth", "page_id": page.get("id")},
                            )
                        )
                    ig = page.get("instagram_business_account")
                    if provider == "instagram" and ig and ig.get("id"):
                        saved.append(
                            self.connect(
                                user_id,
                                "instagram",
                                str(ig["id"]),
                                external_account_name=ig.get("username") or ig.get("name") or page.get("name"),
                                access_token=page_token,
                                metadata={"source": "meta_oauth", "page_id": page.get("id")},
                            )
                        )

            if provider == "whatsapp":
                businesses_resp = await client.get(
                    f"https://graph.facebook.com/{version}/me/businesses",
                    params={"access_token": user_token, "fields": "id,name"},
                )
                businesses_resp.raise_for_status()
                for business in businesses_resp.json().get("data", []):
                    wabas_resp = await client.get(
                        f"https://graph.facebook.com/{version}/{business['id']}/owned_whatsapp_business_accounts",
                        params={"access_token": user_token, "fields": "id,name,phone_numbers{id,display_phone_number,verified_name}"},
                    )
                    if wabas_resp.status_code >= 400:
                        continue
                    for waba in wabas_resp.json().get("data", []):
                        numbers = ((waba.get("phone_numbers") or {}).get("data") or [])
                        for number in numbers:
                            saved.append(
                                self.connect(
                                    user_id,
                                    "whatsapp",
                                    str(number["id"]),
                                    external_account_name=number.get("verified_name") or number.get("display_phone_number") or waba.get("name"),
                                    access_token=user_token,
                                    metadata={
                                        "source": "meta_oauth",
                                        "business_id": business.get("id"),
                                        "business_name": business.get("name"),
                                        "waba_id": waba.get("id"),
                                        "phone": number.get("display_phone_number"),
                                    },
                                )
                            )

            if not saved:
                raise HTTPException(status_code=404, detail="Nenhuma conta compativel encontrada na autorizacao Meta")
            return saved

    def disconnect_provider(self, user_id: int, provider: str) -> dict[str, Any]:
        provider = normalize_provider(provider)
        result = desconectar_conexoes_sociais_por_provider(user_id, provider)
        logger.info("social_provider_disconnected", extra={"user_id": user_id, "provider": provider, "updated": result["updated"]})
        return self.get_provider_status(user_id, provider)

    def set_enabled(self, user_id: int, connection_id: int, enabled: bool) -> dict[str, Any]:
        status = "connected" if enabled else "disabled"
        connection = atualizar_conexao_social(user_id, connection_id, enabled=enabled, status=status)
        if not connection:
            raise ValueError("Conexao nao encontrada")
        return _public_connection(connection)

    def get_provider_status(self, user_id: int, provider: str) -> dict[str, Any]:
        provider = normalize_provider(provider)
        providers = self.list_providers(user_id)
        return next(item for item in providers if item["provider"] == provider)

    def ingest_inbound(
        self,
        provider: str,
        external_account_id: str,
        external_contact_id: str,
        text: str,
        contact_name: str | None = None,
        external_message_id: str | None = None,
        raw_payload: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        provider = normalize_provider(provider)
        connection = buscar_conexao_social_por_canal(provider, external_account_id)
        if not connection:
            logger.warning("social_message_ignored_no_connection", extra={"provider": provider, "account_id": external_account_id})
            return None

        result = salvar_mensagem_omnichannel(
            connection=connection,
            external_contact_id=external_contact_id,
            content=text,
            direction="inbound",
            contact_name=contact_name,
            external_message_id=external_message_id,
            raw_payload=raw_payload or {},
        )
        contact = upsert_business_contact_from_channel(
            user_id=connection["user_id"],
            provider=provider,
            external_contact_id=external_contact_id,
            contact_name=contact_name,
        )
        result["business_contact_id"] = contact.get("id") if contact else None
        logger.info(
            "social_message_ingested",
            extra={"user_id": connection["user_id"], "provider": provider, "conversation_id": result["conversation_id"]},
        )
        return result

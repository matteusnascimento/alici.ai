from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.secrets import seal_secret
from app.integrations.channel_adapters import ChannelAdapters
from app.models.agent import Agent
from app.models.agent_channel import AgentChannel
from app.models.agent_channel_binding import AgentChannelBinding
from app.models.channel_message import ChannelMessage
from app.models.channel_endpoint import ChannelEndpoint
from app.models.channel_webhook_event import ChannelWebhookEvent
from app.models.integration_account import IntegrationAccount
from app.models.user import User
from app.services.agent_runtime_service import AgentRuntimeError, AgentRuntimeService

ACTIVE_PROVIDERS = frozenset({
    "whatsapp",
    "instagram",
    "website_chat",
    "meta_ads",
    "google_ads",
    "google_analytics",
    "omnibees",
    "pms",
    "stripe",
    "api",
    "email",
    "webhook",
})
COMING_SOON_PROVIDERS = frozenset()
SUPPORTED_PROVIDERS = ACTIVE_PROVIDERS | COMING_SOON_PROVIDERS

PROVIDER_CATALOG: dict[str, dict[str, str | bool]] = {
    "whatsapp": {
        "title": "WhatsApp",
        "description": "Atendimento direto pelo WhatsApp Business.",
        "helper": "Base real pronta para vinculo com o agente. A ativacao oficial Meta ainda depende da autenticacao externa.",
        "supports_activation": True,
    },
    "instagram": {
        "title": "Instagram",
        "description": "Resposta automatica para mensagens do Instagram.",
        "helper": "Base real pronta para vinculo com o agente. A ativacao oficial Meta ainda depende da autenticacao externa.",
        "supports_activation": True,
    },
    "website_chat": {
        "title": "Chat do site",
        "description": "Widget embutido para atender visitantes no seu site.",
        "helper": "Nao exige credenciais externas. Depois de vincular, instale o script do widget no site.",
        "supports_activation": True,
    },
    "meta_ads": {
        "title": "Meta Ads",
        "description": "Investimento, campanhas e desempenho de anuncios Meta.",
        "helper": "Conector cadastravel. Sincronizacao real depende de token Meta Ads e conta de anuncios.",
        "supports_activation": True,
    },
    "google_ads": {
        "title": "Google Ads",
        "description": "Campanhas, custo, conversoes e ROAS do Google Ads.",
        "helper": "Conector cadastravel. Sincronizacao real depende de OAuth Google Ads e customer id.",
        "supports_activation": True,
    },
    "google_analytics": {
        "title": "Google Analytics",
        "description": "Origem de trafego, eventos e conversoes do site.",
        "helper": "Conector cadastravel. Sincronizacao real depende de OAuth Google e propriedade GA4.",
        "supports_activation": True,
    },
    "omnibees": {
        "title": "OmniBees",
        "description": "Reservas e disponibilidade para hotelaria.",
        "helper": "Conector cadastravel. Captura real depende de endpoint e credenciais OmniBees.",
        "supports_activation": True,
    },
    "pms": {
        "title": "PMS / Sistema hoteleiro",
        "description": "Reservas, hospedes e disponibilidade vindos do sistema hoteleiro.",
        "helper": "Informe endpoint e credenciais de API do PMS. O AXI so salva depois de testar a conexao.",
        "supports_activation": True,
    },
    "stripe": {
        "title": "Stripe",
        "description": "Billing, assinaturas e eventos financeiros da plataforma.",
        "helper": "Billing Stripe existente permanece no modulo de cobranca; aqui fica apenas o status operacional.",
        "supports_activation": True,
    },
    "api": {
        "title": "API externa",
        "description": "Endpoint HTTP para integrar sistemas internos ou produtos proprios.",
        "helper": "Informe a URL publica da API e, se necessario, um token Bearer para chamadas autenticadas.",
        "supports_activation": True,
    },
    "email": {
        "title": "Email SMTP",
        "description": "Conecte uma caixa SMTP para envio de emails operacionais.",
        "helper": "Informe host, porta, usuario e senha SMTP. TLS e SSL podem ser configurados no painel.",
        "supports_activation": True,
    },
    "webhook": {
        "title": "Webhook",
        "description": "Envie eventos do agente para uma URL externa.",
        "helper": "Informe uma URL publica para receber eventos. Opcionalmente adicione um segredo de assinatura.",
        "supports_activation": True,
    },
}


class ChannelIntegrationService:
    def __init__(self, db: Session):
        self.db = db

    def _agent_or_404(self, user: User, agent_id: int) -> Agent:
        agent = self.db.query(Agent).filter(Agent.id == agent_id, Agent.user_id == user.id).first()
        if not agent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
        return agent

    def _validate_provider(self, provider: str, allow_coming_soon: bool = False) -> str:
        normalized = provider.strip().lower()
        if normalized in ACTIVE_PROVIDERS:
            return normalized
        if allow_coming_soon and normalized in COMING_SOON_PROVIDERS:
            return normalized
        if normalized in COMING_SOON_PROVIDERS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Este provider ainda esta marcado como coming_soon e nao pode ser conectado nesta etapa.",
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provider invalido")

    def _dump_json(self, value: dict[str, Any] | None) -> str:
        return json.dumps(value or {}, ensure_ascii=True)

    def _load_json(self, value: str | None) -> dict[str, Any]:
        if not value:
            return {}
        try:
            data = json.loads(value)
        except json.JSONDecodeError:
            return {}
        return data if isinstance(data, dict) else {}

    def _provider_config(self, payload: dict[str, Any]) -> dict[str, Any]:
        metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
        config = metadata.get("config") if isinstance(metadata.get("config"), dict) else {}
        return config

    def _has_required_config(self, provider: str, payload: dict[str, Any]) -> bool:
        config = self._provider_config(payload)
        if provider == "website_chat":
            return True
        if provider == "whatsapp":
            return bool(payload.get("access_token") and payload.get("external_account_id"))
        if provider == "instagram":
            return bool(payload.get("access_token") and payload.get("external_account_id"))
        if provider == "meta_ads":
            return bool(payload.get("access_token") and (payload.get("external_account_id") or config.get("ad_account_id")))
        if provider in {"google_ads", "google_analytics"}:
            return bool(payload.get("access_token") and (payload.get("external_account_id") or config.get("customer_id")))
        if provider in {"omnibees", "pms"}:
            return bool(config.get("endpoint") and (payload.get("access_token") or config.get("api_key")))
        if provider == "stripe":
            return bool(payload.get("access_token") or config.get("webhook_configured") or config.get("secret_key_configured"))
        if provider == "api":
            return bool(config.get("api_url"))
        if provider == "webhook":
            return bool(config.get("webhook_url"))
        if provider == "email":
            return bool(config.get("smtp_host") and config.get("smtp_port") and config.get("smtp_user") and config.get("smtp_password"))
        return False

    def _derive_account_status(self, provider: str, payload: dict[str, Any]) -> str:
        metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
        token_invalid = bool(metadata.get("token_invalid"))
        runtime_error = bool(metadata.get("runtime_error"))
        webhook_verified = bool(metadata.get("webhook_verified"))

        if provider in COMING_SOON_PROVIDERS:
            return "coming_soon"
        if token_invalid:
            return "auth_required"
        if runtime_error:
            return "error"
        if provider == "website_chat":
            return "connected"
        if provider not in {"whatsapp", "instagram", "meta_ads", "google_ads", "google_analytics"}:
            return "pending_setup" if self._has_required_config(provider, payload) else "auth_required"
        if not payload.get("access_token"):
            return "auth_required"
        if not payload.get("external_account_id") and not payload.get("external_account_name"):
            return "error"
        if webhook_verified:
            return "connected"
        return "pending_setup"

    def _derive_binding_status(self, provider: str, account: IntegrationAccount, endpoint: ChannelEndpoint) -> str:
        if provider in COMING_SOON_PROVIDERS:
            return "coming_soon"
        if not endpoint.is_active:
            return "disconnected"
        if account.status == "error":
            return "error"
        if account.status == "auth_required":
            return "auth_required"
        if provider == "website_chat" and account.status == "connected":
            return "connected"
        if provider not in {"whatsapp", "instagram", "meta_ads", "google_ads", "google_analytics"}:
            return "pending_setup" if account.status == "pending_setup" else account.status
        if endpoint.webhook_status == "active" and account.status == "connected":
            return "connected"
        return "pending_setup"

    def _serialize_account(self, account: IntegrationAccount) -> dict[str, Any]:
        return {
            "id": account.id,
            "provider": account.provider,
            "external_account_id": account.external_account_id,
            "external_account_name": account.external_account_name,
            "status": account.status,
            "metadata": self._load_json(account.metadata_json),
            "created_at": account.created_at,
            "updated_at": account.updated_at,
        }

    def _provider_public_details(self, account_rows: list[IntegrationAccount]) -> dict[str, Any]:
        selected = next((item for item in account_rows if item.status == "connected"), None)
        selected = selected or (account_rows[0] if account_rows else None)
        if not selected:
            return {
                "account_name": None,
                "last_sync_at": None,
                "last_error": None,
                "data_received": None,
                "scopes": [],
            }

        metadata = self._load_json(selected.metadata_json)
        scopes = metadata.get("scopes") or metadata.get("granted_scopes") or []
        if isinstance(scopes, str):
            scopes = [item.strip() for item in scopes.split(",") if item.strip()]
        if not isinstance(scopes, list):
            scopes = []
        return {
            "account_name": selected.external_account_name,
            "last_sync_at": metadata.get("last_sync_at"),
            "last_error": metadata.get("last_error"),
            "data_received": metadata.get("data_received"),
            "scopes": [str(item) for item in scopes],
        }

    def _upsert_integration_account(self, user: User, provider: str, payload: dict[str, Any]) -> IntegrationAccount:
        external_account_id = payload.get("external_account_id")
        external_account_name = payload.get("external_account_name")

        query = self.db.query(IntegrationAccount).filter(
            IntegrationAccount.user_id == user.id,
            IntegrationAccount.provider == provider,
        )
        if external_account_id:
            query = query.filter(IntegrationAccount.external_account_id == str(external_account_id))
        elif external_account_name:
            query = query.filter(IntegrationAccount.external_account_name == str(external_account_name))

        account = query.first()
        if not account:
            account = IntegrationAccount(user_id=user.id, provider=provider)
            self.db.add(account)

        account.external_account_id = str(external_account_id) if external_account_id else account.external_account_id
        account.external_account_name = (
            str(external_account_name) if external_account_name else account.external_account_name or PROVIDER_CATALOG[provider]["title"]
        )
        if payload.get("access_token"):
            account.access_token_encrypted = seal_secret(str(payload["access_token"]))
        if payload.get("refresh_token"):
            account.refresh_token_encrypted = seal_secret(str(payload["refresh_token"]))
        account.metadata_json = self._dump_json(payload.get("metadata") or {})
        account.status = self._derive_account_status(provider, payload)
        self.db.flush()
        return account

    def upsert_connected_account(self, user: User, provider: str, payload: dict[str, Any]) -> IntegrationAccount:
        normalized = self._validate_provider(provider)
        metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
        metadata["webhook_verified"] = True
        payload["metadata"] = metadata
        account = self._upsert_integration_account(user, normalized, payload)
        self.db.commit()
        self.db.refresh(account)
        return account

    def _upsert_channel_endpoint(self, account: IntegrationAccount, provider: str, payload: dict[str, Any]) -> ChannelEndpoint:
        external_channel_id = payload.get("external_channel_id")
        channel_name = payload.get("channel_name") or payload.get("phone_number_or_handle") or account.external_account_name or PROVIDER_CATALOG[provider]["title"]

        query = self.db.query(ChannelEndpoint).filter(
            ChannelEndpoint.integration_account_id == account.id,
            ChannelEndpoint.provider == provider,
        )
        if external_channel_id:
            query = query.filter(ChannelEndpoint.external_channel_id == str(external_channel_id))
        else:
            query = query.filter(ChannelEndpoint.channel_name == str(channel_name))

        endpoint = query.first()
        if not endpoint:
            endpoint = ChannelEndpoint(integration_account_id=account.id, provider=provider, channel_name=str(channel_name))
            self.db.add(endpoint)

        endpoint.external_channel_id = str(external_channel_id) if external_channel_id else endpoint.external_channel_id
        endpoint.channel_name = str(channel_name)
        endpoint.phone_number_or_handle = (
            str(payload.get("phone_number_or_handle")) if payload.get("phone_number_or_handle") else endpoint.phone_number_or_handle
        )
        if provider == "website_chat":
            endpoint.webhook_status = "active"
        elif provider in ACTIVE_PROVIDERS:
            endpoint.webhook_status = "pending_setup"
        else:
            endpoint.webhook_status = "coming_soon"
        endpoint.is_active = True
        self.db.flush()
        return endpoint

    def _legacy_channel_id(self, endpoint: ChannelEndpoint, provider: str) -> str:
        return endpoint.external_channel_id or endpoint.phone_number_or_handle or f"{provider}:{endpoint.id}"

    def _sync_legacy_agent_channel(
        self,
        user: User,
        agent_id: int,
        binding: AgentChannelBinding,
        endpoint: ChannelEndpoint,
        account: IntegrationAccount,
    ) -> AgentChannel:
        legacy_channel_id = self._legacy_channel_id(endpoint, binding.provider)
        legacy = (
            self.db.query(AgentChannel)
            .filter(
                AgentChannel.user_id == user.id,
                AgentChannel.agent_id == agent_id,
                AgentChannel.channel_type == binding.provider,
                AgentChannel.channel_id == legacy_channel_id,
            )
            .first()
        )
        if not legacy:
            legacy = AgentChannel(
                user_id=user.id,
                agent_id=agent_id,
                channel_type=binding.provider,
                channel_id=legacy_channel_id,
            )
            self.db.add(legacy)

        legacy.provider_name = binding.provider
        legacy.external_account_id = account.external_account_id
        legacy.enabled = binding.is_active
        legacy.status = binding.status
        legacy.webhook_url = None
        legacy.last_sync_at = binding.updated_at
        legacy.last_error = binding.last_test_message if binding.last_test_status == "error" else None
        legacy.config_json = self._dump_json(
            {
                "integration_account_id": account.id,
                "channel_endpoint_id": endpoint.id,
                "channel_name": endpoint.channel_name,
                "phone_number_or_handle": endpoint.phone_number_or_handle,
                "webhook_status": endpoint.webhook_status,
            }
        )
        self.db.flush()
        return legacy

    def list_integrations(self, user: User) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for provider, catalog in PROVIDER_CATALOG.items():
            status = self.get_provider_status(user, provider)
            rows.append(
                {
                    "provider": provider,
                    "title": str(catalog["title"]),
                    "description": str(catalog["description"]),
                    "status": status["status"],
                    "helper_text": status["helper_text"],
                    "connected_accounts": status["connected_accounts"],
                    "active_bindings": status["active_bindings"],
                    "supports_activation": bool(catalog["supports_activation"]),
                    "account_name": status["account_name"],
                    "last_sync_at": status["last_sync_at"],
                    "last_error": status["last_error"],
                    "data_received": status["data_received"],
                    "scopes": status["scopes"],
                }
            )
        return rows

    def create_integration_account(self, user: User, payload: dict[str, Any]) -> IntegrationAccount:
        provider = self._validate_provider(str(payload.get("provider") or ""))
        if not payload.get("external_account_id") and not payload.get("external_account_name"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Informe pelo menos um identificador da conta para criar a integracao.",
            )
        account = self._upsert_integration_account(user, provider, payload)
        self.db.commit()
        self.db.refresh(account)
        return account

    def list_accounts(self, user: User) -> list[IntegrationAccount]:
        return (
            self.db.query(IntegrationAccount)
            .filter(IntegrationAccount.user_id == user.id)
            .order_by(IntegrationAccount.updated_at.desc(), IntegrationAccount.id.desc())
            .all()
        )

    def get_provider_status(self, user: User, provider: str) -> dict[str, Any]:
        normalized = self._validate_provider(provider, allow_coming_soon=True)
        if normalized in COMING_SOON_PROVIDERS:
            return {
                "provider": normalized,
                "status": "coming_soon",
                "connected_accounts": 0,
                "active_endpoints": 0,
                "active_bindings": 0,
                "helper_text": str(PROVIDER_CATALOG[normalized]["helper"]),
                "account_name": None,
                "last_sync_at": None,
                "last_error": None,
                "data_received": None,
                "scopes": [],
            }

        accounts = self.db.query(IntegrationAccount).filter(
            IntegrationAccount.user_id == user.id,
            IntegrationAccount.provider == normalized,
        )
        account_rows = accounts.all()
        account_ids = [item.id for item in account_rows]
        endpoints = self.db.query(ChannelEndpoint).filter(ChannelEndpoint.integration_account_id.in_(account_ids)).all() if account_ids else []
        endpoint_ids = [item.id for item in endpoints]
        bindings = self.db.query(AgentChannelBinding).filter(AgentChannelBinding.channel_endpoint_id.in_(endpoint_ids)).all() if endpoint_ids else []

        summary_status = "disconnected"
        if any(item.status == "error" for item in account_rows):
            summary_status = "error"
        elif any(item.status == "connected" for item in account_rows):
            summary_status = "connected"
        elif any(item.status == "pending_setup" for item in account_rows):
            summary_status = "pending_setup"
        elif any(item.status == "auth_required" for item in account_rows):
            summary_status = "auth_required"

        details = self._provider_public_details(account_rows)
        return {
            "provider": normalized,
            "status": summary_status,
            "connected_accounts": len(account_rows),
            "active_endpoints": len([item for item in endpoints if item.is_active]),
            "active_bindings": len([item for item in bindings if item.is_active]),
            "helper_text": str(PROVIDER_CATALOG[normalized]["helper"]),
            **details,
        }

    def disconnect_provider(self, user: User, provider: str) -> dict[str, Any]:
        normalized = self._validate_provider(provider, allow_coming_soon=True)
        accounts = self.db.query(IntegrationAccount).filter(
            IntegrationAccount.user_id == user.id,
            IntegrationAccount.provider == normalized,
        ).all()

        for account in accounts:
            account.status = "disconnected"
            for endpoint in account.endpoints:
                endpoint.is_active = False
                endpoint.webhook_status = "pending_setup"
                for binding in endpoint.bindings:
                    binding.is_active = False
                    binding.status = "disconnected"
                    binding.last_test_status = "disconnected"
                    binding.last_test_message = "Canal desvinculado globalmente."
                    agent = binding.agent
                    self._sync_legacy_agent_channel(user, agent.id, binding, endpoint, account).enabled = False

        self.db.commit()
        return self.get_provider_status(user, normalized)

    def test_provider(self, user: User, provider: str) -> dict[str, Any]:
        normalized = self._validate_provider(provider, allow_coming_soon=True)
        status_summary = self.get_provider_status(user, normalized)
        status_value = status_summary["status"]
        if status_value == "connected":
            message = "Integracao cadastrada e ativa no AXI. A disponibilidade externa depende do provider."
        elif status_value == "pending_setup":
            message = "Integracao cadastrada, mas ainda pendente de validacao externa ou webhook."
        elif status_value == "auth_required":
            message = "Credenciais ou permissao externa ausentes para testar esta integracao."
        elif status_value == "disconnected":
            message = "Nenhuma conta real conectada para este provider."
        else:
            message = status_summary["helper_text"]
        return {
            "provider": normalized,
            "status": status_value,
            "message": message,
            "status_code": 200 if status_value == "connected" else 422,
        }

    def sync_provider(self, user: User, provider: str) -> dict[str, Any]:
        normalized = self._validate_provider(provider, allow_coming_soon=True)
        status_summary = self.get_provider_status(user, normalized)
        if status_summary["status"] != "connected":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Sincronizacao indisponivel: conecte e valide o provider antes de sincronizar dados reais.",
            )
        return {
            "provider": normalized,
            "status": "pending_setup",
            "message": "Provider conectado, mas rotina de sincronizacao externa ainda nao foi configurada para execucao automatica.",
            "status_code": 202,
        }

    def list_agent_channels(self, user: User, agent_id: int) -> list[AgentChannelBinding]:
        self._agent_or_404(user, agent_id)
        return (
            self.db.query(AgentChannelBinding)
            .options(
                joinedload(AgentChannelBinding.channel_endpoint).joinedload(ChannelEndpoint.integration_account)
            )
            .filter(AgentChannelBinding.agent_id == agent_id)
            .order_by(AgentChannelBinding.updated_at.desc())
            .all()
        )

    def connect_agent_channel(self, user: User, agent_id: int, payload: dict[str, Any]) -> AgentChannelBinding:
        self._agent_or_404(user, agent_id)
        provider = self._validate_provider(str(payload.get("provider") or payload.get("provider_key") or ""))
        integration_payload = payload.get("integration") or {}
        endpoint_payload = payload.get("endpoint") or {}

        if not integration_payload:
            integration_payload = {
                "external_account_id": payload.get("integration_account_id") or payload.get("account_id") or payload.get("external_account_id"),
                "external_account_name": payload.get("external_account_name"),
                "access_token": payload.get("access_token"),
                "refresh_token": payload.get("refresh_token"),
                "metadata": payload.get("metadata") or {},
            }
        if not endpoint_payload:
            endpoint_payload = {
                "external_channel_id": payload.get("channel_endpoint_id") or payload.get("endpoint_id") or payload.get("external_channel_id"),
                "channel_name": payload.get("channel_name"),
                "phone_number_or_handle": payload.get("phone_number_or_handle"),
            }

        if not integration_payload.get("external_account_name") and not integration_payload.get("external_account_id"):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Informe a conta conectada.")
        if not endpoint_payload.get("channel_name") and not endpoint_payload.get("phone_number_or_handle") and not endpoint_payload.get("external_channel_id"):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Informe o canal a ser vinculado ao agente.")

        account = self._upsert_integration_account(user, provider, integration_payload)
        endpoint = self._upsert_channel_endpoint(account, provider, endpoint_payload)

        binding = (
            self.db.query(AgentChannelBinding)
            .filter(
                AgentChannelBinding.agent_id == agent_id,
                AgentChannelBinding.channel_endpoint_id == endpoint.id,
            )
            .first()
        )
        if not binding:
            binding = AgentChannelBinding(
                agent_id=agent_id,
                channel_endpoint_id=endpoint.id,
                provider=provider,
            )
            self.db.add(binding)

        binding.provider = provider
        binding.is_active = True
        binding.fallback_enabled = bool(payload.get("fallback_enabled", False))
        binding.status = self._derive_binding_status(provider, account, endpoint)
        self.db.flush()
        self._sync_legacy_agent_channel(user, agent_id, binding, endpoint, account)
        self.db.commit()
        self.db.refresh(binding)
        return binding

    def disconnect_agent_channel(self, user: User, agent_id: int, binding_id: int) -> AgentChannelBinding:
        self._agent_or_404(user, agent_id)
        binding = (
            self.db.query(AgentChannelBinding)
            .options(joinedload(AgentChannelBinding.channel_endpoint).joinedload(ChannelEndpoint.integration_account))
            .filter(AgentChannelBinding.agent_id == agent_id, AgentChannelBinding.id == binding_id)
            .first()
        )
        if not binding:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Binding not found")

        binding.is_active = False
        binding.status = "disconnected"
        binding.last_test_status = "disconnected"
        binding.last_test_message = "Canal desconectado do agente."

        endpoint = binding.channel_endpoint
        account = endpoint.integration_account
        self._sync_legacy_agent_channel(user, agent_id, binding, endpoint, account).enabled = False

        active_bindings = [item for item in endpoint.bindings if item.id != binding.id and item.is_active]
        if not active_bindings:
            endpoint.is_active = False
        if not any(item.is_active for item in account.endpoints):
            account.status = "disconnected"

        self.db.commit()
        self.db.refresh(binding)
        return binding

    def test_agent_channel(self, user: User, agent_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        self._agent_or_404(user, agent_id)
        binding_id = int(payload.get("binding_id") or 0)
        binding = (
            self.db.query(AgentChannelBinding)
            .options(joinedload(AgentChannelBinding.channel_endpoint).joinedload(ChannelEndpoint.integration_account))
            .filter(AgentChannelBinding.agent_id == agent_id, AgentChannelBinding.id == binding_id)
            .first()
        )
        if not binding:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Binding not found")

        endpoint = binding.channel_endpoint
        account = endpoint.integration_account
        binding.last_test_at = datetime.now(tz=timezone.utc)
        test_message = self._create_channel_message(
            user_id=user.id,
            agent_id=agent_id,
            provider=binding.provider,
            direction="internal_test",
            external_message_id=None,
            endpoint_id=endpoint.id,
            binding_id=binding.id,
            payload_summary={"source": "channel_internal_test", "message": payload.get("message")},
            status="processing",
            error_message=None,
        )

        if not binding.is_active:
            binding.last_test_status = "error"
            binding.last_test_message = "Canal esta desconectado do agente."
            test_message.status = "error"
            test_message.error_message = binding.last_test_message
            self.db.commit()
            return {
                "success": False,
                "message": binding.last_test_message,
                "provider": binding.provider,
                "channel_binding_id": binding.id,
                "data": {},
            }

        legacy = self._sync_legacy_agent_channel(user, agent_id, binding, endpoint, account)
        text = str(payload.get("message") or "Teste interno de canal AXI")

        try:
            result = AgentRuntimeService.process_inbound_message(
                self.db,
                user_id=user.id,
                channel_type=binding.provider,
                channel_id=legacy.channel_id,
                external_user_id=f"internal-test-{binding.id}",
                external_conversation_id=f"internal-test-{binding.id}",
                text=text,
                metadata={
                    "source": "channel_internal_test",
                    "binding_id": binding.id,
                    "provider": binding.provider,
                },
                test_mode=True,
            )
            binding.last_test_status = "ok"
            binding.last_test_message = (
                "Teste interno concluido com sucesso. O vinculo esta ativo; a autenticacao oficial externa ainda pode estar pendente."
                if binding.status == "pending_setup"
                else "Teste interno concluido com sucesso."
            )
            test_message.status = "ok"
            self.db.commit()
            return {
                "success": True,
                "message": binding.last_test_message,
                "provider": binding.provider,
                "channel_binding_id": binding.id,
                "data": result,
            }
        except AgentRuntimeError as exc:
            binding.last_test_status = "error"
            binding.last_test_message = str(exc)
            test_message.status = "error"
            test_message.error_message = str(exc)
            self.db.commit()
            return {
                "success": False,
                "message": str(exc),
                "provider": binding.provider,
                "channel_binding_id": binding.id,
                "data": {},
            }

    def serialize_binding(self, binding: AgentChannelBinding) -> dict[str, Any]:
        endpoint = binding.channel_endpoint
        account = endpoint.integration_account
        return {
            "binding_id": binding.id,
            "agent_id": binding.agent_id,
            "channel_endpoint_id": endpoint.id,
            "provider": binding.provider,
            "status": binding.status,
            "is_active": binding.is_active,
            "fallback_enabled": binding.fallback_enabled,
            "external_account_id": account.external_account_id,
            "external_account_name": account.external_account_name,
            "channel_name": endpoint.channel_name,
            "external_channel_id": endpoint.external_channel_id,
            "phone_number_or_handle": endpoint.phone_number_or_handle,
            "webhook_status": endpoint.webhook_status,
            "last_test_at": binding.last_test_at,
            "last_test_status": binding.last_test_status,
            "last_test_message": binding.last_test_message,
            "created_at": binding.created_at,
            "updated_at": binding.updated_at,
        }

    def _find_endpoint_for_provider_channel(self, provider: str, channel_id: str) -> ChannelEndpoint | None:
        return (
            self.db.query(ChannelEndpoint)
            .join(IntegrationAccount, IntegrationAccount.id == ChannelEndpoint.integration_account_id)
            .filter(
                ChannelEndpoint.provider == provider,
                ChannelEndpoint.external_channel_id == channel_id,
                ChannelEndpoint.is_active.is_(True),
            )
            .first()
        )

    def record_webhook_event(self, provider: str, payload: dict[str, Any], event_type: str) -> ChannelWebhookEvent:
        normalized = self._validate_provider(provider, allow_coming_soon=True)
        channel_id = str(payload.get("channel_id") or payload.get("phone_number_id") or payload.get("ig_account_id") or "")
        endpoint = self._find_endpoint_for_provider_channel(normalized, channel_id) if channel_id else None
        event = ChannelWebhookEvent(
            channel_endpoint_id=endpoint.id if endpoint else None,
            provider=normalized,
            event_type=event_type,
            payload_json=self._dump_json(payload),
            processed=False,
        )
        self.db.add(event)
        self.db.flush()
        return event

    def _create_channel_message(
        self,
        *,
        user_id: int,
        agent_id: int | None,
        provider: str,
        direction: str,
        external_message_id: str | None,
        endpoint_id: int | None,
        binding_id: int | None,
        payload_summary: dict[str, Any],
        status: str,
        error_message: str | None,
    ) -> ChannelMessage:
        message = ChannelMessage(
            user_id=user_id,
            agent_id=agent_id,
            provider=provider,
            direction=direction,
            external_message_id=external_message_id,
            endpoint_id=endpoint_id,
            binding_id=binding_id,
            payload_summary=self._dump_json(payload_summary),
            status=status,
            error_message=error_message,
        )
        self.db.add(message)
        self.db.flush()
        return message

    def process_meta_webhook(self, provider: str, payload: dict[str, Any]) -> dict[str, Any]:
        normalized = self._validate_provider(provider)
        normalized_payload = (
            ChannelAdapters.normalize_whatsapp(payload)
            if normalized == "whatsapp"
            else ChannelAdapters.normalize_instagram(payload)
        )
        event = self.record_webhook_event(normalized, normalized_payload, event_type=normalized_payload.get("event_type") or "message_received")
        endpoint = self._find_endpoint_for_provider_channel(normalized, normalized_payload["channel_id"])
        if not endpoint:
            event.error_message = "Channel endpoint not found"
            self.db.commit()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel endpoint not found")

        endpoint.webhook_status = "active"
        binding = next((item for item in endpoint.bindings if item.is_active), None)
        if not binding:
            event.error_message = "Agent binding not found"
            self.db.commit()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent binding not found")

        account = endpoint.integration_account
        if account.status == "pending_setup":
            account.status = "connected"
        binding.status = "connected"
        self._sync_legacy_agent_channel(account.user, binding.agent_id, binding, endpoint, account)

        external_message_id = str(
            normalized_payload.get("external_message_id")
            or normalized_payload.get("external_conversation_id")
            or ""
        )
        channel_message = self._create_channel_message(
            user_id=account.user_id,
            agent_id=binding.agent_id,
            provider=normalized,
            direction="inbound",
            external_message_id=external_message_id or None,
            endpoint_id=endpoint.id,
            binding_id=binding.id,
            payload_summary={
                "channel_id": normalized_payload.get("channel_id"),
                "external_user_id": normalized_payload.get("external_user_id"),
                "text": normalized_payload.get("text"),
                "event_type": normalized_payload.get("event_type"),
            },
            status="processing",
            error_message=None,
        )

        event_type = str(normalized_payload.get("event_type") or "message_received")
        if event_type == "status_update" or not str(normalized_payload.get("text") or "").strip():
            event.processed = True
            channel_message.status = "ok"
            self.db.commit()
            return {
                "status": "accepted",
                "provider": normalized,
                "event_type": event_type,
            }

        try:
            result = AgentRuntimeService.process_inbound_message(
                self.db,
                user_id=account.user_id,
                channel_type=normalized,
                channel_id=self._legacy_channel_id(endpoint, normalized),
                external_user_id=normalized_payload["external_user_id"],
                external_conversation_id=normalized_payload["external_conversation_id"],
                text=normalized_payload["text"],
                metadata=normalized_payload["metadata"],
            )
            event.processed = True
            channel_message.status = "ok"
            self.db.commit()
            return result
        except AgentRuntimeError as exc:
            event.error_message = str(exc)
            binding.status = "error"
            channel_message.status = "error"
            channel_message.error_message = str(exc)
            self.db.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

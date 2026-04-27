from __future__ import annotations

import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.integrations.providers import VALID_PROVIDERS, get_provider
from app.models.agent import Agent
from app.models.agent_channel import AgentChannel
from app.models.user import User

log = logging.getLogger(__name__)


class AgentChannelService:
    def __init__(self, db: Session):
        self.db = db

    def _agent_or_404(self, user: User, agent_id: int) -> Agent:
        item = self.db.query(Agent).filter(Agent.id == agent_id, Agent.user_id == user.id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
        return item

    @staticmethod
    def build_api_key(user_id: int, agent_id: int, channel_id: str) -> str:
        payload = f"{user_id}:{agent_id}:{channel_id}".encode("utf-8")
        return hmac.new(settings.secret_key.encode("utf-8"), payload, hashlib.sha256).hexdigest()

    @staticmethod
    def key_hash(raw: str) -> str:
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def check_key(stored_hash: str | None, candidate: str | None) -> bool:
        if not stored_hash or not candidate:
            return False
        return hmac.compare_digest(stored_hash, AgentChannelService.key_hash(candidate))

    def list_channels(self, user: User, agent_id: int) -> list[AgentChannel]:
        self._agent_or_404(user, agent_id)
        return (
            self.db.query(AgentChannel)
            .filter(AgentChannel.user_id == user.id, AgentChannel.agent_id == agent_id)
            .order_by(AgentChannel.updated_at.desc())
            .all()
        )

    def connect_channel(self, user: User, agent_id: int, payload: dict) -> AgentChannel:
        self._agent_or_404(user, agent_id)
        channel_id = str(payload.get("channel_id") or "")
        if not channel_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="channel_id is required")

        existing = (
            self.db.query(AgentChannel)
            .filter(
                AgentChannel.user_id == user.id,
                AgentChannel.agent_id == agent_id,
                AgentChannel.channel_id == channel_id,
            )
            .first()
        )

        api_key = str(payload.get("api_key") or self.build_api_key(user.id, agent_id, channel_id))

        if existing:
            existing.provider_name = str(payload.get("provider_name") or existing.provider_name)
            existing.channel_type = str(payload.get("channel_type") or existing.channel_type)
            existing.external_account_id = payload.get("external_account_id") or existing.external_account_id
            existing.credential_ref = payload.get("credential_ref") or existing.credential_ref
            existing.enabled = bool(payload.get("enabled", True))
            existing.test_mode = bool(payload.get("test_mode", True))
            existing.config_json = json.dumps(payload.get("config") or {}, ensure_ascii=True)
            existing.api_key_hash = self.key_hash(api_key)
            self.db.commit()
            self.db.refresh(existing)
            return existing

        item = AgentChannel(
            user_id=user.id,
            agent_id=agent_id,
            channel_type=str(payload.get("channel_type") or "website"),
            provider_name=str(payload.get("provider_name") or "internal"),
            external_account_id=payload.get("external_account_id"),
            channel_id=channel_id,
            credential_ref=payload.get("credential_ref"),
            api_key_hash=self.key_hash(api_key),
            enabled=bool(payload.get("enabled", True)),
            test_mode=bool(payload.get("test_mode", True)),
            config_json=json.dumps(payload.get("config") or {}, ensure_ascii=True),
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    # ------------------------------------------------------------------
    # Connections API (novos métodos)
    # ------------------------------------------------------------------

    def _validate_provider(self, channel_type: str) -> None:
        if channel_type.lower() not in VALID_PROVIDERS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Provider inválido: '{channel_type}'. Válidos: {sorted(VALID_PROVIDERS)}",
            )

    def get_or_create_connection(self, user: User, agent_id: int, channel_type: str) -> AgentChannel:
        """Retorna o registro existente ou cria um padrão (status=disconnected)."""
        self._agent_or_404(user, agent_id)
        self._validate_provider(channel_type)
        existing = (
            self.db.query(AgentChannel)
            .filter(
                AgentChannel.user_id == user.id,
                AgentChannel.agent_id == agent_id,
                AgentChannel.channel_type == channel_type.lower(),
            )
            .first()
        )
        if existing:
            return existing
        item = AgentChannel(
            user_id=user.id,
            agent_id=agent_id,
            channel_type=channel_type.lower(),
            channel_id=f"{channel_type.lower()}-{agent_id}",
            status="disconnected",
            enabled=False,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_connections(self, user: User, agent_id: int) -> list[AgentChannel]:
        """Retorna todas as conexões (criando registros padrão se necessário)."""
        self._agent_or_404(user, agent_id)
        existing_types = {
            row.channel_type
            for row in self.db.query(AgentChannel.channel_type)
            .filter(AgentChannel.user_id == user.id, AgentChannel.agent_id == agent_id)
            .all()
        }
        for ct in VALID_PROVIDERS:
            if ct not in existing_types:
                item = AgentChannel(
                    user_id=user.id,
                    agent_id=agent_id,
                    channel_type=ct,
                    channel_id=f"{ct}-{agent_id}",
                    status="disconnected",
                    enabled=False,
                )
                self.db.add(item)
        self.db.commit()
        return (
            self.db.query(AgentChannel)
            .filter(AgentChannel.user_id == user.id, AgentChannel.agent_id == agent_id)
            .order_by(AgentChannel.channel_type)
            .all()
        )

    def connect_provider(self, user: User, agent_id: int, channel_type: str, config: dict[str, Any]) -> AgentChannel:
        self._validate_provider(channel_type)
        channel = self.get_or_create_connection(user, agent_id, channel_type)
        provider = get_provider(channel_type)

        validation = provider.validate_config(config)
        if not validation.success:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=validation.message)

        channel.status = "connecting"
        channel.last_error = None
        self.db.commit()

        result = provider.connect(config)
        channel.config_json = json.dumps(config, ensure_ascii=True)
        channel.enabled = result.success

        if result.success:
            channel.status = "connected"
            channel.last_error = None
            channel.last_sync_at = datetime.now(tz=timezone.utc)
            log.info("channel.connected agent_id=%d channel_type=%s", agent_id, channel_type)
        else:
            channel.status = "error"
            channel.last_error = result.message
            log.warning("channel.connect_failed agent_id=%d channel_type=%s msg=%s", agent_id, channel_type, result.message)

        self.db.commit()
        self.db.refresh(channel)
        return channel

    def disconnect_provider(self, user: User, agent_id: int, channel_type: str) -> AgentChannel:
        self._validate_provider(channel_type)
        channel = self.get_or_create_connection(user, agent_id, channel_type)
        config = json.loads(channel.config_json or "{}")
        provider = get_provider(channel_type)
        result = provider.disconnect(config)

        channel.status = "disconnected"
        channel.enabled = False
        channel.last_error = None if result.success else result.message
        channel.access_token = None
        channel.refresh_token = None
        self.db.commit()
        self.db.refresh(channel)
        log.info("channel.disconnected agent_id=%d channel_type=%s", agent_id, channel_type)
        return channel

    def sync_provider(self, user: User, agent_id: int, channel_type: str) -> AgentChannel:
        self._validate_provider(channel_type)
        channel = self.get_or_create_connection(user, agent_id, channel_type)
        config = json.loads(channel.config_json or "{}")
        provider = get_provider(channel_type)
        result = provider.sync(config)

        if result.success:
            channel.last_sync_at = datetime.now(tz=timezone.utc)
            channel.last_error = None
            log.info("channel.sync_ok agent_id=%d channel_type=%s", agent_id, channel_type)
        else:
            channel.last_error = result.message
            log.warning("channel.sync_failed agent_id=%d channel_type=%s msg=%s", agent_id, channel_type, result.message)

        self.db.commit()
        self.db.refresh(channel)
        return channel

    def test_provider(self, user: User, agent_id: int, channel_type: str) -> dict[str, Any]:
        self._validate_provider(channel_type)
        channel = self.get_or_create_connection(user, agent_id, channel_type)
        config = json.loads(channel.config_json or "{}")
        provider = get_provider(channel_type)
        result = provider.test_connection(config)
        log.info("channel.test agent_id=%d channel_type=%s success=%s", agent_id, channel_type, result.success)
        return {
            "success": result.success,
            "message": result.message,
            "data": result.data,
            "channel_type": channel_type,
        }

    def update_provider_config(self, user: User, agent_id: int, channel_type: str, payload: dict[str, Any]) -> AgentChannel:
        self._validate_provider(channel_type)
        channel = self.get_or_create_connection(user, agent_id, channel_type)

        if "config" in payload:
            channel.config_json = json.dumps(payload["config"], ensure_ascii=True)
        if "enabled" in payload:
            channel.enabled = bool(payload["enabled"])
        if "webhook_url" in payload:
            channel.webhook_url = payload["webhook_url"]
        if "external_account_id" in payload:
            channel.external_account_id = payload["external_account_id"]

        self.db.commit()
        self.db.refresh(channel)
        return channel

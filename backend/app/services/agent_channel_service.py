import hashlib
import hmac
import json

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.agent_channel import AgentChannel
from app.models.user import User


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
        return hashlib.sha256(f"{user_id}:{agent_id}:{channel_id}".encode("utf-8")).hexdigest()

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

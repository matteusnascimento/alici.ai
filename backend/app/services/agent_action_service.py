import json

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.agent_action import AgentAction
from app.models.user import User


class AgentActionService:
    def __init__(self, db: Session):
        self.db = db

    def _agent_or_404(self, user: User, agent_id: int) -> Agent:
        item = self.db.query(Agent).filter(Agent.id == agent_id, Agent.user_id == user.id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
        return item

    def list_actions(self, user: User, agent_id: int) -> list[AgentAction]:
        self._agent_or_404(user, agent_id)
        return (
            self.db.query(AgentAction)
            .filter(AgentAction.user_id == user.id, AgentAction.agent_id == agent_id)
            .order_by(AgentAction.updated_at.desc())
            .all()
        )

    def add_or_update_action(self, user: User, agent_id: int, payload: dict) -> AgentAction:
        self._agent_or_404(user, agent_id)
        name = str(payload.get("name") or "Acao")
        action_type = str(payload.get("action_type") or "custom")

        existing = (
            self.db.query(AgentAction)
            .filter(
                AgentAction.user_id == user.id,
                AgentAction.agent_id == agent_id,
                AgentAction.name == name,
            )
            .first()
        )

        if existing:
            existing.action_type = action_type
            existing.trigger_keywords = payload.get("trigger_keywords")
            existing.config_json = json.dumps(payload.get("config") or {}, ensure_ascii=True)
            existing.enabled = bool(payload.get("enabled", True))
            self.db.commit()
            self.db.refresh(existing)
            return existing

        item = AgentAction(
            user_id=user.id,
            agent_id=agent_id,
            name=name,
            action_type=action_type,
            trigger_keywords=payload.get("trigger_keywords"),
            config_json=json.dumps(payload.get("config") or {}, ensure_ascii=True),
            enabled=bool(payload.get("enabled", True)),
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

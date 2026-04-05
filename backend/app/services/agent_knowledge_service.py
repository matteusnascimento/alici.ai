from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.agent_knowledge import AgentKnowledge
from app.models.user import User


class AgentKnowledgeService:
    def __init__(self, db: Session):
        self.db = db

    def _agent_or_404(self, user: User, agent_id: int) -> Agent:
        item = self.db.query(Agent).filter(Agent.id == agent_id, Agent.user_id == user.id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
        return item

    def list_sources(self, user: User, agent_id: int) -> list[AgentKnowledge]:
        self._agent_or_404(user, agent_id)
        return (
            self.db.query(AgentKnowledge)
            .filter(AgentKnowledge.user_id == user.id, AgentKnowledge.agent_id == agent_id)
            .order_by(AgentKnowledge.updated_at.desc())
            .all()
        )

    def add_source(self, user: User, agent_id: int, payload: dict) -> AgentKnowledge:
        self._agent_or_404(user, agent_id)
        item = AgentKnowledge(
            user_id=user.id,
            agent_id=agent_id,
            title=str(payload.get("title") or "Informacao importante"),
            kind=str(payload.get("kind") or "note"),
            content=str(payload.get("content") or ""),
            tags=payload.get("tags"),
            enabled=bool(payload.get("enabled", True)),
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

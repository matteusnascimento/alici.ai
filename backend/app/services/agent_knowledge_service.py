from fastapi import HTTPException, status
import json
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

    def create_manual_content(
        self,
        user: User,
        agent_id: int,
        *,
        title: str,
        content: str,
        tags: str | None = None,
        enabled: bool = True,
    ) -> AgentKnowledge:
        return self.add_source(
            user,
            agent_id,
            {
                "title": title,
                "kind": "manual",
                "content": content,
                "tags": tags,
                "enabled": enabled,
            },
        )

    def create_faq(
        self,
        user: User,
        agent_id: int,
        *,
        question: str,
        answer: str,
        tags: str | None = None,
        enabled: bool = True,
    ) -> AgentKnowledge:
        payload = {
            "question": question.strip(),
            "answer": answer.strip(),
        }
        title = f"FAQ: {question.strip()}"
        return self.add_source(
            user,
            agent_id,
            {
                "title": title,
                "kind": "faq",
                "content": json.dumps(payload, ensure_ascii=True),
                "tags": tags,
                "enabled": enabled,
            },
        )

    def delete_source(self, user: User, agent_id: int, source_id: int) -> None:
        self._agent_or_404(user, agent_id)
        item = (
            self.db.query(AgentKnowledge)
            .filter(AgentKnowledge.id == source_id, AgentKnowledge.agent_id == agent_id, AgentKnowledge.user_id == user.id)
            .first()
        )
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge source not found")
        self.db.delete(item)
        self.db.commit()

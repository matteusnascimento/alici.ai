from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.user import User
from app.schemas.agent import AgentCreate


class AgentService:
    def __init__(self, db: Session):
        self.db = db

    def list_agents(self, user: User) -> list[Agent]:
        return self.db.query(Agent).filter(Agent.user_id == user.id).order_by(Agent.created_at.desc()).all()

    def create_agent(self, user: User, payload: AgentCreate) -> Agent:
        agent = Agent(user_id=user.id, **payload.model_dump())
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        return agent

    def get_agent(self, user: User, agent_id: int) -> Agent:
        agent = self.db.query(Agent).filter(Agent.user_id == user.id, Agent.id == agent_id).first()
        if not agent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
        return agent

    def update_agent(self, user: User, agent_id: int, payload: AgentCreate) -> Agent:
        agent = self.get_agent(user, agent_id)
        for key, value in payload.model_dump().items():
            setattr(agent, key, value)
        self.db.commit()
        self.db.refresh(agent)
        return agent

    def delete_agent(self, user: User, agent_id: int) -> None:
        agent = self.get_agent(user, agent_id)
        self.db.delete(agent)
        self.db.commit()

    def toggle_agent(self, user: User, agent_id: int) -> Agent:
        agent = self.get_agent(user, agent_id)
        agent.ativo = not agent.ativo
        self.db.commit()
        self.db.refresh(agent)
        return agent

from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agent import Agent


def list_agents(db: Session) -> list[Agent]:
    return db.scalars(select(Agent)).all()


def get_agent(db: Session, agent_id: UUID) -> Agent | None:
    return db.get(Agent, agent_id)


def create_agent(db: Session, payload: dict) -> Agent:
    item = Agent(**payload)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_agent(db: Session, agent: Agent, payload: dict) -> Agent:
    for key, value in payload.items():
        setattr(agent, key, value)
    db.commit()
    db.refresh(agent)
    return agent


def delete_agent(db: Session, agent: Agent) -> None:
    db.delete(agent)
    db.commit()
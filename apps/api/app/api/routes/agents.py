from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.agent import AgentCreate, AgentResponse, AgentUpdate
from app.services.agent_service import create_agent, delete_agent, get_agent, list_agents, update_agent

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=list[AgentResponse])
def route_list(db: Session = Depends(get_db)):
    return list_agents(db)


@router.get("/{agent_id}", response_model=AgentResponse)
def route_get(agent_id: UUID, db: Session = Depends(get_db)):
    item = get_agent(db, agent_id)
    if not item:
        raise HTTPException(status_code=404, detail="not found")
    return item


@router.post("", response_model=AgentResponse)
def route_create(payload: AgentCreate, db: Session = Depends(get_db)):
    return create_agent(db, payload.model_dump())


@router.put("/{agent_id}", response_model=AgentResponse)
def route_update(agent_id: UUID, payload: AgentUpdate, db: Session = Depends(get_db)):
    item = get_agent(db, agent_id)
    if not item:
        raise HTTPException(status_code=404, detail="not found")
    return update_agent(db, item, payload.model_dump(exclude_unset=True))


@router.delete("/{agent_id}")
def route_delete(agent_id: UUID, db: Session = Depends(get_db)):
    item = get_agent(db, agent_id)
    if not item:
        raise HTTPException(status_code=404, detail="not found")
    delete_agent(db, item)
    return {"ok": True}
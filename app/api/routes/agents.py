"""
Agent management routes
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.models import User, Agent, Organization

router = APIRouter()


class AgentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    system_prompt: str
    model: Optional[str] = "gpt-3.5-turbo"
    temperature: Optional[int] = 70
    max_tokens: Optional[int] = 1000
    is_public: Optional[bool] = False


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[int] = None
    max_tokens: Optional[int] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None


@router.get("/")
def list_agents(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """List all agents for the organization"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    agents = db.query(Agent).filter(
        Agent.organization_id == current_user.organization_id
    ).all()

    return [
        {
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
            "model": agent.model,
            "is_active": agent.is_active,
            "is_public": agent.is_public,
            "total_requests": agent.total_requests,
            "created_at": agent.created_at
        }
        for agent in agents
    ]


@router.post("/")
def create_agent(
    agent_data: AgentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Create a new agent"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    import uuid
    agent = Agent(
        id=str(uuid.uuid4()),
        name=agent_data.name,
        description=agent_data.description,
        system_prompt=agent_data.system_prompt,
        model=agent_data.model,
        temperature=agent_data.temperature,
        max_tokens=agent_data.max_tokens,
        is_public=agent_data.is_public,
        organization_id=current_user.organization_id
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return {
        "id": agent.id,
        "name": agent.name,
        "description": agent.description,
        "model": agent.model,
        "created_at": agent.created_at
    }


@router.get("/{agent_id}")
def get_agent(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Get agent details"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.organization_id == current_user.organization_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return {
        "id": agent.id,
        "name": agent.name,
        "description": agent.description,
        "system_prompt": agent.system_prompt,
        "model": agent.model,
        "temperature": agent.temperature,
        "max_tokens": agent.max_tokens,
        "is_active": agent.is_active,
        "is_public": agent.is_public,
        "total_requests": agent.total_requests,
        "created_at": agent.created_at,
        "updated_at": agent.updated_at
    }


@router.put("/{agent_id}")
def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Update agent"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.organization_id == current_user.organization_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Update fields
    for field, value in agent_data.dict(exclude_unset=True).items():
        if value is not None:
            setattr(agent, field, value)

    agent.updated_at = None  # Will be auto-updated
    db.commit()
    db.refresh(agent)

    return {"message": "Agent updated successfully"}


@router.delete("/{agent_id}")
def delete_agent(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Delete agent"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.organization_id == current_user.organization_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    db.delete(agent)
    db.commit()

    return {"message": "Agent deleted successfully"}
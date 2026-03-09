"""
Agent management routes
"""
from typing import List, Optional
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.models import User, Agent, Organization

router = APIRouter()


def _loads_json_or_default(value, default):
    if not value:
        return default
    try:
        return json.loads(value)
    except Exception:
        return default


def _ok(data):
    # /**
    #  * Function: _ok
    #  * Description: Wrap a successful API payload using the standard envelope contract.
    #  * Parameters:
    #  *   data: response data payload.
    #  * Returns:
    #  *   dict with status, data and error fields.
    #  */
    return {"status": "success", "data": data, "error": None}


class AgentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    instructions: Optional[str] = None
    model: Optional[str] = "gpt-3.5-turbo"
    tools: Optional[list[str]] = None
    knowledge: Optional[dict] = None
    memory: Optional[dict] = None
    temperature: Optional[int] = 70
    max_tokens: Optional[int] = 1000
    is_public: Optional[bool] = False


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    instructions: Optional[str] = None
    model: Optional[str] = None
    tools: Optional[list[str]] = None
    knowledge: Optional[dict] = None
    memory: Optional[dict] = None
    temperature: Optional[int] = None
    max_tokens: Optional[int] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None


@router.get("/")
def list_agents(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # /**
    #  * Function: list_agents
    #  * Description: List all agents for the current organization.
    #  * Parameters:
    #  *   db: active SQLAlchemy session.
    #  *   current_user: authenticated user context.
    #  * Returns:
    #  *   Standard API envelope containing agents list.
    #  */
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    agents = db.query(Agent).filter(
        Agent.organization_id == current_user.organization_id
    ).all()

    agents_payload = [
        {
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
            "instructions": agent.instructions or agent.system_prompt or "",
            "model": agent.model,
            "tools": _loads_json_or_default(agent.tools, []),
            "knowledge": _loads_json_or_default(agent.knowledge, {}),
            "memory": _loads_json_or_default(agent.memory, {}),
            "is_active": agent.is_active,
            "is_public": agent.is_public,
            "total_requests": agent.total_requests,
            "created_at": agent.created_at
        }
        for agent in agents
    ]
    return _ok({"agents": agents_payload})


@router.post("/")
def create_agent(
    agent_data: AgentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # /**
    #  * Function: create_agent
    #  * Description: Create a new agent bound to the authenticated organization.
    #  * Parameters:
    #  *   agent_data: validated payload with agent attributes.
    #  *   db: active SQLAlchemy session.
    #  *   current_user: authenticated user context.
    #  * Returns:
    #  *   Standard API envelope containing created agent summary.
    #  */
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    import uuid
    instructions = (agent_data.instructions or agent_data.system_prompt or "").strip()
    if not instructions:
        raise HTTPException(status_code=400, detail="instructions is required")

    agent = Agent(
        id=str(uuid.uuid4()),
        name=agent_data.name,
        description=agent_data.description,
        system_prompt=instructions,
        instructions=instructions,
        model=agent_data.model,
        tools=json.dumps(agent_data.tools or []),
        knowledge=json.dumps(agent_data.knowledge or {}),
        memory=json.dumps(agent_data.memory or {}),
        temperature=agent_data.temperature,
        max_tokens=agent_data.max_tokens,
        is_public=agent_data.is_public,
        organization_id=current_user.organization_id
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return _ok({
        "id": agent.id,
        "name": agent.name,
        "description": agent.description,
        "instructions": agent.instructions or agent.system_prompt or "",
        "model": agent.model,
        "tools": _loads_json_or_default(agent.tools, []),
        "knowledge": _loads_json_or_default(agent.knowledge, {}),
        "memory": _loads_json_or_default(agent.memory, {}),
        "created_at": agent.created_at
    })


@router.get("/{agent_id}")
def get_agent(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # /**
    #  * Function: get_agent
    #  * Description: Return full details for one agent.
    #  * Parameters:
    #  *   agent_id: target agent identifier.
    #  *   db: active SQLAlchemy session.
    #  *   current_user: authenticated user context.
    #  * Returns:
    #  *   Standard API envelope containing agent details.
    #  */
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.organization_id == current_user.organization_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return _ok({
        "id": agent.id,
        "name": agent.name,
        "description": agent.description,
        "instructions": agent.instructions or agent.system_prompt or "",
        "model": agent.model,
        "tools": _loads_json_or_default(agent.tools, []),
        "knowledge": _loads_json_or_default(agent.knowledge, {}),
        "memory": _loads_json_or_default(agent.memory, {}),
        "temperature": agent.temperature,
        "max_tokens": agent.max_tokens,
        "is_active": agent.is_active,
        "is_public": agent.is_public,
        "total_requests": agent.total_requests,
        "created_at": agent.created_at,
        "updated_at": agent.updated_at
    })


@router.put("/{agent_id}")
def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # /**
    #  * Function: update_agent
    #  * Description: Update mutable fields for an existing agent.
    #  * Parameters:
    #  *   agent_id: target agent identifier.
    #  *   agent_data: partial payload with fields to change.
    #  *   db: active SQLAlchemy session.
    #  *   current_user: authenticated user context.
    #  * Returns:
    #  *   Standard API envelope with operation status.
    #  */
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.organization_id == current_user.organization_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Update fields
    update_data = agent_data.dict(exclude_unset=True)
    if "instructions" in update_data and update_data["instructions"] is not None:
        update_data["system_prompt"] = update_data["instructions"]

    for field, value in update_data.items():
        if value is not None:
            if field in {"tools", "knowledge", "memory"}:
                setattr(agent, field, json.dumps(value))
                continue
            setattr(agent, field, value)

    db.commit()
    db.refresh(agent)

    return _ok({"message": "Agent updated successfully", "id": agent.id})


@router.delete("/{agent_id}")
def delete_agent(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # /**
    #  * Function: delete_agent
    #  * Description: Delete an agent owned by the authenticated organization.
    #  * Parameters:
    #  *   agent_id: target agent identifier.
    #  *   db: active SQLAlchemy session.
    #  *   current_user: authenticated user context.
    #  * Returns:
    #  *   Standard API envelope with operation status.
    #  */
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

    return _ok({"message": "Agent deleted successfully", "id": agent_id})
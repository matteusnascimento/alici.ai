from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.agent import AgentCreate, AgentRead, AgentToggleResponse
from app.services.agent_service import AgentService

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=list[AgentRead])
def list_agents(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[AgentRead]:
    return [AgentRead.model_validate(item) for item in AgentService(db).list_agents(current_user)]


@router.post("", response_model=AgentRead)
def create_agent(
    payload: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentRead:
    agent = AgentService(db).create_agent(current_user, payload)
    return AgentRead.model_validate(agent)


@router.get("/{agent_id}", response_model=AgentRead)
def get_agent(agent_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> AgentRead:
    agent = AgentService(db).get_agent(current_user, agent_id)
    return AgentRead.model_validate(agent)


@router.patch("/{agent_id}", response_model=AgentRead)
def update_agent(
    agent_id: int,
    payload: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentRead:
    agent = AgentService(db).update_agent(current_user, agent_id, payload)
    return AgentRead.model_validate(agent)


@router.delete("/{agent_id}", status_code=204)
def delete_agent(agent_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Response:
    AgentService(db).delete_agent(current_user, agent_id)
    return Response(status_code=204)


@router.post("/{agent_id}/toggle", response_model=AgentToggleResponse)
def toggle_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AgentToggleResponse:
    agent = AgentService(db).toggle_agent(current_user, agent_id)
    return AgentToggleResponse(id=agent.id, ativo=agent.ativo)

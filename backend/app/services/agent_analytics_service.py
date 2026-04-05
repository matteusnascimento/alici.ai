from sqlalchemy.orm import Session

from app.models.user import User
from app.services.agent_runtime_service import AgentRuntimeService


class AgentAnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def overview_metrics(self, user: User, agent_id: int) -> dict:
        return AgentRuntimeService.analytics_for_agent(self.db, user_id=user.id, agent_id=agent_id)

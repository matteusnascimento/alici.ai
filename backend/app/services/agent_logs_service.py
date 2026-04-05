import json

from sqlalchemy.orm import Session

from app.models.agent_log import AgentLog
from app.models.user import User


class AgentLogsService:
    def __init__(self, db: Session):
        self.db = db

    def list_logs(self, user: User, agent_id: int, kind: str | None = None) -> list[dict]:
        query = self.db.query(AgentLog).filter(AgentLog.agent_id == agent_id)
        if kind == "errors":
            query = query.filter(AgentLog.status == "error")
        elif kind == "actions":
            query = query.filter(AgentLog.event_type.like("%action%"))
        elif kind == "escalations":
            query = query.filter(AgentLog.event_type.like("%handoff%"))

        items = query.order_by(AgentLog.created_at.desc()).limit(200).all()
        return [
            {
                "id": item.id,
                "event_type": item.event_type,
                "status": item.status,
                "summary": item.summary,
                "input_text": item.input_text,
                "output_text": item.output_text,
                "metadata": json.loads(item.metadata_json or "{}"),
                "created_at": item.created_at.isoformat(),
            }
            for item in items
        ]

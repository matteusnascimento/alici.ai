import json

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.agent_channel import AgentChannel
from app.models.agent_test_message import AgentTestMessage
from app.models.agent_test_session import AgentTestSession
from app.models.user import User
from app.services.agent_runtime_service import AgentRuntimeError, AgentRuntimeService


class AgentTestService:
    def __init__(self, db: Session):
        self.db = db

    def _agent_or_404(self, user: User, agent_id: int) -> Agent:
        item = self.db.query(Agent).filter(Agent.id == agent_id, Agent.user_id == user.id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
        return item

    def run_test(self, user: User, agent_id: int, payload: dict) -> dict:
        agent = self._agent_or_404(user, agent_id)
        text = str(payload.get("text") or "Quero saber mais")
        scenario = str(payload.get("scenario") or "free")
        channel_type = str(payload.get("channel_type") or "api")
        channel_id = f"test:{agent_id}:{channel_type}"

        existing_channel = (
            self.db.query(AgentChannel)
            .filter(
                AgentChannel.user_id == user.id,
                AgentChannel.agent_id == agent_id,
                AgentChannel.channel_type == channel_type,
                AgentChannel.channel_id == channel_id,
            )
            .first()
        )
        if not existing_channel:
            self.db.add(
                AgentChannel(
                    user_id=user.id,
                    agent_id=agent_id,
                    channel_type=channel_type,
                    provider_name="internal-test",
                    channel_id=channel_id,
                    enabled=True,
                    test_mode=True,
                    config_json=json.dumps({}, ensure_ascii=True),
                )
            )
            self.db.flush()

        session = AgentTestSession(
            user_id=user.id,
            agent_id=agent_id,
            scenario=scenario,
            input_text=text,
            output_text="",
            action_trace_json=json.dumps([], ensure_ascii=True),
            context_used="Materiais e informacoes do agente",
            confidence_note="",
            status="running",
        )
        self.db.add(session)
        self.db.flush()

        self.db.add(
            AgentTestMessage(
                session_id=session.id,
                role="user",
                content=text,
                trace_json=json.dumps({"scenario": scenario}, ensure_ascii=True),
            )
        )

        original_active = bool(agent.ativo)
        if not original_active:
            # O teste do sandbox deve funcionar antes da ativacao do agente no ambiente real.
            agent.ativo = True
            self.db.flush()

        try:
            result = AgentRuntimeService.process_inbound_message(
                self.db,
                user_id=user.id,
                channel_type=channel_type,
                channel_id=channel_id,
                external_user_id=f"sandbox:{user.id}",
                external_conversation_id=f"sandbox-conv:{agent_id}",
                text=text,
                metadata={"source": "agent-test-service", "scenario": scenario},
            )
        finally:
            if not original_active:
                agent.ativo = False
                self.db.flush()

        self.db.add(
            AgentTestMessage(
                session_id=session.id,
                role="assistant",
                content=str(result.get("response") or ""),
                trace_json=json.dumps({"actions": result.get("actions") or []}, ensure_ascii=True),
            )
        )

        session.output_text = str(result.get("response") or "")
        session.action_trace_json = json.dumps(result.get("actions") or [], ensure_ascii=True)
        session.context_used = "Materiais e informacoes do agente"
        session.confidence_note = "Resposta baseada no contexto configurado"
        session.status = "completed"
        self.db.commit()
        self.db.refresh(session)

        return {
            "test_id": session.id,
            "scenario": session.scenario,
            "response": session.output_text,
            "actions": json.loads(session.action_trace_json or "[]"),
            "source": session.context_used,
            "confidence_note": session.confidence_note,
            "status": session.status,
        }

    def list_tests(self, user: User, agent_id: int) -> list[AgentTestSession]:
        self._agent_or_404(user, agent_id)
        return (
            self.db.query(AgentTestSession)
            .filter(AgentTestSession.user_id == user.id, AgentTestSession.agent_id == agent_id)
            .order_by(AgentTestSession.created_at.desc())
            .limit(100)
            .all()
        )

    def get_test(self, user: User, agent_id: int, session_id: int) -> dict:
        self._agent_or_404(user, agent_id)
        session = (
            self.db.query(AgentTestSession)
            .filter(
                AgentTestSession.id == session_id,
                AgentTestSession.user_id == user.id,
                AgentTestSession.agent_id == agent_id,
            )
            .first()
        )
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test session not found")

        messages = (
            self.db.query(AgentTestMessage)
            .filter(AgentTestMessage.session_id == session.id)
            .order_by(AgentTestMessage.created_at.asc())
            .all()
        )

        return {
            "id": session.id,
            "scenario": session.scenario,
            "status": session.status,
            "session_summary": session.output_text[:180],
            "messages": [
                {
                    "id": item.id,
                    "role": item.role,
                    "content": item.content,
                    "trace": json.loads(item.trace_json or "{}"),
                    "created_at": item.created_at.isoformat(),
                }
                for item in messages
            ],
            "created_at": session.created_at.isoformat(),
        }

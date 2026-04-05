from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.agent_action import AgentAction
from app.models.agent_channel import AgentChannel
from app.models.agent_knowledge import AgentKnowledge
from app.models.agent_test_session import AgentTestSession
from app.models.user import User


class AgentSetupService:
    TOTAL_STEPS = 5

    def __init__(self, db: Session):
        self.db = db

    def _agent_or_404(self, user: User, agent_id: int) -> Agent:
        agent = self.db.query(Agent).filter(Agent.id == agent_id, Agent.user_id == user.id).first()
        if not agent:
            raise ValueError("Agent not found")
        return agent

    def _counts(self, user: User, agent_id: int) -> dict[str, int]:
        channels_count = (
            self.db.query(func.count(AgentChannel.id))
            .filter(
                AgentChannel.user_id == user.id,
                AgentChannel.agent_id == agent_id,
                AgentChannel.enabled.is_(True),
            )
            .scalar()
            or 0
        )

        knowledge_count = (
            self.db.query(func.count(AgentKnowledge.id))
            .filter(
                AgentKnowledge.user_id == user.id,
                AgentKnowledge.agent_id == agent_id,
                AgentKnowledge.enabled.is_(True),
            )
            .scalar()
            or 0
        )

        actions_count = (
            self.db.query(func.count(AgentAction.id))
            .filter(
                AgentAction.user_id == user.id,
                AgentAction.agent_id == agent_id,
                AgentAction.enabled.is_(True),
            )
            .scalar()
            or 0
        )

        tests_count = (
            self.db.query(func.count(AgentTestSession.id))
            .filter(
                AgentTestSession.user_id == user.id,
                AgentTestSession.agent_id == agent_id,
                AgentTestSession.status.in_(["ok", "completed", "success"]),
            )
            .scalar()
            or 0
        )

        return {
            "channels": int(channels_count),
            "knowledge": int(knowledge_count),
            "actions": int(actions_count),
            "tests": int(tests_count),
        }

    def _recommended_next_step(self, agent_id: int, state: dict[str, bool]) -> dict[str, str]:
        if not state["channels_connected"]:
            return {
                "key": "channels_connected",
                "title": "Conectar canais",
                "description": "Conecte ao menos um canal para o agente operar no seu negocio.",
                "route": f"/app/agents/{agent_id}/channels",
                "cta": "Conectar agora",
            }

        if not state["knowledge_added"]:
            return {
                "key": "knowledge_added",
                "title": "Adicionar conhecimento",
                "description": "Inclua instrucoes e materiais para respostas mais assertivas.",
                "route": f"/app/agents/{agent_id}/knowledge",
                "cta": "Adicionar agora",
            }

        if not state["actions_configured"]:
            return {
                "key": "actions_configured",
                "title": "Definir acoes",
                "description": "Configure acoes para automatizar tarefas do agente.",
                "route": f"/app/agents/{agent_id}/actions",
                "cta": "Configurar acoes",
            }

        if not state["test_completed"]:
            return {
                "key": "test_completed",
                "title": "Fazer teste",
                "description": "Rode um teste sandbox para validar o comportamento do agente.",
                "route": f"/app/agents/{agent_id}/test",
                "cta": "Testar agora",
            }

        return {
            "key": "activation_ready",
            "title": "Ativar agente",
            "description": "Seu agente esta pronto. Ative para comecar a operar em producao.",
            "route": f"/app/agents/{agent_id}/settings",
            "cta": "Ativar agente",
        }

    def _derive_status(self, agent: Agent, activation_ready: bool, completed_non_activation: int) -> str:
        if agent.ativo:
            return "active"
        if activation_ready:
            return "ready"
        if completed_non_activation == 0:
            return "draft"
        return "incomplete"

    def get_setup_status(self, user: User, agent_id: int) -> dict:
        agent = self._agent_or_404(user, agent_id)
        counts = self._counts(user, agent_id)

        channels_connected = counts["channels"] > 0
        knowledge_added = counts["knowledge"] > 0
        actions_configured = counts["actions"] > 0
        test_completed = counts["tests"] > 0
        activation_ready = channels_connected and knowledge_added and actions_configured and test_completed

        checklist = [
            {
                "key": "channels_connected",
                "label": "Conectar canais",
                "completed": channels_connected,
                "detail": "1+ canal conectado" if channels_connected else "Nenhum canal conectado",
                "route": f"/app/agents/{agent_id}/channels",
                "helper_text": "Escolha onde o agente vai atender.",
            },
            {
                "key": "knowledge_added",
                "label": "Adicionar conhecimento",
                "completed": knowledge_added,
                "detail": f"{counts['knowledge']} fonte(s) adicionada(s)" if knowledge_added else "Nenhuma informacao adicionada",
                "route": f"/app/agents/{agent_id}/knowledge",
                "helper_text": "Adicione materiais e instrucoes do negocio.",
            },
            {
                "key": "actions_configured",
                "label": "Definir acoes",
                "completed": actions_configured,
                "detail": f"{counts['actions']} acao(oes) configurada(s)" if actions_configured else "Nenhuma acao configurada",
                "route": f"/app/agents/{agent_id}/actions",
                "helper_text": "Habilite automacoes permitidas ao agente.",
            },
            {
                "key": "test_completed",
                "label": "Fazer teste",
                "completed": test_completed,
                "detail": f"{counts['tests']} teste(s) concluido(s)" if test_completed else "Nenhum teste realizado",
                "route": f"/app/agents/{agent_id}/test",
                "helper_text": "Valide respostas no sandbox antes da ativacao.",
            },
            {
                "key": "activation_ready",
                "label": "Ativar agente",
                "completed": activation_ready and agent.ativo,
                "detail": "Agente ativo" if agent.ativo else ("Pronto para ativacao" if activation_ready else "Configuracao ainda incompleta"),
                "route": f"/app/agents/{agent_id}/settings",
                "helper_text": "Ative quando os requisitos minimos estiverem completos.",
            },
        ]

        completed_steps = sum(1 for item in checklist if item["completed"])
        progress_percent = int((completed_steps / self.TOTAL_STEPS) * 100)

        state = {
            "channels_connected": channels_connected,
            "knowledge_added": knowledge_added,
            "actions_configured": actions_configured,
            "test_completed": test_completed,
            "activation_ready": activation_ready,
        }

        recommended_next_step = self._recommended_next_step(agent_id, state)
        missing_steps = sum(1 for item in checklist if not item["completed"])
        summary_message = (
            "Seu agente esta ativo e operando."
            if agent.ativo
            else (
                "Seu agente esta pronto para ativacao."
                if missing_steps == 0
                else f"Seu agente ainda precisa de {missing_steps} etapa(s) para comecar a operar."
            )
        )

        return {
            "progress_percent": progress_percent,
            "completed_steps": completed_steps,
            "total_steps": self.TOTAL_STEPS,
            "activation_ready": activation_ready,
            "summary_message": summary_message,
            "recommended_next_step": recommended_next_step,
            "checklist": checklist,
            "status": self._derive_status(agent, activation_ready, int(channels_connected) + int(knowledge_added) + int(actions_configured) + int(test_completed)),
            "counts": counts,
        }

    def get_readiness(self, user: User, agent_id: int) -> dict:
        setup = self.get_setup_status(user, agent_id)

        validation_errors: list[str] = []
        for item in setup["checklist"]:
            if item["key"] == "activation_ready":
                continue
            if not item["completed"]:
                validation_errors.append(item["label"])

        return {
            "activation_ready": setup["activation_ready"],
            "status": setup["status"],
            "progress_percent": setup["progress_percent"],
            "validation_errors": validation_errors,
        }

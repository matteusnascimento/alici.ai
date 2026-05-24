from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.user import User
from app.services.agent_analytics_service import AgentAnalyticsService
from app.services.agent_channel_service import AgentChannelService
from app.services.agent_logs_service import AgentLogsService


class AgentOverviewService:
    def __init__(self, db: Session):
        self.db = db

    def get_overview(self, user: User, agent_id: int) -> dict:
        agent = self.db.query(Agent).filter(Agent.id == agent_id, Agent.user_id == user.id).first()
        if not agent:
            raise ValueError("Agent not found")

        analytics = AgentAnalyticsService(self.db).overview_metrics(user, agent_id)
        channels = AgentChannelService(self.db).list_channels(user, agent_id)
        logs = AgentLogsService(self.db).list_logs(user, agent_id)[:8]

        return {
            "agent": {
                "id": agent.id,
                "nome": agent.nome,
                "funcao": agent.funcao,
                "linguagem": agent.linguagem,
                "status": "ativo" if agent.ativo else "pausado",
            },
            "kpis": {
                "conversas_atendidas": analytics.get("total_conversations", 0),
                "leads_capturados": analytics.get("leads_captured", 0),
                "encaminhamentos_humano": analytics.get("human_handoffs", 0),
                "tempo_medio_resposta_ms": analytics.get("average_response_time_ms", 0),
            },
            "canais_ativos": [
                {
                    "channel_type": item.channel_type,
                    "status": "Conectado" if item.enabled else "Nao conectado",
                }
                for item in channels
            ],
            "historico_de_atividade": logs,
        }

import json

from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.agent_configuration import AgentConfiguration
from app.models.user import User


class AgentSettingsService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _loads(value: str | None) -> dict:
        if not value:
            return {}
        try:
            data = json.loads(value)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def get_settings(self, user: User, agent_id: int) -> dict:
        agent = self.db.query(Agent).filter(Agent.id == agent_id, Agent.user_id == user.id).first()
        if not agent:
            raise ValueError("Agent not found")

        cfg = self.db.query(AgentConfiguration).filter(AgentConfiguration.agent_id == agent_id, AgentConfiguration.user_id == user.id).first()
        if not cfg:
            return {
                "basic": {
                    "name": agent.nome,
                    "role": agent.funcao,
                    "language": agent.linguagem,
                    "tone": None,
                    "working_hours": None,
                    "active": agent.ativo,
                    "fallback_to_human": True,
                },
                "advanced": {
                    "instrucoes_principais_do_agente": None,
                    "modelo": None,
                    "temperature": None,
                    "opcoes_avancadas": {},
                },
            }

        return {
            "basic": {
                "name": agent.nome,
                "role": agent.funcao,
                "language": cfg.language,
                "tone": cfg.tone,
                "working_hours": cfg.working_hours,
                "active": agent.ativo,
                "fallback_to_human": cfg.fallback_to_human,
            },
            "advanced": {
                "instrucoes_principais_do_agente": cfg.system_instructions,
                "modelo": cfg.model_name,
                "temperature": cfg.temperature,
                "opcoes_avancadas": self._loads(cfg.advanced_json),
            },
        }

    def save_settings(self, user: User, agent_id: int, payload: dict) -> dict:
        agent = self.db.query(Agent).filter(Agent.id == agent_id, Agent.user_id == user.id).first()
        if not agent:
            raise ValueError("Agent not found")

        basic = payload.get("basic") or {}
        advanced = payload.get("advanced") or {}

        agent.nome = str(basic.get("name", agent.nome))
        agent.funcao = str(basic.get("role", agent.funcao))
        agent.ativo = bool(basic.get("active", agent.ativo))

        cfg = self.db.query(AgentConfiguration).filter(AgentConfiguration.agent_id == agent_id, AgentConfiguration.user_id == user.id).first()
        if not cfg:
            cfg = AgentConfiguration(user_id=user.id, agent_id=agent_id)
            self.db.add(cfg)

        cfg.language = str(basic.get("language", cfg.language or "pt-BR"))
        cfg.tone = basic.get("tone")
        cfg.working_hours = basic.get("working_hours")
        cfg.fallback_to_human = bool(basic.get("fallback_to_human", True))
        cfg.system_instructions = advanced.get("instrucoes_principais_do_agente")
        cfg.model_name = advanced.get("modelo")
        cfg.temperature = str(advanced.get("temperature")) if advanced.get("temperature") is not None else None
        cfg.advanced_json = json.dumps(advanced.get("opcoes_avancadas") or {}, ensure_ascii=True)

        self.db.commit()
        return {"saved": True}

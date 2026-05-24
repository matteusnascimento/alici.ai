from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.user import User
from app.services.agent_setup_service import AgentSetupService


class AgentActivationService:
    def __init__(self, db: Session):
        self.db = db

    def _agent_or_404(self, user: User, agent_id: int) -> Agent:
        item = self.db.query(Agent).filter(Agent.id == agent_id, Agent.user_id == user.id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
        return item

    def activate(self, user: User, agent_id: int) -> Agent:
        item = self._agent_or_404(user, agent_id)
        readiness = AgentSetupService(self.db).get_readiness(user, agent_id)
        if not readiness["activation_ready"]:
            errors = readiness["validation_errors"]
            if len(errors) == 1:
                message = f"Seu agente ainda precisa de {errors[0]} antes da ativacao."
            else:
                joined = ", ".join(errors[:-1]) + f" e {errors[-1]}" if len(errors) > 1 else "configuracao minima"
                message = f"Seu agente ainda precisa de {joined} antes da ativacao."

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "activation_blocked",
                    "message": message,
                    "validation_errors": errors,
                    "readiness": readiness,
                },
            )

        item.ativo = True
        item.archived = False
        self.db.commit()
        self.db.refresh(item)
        return item

    def pause(self, user: User, agent_id: int) -> Agent:
        item = self._agent_or_404(user, agent_id)
        item.ativo = False
        self.db.commit()
        self.db.refresh(item)
        return item

    def duplicate(self, user: User, agent_id: int) -> Agent:
        item = self._agent_or_404(user, agent_id)
        copy = Agent(
            user_id=user.id,
            nome=f"{item.nome} (copia)",
            funcao=item.funcao,
            tipo=item.tipo,
            linguagem=item.linguagem,
            prompt=item.prompt,
            whatsapp=item.whatsapp,
            instagram=item.instagram,
            api=item.api,
            outros=item.outros,
            outros_nome=item.outros_nome,
            ativo=False,
            archived=False,
        )
        self.db.add(copy)
        self.db.commit()
        self.db.refresh(copy)
        return copy

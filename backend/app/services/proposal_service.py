from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import uuid
from datetime import date

from app.models.proposal import Proposal
from app.schemas.proposal import ProposalCreate, ProposalRead, ProposalUpdate


class ProposalService:
    def __init__(self, db: Session):
        self.db = db

    def _proposal_or_404(self, proposal_id: int) -> Proposal:
        """Busca proposta por ID ou lança 404."""
        proposal = self.db.query(Proposal).filter(Proposal.id == proposal_id).first()
        if not proposal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proposta não encontrada",
            )
        return proposal

    def _generate_proposal_id(self) -> str:
        """Gera ID único para proposta."""
        return f"PROP-{date.today().year}-{uuid.uuid4().hex[:3].upper()}"

    def create_proposal(self, proposal_data: ProposalCreate) -> ProposalRead:
        """Cria uma nova proposta."""
        # Valida se lead existe
        from app.services.lead_service import LeadService
        lead_service = LeadService(self.db)
        lead_service._lead_or_404(proposal_data.lead_id)

        proposal = Proposal(
            proposal_id=self._generate_proposal_id(),
            **proposal_data.model_dump(),
        )

        self.db.add(proposal)
        try:
            self.db.commit()
            self.db.refresh(proposal)
            return ProposalRead.model_validate(proposal)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao criar proposta",
            )

    def get_proposal(self, proposal_id: int) -> ProposalRead:
        """Busca proposta por ID."""
        proposal = self._proposal_or_404(proposal_id)
        return ProposalRead.model_validate(proposal)

    def update_proposal(self, proposal_id: int, proposal_data: ProposalUpdate) -> ProposalRead:
        """Atualiza proposta."""
        proposal = self._proposal_or_404(proposal_id)
        update_data = proposal_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(proposal, field, value)
        self.db.commit()
        self.db.refresh(proposal)
        return ProposalRead.model_validate(proposal)

    def list_proposals_by_lead(self, lead_id: int) -> list[ProposalRead]:
        """Lista propostas de um lead."""
        proposals = self.db.query(Proposal).filter(Proposal.lead_id == lead_id).all()
        return [ProposalRead.model_validate(proposal) for proposal in proposals]
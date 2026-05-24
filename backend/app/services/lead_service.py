from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadRead, LeadUpdate


class LeadService:
    def __init__(self, db: Session):
        self.db = db

    def _lead_or_404(self, lead_id: int) -> Lead:
        """Busca lead por ID ou lança 404."""
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead não encontrado",
            )
        return lead

    def create_lead(self, lead_data: LeadCreate) -> LeadRead:
        """Cria um novo lead."""
        lead = Lead(**lead_data.model_dump())
        self.db.add(lead)
        try:
            self.db.commit()
            self.db.refresh(lead)
            return LeadRead.model_validate(lead)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado",
            )

    def get_lead(self, lead_id: int) -> LeadRead:
        """Busca lead por ID."""
        lead = self._lead_or_404(lead_id)
        return LeadRead.model_validate(lead)

    def get_lead_by_email(self, email: str) -> LeadRead | None:
        """Busca lead por email."""
        lead = self.db.query(Lead).filter(Lead.email == email).first()
        if lead:
            return LeadRead.model_validate(lead)
        return None

    def update_lead(self, lead_id: int, lead_data: LeadUpdate) -> LeadRead:
        """Atualiza lead."""
        lead = self._lead_or_404(lead_id)
        update_data = lead_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(lead, field, value)
        self.db.commit()
        self.db.refresh(lead)
        return LeadRead.model_validate(lead)

    def list_leads(self, skip: int = 0, limit: int = 100) -> list[LeadRead]:
        """Lista leads com paginação."""
        leads = self.db.query(Lead).offset(skip).limit(limit).all()
        return [LeadRead.model_validate(lead) for lead in leads]
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProposalBase(BaseModel):
    lead_id: int
    proposal_type: str
    value: float
    status: str = "draft"
    content: Optional[str] = None
    file_path: Optional[str] = None


class ProposalCreate(ProposalBase):
    pass


class ProposalRead(ProposalBase):
    id: int
    proposal_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProposalUpdate(BaseModel):
    proposal_type: Optional[str] = None
    value: Optional[float] = None
    status: Optional[str] = None
    content: Optional[str] = None
    file_path: Optional[str] = None
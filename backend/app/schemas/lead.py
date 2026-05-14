from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime


class LeadBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    lead_source: str = "direct"
    stage: str = "lead"
    value: Optional[float] = None
    notes: Optional[str] = None


class LeadCreate(LeadBase):
    pass


class LeadRead(LeadBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    lead_source: Optional[str] = None
    stage: Optional[str] = None
    value: Optional[float] = None
    notes: Optional[str] = None

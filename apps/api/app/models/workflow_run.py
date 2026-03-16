import uuid

from sqlalchemy import ForeignKey, String, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class WorkflowRun(TimestampMixin, Base):
    __tablename__ = "workflow_runs"

    workflow_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    output: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    workflow = relationship("Workflow", back_populates="runs")
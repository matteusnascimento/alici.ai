from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.workflow import Workflow


def list_workflows(db: Session) -> list[Workflow]:
    return db.scalars(select(Workflow)).all()


def get_workflow(db: Session, workflow_id: UUID) -> Workflow | None:
    return db.get(Workflow, workflow_id)


def create_workflow(db: Session, payload: dict) -> Workflow:
    item = Workflow(**payload)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_workflow(db: Session, workflow: Workflow, payload: dict) -> Workflow:
    for key, value in payload.items():
        setattr(workflow, key, value)
    db.commit()
    db.refresh(workflow)
    return workflow


def delete_workflow(db: Session, workflow: Workflow) -> None:
    db.delete(workflow)
    db.commit()
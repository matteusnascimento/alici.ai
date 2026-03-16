from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.workflow import WorkflowCreate, WorkflowResponse, WorkflowUpdate
from app.services.workflow_service import create_workflow, delete_workflow, get_workflow, list_workflows, update_workflow

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("", response_model=list[WorkflowResponse])
def route_list(db: Session = Depends(get_db)):
    return list_workflows(db)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
def route_get(workflow_id: UUID, db: Session = Depends(get_db)):
    item = get_workflow(db, workflow_id)
    if not item:
        raise HTTPException(status_code=404, detail="not found")
    return item


@router.post("", response_model=WorkflowResponse)
def route_create(payload: WorkflowCreate, db: Session = Depends(get_db)):
    return create_workflow(db, payload.model_dump())


@router.put("/{workflow_id}", response_model=WorkflowResponse)
def route_update(workflow_id: UUID, payload: WorkflowUpdate, db: Session = Depends(get_db)):
    item = get_workflow(db, workflow_id)
    if not item:
        raise HTTPException(status_code=404, detail="not found")
    return update_workflow(db, item, payload.model_dump(exclude_unset=True))


@router.delete("/{workflow_id}")
def route_delete(workflow_id: UUID, db: Session = Depends(get_db)):
    item = get_workflow(db, workflow_id)
    if not item:
        raise HTTPException(status_code=404, detail="not found")
    delete_workflow(db, item)
    return {"ok": True}
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.knowledge import KnowledgeCreate, KnowledgeResponse, KnowledgeUpdate
from app.services.knowledge_service import create_document_with_chunks, delete_document, get_document, list_documents, update_document

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("", response_model=list[KnowledgeResponse])
def route_list(db: Session = Depends(get_db)):
    return list_documents(db)


@router.get("/{doc_id}", response_model=KnowledgeResponse)
def route_get(doc_id: UUID, db: Session = Depends(get_db)):
    item = get_document(db, doc_id)
    if not item:
        raise HTTPException(status_code=404, detail="not found")
    return item


@router.post("", response_model=KnowledgeResponse)
def route_create(payload: KnowledgeCreate, db: Session = Depends(get_db)):
    return create_document_with_chunks(db, payload.model_dump())


@router.put("/{doc_id}", response_model=KnowledgeResponse)
def route_update(doc_id: UUID, payload: KnowledgeUpdate, db: Session = Depends(get_db)):
    item = get_document(db, doc_id)
    if not item:
        raise HTTPException(status_code=404, detail="not found")
    return update_document(db, item, payload.model_dump(exclude_unset=True))


@router.delete("/{doc_id}")
def route_delete(doc_id: UUID, db: Session = Depends(get_db)):
    item = get_document(db, doc_id)
    if not item:
        raise HTTPException(status_code=404, detail="not found")
    delete_document(db, item)
    return {"ok": True}
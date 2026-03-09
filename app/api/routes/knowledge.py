"""Knowledge base routes: upload and query documents."""

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.services.auth_service import AuthService
from app.services.knowledge_service import KnowledgeService

router = APIRouter()
knowledge_service = KnowledgeService()


def _ok(data):
    return {"status": "success", "data": data, "error": None}


class KnowledgeQueryRequest(BaseModel):
    query: str
    top_k: int = 5


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    # WARNING: Uploaded file is read into memory and not persisted to disk.
    # For production deployments, replace in-memory handling with S3/R2/Supabase
    # storage before deploying at scale.
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    payload = await file.read()
    if not payload:
        raise HTTPException(status_code=400, detail="File is empty")

    try:
        text = knowledge_service.extract_text(file.filename, payload)
        document = knowledge_service.ingest_document(
            db=db,
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            filename=file.filename,
            text=text,
            title=title,
        )
        db.commit()
        db.refresh(document)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))

    data = {
        "document_id": document.id,
        "filename": document.filename,
        "file_type": document.file_type,
        "total_chunks": document.total_chunks,
    }
    return _ok(data)


@router.post("/query")
def query_documents(
    payload: KnowledgeQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    query = (payload.query or "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")

    chunks = knowledge_service.search_chunks(
        db=db,
        organization_id=current_user.organization_id,
        query=query,
        top_k=payload.top_k,
    )

    answer = knowledge_service.synthesize_answer(query, chunks)
    payload_data = {
        "query": query,
        "answer": answer,
        "references": [
            {
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "excerpt": chunk.content[:240],
            }
            for chunk in chunks
        ],
    }
    return _ok(payload_data)


@router.get("")
@router.get("/list")
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    docs = knowledge_service.list_documents(
        db=db,
        organization_id=current_user.organization_id,
        limit=200,
    )
    data = [
        {
            "id": doc.id,
            "title": doc.title,
            "filename": doc.filename,
            "file_type": doc.file_type,
            "total_chunks": doc.total_chunks,
            "created_at": doc.created_at,
        }
        for doc in docs
    ]
    return _ok({"documents": data})


@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user),
):
    deleted = knowledge_service.delete_document(
        db=db,
        organization_id=current_user.organization_id,
        document_id=document_id,
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")

    db.commit()
    return _ok({"deleted": True, "document_id": document_id})

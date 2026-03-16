from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge_document import KnowledgeDocument
from app.models.knowledge_chunk import KnowledgeChunk


def chunk_text(content: str, size: int = 300) -> list[str]:
    words = content.split()
    chunks = []
    current = []
    for word in words:
        current.append(word)
        if len(" ".join(current)) >= size:
            chunks.append(" ".join(current))
            current = []
    if current:
        chunks.append(" ".join(current))
    return chunks


def list_documents(db: Session) -> list[KnowledgeDocument]:
    return db.scalars(select(KnowledgeDocument)).all()


def get_document(db: Session, doc_id: UUID) -> KnowledgeDocument | None:
    return db.get(KnowledgeDocument, doc_id)


def create_document_with_chunks(db: Session, payload: dict) -> KnowledgeDocument:
    doc = KnowledgeDocument(**payload)
    db.add(doc)
    db.flush()

    for idx, chunk in enumerate(chunk_text(doc.content)):
        db.add(KnowledgeChunk(document_id=doc.id, chunk_index=idx, content=chunk))

    db.commit()
    db.refresh(doc)
    return doc


def update_document(db: Session, doc: KnowledgeDocument, payload: dict) -> KnowledgeDocument:
    for key, value in payload.items():
        setattr(doc, key, value)
    db.commit()
    db.refresh(doc)
    return doc


def delete_document(db: Session, doc: KnowledgeDocument) -> None:
    db.delete(doc)
    db.commit()
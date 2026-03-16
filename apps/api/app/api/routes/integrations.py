from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.integration import Integration

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("")
def list_items(db: Session = Depends(get_db)):
    return db.scalars(select(Integration)).all()


@router.get("/{item_id}")
def get_item(item_id: UUID, db: Session = Depends(get_db)):
    item = db.get(Integration, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="not found")
    return item


@router.post("")
def create_item(payload: dict, db: Session = Depends(get_db)):
    item = Integration(**payload)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}")
def update_item(item_id: UUID, payload: dict, db: Session = Depends(get_db)):
    item = db.get(Integration, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="not found")
    for k, v in payload.items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}")
def delete_item(item_id: UUID, db: Session = Depends(get_db)):
    item = db.get(Integration, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
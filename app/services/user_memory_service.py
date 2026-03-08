"""User memory extraction and retrieval service."""

import re
import uuid
from typing import Iterable, List

from sqlalchemy.orm import Session

from app.models import UserMemory


class UserMemoryService:
    """Stores lightweight long-term facts per user."""

    _PATTERNS: list[tuple[re.Pattern[str], str]] = [
        (re.compile(r"\bmeu restaurante abre as\s+([^\.;,!\n]+)", re.IGNORECASE), "restaurant_opening_hours"),
        (re.compile(r"\bmeu nome e\s+([^\.;,!\n]+)", re.IGNORECASE), "user_name"),
        (re.compile(r"\btrabalho com\s+([^\.;,!\n]+)", re.IGNORECASE), "user_profession"),
    ]

    def capture_from_message(self, db: Session, user_id: str, organization_id: str, message: str) -> list[UserMemory]:
        """Extract known fact patterns from a user message and persist them."""
        extracted: list[tuple[str, str]] = []
        normalized = (message or "").strip()
        if not normalized:
            return []

        for pattern, key in self._PATTERNS:
            match = pattern.search(normalized)
            if not match:
                continue
            value = match.group(1).strip()
            if value:
                extracted.append((key, value))

        created: list[UserMemory] = []
        for key, value in extracted:
            created.append(self.upsert_memory(db, user_id, organization_id, key, value))
        return created

    def upsert_memory(self, db: Session, user_id: str, organization_id: str, key: str, value: str) -> UserMemory:
        existing = (
            db.query(UserMemory)
            .filter(UserMemory.user_id == user_id, UserMemory.key == key)
            .first()
        )
        if existing:
            existing.value = value
            return existing

        memory = UserMemory(
            id=str(uuid.uuid4()),
            user_id=user_id,
            organization_id=organization_id,
            key=key,
            value=value,
        )
        db.add(memory)
        return memory

    def list_memory(self, db: Session, user_id: str, limit: int = 100) -> List[UserMemory]:
        return (
            db.query(UserMemory)
            .filter(UserMemory.user_id == user_id)
            .order_by(UserMemory.timestamp.desc())
            .limit(max(1, min(limit, 500)))
            .all()
        )

    def build_memory_context(self, memories: Iterable[UserMemory]) -> str:
        lines = []
        for item in memories:
            lines.append(f"- {item.key}: {item.value}")
        if not lines:
            return ""
        return "Known user facts:\n" + "\n".join(lines)

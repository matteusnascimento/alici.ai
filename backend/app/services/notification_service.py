from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationRead


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def list_notifications(self, user: User) -> list[NotificationRead]:
        rows = (
            self.db.query(Notification)
            .filter(Notification.user_id == user.id)
            .order_by(Notification.lida.asc(), Notification.horario.desc(), Notification.id.desc())
            .limit(50)
            .all()
        )
        return [NotificationRead.model_validate(item) for item in rows]

    def mark_read(self, user: User, notification_id: int) -> NotificationRead:
        notification = self._notification_or_404(user, notification_id)
        if not notification.lida:
            notification.lida = True
            notification.read_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(notification)
        return NotificationRead.model_validate(notification)

    def mark_all_read(self, user: User) -> list[NotificationRead]:
        rows = self.db.query(Notification).filter(Notification.user_id == user.id).all()
        now = datetime.now(timezone.utc)
        changed = False
        for notification in rows:
            if not notification.lida:
                notification.lida = True
                notification.read_at = now
                changed = True
        if changed:
            self.db.commit()
            for notification in rows:
                self.db.refresh(notification)
        return self.list_notifications(user)

    def _notification_or_404(self, user: User, notification_id: int) -> Notification:
        notification = (
            self.db.query(Notification)
            .filter(Notification.id == notification_id, Notification.user_id == user.id)
            .first()
        )
        if not notification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notificacao nao encontrada.")
        return notification

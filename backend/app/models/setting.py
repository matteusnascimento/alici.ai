from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    background_conversation: Mapped[bool] = mapped_column(Boolean, default=True)
    autocomplete: Mapped[bool] = mapped_column(Boolean, default=True)
    trending: Mapped[bool] = mapped_column(Boolean, default=True)
    sequence: Mapped[bool] = mapped_column(Boolean, default=False)
    split_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    language: Mapped[str] = mapped_column(String(20), default="pt-BR")
    voice: Mapped[str] = mapped_column(String(40), default="neutral")
    theme_mode: Mapped[str] = mapped_column(String(20), default="dark")
    accent_color: Mapped[str] = mapped_column(String(30), default="cyan")
    haptic_feedback: Mapped[bool] = mapped_column(Boolean, default=False)
    interface_animations: Mapped[bool] = mapped_column(Boolean, default=True)
    advanced_visual_effects: Mapped[bool] = mapped_column(Boolean, default=True)
    compact_menus: Mapped[bool] = mapped_column(Boolean, default=False)
    contextual_tips: Mapped[bool] = mapped_column(Boolean, default=True)
    confirm_critical_actions: Mapped[bool] = mapped_column(Boolean, default=True)
    open_last_module: Mapped[bool] = mapped_column(Boolean, default=True)
    autosave_filters: Mapped[bool] = mapped_column(Boolean, default=True)
    keyboard_shortcuts: Mapped[bool] = mapped_column(Boolean, default=True)
    show_quick_metrics: Mapped[bool] = mapped_column(Boolean, default=True)
    assistant_mode: Mapped[str] = mapped_column(String(30), default="automatico")
    assistant_response_detail: Mapped[str] = mapped_column(String(30), default="normais")
    assistant_tone: Mapped[str] = mapped_column(String(30), default="profissional")
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    push_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    product_updates: Mapped[bool] = mapped_column(Boolean, default=True)
    marketing_notifications: Mapped[bool] = mapped_column(Boolean, default=False)
    security_alerts: Mapped[bool] = mapped_column(Boolean, default=True)
    archived_chat_visibility: Mapped[bool] = mapped_column(Boolean, default=True)

    user = relationship("User", back_populates="settings")

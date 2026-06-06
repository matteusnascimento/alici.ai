from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class WebsiteEvent(Base):
    __tablename__ = "website_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    site_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    visitor_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    session_id: Mapped[str] = mapped_column(String(120), index=True)
    event_type: Mapped[str] = mapped_column(String(60), index=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    state: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    country: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    traffic_source: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    device: Mapped[str | None] = mapped_column(String(80), nullable=True)
    utm_source: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    utm_medium: Mapped[str | None] = mapped_column(String(120), nullable=True)
    utm_campaign: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    utm_term: Mapped[str | None] = mapped_column(String(160), nullable=True)
    utm_content: Mapped[str | None] = mapped_column(String(160), nullable=True)
    page_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    referrer: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    pages_visited: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    search_query: Mapped[str | None] = mapped_column(String(255), nullable=True)
    click_target: Mapped[str | None] = mapped_column(String(255), nullable=True)
    quote_value: Mapped[float | None] = mapped_column(Float(), nullable=True)
    reservation_value: Mapped[float | None] = mapped_column(Float(), nullable=True)
    payload_json: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

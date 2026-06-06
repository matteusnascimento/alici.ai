from __future__ import annotations

from collections import defaultdict
import json

from sqlalchemy.orm import Session

from app.models.website_event import WebsiteEvent
from app.schemas.tracker import TrackerSummaryItem, WebsiteEventCreate, WebsiteEventRead


class WebsiteTrackerService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _safe_json(payload: dict[str, object]) -> str:
        return json.dumps(payload, ensure_ascii=True, default=str)

    def record_event(self, payload: WebsiteEventCreate) -> WebsiteEventRead:
        event = WebsiteEvent(
            site_id=payload.site_id,
            visitor_id=payload.visitor_id,
            session_id=payload.session_id,
            event_type=payload.event_type,
            city=payload.city,
            state=payload.state,
            country=payload.country,
            traffic_source=payload.traffic_source,
            device=payload.device,
            utm_source=payload.utm_source,
            utm_medium=payload.utm_medium,
            utm_campaign=payload.utm_campaign,
            utm_term=payload.utm_term,
            utm_content=payload.utm_content,
            page_url=payload.page_url,
            referrer=payload.referrer,
            duration_seconds=payload.duration_seconds,
            pages_visited=payload.pages_visited,
            search_query=payload.search_query,
            click_target=payload.click_target,
            quote_value=payload.quote_value,
            reservation_value=payload.reservation_value,
            payload_json=self._safe_json(payload.metadata),
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return WebsiteEventRead(id=event.id, status="accepted", event_type=event.event_type, session_id=event.session_id)

    def origin_demand(self) -> list[TrackerSummaryItem]:
        rows = self.db.query(WebsiteEvent).all()
        buckets: dict[tuple[str, str, str, str], dict[str, object]] = defaultdict(
            lambda: {
                "sessions": set(),
                "buscas": 0,
                "cotacoes": 0,
                "reservas": 0,
                "receita": 0.0,
            }
        )
        for event in rows:
            channel = event.traffic_source or event.utm_source or "Website"
            key = (event.city or "", event.state or "", event.country or "", channel)
            bucket = buckets[key]
            bucket["sessions"].add(event.visitor_id or event.session_id)  # type: ignore[union-attr]
            if event.event_type in {"search", "busca"}:
                bucket["buscas"] = int(bucket["buscas"]) + 1
            if event.event_type in {"quote", "cotacao", "quotation"}:
                bucket["cotacoes"] = int(bucket["cotacoes"]) + 1
            if event.event_type in {"reservation", "reserva", "booking"}:
                bucket["reservas"] = int(bucket["reservas"]) + 1
                bucket["receita"] = float(bucket["receita"]) + float(event.reservation_value or event.quote_value or 0.0)

        result: list[TrackerSummaryItem] = []
        for (city, state, country, channel), bucket in buckets.items():
            visitantes = len(bucket["sessions"])  # type: ignore[arg-type]
            reservas = int(bucket["reservas"])
            result.append(
                TrackerSummaryItem(
                    city=city or None,
                    state=state or None,
                    country=country or None,
                    channel=channel,
                    visitantes=visitantes,
                    buscas=int(bucket["buscas"]),
                    cotacoes=int(bucket["cotacoes"]),
                    reservas=reservas,
                    receita=round(float(bucket["receita"]), 2),
                    conversao=round((reservas * 100 / visitantes), 2) if visitantes else 0.0,
                )
            )
        return sorted(result, key=lambda item: (item.receita, item.reservas, item.visitantes), reverse=True)

from pydantic import BaseModel, Field


class WebsiteEventCreate(BaseModel):
    site_id: str | None = None
    session_id: str
    event_type: str = Field(default="page_view")
    city: str | None = None
    state: str | None = None
    country: str | None = None
    traffic_source: str | None = None
    device: str | None = None
    utm_source: str | None = None
    utm_medium: str | None = None
    utm_campaign: str | None = None
    page_url: str | None = None
    referrer: str | None = None
    duration_seconds: int | None = None
    pages_visited: int | None = None
    click_target: str | None = None
    quote_value: float | None = None
    reservation_value: float | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class WebsiteEventRead(BaseModel):
    id: int
    status: str
    event_type: str
    session_id: str


class TrackerSummaryItem(BaseModel):
    city: str | None = None
    state: str | None = None
    country: str | None = None
    channel: str
    visitantes: int
    buscas: int
    cotacoes: int
    reservas: int
    receita: float
    conversao: float

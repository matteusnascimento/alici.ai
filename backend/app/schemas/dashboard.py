from pydantic import BaseModel


class UsageBar(BaseModel):
    label: str
    value: int


class DashboardStats(BaseModel):
    total_messages: int
    total_agents: int
    revenue: float
    conversions: int
    clicks: int
    quotes: int
    usage_bars: list[UsageBar]


class DashboardOverview(BaseModel):
    total_messages: int
    total_agents: int
    active_agents: int
    current_plan: str


class DashboardUsage(BaseModel):
    messages_used: int
    messages_limit: int
    agents_used: int
    agents_limit: int


class DashboardMetricItem(BaseModel):
    key: str
    value: float


class DashboardMetrics(BaseModel):
    items: list[DashboardMetricItem]


class DashboardAIHealth(BaseModel):
    provider: str
    status: str
    model: str
    latency_ms: float
    error_type: str | None = None
    status_code: int | None = None


class DashboardAIMetrics(BaseModel):
    window: str
    total_requests: int
    success_requests: int
    error_requests: int
    rate_limit_429: int
    avg_latency_ms: float
    trend: list[UsageBar]
    trend_429: list[UsageBar]

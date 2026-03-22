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

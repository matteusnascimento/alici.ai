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

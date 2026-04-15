from pydantic import BaseModel


class RevenueSummary(BaseModel):
    receita_total: float
    reservas_fechadas: int
    ticket_medio: float
    conversao_total: float
    leads_recebidos: int
    roi_estimado: float
    remarketing_recuperado: float
    agentes_gerando_receita: int


class RevenueReservationItem(BaseModel):
    reserva: str
    cliente: str
    canal: str
    origem: str
    valor: float
    status: str
    agente_responsavel: str


class RevenueRemarketing(BaseModel):
    leads_em_remarketing: int
    leads_reativados: int
    reservas_recuperadas: int
    receita_recuperada: float
    taxa_recuperacao: float
    campanha_mais_forte: str


class RevenueFunnelStep(BaseModel):
    etapa: str
    total: int


class RevenueBreakdownItem(BaseModel):
    label: str
    valor: float


class RevenueOpportunityStatusItem(BaseModel):
    status: str
    total: int


class RevenueIntelligenceSnapshot(BaseModel):
    summary: RevenueSummary
    reservas: list[RevenueReservationItem]
    remarketing: RevenueRemarketing
    funil: list[RevenueFunnelStep]
    receita_por_canal: list[RevenueBreakdownItem]
    receita_por_agente: list[RevenueBreakdownItem]
    status_oportunidades: list[RevenueOpportunityStatusItem]


class RevenueSeriesPoint(BaseModel):
    label: str
    start_date: str
    end_date: str | None = None
    receita: float
    reservas_fechadas: int


class RevenueSeriesResponse(BaseModel):
    days: int
    granularity: str
    points: list[RevenueSeriesPoint]

from pydantic import BaseModel, ConfigDict, Field


class MarketingCampaignRequest(BaseModel):
    company_name: str
    audience: str
    objective: str
    offer: str
    tone: str = "premium"


class MarketingCampaignResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    campaign: str
    copy_text: str = Field(serialization_alias="copy")
    cta: str
    ad_structure: str
    creative_suggestion: str


class MarketingTool(BaseModel):
    id: str
    name: str
    description: str
    active: bool = True


class MarketingProjectCreate(BaseModel):
    name: str
    audience: str
    objective: str
    offer: str
    tone: str = "premium"
    notes: str | None = None


class MarketingProjectRead(BaseModel):
    id: int
    name: str
    audience: str
    objective: str
    offer: str
    tone: str
    notes: str | None = None
    created_at: str


class MarketingProjectUpdate(BaseModel):
    name: str | None = None
    audience: str | None = None
    objective: str | None = None
    offer: str | None = None
    tone: str | None = None
    notes: str | None = None


class MarketingCopyRequest(BaseModel):
    prompt: str


class MarketingCopyResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    copy_text: str = Field(serialization_alias="copy")


class MarketingImagePromptResponse(BaseModel):
    prompt: str


class MarketingContentRequest(BaseModel):
    project_id: int
    context: str
    type: str = "social_post"


class MarketingContentResponse(BaseModel):
    copies: list[str]
    cta: str
    hook: str
    hashtags: list[str] = Field(default_factory=list)


class MarketingDataStatus(BaseModel):
    status: str = "empty"
    message: str


class MarketingKpiRead(BaseModel):
    key: str
    label: str
    value: float | None = None
    variation: float | None = None
    status: str = "empty"
    message: str


class MarketingOverviewResponse(BaseModel):
    status: str
    projects_count: int
    kpis: list[MarketingKpiRead]
    message: str


class MarketingSeriesPoint(BaseModel):
    label: str
    receita: float | None = None
    investimento: float | None = None


class MarketingRevenueInvestmentResponse(BaseModel):
    status: str
    points: list[MarketingSeriesPoint] = Field(default_factory=list)
    message: str


class MarketingChannelRevenueRead(BaseModel):
    channel: str
    receita: float | None = None
    percentual: float | None = None
    roas: float | None = None
    leads: int | None = None
    reservas: int | None = None


class MarketingChannelRevenueResponse(BaseModel):
    status: str
    channels: list[MarketingChannelRevenueRead] = Field(default_factory=list)
    message: str


class MarketingFunnelStepRead(BaseModel):
    stage: str
    count: int | None = None
    conversion_rate: float | None = None
    amount: float | None = None


class MarketingFunnelResponse(BaseModel):
    status: str
    stages: list[MarketingFunnelStepRead] = Field(default_factory=list)
    message: str


class MarketingCampaignListItem(BaseModel):
    id: int
    name: str
    objective: str
    audience: str
    status: str
    source: str


class MarketingCampaignListResponse(BaseModel):
    status: str
    campaigns: list[MarketingCampaignListItem] = Field(default_factory=list)
    message: str

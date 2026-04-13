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

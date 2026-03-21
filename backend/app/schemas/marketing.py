from pydantic import BaseModel


class MarketingCampaignRequest(BaseModel):
    company_name: str
    audience: str
    objective: str
    offer: str
    tone: str = "premium"


class MarketingCampaignResponse(BaseModel):
    campaign: str
    copy: str
    cta: str
    ad_structure: str
    creative_suggestion: str

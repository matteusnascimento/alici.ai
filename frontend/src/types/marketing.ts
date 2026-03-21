export interface MarketingCampaignInput {
  company_name: string;
  audience: string;
  objective: string;
  offer: string;
  tone: string;
}

export interface MarketingCampaignResult {
  campaign: string;
  copy: string;
  cta: string;
  ad_structure: string;
  creative_suggestion: string;
}

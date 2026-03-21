import { apiFetch } from './api';
import type { MarketingCampaignInput, MarketingCampaignResult } from '../types/marketing';

export function generateCampaign(payload: MarketingCampaignInput) {
  return apiFetch<MarketingCampaignResult>('/marketing/campaign', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

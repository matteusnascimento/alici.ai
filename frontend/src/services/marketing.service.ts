import { apiFetch } from './api';
import type {
  MarketingCampaignInput,
  MarketingCampaignList,
  MarketingCampaignResult,
  MarketingDataStatus,
  MarketingFunnel,
  MarketingKpi,
  MarketingOverview,
  MarketingProject,
  MarketingProjectCreate,
  MarketingProjectUpdate,
} from '../types/marketing';

interface MarketingCampaignApiResponse {
  campaign: string;
  copy?: string;
  copy_text?: string;
  cta: string;
  ad_structure: string;
  creative_suggestion: string;
}

export function generateCampaign(payload: MarketingCampaignInput) {
  return apiFetch<MarketingCampaignApiResponse>('/marketing/campaign', {
    method: 'POST',
    body: JSON.stringify({
      company_name: payload.business_name,
      audience: payload.target_audience,
      objective: payload.campaign_goal,
      offer: payload.offer,
      tone: payload.tone,
    }),
  }).then((response): MarketingCampaignResult => {
    const primaryCopy = response.copy ?? response.copy_text ?? '';
    return {
      campaign_headline: response.campaign,
      primary_copy: primaryCopy,
      secondary_copy: response.ad_structure,
      cta_suggestions: [response.cta],
      offer_angle: response.ad_structure,
      pain_points: [],
      objections: [],
      positioning_summary: response.campaign,
      creative_suggestion: response.creative_suggestion,
    };
  });
}

export function listProjects(): Promise<MarketingProject[]> {
  return apiFetch<MarketingProject[]>('/marketing/projects');
}

export function getMarketingOverview(): Promise<MarketingOverview> {
  return apiFetch<MarketingOverview>('/marketing/overview');
}

export function getMarketingKpis(): Promise<MarketingKpi[]> {
  return apiFetch<MarketingKpi[]>('/marketing/kpis');
}

export function listCampaigns(): Promise<MarketingCampaignList> {
  return apiFetch<MarketingCampaignList>('/marketing/campaigns');
}

export function getMarketingFunnel(): Promise<MarketingFunnel> {
  return apiFetch<MarketingFunnel>('/marketing/funnel');
}

export function listMarketingResource(resource: 'action-plans' | 'calendar' | 'content' | 'audiences' | 'automations' | 'reports' | 'insights') {
  return apiFetch<MarketingDataStatus[]>(`/marketing/${resource}`);
}

export function createProject(data: MarketingProjectCreate): Promise<MarketingProject> {
  return apiFetch<MarketingProject>('/marketing/projects', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export function getProject(id: number): Promise<MarketingProject> {
  return apiFetch<MarketingProject>(`/marketing/projects/${id}`);
}

export function updateProject(id: number, data: MarketingProjectUpdate): Promise<MarketingProject> {
  return apiFetch<MarketingProject>(`/marketing/projects/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export function deleteProject(id: number): Promise<void> {
  return apiFetch<void>(`/marketing/projects/${id}`, { method: 'DELETE' });
}

export function generateCopy(projectId: number, context: string, type: string = 'social_post') {
  return apiFetch<{ copies: string[]; cta: string; hook: string; hashtags: string[] }>('/marketing/generate-content', {
    method: 'POST',
    body: JSON.stringify({ project_id: projectId, context, type }),
  });
}

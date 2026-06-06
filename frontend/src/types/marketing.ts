export type MarketingSectionId =
  | 'campaigns'
  | 'creatives'
  | 'content-planner'
  | 'posts-copy'
  | 'funnels'
  | 'whatsapp'
  | 'landing-pages'
  | 'templates'
  | 'analytics';

export interface MarketingProject {
  id: number;
  name: string;
  audience: string;
  objective: string;
  offer: string;
  tone: string;
  channels?: string | null;
  budget?: number | null;
  creative_project_id?: string | null;
  status?: string;
  published_at?: string | null;
  last_publish_error?: string | null;
  notes?: string | null;
  created_at: string;
}

export interface MarketingKpi {
  key: string;
  label: string;
  value?: number | null;
  variation?: number | null;
  status: string;
  message: string;
}

export interface MarketingOverview {
  status: string;
  projects_count: number;
  kpis: MarketingKpi[];
  message: string;
}

export interface MarketingDataStatus {
  status: string;
  message: string;
}

export interface MarketingAudience {
  id: number;
  name: string;
  city?: string | null;
  state?: string | null;
  country?: string | null;
  ticket?: string | null;
  source?: string | null;
  reservations?: string | null;
  behavior?: string | null;
  created_at: string;
}

export type MarketingAudienceCreate = Omit<MarketingAudience, 'id' | 'created_at'>;

export interface MarketingCalendarEvent {
  id: number;
  title: string;
  date: string;
  channel?: string | null;
  status: string;
  notes?: string | null;
  created_at: string;
}

export type MarketingCalendarEventCreate = Omit<MarketingCalendarEvent, 'id' | 'created_at'>;

export interface MarketingCampaignListItem {
  id: number;
  name: string;
  objective: string;
  audience: string;
  status: string;
  source: string;
  channels?: string | null;
  budget?: number | null;
  last_publish_error?: string | null;
}

export interface MarketingCampaignList {
  status: string;
  campaigns: MarketingCampaignListItem[];
  message: string;
}

export interface MarketingFunnel {
  status: string;
  stages: Array<{
    stage: string;
    count?: number | null;
    conversion_rate?: number | null;
    amount?: number | null;
  }>;
  message: string;
}

export interface MarketingProjectCreate {
  name: string;
  audience: string;
  objective: string;
  offer: string;
  tone?: string;
  channels?: string | null;
  budget?: number | null;
  creative_project_id?: string | null;
  status?: string;
  notes?: string;
}

export interface MarketingProjectUpdate {
  name?: string;
  audience?: string;
  objective?: string;
  offer?: string;
  tone?: string;
  channels?: string | null;
  budget?: number | null;
  creative_project_id?: string | null;
  status?: string;
  notes?: string;
}

export interface MarketingTemplateProfile {
  businessName: string;
  marketSegment: string;
  audience: string;
  offer: string;
  tone: string;
  platform: string;
}

export interface MarketingCampaignInput {
  business_name: string;
  market_segment: string;
  target_audience: string;
  campaign_goal: string;
  offer: string;
  tone: string;
  channel: string;
  campaign_type: string;
  budget_range: string;
  call_to_action: string;
}

export interface MarketingCampaignResult {
  campaign_headline: string;
  primary_copy: string;
  secondary_copy: string;
  cta_suggestions: string[];
  offer_angle: string;
  pain_points: string[];
  objections: string[];
  positioning_summary: string;
  creative_suggestion: string;
}

export interface CreativeIdeasInput {
  niche: string;
  audience: string;
  objective: string;
  platform: string;
  tone: string;
}

export interface CreativeIdea {
  title: string;
  concept: string;
  hook: string;
  cta: string;
}

export interface ContentPlanInput {
  business_type: string;
  target_audience: string;
  goal: string;
  frequency_per_week: string;
  content_pillars: string;
  timeframe: string;
  platform: string;
}

export interface ContentPlanResult {
  weekly_plan: string[];
  monthly_plan: string[];
  content_pillar_breakdown: string[];
  posting_suggestions: string[];
  campaign_dates: string[];
  grouped_ideas: Record<'attraction' | 'authority' | 'conversion' | 'retention', string[]>;
}

export interface PostCopyInput {
  content_type: string;
  audience: string;
  goal: string;
  product_service: string;
  tone: string;
  cta: string;
}

export interface PostCopyResult {
  main_copy: string;
  variations: string[];
  cta_lines: string[];
  hashtags: string[];
  hook_suggestion: string;
}

export interface FunnelInput {
  business: string;
  offer: string;
  target_audience: string;
  acquisition_channel: string;
  funnel_objective: string;
}

export interface FunnelStage {
  stage: string;
  content: string;
  messaging_goal: string;
  cta: string;
  objections: string;
  nurturing: string;
}

export interface FunnelResult {
  stages: FunnelStage[];
}

export interface WhatsAppFlowInput {
  business_type: string;
  customer_stage: string;
  objective: string;
  tone: string;
  offer: string;
}

export interface WhatsAppFlowResult {
  sequence: string[];
  follow_up_timing: string[];
  variations: string[];
  human_version: string;
  direct_version: string;
}

export interface LandingPageInput {
  business: string;
  audience: string;
  offer: string;
  promise: string;
  tone: string;
  cta_objective: string;
}

export interface LandingPageResult {
  hero_title: string;
  subtitle: string;
  benefit_bullets: string[];
  offer_section: string;
  objections_section: string[];
  faq: string[];
  final_cta: string;
  proof_section: string;
}

export interface MarketingTemplate {
  id: string;
  title: string;
  niche: string;
  description: string;
  included_assets: string[];
  profile: MarketingTemplateProfile;
}

export interface MarketingAnalytics {
  cards: Array<{ label: string; value: string; change: string }>;
  engagement_trend: Array<{ week: string; value: number }>;
  content_output_by_week: Array<{ week: string; posts: number }>;
  channel_usage: Array<{ channel: string; percentage: number }>;
  conversion_by_campaign_type: Array<{ type: string; percentage: number }>;
}

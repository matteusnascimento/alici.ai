export type StudioSection = 'create' | 'manage' | 'brand' | 'projects' | 'edit' | 'content';

export interface StudioNavItem {
  key: string;
  label: string;
  route: string;
  section: StudioSection;
}

export interface StudioProject {
  id: number;
  user_id: number;
  project_type: string;
  title: string;
  status: string;
  metadata: Record<string, unknown>;
  canvas_data: Record<string, unknown>;
  layers: Array<Record<string, unknown>>;
  timeline_data: Record<string, unknown>;
  export_settings: Record<string, unknown>;
  preview_thumbnail_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface StudioVersion {
  id: number;
  user_id: number;
  project_id: number;
  label: string;
  canvas_data: Record<string, unknown>;
  layers: Array<Record<string, unknown>>;
  timeline_data: Record<string, unknown>;
  created_at: string;
}

export interface StudioAsset {
  id: number;
  user_id: number;
  project_id: number | null;
  asset_type: string;
  name: string;
  file_url: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface StudioTemplate {
  id: number;
  user_id: number | null;
  name: string;
  category: string;
  style_tag: string | null;
  template_data: Record<string, unknown>;
  preview_url: string | null;
  is_public: boolean;
  created_at: string;
}

export interface StudioTemplateCatalogItem {
  id: string;
  name: string;
  category: string;
  type: 'photo' | 'video' | 'social' | 'ad';
  thumbnail_url: string | null;
  preview_video_url: string | null;
  premium: boolean;
  template_json: Record<string, unknown>;
}

export interface StudioExport {
  id: number;
  user_id: number;
  project_id: number;
  export_type: string;
  file_url: string;
  status: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface StudioGenerateResponse {
  generation_id: number;
  status: string;
  result: Record<string, unknown>;
}

export interface StudioRecentProjectItem {
  id: number;
  title: string;
  project_type: string;
  status: string;
  updated_at: string;
  thumbnail_url: string | null;
}

export interface StudioRecentExportItem {
  id: number;
  project_id: number;
  project_title: string;
  file_name: string;
  export_type: string;
  source: string;
  file_url: string;
  created_at: string;
}

export interface StudioBrandSummary {
  logos_count: number;
  templates_count: number;
  palettes_count: number;
  assets_count: number;
}

export interface StudioOverviewResponse {
  recent_projects: StudioRecentProjectItem[];
  recent_exports: StudioRecentExportItem[];
  brand_summary: StudioBrandSummary;
  suggested_actions: Array<{
    id: string;
    label: string;
    description: string;
    route: string;
  }>;
}

export interface StudioToolActionResponse {
  project: StudioProject;
  generation: StudioGenerateResponse | null;
  message: string;
}

export interface StudioWebImage {
  id: string;
  provider: 'pexels' | 'unsplash';
  title: string;
  image_url: string;
  thumb_url: string;
  author_name: string | null;
  author_url: string | null;
  source_url: string;
}

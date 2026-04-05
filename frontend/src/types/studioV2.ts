export type StudioSection = 'create' | 'edit' | 'content' | 'brand' | 'projects';

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

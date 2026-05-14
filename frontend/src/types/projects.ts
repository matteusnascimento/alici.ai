import type { StudioToolType } from './studio';

export interface StudioProject {
  id: string;
  type: StudioToolType;
  title: string;
  description: string;
  route: string;
  created_at: string;
  updated_at: string;
  input_data: Record<string, unknown>;
  output_data: Record<string, unknown>;
  metadata: Record<string, unknown>;
  preview: string;
}

export interface SaveProjectPayload {
  type: StudioToolType;
  title: string;
  description: string;
  route: string;
  input_data: Record<string, unknown>;
  output_data: Record<string, unknown>;
  metadata?: Record<string, unknown>;
  preview?: string;
}

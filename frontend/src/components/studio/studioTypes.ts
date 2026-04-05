import type { LucideIcon } from 'lucide-react';

export type StudioToolId =
  | 'ads'
  | 'product-photos'
  | 'poster-ai'
  | 'ai-generator'
  | 'ai-media'
  | 'ai-avatar'
  | 'photo-editor'
  | 'photo-tools'
  | 'remove-bg'
  | 'retouch'
  | 'enhance'
  | 'captions'
  | 'teleprompter'
  | 'audio-tools'
  | 'speed-adjust'
  | 'scripts-hooks'
  | 'marketing-tools'
  | 'projects'
  | 'library'
  | 'cloud-space';

export interface StudioTool {
  id: StudioToolId;
  title: string;
  description: string;
  category: 'Create / Generate' | 'Photo / Image' | 'Video / Content' | 'Business / Workspace';
  icon: LucideIcon;
}

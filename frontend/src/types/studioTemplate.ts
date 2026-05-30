export type StudioTemplateFieldType = 'text' | 'image' | 'color' | 'video' | 'logo' | 'cta' | 'background';
export type StudioTemplatePlan = 'free' | 'premium';
export type StudioTemplateProjectType = 'story' | 'reel' | 'video' | 'poster' | 'document' | 'presentation' | 'email' | 'landing';

export interface StudioTemplateField {
  id: string;
  label: string;
  type: StudioTemplateFieldType;
  defaultValue: string;
}

export interface StudioLayerFilters {
  brightness?: number;
  contrast?: number;
  saturate?: number;
  blur?: number;
  grayscale?: number;
  sepia?: number;
  hueRotate?: number;
  opacity?: number;
}

export interface StudioTemplateLayer {
  id: string;
  type: 'image' | 'video' | 'text' | 'shape' | 'logo';
  field?: string;
  shape?: 'rectangle' | 'circle';
  x: number;
  y: number;
  width?: number;
  height?: number;
  opacity?: number;
  fill?: string;
  fontSize?: number;
  fontWeight?: number;
  color?: string;
  borderRadius?: number;
  filters?: StudioLayerFilters;
  effect?: string | null;
}

export interface StudioTemplateCanvas {
  width: number;
  height: number;
  background: string;
  layers: StudioTemplateLayer[];
}

export interface StudioTemplateDefinition {
  id: string;
  name: string;
  category: string;
  type: StudioTemplateProjectType;
  format: string;
  plan: StudioTemplatePlan;
  thumbnail: string;
  tags: string[];
  fields: StudioTemplateField[];
  canvas: StudioTemplateCanvas;
  source: 'mine' | 'premium' | 'recommended';
}

export type StudioTemplate = StudioTemplateDefinition & {
  layers: StudioTemplateLayer[];
};

export interface StudioProjectFromTemplate {
  id: string;
  templateId: string;
  name: string;
  type: StudioTemplateProjectType;
  format: string;
  fields: Record<string, string>;
  canvas: StudioTemplateCanvas;
  selectedEffects: string[];
  createdAt: string;
  updatedAt: string;
}

export interface StudioEffectDefinition {
  id: string;
  label: string;
  group: 'image-filter' | 'image-adjustment' | 'image-advanced' | 'text-effect' | 'video-transition' | 'video-motion' | 'video-color' | 'video-text' | 'video-overlay' | 'magic';
  target: 'image' | 'text' | 'video' | 'project';
  cssFilters?: StudioLayerFilters;
  previewClass?: string;
  status?: 'available' | 'coming_soon';
}

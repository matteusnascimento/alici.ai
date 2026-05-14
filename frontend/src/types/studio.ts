export type StudioToolType =
  | 'ads'
  | 'product-photos'
  | 'poster'
  | 'photo-editor'
  | 'remove-background'
  | 'retouch'
  | 'auto-enhance'
  | 'captions'
  | 'audio-tools'
  | 'teleprompter'
  | 'marketing-tools'
  | 'projects'
  | 'library'
  | 'cloud';

export interface AdsInput {
  businessName: string;
  segment: string;
  targetAudience: string;
  productService: string;
  offer: string;
  objective: string;
  tone: string;
  platform: string;
  campaignType: string;
  budgetRange: string;
  cta: string;
}

export interface AdsOutput {
  campaignHeadline: string;
  mainCopy: string;
  shortCopyVariation: string;
  ctaSuggestions: string[];
  creativeAngle: string;
  hookIdeas: string[];
  painPoints: string[];
  objections: string[];
  positioningSummary: string;
}

export interface ProductPhotosInput {
  productType: string;
  visualStyle: string;
  backgroundStyle: string;
  outputFormat: string;
  platformDestination: string;
  prompt: string;
  uploads: Array<{ name: string; size: number; type: string }>;
}

export interface ProductPhotosOutput {
  previews: string[];
  styleVariations: string[];
  exportFormats: string[];
}

export interface PosterInput {
  title: string;
  subtitle: string;
  offer: string;
  eventOrProduct: string;
  cta: string;
  style: string;
  targetAudience: string;
  sizeFormat: string;
}

export interface PosterOutput {
  posterBrief: string;
  layoutSuggestion: string;
  headlineHierarchy: string[];
  colorStyleRecommendation: string;
  exportBlock: string;
}

export interface PhotoEditorInput {
  uploads: Array<{ name: string; size: number; type: string }>;
  selectedTool: string;
  settings: Record<string, number | string | boolean>;
}

export interface PhotoEditorOutput {
  history: string[];
  processedPreview: string;
}

export interface RemoveBackgroundInput {
  uploads: Array<{ name: string; size: number; type: string }>;
}

export interface RemoveBackgroundOutput {
  summary: string;
  processedPreview: string;
}

export interface RetouchInput {
  uploads: Array<{ name: string; size: number; type: string }>;
  retouchMode: string;
  intensity: number;
  cleanupMode: string;
}

export interface RetouchOutput {
  beforeAfterSummary: string;
  processedPreview: string;
}

export interface AutoEnhanceInput {
  uploads: Array<{ name: string; size: number; type: string }>;
  enhancementMode: string;
  outputSize: string;
}

export interface AutoEnhanceOutput {
  enhancementsApplied: string[];
  processedPreview: string;
}

export interface CaptionsInput {
  mediaName: string;
  language: string;
  tone: string;
  captionType: string;
  outputFormat: string;
}

export interface CaptionsOutput {
  subtitleBlocks: string[];
  captionText: string;
  socialCaptionSuggestion: string;
  exportText: string;
}

export interface AudioToolsInput {
  objective: string;
  audience: string;
  duration: string;
  tone: string;
  platform: string;
}

export interface AudioToolsOutput {
  audioScript: string;
  narrationSequence: string[];
  ctaEnding: string;
  speakingGuide: string;
}

export interface TeleprompterInput {
  scriptText: string;
  readingSpeedWpm: number;
  sections: string;
  recordingMode: string;
}

export interface TeleprompterOutput {
  formattedScriptBlocks: string[];
  timingEstimateMinutes: number;
  segmentedReadingBlocks: string[];
}

export interface MarketingToolsInput {
  tab: 'campaigns' | 'copy' | 'funnels' | 'whatsapp' | 'content-planner';
  context: string;
}

export interface MarketingToolsOutput {
  lines: string[];
}

export interface LibraryTemplate {
  id: string;
  title: string;
  category: string;
  description: string;
  targetToolRoute: string;
  presetData: Record<string, unknown>;
}

export interface CloudAsset {
  id: string;
  name: string;
  category: string;
  sizeKb: number;
  linkedProjectId?: string;
}

import { apiFetch } from './api';
import type {
  StudioAsset,
  StudioBrandSummary,
  StudioExport,
  StudioGenerateResponse,
  StudioOverviewResponse,
  StudioProject,
  StudioRecentExportItem,
  StudioRecentProjectItem,
  StudioTemplate,
  StudioTemplateCatalogItem,
  StudioToolActionResponse,
  StudioWebImage,
  StudioVersion,
} from '../types/studioV2';

export function getStudioOverview() {
  return apiFetch<StudioOverviewResponse>('/studio/overview');
}

export function listStudioRecentProjects(limit = 6) {
  return apiFetch<StudioRecentProjectItem[]>(`/studio/projects/recent?limit=${limit}`);
}

export function listStudioRecentExports(limit = 6) {
  return apiFetch<StudioRecentExportItem[]>(`/studio/exports/recent?limit=${limit}`);
}

export function getStudioBrandSummary() {
  return apiFetch<StudioBrandSummary>('/studio/brand/summary');
}

export function listStudioProjects() {
  return apiFetch<StudioProject[]>('/studio/projects');
}

export function createStudioProject(payload: {
  project_type: string;
  title: string;
  metadata?: Record<string, unknown>;
  canvas_data?: Record<string, unknown>;
  layers?: Array<Record<string, unknown>>;
  timeline_data?: Record<string, unknown>;
  export_settings?: Record<string, unknown>;
  preview_thumbnail_url?: string;
}) {
  return apiFetch<StudioProject>('/studio/projects', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getStudioProject(projectId: number) {
  return apiFetch<StudioProject>(`/studio/projects/${projectId}`);
}

export function updateStudioProject(projectId: number, payload: Record<string, unknown>) {
  return apiFetch<StudioProject>(`/studio/projects/${projectId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export function saveStudioProject(projectId: number, payload: Record<string, unknown>) {
  return apiFetch<StudioProject>(`/studio/projects/${projectId}/save`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function duplicateStudioProject(projectId: number) {
  return apiFetch<StudioProject>(`/studio/projects/${projectId}/duplicate`, { method: 'POST' });
}

export function listStudioVersions(projectId: number) {
  return apiFetch<StudioVersion[]>(`/studio/projects/${projectId}/versions`);
}

export function createStudioVersion(projectId: number, payload: { label: string; canvas_data?: Record<string, unknown>; layers?: Array<Record<string, unknown>>; timeline_data?: Record<string, unknown> }) {
  return apiFetch<StudioVersion>(`/studio/projects/${projectId}/versions`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function exportStudioProject(projectId: number, payload: { export_type: 'png' | 'jpg' | 'webp' | 'mp4' | 'pdf' | 'zip'; options?: Record<string, unknown> }) {
  return apiFetch<StudioExport>(`/studio/projects/${projectId}/export`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function listStudioExports(projectId?: number) {
  const suffix = projectId ? `?project_id=${projectId}` : '';
  return apiFetch<StudioExport[]>(`/studio/exports${suffix}`);
}

function generate(path: string, payload: Record<string, unknown>) {
  return apiFetch<StudioGenerateResponse>(`/studio/generate/${path}`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export const studioGeneratePoster = (payload: Record<string, unknown>) => generate('poster', payload);
export const studioGenerateStory = (payload: Record<string, unknown>) => generate('story', payload);
export const studioGenerateBanner = (payload: Record<string, unknown>) => generate('banner', payload);
export const studioGenerateAdCopy = (payload: Record<string, unknown>) => generate('ad-copy', payload);
export const studioGenerateHeadline = (payload: Record<string, unknown>) => generate('headline', payload);
export const studioGenerateVariations = (payload: Record<string, unknown>) => generate('variations', payload);
export const studioGenerateBrandStyle = (payload: Record<string, unknown>) => generate('brand-style', payload);

function image(path: string, payload: Record<string, unknown>) {
  return apiFetch<StudioGenerateResponse>(`/studio/image/${path}`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export const studioImageRemoveBackground = (payload: Record<string, unknown>) => image('remove-background', payload);
export const studioImageRetouch = (payload: Record<string, unknown>) => image('retouch', payload);
export const studioImageEnhance = (payload: Record<string, unknown>) => image('enhance', payload);
export const studioImageResize = (payload: Record<string, unknown>) => image('resize', payload);
export const studioImageFilter = (payload: Record<string, unknown>) => image('filter', payload);
export const studioImageUpscale = (payload: Record<string, unknown>) => image('upscale', payload);

function video(path: string, payload: Record<string, unknown>) {
  return apiFetch<StudioGenerateResponse>(`/studio/video/${path}`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export const studioVideoGenerate = (payload: Record<string, unknown>) => video('generate', payload);
export const studioVideoCaptions = (payload: Record<string, unknown>) => video('captions', payload);
export const studioVideoCut = (payload: Record<string, unknown>) => video('cut', payload);
export const studioVideoVoiceover = (payload: Record<string, unknown>) => video('voiceover', payload);
export const studioVideoExport = (payload: Record<string, unknown>) => video('export', payload);
export const studioVideoThumbnail = (payload: Record<string, unknown>) => video('thumbnail', payload);

export function studioCreatePoster(payload: Record<string, unknown>) {
  return apiFetch<StudioToolActionResponse>('/studio/poster/create', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function studioCreateStory(payload: Record<string, unknown>) {
  return apiFetch<StudioToolActionResponse>('/studio/story/create', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function studioCreateAd(payload: Record<string, unknown>) {
  return apiFetch<StudioToolActionResponse>('/studio/ad-builder/create', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function studioCreateVideo(payload: Record<string, unknown>) {
  return apiFetch<StudioToolActionResponse>('/studio/video-editor/create', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function studioPhotoEdit(payload: Record<string, unknown>) {
  return apiFetch<StudioToolActionResponse>('/studio/photo-editor/save', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function studioBackgroundRemove(payload: Record<string, unknown>) {
  return apiFetch<StudioToolActionResponse>('/studio/background-remove/process', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function studioCaptionGenerate(payload: Record<string, unknown>) {
  return apiFetch<StudioGenerateResponse>('/studio/caption/generate', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function studioCtaGenerate(payload: Record<string, unknown>) {
  return apiFetch<StudioGenerateResponse>('/studio/cta/generate', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function studioCopyGenerate(payload: Record<string, unknown>) {
  return apiFetch<StudioGenerateResponse>('/studio/copy/generate', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function studioAICreativeGenerate(payload: Record<string, unknown>) {
  return apiFetch<StudioGenerateResponse>('/studio/ai-creative/generate', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function listStudioAssets() {
  return apiFetch<StudioAsset[]>('/studio/assets/list');
}

export function uploadStudioAsset(payload: {
  file: File;
  assetType?: string;
  projectId?: number | null;
}) {
  const formData = new FormData();
  formData.append('file', payload.file);
  const params = new URLSearchParams();
  if (payload.assetType) params.set('asset_type', payload.assetType);
  if (typeof payload.projectId === 'number') params.set('project_id', String(payload.projectId));
  const query = params.toString();
  return apiFetch<StudioAsset>(`/studio/assets/upload${query ? `?${query}` : ''}`, {
    method: 'POST',
    body: formData,
  });
}

export function deleteStudioAsset(assetId: number) {
  return apiFetch<{ deleted: boolean }>(`/studio/assets/delete/${assetId}`, { method: 'DELETE' });
}

export function listStudioTemplates() {
  return apiFetch<StudioTemplate[]>('/studio/templates/list');
}

export function listStudioTemplateCatalog() {
  return apiFetch<StudioTemplateCatalogItem[]>('/studio/templates/catalog');
}

export function applyStudioTemplate(payload: { template_id: number; project_id: number }) {
  return apiFetch<{ applied: boolean; project: StudioProject }>('/studio/templates/apply', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function searchStudioWebImages(query: string, limit = 12) {
  const params = new URLSearchParams({ query, limit: String(limit) });
  return apiFetch<StudioWebImage[]>(`/studio/web-images/search?${params.toString()}`);
}

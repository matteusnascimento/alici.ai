import { apiFetch } from './api';
import type { StudioAsset, StudioExport, StudioGenerateResponse, StudioProject, StudioTemplate, StudioVersion } from '../types/studioV2';

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

export function listStudioAssets() {
  return apiFetch<StudioAsset[]>('/studio/assets/list');
}

export function deleteStudioAsset(assetId: number) {
  return apiFetch<{ deleted: boolean }>(`/studio/assets/delete/${assetId}`, { method: 'DELETE' });
}

export function listStudioTemplates() {
  return apiFetch<StudioTemplate[]>('/studio/templates/list');
}

export function applyStudioTemplate(payload: { template_id: number; project_id: number }) {
  return apiFetch<{ applied: boolean; project: StudioProject }>('/studio/templates/apply', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

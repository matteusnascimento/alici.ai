import { STUDIO_EFFECTS } from '../data/studioEffects';
import type { StudioEffectDefinition, StudioLayerFilters } from '../types/studioTemplate';

export function listStudioEffects(): StudioEffectDefinition[] {
  return STUDIO_EFFECTS.map((effect) => ({ ...effect, cssFilters: effect.cssFilters ? { ...effect.cssFilters } : undefined }));
}

export function buildCssFilter(filters?: StudioLayerFilters): string {
  if (!filters) return '';
  const parts: string[] = [];
  if (filters.brightness !== undefined) parts.push(`brightness(${filters.brightness})`);
  if (filters.contrast !== undefined) parts.push(`contrast(${filters.contrast})`);
  if (filters.saturate !== undefined) parts.push(`saturate(${filters.saturate})`);
  if (filters.blur !== undefined) parts.push(`blur(${filters.blur}px)`);
  if (filters.grayscale !== undefined) parts.push(`grayscale(${filters.grayscale})`);
  if (filters.sepia !== undefined) parts.push(`sepia(${filters.sepia})`);
  if (filters.hueRotate !== undefined) parts.push(`hue-rotate(${filters.hueRotate}deg)`);
  if (filters.opacity !== undefined) parts.push(`opacity(${filters.opacity})`);
  return parts.join(' ');
}

export function mergeLayerFilters(current: StudioLayerFilters | undefined, next: StudioLayerFilters | undefined): StudioLayerFilters {
  return { ...(current || {}), ...(next || {}) };
}

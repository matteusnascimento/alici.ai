import type { StudioNavItem, StudioSection } from '../../../types/studioV2';
import { CREATE_TOOLS, MANAGE_LINKS, LIBRARY_LINKS } from './config/studioToolsConfig';

export const studioSections: Array<{ key: StudioSection; label: string }> = [
  { key: 'create', label: 'Criar' },
  { key: 'manage', label: 'Gerenciar' },
  { key: 'brand', label: 'Biblioteca' },
];

/**
 * Build studioNavItems from centralized config
 * SINGLE SOURCE OF TRUTH: studioToolsConfig.ts
 */
export const studioNavItems: StudioNavItem[] = [
  // CREATE section
  ...CREATE_TOOLS.map((tool) => ({
    key: tool.id,
    label: tool.title,
    route: tool.path,
    section: 'create' as const,
  })),
  // MANAGE section
  ...MANAGE_LINKS.map((link) => ({
    key: link.id,
    label: link.title,
    route: link.path,
    section: 'manage' as const,
  })),
  // LIBRARY section
  ...LIBRARY_LINKS.map((link) => ({
    key: link.id,
    label: link.title,
    route: link.path,
    section: 'brand' as const,
  })),
];

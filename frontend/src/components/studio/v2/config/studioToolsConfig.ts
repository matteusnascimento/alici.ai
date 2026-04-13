/**
 * SINGLE SOURCE OF TRUTH for all Studio tools, sections, and navigation
 * Designed for zero duplication across Home, Sidebar, and all Studio pages
 */

import { LucideIcon, Zap, Video, Image, BookOpen, Palette, Archive, LayoutGrid, List } from 'lucide-react';

export type StudioSection = 'create' | 'continue' | 'manage' | 'library';
export type ToolType = 'creation' | 'edit' | 'content' | 'workspace' | 'navigation';

export interface StudioTool {
  id: string;
  title: string;
  description: string;
  icon: LucideIcon;
  path: string;
  section: 'create';
  type: 'creation';
  color: string;
  gradient: string;
  badge?: string;
  comingSoon?: boolean;
}

export interface StudioNavLink {
  id: string;
  title: string;
  description: string;
  icon: LucideIcon;
  path: string;
  section: 'manage' | 'library';
  type: 'navigation';
  color: string;
}

export type StudioItem = StudioTool | StudioNavLink;

/**
 * ==========================================
 * SEÇÃO 1: CRIAR
 * ==========================================
 * Ferramentas de criação principal (top priority)
 * Displayed with large cards, strong visuals, prominent CTAs
 */
export const CREATE_TOOLS: StudioTool[] = [
  {
    id: 'video-editor',
    title: 'Editor de Vídeo IA',
    description: 'Crie vídeos profissionais com IA',
    icon: Video,
    path: '/app/studio/video-editor',
    section: 'create',
    type: 'creation',
    color: 'from-blue-500 to-cyan-500',
    gradient: 'bg-gradient-to-br from-blue-500/10 to-cyan-500/10',
  },
  {
    id: 'photo-editor',
    title: 'Editor de Fotos IA',
    description: 'Edite fotos com ajustes inteligentes',
    icon: Image,
    path: '/app/studio/photo-editor',
    section: 'create',
    type: 'creation',
    color: 'from-purple-500 to-pink-500',
    gradient: 'bg-gradient-to-br from-purple-500/10 to-pink-500/10',
  },
  {
    id: 'poster-ai',
    title: 'Criar Anúncio',
    description: 'Gere anúncios visuais com IA',
    icon: LayoutGrid,
    path: '/app/studio/ad-builder',
    section: 'create',
    type: 'creation',
    color: 'from-orange-500 to-red-500',
    gradient: 'bg-gradient-to-br from-orange-500/10 to-red-500/10',
  },
  {
    id: 'story-ai',
    title: 'Criar Story',
    description: 'Stories animadas para redes sociais',
    icon: Zap,
    path: '/app/studio/story',
    section: 'create',
    type: 'creation',
    color: 'from-emerald-500 to-teal-500',
    gradient: 'bg-gradient-to-br from-emerald-500/10 to-teal-500/10',
  },
  {
    id: 'thumbnail',
    title: 'Criar Thumbnail',
    description: 'Miniaturas chamativas para vídeos',
    icon: Image,
    path: '/app/studio/banner',
    section: 'create',
    type: 'creation',
    color: 'from-rose-500 to-pink-500',
    gradient: 'bg-gradient-to-br from-rose-500/10 to-pink-500/10',
  },
];

/**
 * ==========================================
 * SEÇÃO 2: CONTINUAR
 * ==========================================
 * Recent projects management
 * This is NOT a config array - it's generated from database
 * See StudioHomePage for listing logic
 */
export const CONTINUE_SECTION = {
  id: 'continue',
  title: 'Continuar',
  description: 'Retorne aos seus projetos recentes',
  maxItems: 5,
  viewAllPath: '/app/studio/projects',
};

/**
 * ==========================================
 * SEÇÃO 3: GERENCIAR
 * ==========================================
 * Organization & management (NOT creation tools)
 * These are navigation links to specialized pages
 */
export const MANAGE_LINKS: StudioNavLink[] = [
  {
    id: 'projects',
    title: 'Projetos',
    description: 'Organize todos os seus projetos',
    icon: LayoutGrid,
    path: '/app/studio/projects',
    section: 'manage',
    type: 'navigation',
    color: 'from-slate-400 to-slate-600',
  },
  {
    id: 'exports',
    title: 'Exportações',
    description: 'Histórico de arquivos exportados',
    icon: Archive,
    path: '/app/studio/exports',
    section: 'manage',
    type: 'navigation',
    color: 'from-purple-400 to-purple-600',
  },
  {
    id: 'history',
    title: 'Histórico',
    description: 'Versions e histórico completo',
    icon: List,
    path: '/app/studio/exports', // Maps to exports as temporary data container
    section: 'manage',
    type: 'navigation',
    color: 'from-amber-400 to-amber-600',
  },
];

/**
 * ==========================================
 * SEÇÃO 4: BIBLIOTECA
 * ==========================================
 * Brand & Assets management
 * These are navigation links, not creation tools
 */
export const LIBRARY_LINKS: StudioNavLink[] = [
  {
    id: 'brand-kit',
    title: 'Brand Kit',
    description: 'Paletas, logos e guidelines',
    icon: Palette,
    path: '/app/studio/brand-kit',
    section: 'library',
    type: 'navigation',
    color: 'from-cyan-400 to-cyan-600',
  },
  {
    id: 'assets',
    title: 'Assets',
    description: 'Imagens, vídeos e mídia',
    icon: Archive,
    path: '/app/studio/assets',
    section: 'library',
    type: 'navigation',
    color: 'from-green-400 to-green-600',
  },
  {
    id: 'templates',
    title: 'Templates',
    description: 'Modelos prontos para usar',
    icon: BookOpen,
    path: '/app/studio/templates',
    section: 'library',
    type: 'navigation',
    color: 'from-indigo-400 to-indigo-600',
  },
  {
    id: 'logos',
    title: 'Logos',
    description: 'Suas logos e variações',
    icon: Zap,
    path: '/app/studio/brand-kit',
    section: 'library',
    type: 'navigation',
    color: 'from-rose-400 to-rose-600',
  },
];

/**
 * All navigation items (for sidebar, etc.)
 * Does NOT include CREATE section (those are action tools, not nav)
 */
export const NAVIGATION_ITEMS = [
  ...MANAGE_LINKS,
  ...LIBRARY_LINKS,
];

/**
 * All creation tools by category for sidebar
 */
export const SIDEBAR_TOOLS = {
  creation: CREATE_TOOLS,
  editing: [
    // These would be nested within relevant editor pages (Video, Photo, etc.)
    // Not shown in main sidebar
  ],
};

/**
 * Helper: Get tool by ID
 */
export function getToolById(id: string): StudioItem | undefined {
  return [...CREATE_TOOLS, ...MANAGE_LINKS, ...LIBRARY_LINKS].find(tool => tool.id === id);
}

/**
 * Helper: Get all items for a section
 */
export function getItemsBySection(section: StudioSection): StudioItem[] {
  switch (section) {
    case 'create':
      return CREATE_TOOLS;
    case 'manage':
      return MANAGE_LINKS;
    case 'library':
      return LIBRARY_LINKS;
    case 'continue':
      return []; // Dynamic - from database
    default:
      return [];
  }
}

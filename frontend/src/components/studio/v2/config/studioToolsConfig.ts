import {
  Captions,
  Clapperboard,
  Crop,
  Eraser,
  FolderOpen,
  ImageUp,
  LayoutTemplate,
  Megaphone,
  Music2,
  Palette,
  Scissors,
  Sparkles,
  Type,
  UploadCloud,
  UserCircle,
  Wand2,
  type LucideIcon,
} from 'lucide-react';

export type StudioToolCategory = 'create' | 'edit' | 'ai' | 'library' | 'manage';

export interface StudioToolItem {
  id: string;
  title: string;
  description: string;
  path: string;
  icon: LucideIcon;
  category: StudioToolCategory;
  featured?: boolean;
  badge?: string;
}

export const STUDIO_TOOLS: StudioToolItem[] = [
  {
    id: 'video-editor',
    title: 'Editor unificado',
    description: 'Foto, video, IA, layers, timeline e exportacao em um fluxo.',
    path: '/app/studio/editor',
    icon: Clapperboard,
    category: 'create',
    featured: true,
  },
  {
    id: 'photo-editor',
    title: 'Editar foto',
    description: 'Upload, selecao, fundo, corte, ajustes e IA visual.',
    path: '/app/studio/tools/photo-editor',
    icon: ImageUp,
    category: 'create',
    featured: true,
  },
  {
    id: 'ai-creator',
    title: 'Gerador de IA',
    description: 'Crie imagens, anuncios e variacoes a partir de briefing.',
    path: '/app/studio/ai-creative',
    icon: Wand2,
    category: 'ai',
    featured: true,
  },
  {
    id: 'templates',
    title: 'Templates',
    description: 'Modelos profissionais para posts, videos e campanhas.',
    path: '/app/studio/templates',
    icon: LayoutTemplate,
    category: 'library',
    featured: true,
  },
  {
    id: 'autocut',
    title: 'AutoCut',
    description: 'Corte rapido de video com timeline objetiva.',
    path: '/app/studio/editor/video?mode=new&entry=autocut',
    icon: Scissors,
    category: 'edit',
  },
  {
    id: 'captions',
    title: 'Legendas',
    description: 'Gere legendas, CTA e textos curtos para redes.',
    path: '/app/studio/tools/caption',
    icon: Captions,
    category: 'edit',
  },
  {
    id: 'remove-background',
    title: 'Remover fundo',
    description: 'Processamento de imagem para recorte e composicao.',
    path: '/app/studio/tools/remove-background',
    icon: Eraser,
    category: 'edit',
  },
  {
    id: 'resize',
    title: 'Redimensionar',
    description: 'Adapte criativos para feed, story, reels e banners.',
    path: '/app/studio/tools/ad',
    icon: Crop,
    category: 'edit',
  },
  {
    id: 'marketing',
    title: 'Marketing',
    description: 'CTA, copy e estrutura de campanhas com IA.',
    path: '/app/studio/tools/cta',
    icon: Megaphone,
    category: 'ai',
  },
  {
    id: 'text',
    title: 'Texto',
    description: 'Titulos, subtitulos, estilos e camadas textuais.',
    path: '/app/studio/editor/video?mode=new&entry=text',
    icon: Type,
    category: 'edit',
  },
  {
    id: 'audio',
    title: 'Audio',
    description: 'Voiceover, trilha e estrutura sonora para video.',
    path: '/app/studio/editor/video?mode=new&entry=audio',
    icon: Music2,
    category: 'edit',
  },
  {
    id: 'uploads',
    title: 'Uploads',
    description: 'Envie imagens, videos e audios para seus projetos.',
    path: '/app/studio/assets',
    icon: UploadCloud,
    category: 'library',
  },
  {
    id: 'assets',
    title: 'Assets',
    description: 'Biblioteca de midias, logos e arquivos de marca.',
    path: '/app/studio/assets',
    icon: FolderOpen,
    category: 'library',
  },
  {
    id: 'brand-kit',
    title: 'Marca',
    description: 'Paletas, logos, fontes e identidade visual.',
    path: '/app/studio/brand-kit',
    icon: Palette,
    category: 'manage',
  },
  {
    id: 'projects',
    title: 'Projetos',
    description: 'Organize, retome e exporte trabalhos reais.',
    path: '/app/studio/projects',
    icon: FolderOpen,
    category: 'manage',
  },
];

export const CREATE_TOOLS = STUDIO_TOOLS.filter((tool) => tool.category === 'create' || tool.category === 'ai');
export const MANAGE_LINKS = STUDIO_TOOLS.filter((tool) => tool.category === 'manage');
export const LIBRARY_LINKS = STUDIO_TOOLS.filter((tool) => tool.category === 'library' || tool.category === 'edit');

export const STUDIO_BOTTOM_NAV: StudioToolItem[] = [
  STUDIO_TOOLS.find((tool) => tool.id === 'video-editor')!,
  STUDIO_TOOLS.find((tool) => tool.id === 'templates')!,
  STUDIO_TOOLS.find((tool) => tool.id === 'ai-creator')!,
  STUDIO_TOOLS.find((tool) => tool.id === 'projects')!,
  STUDIO_TOOLS.find((tool) => tool.id === 'brand-kit')!,
];

export function findStudioTool(id: string) {
  return STUDIO_TOOLS.find((tool) => tool.id === id);
}

export function filterStudioTools(query: string) {
  const normalized = query.trim().toLowerCase();
  if (!normalized) return STUDIO_TOOLS;
  return STUDIO_TOOLS.filter((tool) => `${tool.title} ${tool.description}`.toLowerCase().includes(normalized));
}

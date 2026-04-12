import {
  Captions,
  Clapperboard,
  FileVideo,
  ImageUp,
  Layers3,
  Megaphone,
  MessageSquareQuote,
  Scissors,
  Sparkles,
  Wand2,
  type LucideIcon,
} from 'lucide-react';

export interface StudioHomeAction {
  id: string;
  label: string;
  description: string;
  path: string;
  tone: 'primary' | 'secondary';
}

export interface StudioHomeTool {
  id: string;
  title: string;
  description: string;
  icon: LucideIcon;
  path: string;
  badge?: string;
}

export interface StudioHomeCategory {
  id: string;
  label: string;
  description: string;
  tools: StudioHomeTool[];
}

export const STUDIO_HOME_ACTIONS: StudioHomeAction[] = [
  {
    id: 'new-project',
    label: 'Novo projeto',
    description: 'Abra o editor principal e comece um projeto em branco.',
    path: '/app/studio/editor/video?mode=new',
    tone: 'primary',
  },
  {
    id: 'edit-media',
    label: 'Editar midia',
    description: 'Entre direto nas ferramentas de edicao para ajustar uma midia existente.',
    path: '/app/studio/tools/photo-editor',
    tone: 'secondary',
  },
];

export const STUDIO_HOME_CATEGORIES: StudioHomeCategory[] = [
  {
    id: 'creation',
    label: 'Criacao',
    description: 'Fluxos para iniciar pecas e campanhas rapidamente.',
    tools: [
      {
        id: 'generate-video',
        title: 'Gerar video IA',
        description: 'Monte um video vertical com base em prompt e assets.',
        icon: FileVideo,
        path: '/app/studio/editor/video?mode=new&entry=ai-video',
        badge: 'Principal',
      },
      {
        id: 'create-ad',
        title: 'Criar anuncio',
        description: 'Monte criativos de anuncio com estrutura comercial.',
        icon: Megaphone,
        path: '/app/studio/tools/ad',
      },
      {
        id: 'create-story',
        title: 'Criar story',
        description: 'Gere story vertical com narrativa pronta para social.',
        icon: Clapperboard,
        path: '/app/studio/tools/story',
      },
    ],
  },
  {
    id: 'editing',
    label: 'Edicao',
    description: 'Ferramentas para lapidar video e imagem com rapidez.',
    tools: [
      {
        id: 'video-editor',
        title: 'Editor de video',
        description: 'Timeline, texto, audio, filtros e exportacao.',
        icon: Layers3,
        path: '/app/studio/editor/video',
      },
      {
        id: 'photo-editor',
        title: 'Editor de fotos',
        description: 'Ajustes, crop, filtros e refinamentos visuais.',
        icon: ImageUp,
        path: '/app/studio/tools/photo-editor',
      },
      {
        id: 'autocut',
        title: 'AutoCut',
        description: 'Corte automatico de takes para versoes curtas.',
        icon: Scissors,
        path: '/app/studio/tools/auto-cut',
      },
    ],
  },
  {
    id: 'ai',
    label: 'IA',
    description: 'Automacoes visuais para ganhar velocidade na producao.',
    tools: [
      {
        id: 'remove-background',
        title: 'Remover fundo',
        description: 'Recorte rapido para produto, avatar ou criativo.',
        icon: Wand2,
        path: '/app/studio/tools/remove-background',
      },
      {
        id: 'avatar-ia',
        title: 'Avatar IA',
        description: 'Experimente apresentacao com avatar e voz sintetica.',
        icon: Sparkles,
        path: '/app/studio/tools/avatar',
      },
      {
        id: 'enhance-image',
        title: 'Melhorar imagem',
        description: 'Aprimore nitidez, cor e contraste com IA.',
        icon: Sparkles,
        path: '/app/studio/tools/enhance',
      },
    ],
  },
  {
    id: 'marketing',
    label: 'Marketing',
    description: 'Blocos de campanha e copy para acelerar entrega.',
    tools: [
      {
        id: 'generate-cta',
        title: 'Gerar CTA',
        description: 'Produza chamadas para acao prontas para criativos.',
        icon: MessageSquareQuote,
        path: '/app/studio/tools/cta',
      },
      {
        id: 'create-campaign',
        title: 'Criar campanha',
        description: 'Organize briefing, variacoes e distribuicao.',
        icon: Captions,
        path: '/app/studio/tools/campaign',
      },
    ],
  },
];

export function resolveStudioProjectRoute(projectType: string, projectId: number | string) {
  const normalized = String(projectType).toLowerCase();
  if (normalized.includes('video')) return `/app/studio/editor/video/${projectId}`;
  if (normalized.includes('photo')) return `/app/studio/tools/photo-editor`;
  if (normalized.includes('story')) return '/app/studio/tools/story';
  if (normalized.includes('campaign')) return '/app/studio/tools/campaign';
  if (normalized.includes('cta')) return '/app/studio/tools/cta';
  return '/app/studio/projects';
}

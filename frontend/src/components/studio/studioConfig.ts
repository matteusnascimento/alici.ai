import {
  Aperture,
  AudioLines,
  Cloud,
  Eraser,
  GalleryVerticalEnd,
  Image,
  Library,
  Megaphone,
  MessageSquareText,
  ScanText,
  Sparkles,
  Speech,
  Timer,
  Wand2,
} from 'lucide-react';
import type { ComponentType } from 'react';

import type { StudioToolType } from '../../types/studio';

export interface StudioNavItem {
  type: StudioToolType;
  title: string;
  description: string;
  route: string;
  category: 'Create / Generate' | 'Photo / Image' | 'Video / Content' | 'Business / Workspace';
  icon: ComponentType<{ size?: string | number }>;
}

export const studioNavItems: StudioNavItem[] = [
  { type: 'ads', title: 'Anuncios Inteligentes', description: 'Campanhas e ativos de anuncio.', route: '/app/studio/ads', category: 'Create / Generate', icon: Megaphone },
  { type: 'product-photos', title: 'Fotos do Produto', description: 'Fluxo visual para produto.', route: '/app/studio/product-photos', category: 'Create / Generate', icon: Image },
  { type: 'poster', title: 'Poster com IA', description: 'Brief e estrutura de poster.', route: '/app/studio/poster', category: 'Create / Generate', icon: Wand2 },
  { type: 'photo-editor', title: 'Editor de Fotos IA', description: 'Workspace de edicao.', route: '/app/studio/photo-editor', category: 'Photo / Image', icon: Aperture },
  { type: 'remove-background', title: 'Remover Fundo', description: 'Fluxo rapido de recorte.', route: '/app/studio/remove-background', category: 'Photo / Image', icon: Eraser },
  { type: 'retouch', title: 'Retoque', description: 'Correcao e polimento.', route: '/app/studio/retouch', category: 'Photo / Image', icon: Sparkles },
  { type: 'auto-enhance', title: 'Aprimorar Automaticamente', description: 'Enhancement com um clique.', route: '/app/studio/auto-enhance', category: 'Photo / Image', icon: ScanText },
  { type: 'captions', title: 'Legendas Automaticas', description: 'Subtitulos e caption social.', route: '/app/studio/captions', category: 'Video / Content', icon: Speech },
  { type: 'audio-tools', title: 'Ferramentas de Audio', description: 'Script, narracao e hooks.', route: '/app/studio/audio-tools', category: 'Video / Content', icon: AudioLines },
  { type: 'teleprompter', title: 'Teleprompter', description: 'Roteiro e pacing de leitura.', route: '/app/studio/teleprompter', category: 'Video / Content', icon: Timer },
  { type: 'marketing-tools', title: 'Ferramentas de Marketing', description: 'Campanhas, copy e funis.', route: '/app/studio/marketing-tools', category: 'Business / Workspace', icon: MessageSquareText },
  { type: 'projects', title: 'Projetos', description: 'Hub de trabalhos salvos.', route: '/app/studio/projects', category: 'Business / Workspace', icon: GalleryVerticalEnd },
  { type: 'library', title: 'Biblioteca', description: 'Templates e presets.', route: '/app/studio/library', category: 'Business / Workspace', icon: Library },
  { type: 'cloud', title: 'Espaco / Cloud', description: 'Assets e anexos.', route: '/app/studio/cloud', category: 'Business / Workspace', icon: Cloud },
];

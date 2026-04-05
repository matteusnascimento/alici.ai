import {
  Aperture,
  Clapperboard,
  Eraser,
  Image,
  Images,
  Library,
  Megaphone,
  Mic,
  Palette,
  Rocket,
  ScanText,
  Sparkles,
  Speech,
  Timer,
  UserSquare2,
  Video,
  Wand,
  Workflow,
  FolderKanban,
  Cloud,
} from 'lucide-react';

import { StudioToolCard } from './StudioToolCard';
import type { StudioTool, StudioToolId } from './studioTypes';

const tools: StudioTool[] = [
  { id: 'ads', title: 'Anuncios Inteligentes', description: 'Campanhas, copies e angulos criativos com IA.', category: 'Create / Generate', icon: Megaphone },
  { id: 'product-photos', title: 'Fotos do Produto', description: 'Geracao visual para ecommerce, social e catalogo.', category: 'Create / Generate', icon: Image },
  { id: 'poster-ai', title: 'Poster com IA', description: 'Construtor visual para oferta, evento e promocoes.', category: 'Create / Generate', icon: Palette },
  { id: 'ai-generator', title: 'Gerador de IA', description: 'Combina prompt, estilo e output em fluxo rapido.', category: 'Create / Generate', icon: Wand },
  { id: 'ai-media', title: 'Midia de IA', description: 'Pipeline de ativos para imagem e video.', category: 'Create / Generate', icon: Video },
  { id: 'ai-avatar', title: 'Modelo de IA / Avatar', description: 'Persona visual para campanhas e social content.', category: 'Create / Generate', icon: UserSquare2 },

  { id: 'photo-editor', title: 'Editor de Fotos IA', description: 'Workspace visual com acoes de edicao inteligente.', category: 'Photo / Image', icon: Aperture },
  { id: 'photo-tools', title: 'Ferramentas de Foto', description: 'Pacote de ajustes e refinamentos rapidos.', category: 'Photo / Image', icon: Images },
  { id: 'remove-bg', title: 'Remover Plano de Fundo', description: 'Recorte instantaneo para materiais comerciais.', category: 'Photo / Image', icon: Eraser },
  { id: 'retouch', title: 'Retoque', description: 'Correcoes finas para acabamento profissional.', category: 'Photo / Image', icon: Sparkles },
  { id: 'enhance', title: 'Aprimorar Automaticamente', description: 'Auto enhancement para brilho, nitidez e cor.', category: 'Photo / Image', icon: ScanText },

  { id: 'captions', title: 'Legendas Automaticas', description: 'Gere legendas para videos e reels.', category: 'Video / Content', icon: Speech },
  { id: 'teleprompter', title: 'Teleprompter', description: 'Roteiro fluido para gravacoes comerciais.', category: 'Video / Content', icon: Clapperboard },
  { id: 'audio-tools', title: 'Ferramentas de Audio', description: 'Limpeza, ganho e equalizacao inteligente.', category: 'Video / Content', icon: Mic },
  { id: 'speed-adjust', title: 'Ajustar Velocidade', description: 'Controle de ritmo para cortes e anuncios.', category: 'Video / Content', icon: Timer },
  { id: 'scripts-hooks', title: 'Scripts / Hooks / Criativos', description: 'Biblioteca de ideias de roteiro e abertura.', category: 'Video / Content', icon: Rocket },

  { id: 'marketing-tools', title: 'Ferramentas de Marketing', description: 'Campanhas, funis, WhatsApp e copy em um painel.', category: 'Business / Workspace', icon: Workflow },
  { id: 'projects', title: 'Projetos', description: 'Organize jobs, ativos e historico por cliente.', category: 'Business / Workspace', icon: FolderKanban },
  { id: 'library', title: 'Biblioteca', description: 'Acervo de templates, estilos e variações.', category: 'Business / Workspace', icon: Library },
  { id: 'cloud-space', title: 'Espaco / Cloud', description: 'Arquivos criativos e compartilhamento em equipe.', category: 'Business / Workspace', icon: Cloud },
];

interface StudioToolGridProps {
  activeTool: StudioToolId | null;
  onSelect: (toolId: StudioToolId) => void;
}

const categories: StudioTool['category'][] = ['Create / Generate', 'Photo / Image', 'Video / Content', 'Business / Workspace'];

export function StudioToolGrid({ activeTool, onSelect }: StudioToolGridProps) {
  return (
    <section className="space-y-6">
      {categories.map((category) => (
        <div key={category} className="rounded-3xl border border-white/10 bg-white/[0.02] p-4 md:p-5">
          <h2 className="mb-4 font-display text-xl text-white">{category}</h2>
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {tools
              .filter((tool) => tool.category === category)
              .map((tool) => (
                <StudioToolCard key={tool.id} tool={tool} active={activeTool === tool.id} onClick={() => onSelect(tool.id)} />
              ))}
          </div>
        </div>
      ))}
    </section>
  );
}

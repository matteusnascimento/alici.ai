import { type ComponentType, useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { BookOpen, Camera, Captions, FolderOpen, ImagePlus, Layers3, Megaphone, Palette, Search, Sparkles, SquarePlay, WandSparkles } from 'lucide-react';

import { useToast } from '../../../hooks/useToast';
import { getStudioOverview } from '../../../services/studio.service';
import type { StudioOverviewResponse } from '../../../types/studioV2';

type Tool = {
  id: string;
  name: string;
  description: string;
  route: string;
  category: 'Criacao' | 'Edicao' | 'Conteudo' | 'Video' | 'Marca' | 'IA';
  status?: 'available' | 'soon';
  icon: ComponentType<{ className?: string }>;
};

const primaryTools: Tool[] = [
  { id: 'photo-editor', name: 'Editor de Fotos', description: 'Upload, edicao por camadas e exportacao profissional.', route: '/app/studio/photo-editor', category: 'Edicao', icon: Camera },
  { id: 'poster', name: 'Criar Poster', description: 'Montagem promocional com templates e IA para composicao.', route: '/app/studio/poster', category: 'Criacao', icon: ImagePlus },
  { id: 'story', name: 'Criar Story', description: 'Fluxo vertical com headline curta, CTA e sequencia de stories.', route: '/app/studio/story', category: 'Criacao', icon: SquarePlay },
  { id: 'ad-builder', name: 'Criar Anuncio', description: 'Workspace de criativos publicitarios com variacoes A/B.', route: '/app/studio/ad-builder', category: 'Criacao', icon: Megaphone },
  { id: 'video-editor', name: 'Criar Video', description: 'Editor simplificado com timeline, texto, audio e CTA final.', route: '/app/studio/video-editor', category: 'Video', icon: WandSparkles },
  { id: 'background-remove', name: 'Remover Fundo', description: 'Preview original x sem fundo e opcoes de fundo final.', route: '/app/studio/background-remove', category: 'Edicao', icon: Layers3 },
  { id: 'caption-generator', name: 'Gerar Legenda', description: 'Legendas com CTA, hashtags e variacoes por canal.', route: '/app/studio/caption-generator', category: 'Conteudo', icon: Captions },
  { id: 'cta-generator', name: 'Gerar CTA', description: 'CTA orientado por objetivo, publico e tom de voz.', route: '/app/studio/cta-generator', category: 'Conteudo', icon: Megaphone },
  { id: 'promo-copy', name: 'Gerar Texto Promocional', description: 'Copy promocional com sugestoes de promessa e oferta.', route: '/app/studio/promo-copy', category: 'Conteudo', icon: BookOpen },
  { id: 'brand-kit', name: 'Brand Kit', description: 'Logos, paletas, fontes, templates e assets reutilizaveis.', route: '/app/studio/brand-kit', category: 'Marca', icon: Palette },
  { id: 'projects', name: 'Projetos', description: 'Abrir, duplicar, renomear e organizar seus projetos.', route: '/app/studio/projects', category: 'Marca', icon: FolderOpen },
  { id: 'exports', name: 'Exportacoes', description: 'Historico de exportacoes com reabertura e novo download.', route: '/app/studio/exports', category: 'Marca', icon: Layers3 },
  { id: 'campaign', name: 'Criar Campanha', description: 'Construa campanha completa a partir do briefing.', route: '/app/studio/campaign', category: 'Criacao', icon: Sparkles },
  { id: 'media-library', name: 'Biblioteca de Midia', description: 'Repositorio de imagens, videos e arquivos do Studio.', route: '/app/studio/media-library', category: 'Marca', icon: FolderOpen },
  { id: 'ai-creative', name: 'IA Criativa', description: 'Assistente para ideia, headline, CTA e formato de criativo.', route: '/app/studio/ai-creative', category: 'IA', icon: WandSparkles },
];

const categoryTabs = ['Tudo', 'Criacao', 'Edicao', 'Conteudo', 'Video', 'Marca', 'IA'] as const;

const projectRouteByType: Record<string, string> = {
  poster: '/app/studio/poster',
  story: '/app/studio/story',
  ad: '/app/studio/ad-builder',
  banner: '/app/studio/ad-builder',
  video: '/app/studio/video-editor',
  'video-editor': '/app/studio/video-editor',
  captions: '/app/studio/caption-generator',
  'caption-generator': '/app/studio/caption-generator',
  'photo-edit': '/app/studio/photo-editor',
  'photo-editor': '/app/studio/photo-editor',
  'background-remove': '/app/studio/background-remove',
  'cta-generator': '/app/studio/cta-generator',
  'promo-copy': '/app/studio/promo-copy',
  'ai-creative': '/app/studio/ai-creative',
  campaign: '/app/studio/campaign',
};

function resolveProjectRoute(projectType: string): string {
  return projectRouteByType[projectType] || '/app/studio/projects';
}

export function StudioHomePage() {
  const navigate = useNavigate();
  const toast = useToast();
  const [query, setQuery] = useState('');
  const [activeTab, setActiveTab] = useState<(typeof categoryTabs)[number]>('Tudo');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [overview, setOverview] = useState<StudioOverviewResponse | null>(null);

  useEffect(() => {
    let mounted = true;

    async function load() {
      setLoading(true);
      try {
        const data = await getStudioOverview();
        if (mounted) {
          setOverview(data);
          setError(null);
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Falha ao carregar Studio Overview.');
          toast.error('Falha de API ao carregar o Studio Home.');
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    void load();
    return () => {
      mounted = false;
    };
  }, []);

  const filteredTools = useMemo(() => {
    const term = query.trim().toLowerCase();
    return primaryTools.filter((tool) => {
      const matchesQuery = !term || `${tool.name} ${tool.description}`.toLowerCase().includes(term);
      const matchesTab = activeTab === 'Tudo' || tool.category === activeTab;
      return matchesQuery && matchesTab;
    });
  }, [activeTab, query]);

  return (
    <div className="space-y-6 pb-6">
      <section className="rounded-3xl border border-cyan-400/20 bg-[radial-gradient(circle_at_10%_10%,rgba(0,212,255,0.22),transparent_45%),radial-gradient(circle_at_90%_10%,rgba(17,189,142,0.18),transparent_30%),linear-gradient(150deg,#031224,#092d48)] p-6 md:p-8">
        <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">AXI Studio</p>
        <h1 className="mt-3 max-w-3xl font-display text-4xl leading-tight text-white md:text-5xl">Workspace criativo profissional para produzir, editar e exportar criativos.</h1>
        <p className="mt-3 max-w-2xl text-sm text-slate-200">A home mostra somente ferramentas principais. Subferramentas aparecem apenas dentro de cada workspace.</p>

        <div className="mt-6 grid gap-3 md:grid-cols-[1fr_auto_auto]">
          <label className="flex items-center gap-2 rounded-2xl border border-white/15 bg-black/25 px-4 py-3 text-sm text-slate-100">
            <Search className="h-4 w-4 text-cyan-200" />
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Buscar acao, ferramenta ou fluxo"
              className="w-full bg-transparent text-sm text-white outline-none placeholder:text-slate-400"
            />
          </label>
          <button
            type="button"
            onClick={() => {
              toast.info('Abrindo fluxo de novo projeto.');
              navigate('/app/studio/poster');
            }}
            className="rounded-2xl bg-cyan px-5 py-3 text-sm font-semibold text-ink transition hover:brightness-105 active:scale-[0.98]"
            title="Criar um novo projeto no Studio"
          >
            Novo projeto
          </button>
          <button
            type="button"
            onClick={() => {
              toast.info('Abrindo biblioteca de midia.');
              navigate('/app/studio/media-library');
            }}
            className="rounded-2xl border border-white/20 bg-white/5 px-5 py-3 text-sm font-semibold text-white transition hover:border-cyan-300/45 hover:bg-cyan-400/10 active:scale-[0.98]"
            title="Abrir biblioteca de midia e marca"
          >
            Abrir biblioteca
          </button>
        </div>
      </section>

      <section className="space-y-3">
        <div className="flex flex-wrap gap-2">
          {categoryTabs.map((tab) => (
            <button
              key={tab}
              type="button"
              onClick={() => setActiveTab(tab)}
              className={`rounded-xl border px-3 py-2 text-sm transition ${activeTab === tab ? 'border-cyan-300/55 bg-cyan-400/10 text-cyan-100' : 'border-white/10 bg-white/5 text-slate-200 hover:border-cyan-300/35'}`}
            >
              {tab}
            </button>
          ))}
        </div>
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {filteredTools.map((tool) => (
            <Link
              key={tool.id}
              to={tool.route}
              onClick={(event) => {
                if (tool.status === 'soon') {
                  event.preventDefault();
                  toast.warning(`${tool.name} estara disponivel em breve.`);
                  return;
                }
                toast.info(`Abrindo ${tool.name}.`);
              }}
              className="group rounded-2xl border border-white/10 bg-white/5 p-4 transition hover:-translate-y-0.5 hover:border-cyan-300/45 hover:bg-cyan-400/10 active:scale-[0.99]"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="rounded-xl border border-white/10 bg-black/25 p-2 text-cyan-100 transition group-hover:border-cyan-300/50 group-hover:bg-cyan-500/20">
                  <tool.icon className="h-4 w-4" />
                </div>
                <span className={`rounded-lg border px-2 py-0.5 text-[10px] uppercase tracking-[0.2em] ${tool.status === 'soon' ? 'border-amber-200/35 text-amber-100' : 'border-white/15 text-slate-200'}`}>
                  {tool.status === 'soon' ? 'Em breve' : 'Abrir workspace'}
                </span>
              </div>
              <p className="mt-3 text-sm font-semibold text-white">{tool.name}</p>
              <p className="mt-1 text-xs text-slate-300">{tool.description}</p>
            </Link>
          ))}
          {filteredTools.length === 0 ? <p className="text-sm text-slate-400">Nenhuma ferramenta encontrada para este filtro.</p> : null}
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-3">
        <article className="rounded-3xl border border-white/10 bg-white/5 p-4 xl:col-span-2">
          <div className="flex items-center justify-between">
            <h3 className="font-display text-2xl text-white">Projetos recentes</h3>
            <Link to="/app/studio/projects" className="text-xs uppercase tracking-[0.2em] text-cyan-200">Ver todos</Link>
          </div>
          {loading ? <div className="mt-4 grid gap-2"><div className="h-10 animate-pulse rounded-xl bg-white/10" /><div className="h-10 animate-pulse rounded-xl bg-white/10" /></div> : null}
          {error ? <p className="mt-4 text-sm text-coral">{error}</p> : null}
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {(overview?.recent_projects || []).map((project) => (
              <article key={project.id} className="rounded-2xl border border-white/10 bg-black/20 p-3">
                <div className="flex items-center justify-between gap-2">
                  <p className="font-semibold text-white">{project.title}</p>
                  <span className="rounded-lg border border-white/15 px-2 py-0.5 text-[10px] uppercase tracking-[0.2em] text-slate-300">{project.status}</span>
                </div>
                <p className="mt-1 text-xs text-slate-400">{project.project_type}</p>
                <p className="mt-1 text-xs text-slate-500">Ultima edicao: {new Date(project.updated_at).toLocaleString('pt-BR')}</p>
                <div className="mt-3 flex items-center justify-between">
                  <span className="text-xs text-slate-400">{project.thumbnail_url ? 'Thumbnail disponivel' : 'Sem thumbnail'}</span>
                  <Link
                    to={resolveProjectRoute(project.project_type)}
                    onClick={() => toast.info(`Abrindo projeto ${project.title}.`)}
                    className="rounded-lg border border-cyan-300/45 px-3 py-1 text-xs font-semibold text-cyan-100"
                  >
                    Abrir
                  </Link>
                </div>
              </article>
            ))}
            {!loading && (overview?.recent_projects.length || 0) === 0 ? <p className="text-sm text-slate-400">Nenhum projeto recente. Clique em Novo projeto para comecar.</p> : null}
          </div>
        </article>

        <article className="rounded-3xl border border-white/10 bg-white/5 p-4">
          <div className="flex items-center justify-between">
            <h3 className="font-display text-2xl text-white">Acoes sugeridas</h3>
          </div>
          <div className="mt-4 space-y-2">
            {(overview?.suggested_actions || []).map((action) => (
              <Link key={action.id} to={action.route} className="block rounded-xl border border-white/10 bg-black/20 p-3 transition hover:border-cyan-300/45 hover:bg-cyan-400/10">
                <p className="text-sm font-semibold text-white">{action.label}</p>
                <p className="mt-1 text-xs text-slate-300">{action.description}</p>
              </Link>
            ))}
            {!loading && (overview?.suggested_actions.length || 0) === 0 ? <p className="text-sm text-slate-400">Sem sugestoes no momento. Experimente abrir o Editor de Fotos.</p> : null}
          </div>
        </article>
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        <article className="rounded-3xl border border-white/10 bg-white/5 p-4">
          <div className="flex items-center justify-between">
            <h3 className="font-display text-xl text-white">Biblioteca da marca</h3>
            <Link to="/app/studio/brand-kit" className="text-xs uppercase tracking-[0.2em] text-cyan-200">Abrir brand kit</Link>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
            <Link to="/app/studio/brand?tab=logos" className="rounded-xl border border-white/10 bg-black/20 p-3 text-slate-200 hover:border-cyan-300/45">Logos: {overview?.brand_summary.logos_count || 0}</Link>
            <Link to="/app/studio/brand?tab=templates" className="rounded-xl border border-white/10 bg-black/20 p-3 text-slate-200 hover:border-cyan-300/45">Templates: {overview?.brand_summary.templates_count || 0}</Link>
            <Link to="/app/studio/brand?tab=palettes" className="rounded-xl border border-white/10 bg-black/20 p-3 text-slate-200 hover:border-cyan-300/45">Paletas: {overview?.brand_summary.palettes_count || 0}</Link>
            <Link to="/app/studio/brand?tab=assets" className="rounded-xl border border-white/10 bg-black/20 p-3 text-slate-200 hover:border-cyan-300/45">Assets: {overview?.brand_summary.assets_count || 0}</Link>
          </div>
        </article>

        <article className="rounded-3xl border border-white/10 bg-white/5 p-4">
          <div className="flex items-center justify-between">
            <h3 className="font-display text-xl text-white">Exportacoes recentes</h3>
            <Link to="/app/studio/exports" className="text-xs uppercase tracking-[0.2em] text-cyan-200">Ver todas</Link>
          </div>
          <div className="mt-4 space-y-2 text-sm text-slate-300">
            {(overview?.recent_exports || []).map((exportItem) => (
              <article key={exportItem.id} className="rounded-xl border border-white/10 bg-black/20 p-3">
                <p className="font-semibold text-white">{exportItem.file_name}</p>
                <p className="text-xs text-slate-400">{exportItem.export_type.toUpperCase()} • {new Date(exportItem.created_at).toLocaleString('pt-BR')}</p>
                <p className="text-xs text-slate-500">Origem: {exportItem.source}</p>
                <div className="mt-2 flex gap-2">
                  <a href={exportItem.file_url} onClick={() => toast.success('Download iniciado.')} className="rounded-lg border border-cyan-300/45 px-3 py-1 text-xs text-cyan-100">Baixar</a>
                  <Link to={resolveProjectRoute(exportItem.source)} onClick={() => toast.info('Abrindo projeto de origem.')} className="rounded-lg border border-white/20 px-3 py-1 text-xs text-white">Abrir</Link>
                </div>
              </article>
            ))}
            {!loading && (overview?.recent_exports.length || 0) === 0 ? <p className="text-sm text-slate-400">Nenhuma exportacao recente.</p> : null}
          </div>
        </article>
      </section>
    </div>
  );
}

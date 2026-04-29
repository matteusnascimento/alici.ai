import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  AlertTriangle,
  Captions,
  Clapperboard,
  Clock3,
  FolderOpen,
  ImageUp,
  Layers3,
  Loader2,
  Megaphone,
  Monitor,
  Music2,
  Palette,
  Scissors,
  Sparkles,
  UserCircle,
  Wand2,
  type LucideIcon,
} from 'lucide-react';

import { getStudioOverview } from '../../../services/studio.service';
import type { StudioOverviewResponse, StudioRecentProjectItem } from '../../../types/studioV2';
import { resolveStudioProjectRoute } from './config/studioHomeConfig';

const cn = (...classes: Array<string | false | null | undefined>) => classes.filter(Boolean).join(' ');

const emptyOverview: StudioOverviewResponse = {
  recent_projects: [],
  recent_exports: [],
  brand_summary: {
    logos_count: 0,
    templates_count: 0,
    palettes_count: 0,
    assets_count: 0,
  },
  suggested_actions: [],
};

const heroActions = [
  {
    id: 'new-video',
    title: 'Novo video',
    subtitle: 'Abra o editor real e comece do zero',
    path: '/app/studio/editor/video?mode=new',
    icon: Layers3,
    tone: 'primary',
  },
  {
    id: 'edit-photo',
    title: 'Editar foto',
    subtitle: 'Upload, ajustes e ferramentas de imagem',
    path: '/app/studio/tools/photo-editor',
    icon: ImageUp,
    tone: 'secondary',
  },
];

const quickTools: Array<{ name: string; description: string; path: string; icon: LucideIcon }> = [
  {
    name: 'AutoCut',
    description: 'Editor de video com entrada de corte',
    path: '/app/studio/editor/video?mode=new&entry=autocut',
    icon: Scissors,
  },
  {
    name: 'Retoque',
    description: 'Editor de fotos',
    path: '/app/studio/tools/photo-editor',
    icon: ImageUp,
  },
  {
    name: 'Templates',
    description: 'Modelos reais do Studio',
    path: '/app/studio/templates',
    icon: Sparkles,
  },
  {
    name: 'Gerador de IA',
    description: 'Briefing para IA criativa',
    path: '/app/studio/ai-creative',
    icon: Wand2,
  },
  {
    name: 'Aprimorar',
    description: 'Ajustes de imagem',
    path: '/app/studio/tools/photo-editor',
    icon: Sparkles,
  },
  {
    name: 'Foto',
    description: 'Ferramentas de imagem',
    path: '/app/studio/tools/photo-editor',
    icon: ImageUp,
  },
  {
    name: 'Marketing',
    description: 'CTA e copy de campanha',
    path: '/app/studio/tools/cta',
    icon: Megaphone,
  },
  {
    name: 'Desktop',
    description: 'Projetos salvos',
    path: '/app/studio/projects',
    icon: Monitor,
  },
  {
    name: 'Remover fundo',
    description: 'Processamento de imagem',
    path: '/app/studio/tools/remove-background',
    icon: Wand2,
  },
  {
    name: 'Legendas',
    description: 'Texto, CTA e hashtags',
    path: '/app/studio/tools/caption',
    icon: Captions,
  },
  {
    name: 'Assets',
    description: 'Biblioteca de midias',
    path: '/app/studio/assets',
    icon: FolderOpen,
  },
  {
    name: 'Audio',
    description: 'Editor de video e voiceover',
    path: '/app/studio/editor/video?mode=new&entry=audio',
    icon: Music2,
  },
];

const bottomNav: Array<{ label: string; path: string; icon: LucideIcon; active?: boolean }> = [
  { label: 'Editar', path: '/app/studio', icon: Scissors, active: true },
  { label: 'Modelos', path: '/app/studio/templates', icon: Clapperboard },
  { label: 'IA', path: '/app/studio/ai-creative', icon: Wand2 },
  { label: 'Projetos', path: '/app/studio/projects', icon: FolderOpen },
  { label: 'Marca', path: '/app/studio/brand-kit', icon: UserCircle },
];

const projectCardStyles = [
  { background: 'var(--studio-project-a)', color: 'var(--studio-project-on-a)' },
  { background: 'var(--studio-project-b)', color: 'var(--studio-project-on-b)' },
  { background: 'var(--studio-project-c)', color: 'var(--studio-project-on-c)' },
];

function normalizeStudioRoute(route: string) {
  const routeAliases: Record<string, string> = {
    '/app/studio/poster': '/app/studio/tools/ad',
    '/app/studio/ad-builder': '/app/studio/tools/ad',
    '/app/studio/story': '/app/studio/tools/story',
    '/app/studio/photo-editor': '/app/studio/tools/photo-editor',
    '/app/studio/video-editor': '/app/studio/editor/video',
    '/app/studio/caption-generator': '/app/studio/tools/caption',
    '/app/studio/brand': '/app/studio/brand-kit',
  };

  return routeAliases[route] || route;
}

function formatUpdatedAt(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return 'sem data';
  }

  return date.toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function recentProjectRoute(project: StudioRecentProjectItem) {
  return resolveStudioProjectRoute(project.project_type, project.id);
}

function StudioProjectStrip({ projects }: { projects: StudioRecentProjectItem[] }) {
  if (projects.length === 0) {
    return (
      <div className="mb-8 rounded-[1.75rem] border border-dashed border-[var(--studio-border)] bg-[var(--studio-card-strong)] p-4 text-sm font-semibold text-[var(--studio-muted)] shadow-[var(--studio-tile-shadow)] sm:p-5">
        Projetos criados no backend aparecem aqui. Comece em Novo video, Criar anuncio ou Gerador de IA.
      </div>
    );
  }

  return (
    <div className="mb-8 flex max-w-full gap-3 overflow-x-auto px-1 pb-3 sm:gap-4">
      {projects.slice(0, 6).map((project, index) => (
        <Link
          key={project.id}
          to={recentProjectRoute(project)}
          style={projectCardStyles[index % projectCardStyles.length]}
          className="min-w-[min(148px,72vw)] max-w-[176px] flex-shrink-0 rounded-[1.5rem] p-4 text-left shadow-[var(--studio-tile-shadow)] transition hover:-translate-y-1"
        >
          <div className="mb-6 inline-flex rounded-full bg-black/35 px-2 py-1 text-xs font-bold text-white">
            {String(index + 1).padStart(2, '0')}
          </div>
          <p className="line-clamp-2 break-words text-sm font-black">{project.title}</p>
          <p className="mt-2 flex items-center gap-1 text-[11px] opacity-75">
            <Clock3 size={12} /> {formatUpdatedAt(project.updated_at)}
          </p>
        </Link>
      ))}
    </div>
  );
}

export function StudioHomePage() {
  const [overview, setOverview] = useState<StudioOverviewResponse>(emptyOverview);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    async function loadOverview() {
      setLoading(true);
      try {
        const data = await getStudioOverview();
        if (!mounted) return;
        setOverview({
          ...emptyOverview,
          ...data,
          brand_summary: {
            ...emptyOverview.brand_summary,
            ...data.brand_summary,
          },
        });
        setError(null);
      } catch (err) {
        if (!mounted) return;
        setError(err instanceof Error ? err.message : 'Falha ao carregar Studio.');
        setOverview(emptyOverview);
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    void loadOverview();
    return () => {
      mounted = false;
    };
  }, []);

  const brandTotal = useMemo(
    () => overview.brand_summary.logos_count + overview.brand_summary.templates_count + overview.brand_summary.palettes_count + overview.brand_summary.assets_count,
    [overview.brand_summary],
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="relative flex min-h-[calc(100vh-7rem)] w-full max-w-full flex-col overflow-hidden rounded-[2rem] border border-[var(--studio-border)] bg-[var(--studio-bg)] text-[var(--studio-text)] shadow-soft"
    >
      <div className="mx-auto flex w-full max-w-[1040px] flex-1 flex-col px-4 py-5 sm:px-6 sm:py-7 md:px-8">
        <div className="mb-7 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="min-w-0">
            <div className="text-[11px] font-semibold uppercase tracking-[0.28em] text-cyan-600">AXI Studio</div>
            <h1 className="mt-2 break-words text-3xl font-black tracking-tight sm:text-4xl">Criar com IA</h1>
            <p className="mt-2 max-w-xl text-sm font-medium text-[var(--studio-muted)]">
              A arquitetura visual do Studio voltou, agora conectada a ferramentas, assets e projetos reais.
            </p>
          </div>
          <Link to="/app/studio/brand-kit" className="inline-flex shrink-0 items-center justify-center rounded-full bg-[var(--studio-ink)] px-5 py-2 text-sm font-semibold text-[var(--studio-on-ink)] shadow-lg">
            Marca {brandTotal}
          </Link>
        </div>

        {loading ? (
          <div className="mb-5 flex items-center gap-2 rounded-2xl border border-[var(--studio-border)] bg-[var(--studio-card-strong)] px-4 py-3 text-sm font-semibold text-[var(--studio-muted)]">
            <Loader2 className="h-4 w-4 animate-spin text-cyan-600" /> Carregando dados reais do Studio...
          </div>
        ) : null}

        {error ? (
          <div className="mb-5 flex items-center gap-2 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700">
            <AlertTriangle className="h-4 w-4" /> {error}
          </div>
        ) : null}

        <div className="mb-7 grid max-w-full gap-4 sm:gap-5 md:grid-cols-[minmax(0,1.15fr)_minmax(0,0.85fr)]">
          {heroActions.map((action) => {
            const Icon = action.icon;
            return (
              <Link
                key={action.id}
                to={action.path}
                style={{
                  background: action.tone === 'primary' ? 'var(--studio-hero-primary)' : 'var(--studio-hero-secondary)',
                }}
                className="group min-w-0 rounded-[28px] border border-[var(--studio-border)] p-5 text-left shadow-[var(--studio-shadow)] transition hover:-translate-y-1 sm:p-7"
              >
                <div className="mb-8 flex h-14 w-14 items-center justify-center rounded-2xl bg-[var(--studio-ink)] text-[var(--studio-on-ink)] sm:mb-10">
                  <Icon size={28} />
                </div>
                <div className="break-words text-2xl font-black">{action.title}</div>
                <div className="mt-1 text-sm font-medium text-[var(--studio-muted)]">{action.subtitle}</div>
              </Link>
            );
          })}
        </div>

        <StudioProjectStrip projects={overview.recent_projects} />

        <div className="grid flex-1 grid-cols-[repeat(auto-fit,minmax(92px,1fr))] gap-x-3 gap-y-6 pb-6 sm:grid-cols-[repeat(auto-fit,minmax(108px,1fr))] sm:gap-x-5 lg:grid-cols-[repeat(auto-fit,minmax(112px,1fr))]">
          {quickTools.map((tool) => {
            const Icon = tool.icon;
            return (
              <Link key={tool.name} to={tool.path} className="group flex min-w-0 flex-col items-center text-center transition hover:-translate-y-1">
                <div className="mb-3 flex h-16 w-16 items-center justify-center rounded-[22px] bg-[var(--studio-card)] text-[var(--studio-text)] shadow-[var(--studio-tile-shadow)] ring-1 ring-[var(--studio-border)] transition group-hover:ring-cyan-300/70 sm:h-[72px] sm:w-[72px] sm:rounded-[24px]">
                  <Icon size={26} />
                </div>
                <span className="max-w-full break-words text-sm font-black leading-tight text-[var(--studio-text)] sm:text-base">{tool.name}</span>
                <span className="mt-1 max-w-[124px] break-words text-[11px] font-semibold leading-tight text-[var(--studio-soft)]">{tool.description}</span>
              </Link>
            );
          })}
        </div>

        {overview.suggested_actions.length > 0 ? (
          <div className="mb-5 grid grid-cols-[repeat(auto-fit,minmax(180px,1fr))] gap-3">
            {overview.suggested_actions.slice(0, 3).map((action) => (
              <Link
                key={action.id}
                to={normalizeStudioRoute(action.route)}
                className="min-w-0 rounded-2xl border border-[var(--studio-border)] bg-[var(--studio-card-strong)] p-4 text-left shadow-[var(--studio-tile-shadow)] transition hover:-translate-y-0.5 hover:border-cyan-300"
              >
                <p className="break-words text-sm font-black text-[var(--studio-text)]">{action.label}</p>
                <p className="mt-1 break-words text-xs font-semibold leading-5 text-[var(--studio-soft)]">{action.description}</p>
              </Link>
            ))}
          </div>
        ) : null}
      </div>

      <div className="border-t border-[var(--studio-border)] bg-[var(--studio-surface)] backdrop-blur-xl">
        <div className="mx-auto grid max-w-[1040px] grid-cols-5 gap-1 px-2 py-2 text-center text-[11px] font-bold text-[var(--studio-soft)] sm:px-6 sm:py-3 sm:text-sm">
          {bottomNav.map((item) => {
            const Icon = item.icon;
            return (
              <Link key={item.label} to={item.path} className={cn('flex min-w-0 flex-col items-center gap-1 px-1 transition hover:text-[var(--studio-text)]', item.active ? 'text-[var(--studio-text)]' : 'text-[var(--studio-soft)]')}>
                <Icon className="h-6 w-6 sm:h-7 sm:w-7" />
                <span className="max-w-full truncate">{item.label}</span>
              </Link>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
}

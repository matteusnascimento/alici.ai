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
      <div className="mb-8 rounded-[1.75rem] border border-dashed border-slate-300 bg-white/65 p-5 text-sm font-semibold text-slate-600 shadow-[0_18px_45px_rgba(44,69,104,0.08)]">
        Projetos criados no backend aparecem aqui. Comece em Novo video, Criar anuncio ou Gerador de IA.
      </div>
    );
  }

  return (
    <div className="mb-8 flex gap-4 overflow-x-auto pb-2">
      {projects.slice(0, 6).map((project, index) => (
        <Link
          key={project.id}
          to={recentProjectRoute(project)}
          className={cn(
            'min-w-[148px] rounded-[1.5rem] p-4 text-left shadow-[0_20px_50px_rgba(21,38,66,0.12)] transition hover:-translate-y-1',
            index % 3 === 0 && 'bg-[linear-gradient(135deg,#132033,#415f83)] text-white',
            index % 3 === 1 && 'bg-[linear-gradient(135deg,#e9eef6,#c6d8f0)] text-[#101522]',
            index % 3 === 2 && 'bg-[linear-gradient(135deg,#0e1628,rgb(var(--accent-rgb)/0.95))] text-white',
          )}
        >
          <div className="mb-6 inline-flex rounded-full bg-black/35 px-2 py-1 text-xs font-bold text-white">
            {String(index + 1).padStart(2, '0')}
          </div>
          <p className="line-clamp-2 text-sm font-black">{project.title}</p>
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
      className="relative min-h-[calc(100vh-7rem)] overflow-hidden rounded-[2rem] bg-[#f7fbff] text-[#101522] shadow-soft"
    >
      <div className="mx-auto flex min-h-[calc(100vh-7rem)] max-w-[1040px] flex-col px-6 py-7 md:px-8">
        <div className="mb-7 flex items-start justify-between gap-4">
          <div>
            <div className="text-[11px] font-semibold uppercase tracking-[0.28em] text-cyan-600">AXI Studio</div>
            <h1 className="mt-2 text-4xl font-black tracking-tight">Criar com IA</h1>
            <p className="mt-2 max-w-xl text-sm font-medium text-slate-600">
              A arquitetura visual do Studio voltou, agora conectada a ferramentas, assets e projetos reais.
            </p>
          </div>
          <Link to="/app/studio/brand-kit" className="rounded-full bg-[#101522] px-5 py-2 text-sm font-semibold text-white shadow-lg">
            Marca {brandTotal}
          </Link>
        </div>

        {loading ? (
          <div className="mb-5 flex items-center gap-2 rounded-2xl border border-slate-200 bg-white/80 px-4 py-3 text-sm font-semibold text-slate-600">
            <Loader2 className="h-4 w-4 animate-spin text-cyan-600" /> Carregando dados reais do Studio...
          </div>
        ) : null}

        {error ? (
          <div className="mb-5 flex items-center gap-2 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700">
            <AlertTriangle className="h-4 w-4" /> {error}
          </div>
        ) : null}

        <div className="mb-7 grid gap-5 md:grid-cols-[1.2fr_0.8fr]">
          {heroActions.map((action) => {
            const Icon = action.icon;
            return (
              <Link
                key={action.id}
                to={action.path}
                className={cn(
                  'group rounded-[28px] p-7 text-left shadow-[0_24px_70px_rgba(58,99,145,0.18)] transition hover:-translate-y-1 hover:shadow-[0_30px_90px_rgba(58,99,145,0.25)]',
                  action.tone === 'primary'
                    ? 'bg-gradient-to-br from-[#dceeff] to-[#b9d7f4]'
                    : 'bg-gradient-to-br from-[#e7f4ff] to-[#c8def4]',
                )}
              >
                <div className="mb-10 flex h-14 w-14 items-center justify-center rounded-2xl bg-[#0b1020] text-white">
                  <Icon size={28} />
                </div>
                <div className="text-2xl font-black">{action.title}</div>
                <div className="mt-1 text-sm font-medium text-slate-600">{action.subtitle}</div>
              </Link>
            );
          })}
        </div>

        <StudioProjectStrip projects={overview.recent_projects} />

        <div className="grid flex-1 grid-cols-3 gap-x-5 gap-y-7 pb-28 sm:grid-cols-4 lg:grid-cols-6">
          {quickTools.map((tool) => {
            const Icon = tool.icon;
            return (
              <Link key={tool.name} to={tool.path} className="group flex flex-col items-center text-center transition hover:-translate-y-1">
                <div className="mb-3 flex h-[72px] w-[72px] items-center justify-center rounded-[24px] bg-white text-[#333946] shadow-[0_15px_45px_rgba(48,63,88,0.12)] ring-1 ring-slate-200/70 transition group-hover:ring-cyan-300/70">
                  <Icon size={26} />
                </div>
                <span className="max-w-[120px] text-base font-black leading-tight text-[#343842]">{tool.name}</span>
                <span className="mt-1 max-w-[124px] text-[11px] font-semibold leading-tight text-slate-500">{tool.description}</span>
              </Link>
            );
          })}
        </div>

        {overview.suggested_actions.length > 0 ? (
          <div className="mb-5 grid gap-3 md:grid-cols-3">
            {overview.suggested_actions.slice(0, 3).map((action) => (
              <Link
                key={action.id}
                to={normalizeStudioRoute(action.route)}
                className="rounded-2xl border border-slate-200 bg-white/80 p-4 text-left shadow-[0_16px_38px_rgba(48,63,88,0.08)] transition hover:-translate-y-0.5 hover:border-cyan-300"
              >
                <p className="text-sm font-black text-[#101522]">{action.label}</p>
                <p className="mt-1 text-xs font-semibold leading-5 text-slate-500">{action.description}</p>
              </Link>
            ))}
          </div>
        ) : null}
      </div>

      <div className="absolute inset-x-0 bottom-0 border-t border-slate-200 bg-white/95 backdrop-blur-xl">
        <div className="mx-auto grid max-w-[1040px] grid-cols-5 px-6 py-3 text-center text-sm font-bold text-slate-400">
          {bottomNav.map((item) => {
            const Icon = item.icon;
            return (
              <Link key={item.label} to={item.path} className={cn('flex flex-col items-center gap-1 transition hover:text-black', item.active ? 'text-black' : 'text-slate-400')}>
                <Icon size={28} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
}

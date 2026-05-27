import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  AlertTriangle,
  Clock3,
  Crown,
  Search,
  Sparkles,
} from 'lucide-react';

import { getStudioOverview } from '../../../services/studio.service';
import type { StudioOverviewResponse, StudioRecentProjectItem } from '../../../types/studioV2';
import { resolveStudioProjectRoute } from './config/studioHomeConfig';
import { filterStudioTools, STUDIO_BOTTOM_NAV, STUDIO_TOOLS } from './config/studioToolsConfig';

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

const projectCardStyles = [
  { background: 'var(--studio-project-a)', color: 'var(--studio-project-on-a)' },
  { background: 'var(--studio-project-b)', color: 'var(--studio-project-on-b)' },
  { background: 'var(--studio-project-c)', color: 'var(--studio-project-on-c)' },
];

function formatUpdatedAt(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'sem data';
  return date.toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
}

function StudioProjectStrip({ projects }: { projects: StudioRecentProjectItem[] }) {
  if (projects.length === 0) {
    return (
      <div className="rounded-[1.75rem] border border-dashed border-[var(--studio-border)] bg-[var(--studio-card-strong)] p-5 text-sm font-semibold text-[var(--studio-muted)] shadow-[var(--studio-tile-shadow)]">
        Nenhum projeto recente ainda. Comece por Novo video, Editar foto ou escolha uma ferramenta do Studio.
      </div>
    );
  }

  return (
    <div className="flex max-w-full gap-3 overflow-x-auto px-1 pb-3 sm:gap-4">
      {projects.slice(0, 6).map((project, index) => (
        <Link
          key={project.id}
          to={resolveStudioProjectRoute(project.project_type, project.id)}
          style={projectCardStyles[index % projectCardStyles.length]}
          className="min-w-[156px] max-w-[184px] flex-shrink-0 rounded-[1.5rem] p-4 text-left shadow-[var(--studio-tile-shadow)] transition hover:-translate-y-1"
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
  const [search, setSearch] = useState('');

  useEffect(() => {
    let mounted = true;
    async function loadOverview() {
      setLoading(true);
      try {
        const data = await getStudioOverview();
        if (!mounted) return;
        setOverview({ ...emptyOverview, ...data, brand_summary: { ...emptyOverview.brand_summary, ...data.brand_summary } });
        setError(null);
      } catch (err) {
        if (!mounted) return;
        setError(err instanceof Error ? err.message : 'Falha ao carregar Studio.');
        setOverview(emptyOverview);
      } finally {
        if (mounted) setLoading(false);
      }
    }
    void loadOverview();
    return () => {
      mounted = false;
    };
  }, []);

  const filteredTools = useMemo(() => {
    return filterStudioTools(search);
  }, [search]);

  const featuredTools = STUDIO_TOOLS.filter((tool) => tool.featured);
  const libraryTools = search.trim() ? filteredTools : filteredTools.filter((tool) => !tool.featured);

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="relative flex min-h-[calc(100vh-7rem)] w-full max-w-full flex-col overflow-hidden rounded-[2rem] border border-[var(--studio-border)] bg-[var(--studio-bg)] text-[var(--studio-text)] shadow-soft"
    >
      <div className="mx-auto flex w-full max-w-[1440px] flex-1 flex-col px-4 py-5 sm:px-6 sm:py-7 md:px-8">
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="min-w-0">
            <div className="text-[11px] font-semibold uppercase tracking-[0.28em] text-cyan-600">AXI Studio</div>
            <h1 className="mt-2 break-words text-3xl font-black tracking-tight sm:text-4xl">Bora criar bonito?</h1>
            <p className="mt-2 max-w-xl text-sm font-medium text-[var(--studio-muted)]">
              Crie videos, posts e campanhas com IA. O Studio agora organiza criacao, edicao e canais conectados em um fluxo unico.
            </p>
          </div>
          <div className="flex shrink-0 flex-wrap gap-2">
            <Link to="/app/studio/templates" className="inline-flex items-center gap-2 rounded-full border border-[var(--studio-border)] bg-[var(--studio-card)] px-4 py-2 text-sm font-semibold text-[var(--studio-text)] shadow-sm">
              <Sparkles size={16} /> Modelos
            </Link>
            <Link to="/app/account/overview" className="inline-flex items-center gap-2 rounded-full bg-[var(--studio-ink)] px-5 py-2 text-sm font-semibold text-[var(--studio-on-ink)] shadow-lg">
              <Crown size={15} /> Upgrade
            </Link>
          </div>
        </div>

        <div className="mb-7">
          <div className="rounded-[2rem] border border-[var(--studio-border)] bg-[var(--studio-card-strong)] p-4 shadow-[var(--studio-shadow)] sm:p-6">
            <div className="flex items-center gap-3 rounded-[1.5rem] border border-[var(--studio-border)] bg-white px-4 py-3 text-slate-950 shadow-lg">
              <Search size={22} />
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Busque designs, campanhas, videos, posts ou ferramentas"
                className="h-10 min-w-0 flex-1 bg-transparent text-sm font-semibold outline-none placeholder:text-slate-500 sm:text-base"
              />
            </div>
            <div className="mt-5 grid gap-3 sm:grid-cols-4">
              {featuredTools.map((tool) => {
                const Icon = tool.icon;
                return (
                  <Link key={tool.id} to={tool.path} className="group rounded-2xl border border-[var(--studio-border)] bg-[var(--studio-card)] p-3 text-center shadow-[var(--studio-tile-shadow)] transition hover:-translate-y-1">
                    <div className="mx-auto mb-2 flex h-12 w-12 items-center justify-center rounded-2xl bg-[var(--studio-card-strong)] text-[var(--studio-text)] ring-1 ring-[var(--studio-border)]">
                      <Icon size={22} />
                    </div>
                    <span className="text-xs font-black leading-tight text-[var(--studio-text)]">{tool.title}</span>
                  </Link>
                );
              })}
            </div>
          </div>
        </div>

        {loading ? (
          <div className="mb-5 h-2 overflow-hidden rounded-full bg-[var(--studio-card-strong)]">
            <div className="h-full w-1/3 animate-pulse rounded-full bg-cyan" />
          </div>
        ) : null}

        {error ? (
          <div className="mb-5 flex items-center gap-2 rounded-2xl border border-amber-400/20 bg-amber-400/10 px-4 py-3 text-sm font-semibold text-amber-100">
            <AlertTriangle className="h-4 w-4" /> Projetos recentes indisponiveis agora. As ferramentas continuam funcionando.
          </div>
        ) : null}

        <div className="mb-7">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-display text-2xl font-black text-[var(--studio-text)]">Recentes</h2>
            <Link to="/app/studio/projects" className="text-sm font-semibold text-[var(--studio-muted)] hover:text-[var(--studio-text)]">Ver projetos</Link>
          </div>
          <StudioProjectStrip projects={overview.recent_projects} />
        </div>

        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-display text-2xl font-black text-[var(--studio-text)]">Mais ferramentas</h2>
          <span className="text-sm font-semibold text-[var(--studio-muted)]">{libraryTools.length} opcoes</span>
        </div>

        <div className="grid flex-1 grid-cols-[repeat(auto-fit,minmax(104px,1fr))] gap-x-4 gap-y-6 pb-6">
          {libraryTools.map((tool) => {
            const Icon = tool.icon;
            return (
              <Link key={tool.id} to={tool.path} className="group flex min-w-0 flex-col items-center text-center transition hover:-translate-y-1">
                <div className="mb-3 flex h-16 w-16 items-center justify-center rounded-[22px] bg-[var(--studio-card)] text-[var(--studio-text)] shadow-[var(--studio-tile-shadow)] ring-1 ring-[var(--studio-border)] transition group-hover:ring-cyan-300/70 sm:h-[72px] sm:w-[72px] sm:rounded-[24px]">
                  <Icon size={26} />
                </div>
                <span className="max-w-full break-words text-sm font-black leading-tight text-[var(--studio-text)]">{tool.title}</span>
                <span className="mt-1 max-w-[124px] break-words text-[11px] font-semibold leading-tight text-[var(--studio-soft)]">{tool.description}</span>
              </Link>
            );
          })}
        </div>
      </div>

      <div className="border-t border-[var(--studio-border)] bg-[var(--studio-surface)] backdrop-blur-xl">
        <div className="mx-auto grid max-w-[1040px] grid-cols-5 gap-1 px-2 py-2 text-center text-[11px] font-bold text-[var(--studio-soft)] sm:px-6 sm:py-3 sm:text-sm">
          {STUDIO_BOTTOM_NAV.map((item) => {
            const Icon = item.icon;
            return (
              <Link key={item.id} to={item.id === 'video-editor' ? '/app/studio' : item.path} className={['flex min-w-0 flex-col items-center gap-1 px-1 transition hover:text-[var(--studio-text)]', item.id === 'video-editor' ? 'text-[var(--studio-text)]' : 'text-[var(--studio-soft)]'].join(' ')}>
                <Icon className="h-6 w-6 sm:h-7 sm:w-7" />
                <span className="max-w-full truncate">{item.id === 'video-editor' ? 'Criar' : item.title}</span>
              </Link>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
}

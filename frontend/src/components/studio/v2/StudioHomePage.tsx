import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle, ArrowRight, Clock3, FolderOpen, Loader2, Palette, Sparkles } from 'lucide-react';

import { getStudioOverview } from '../../../services/studio.service';
import type { StudioOverviewResponse, StudioRecentProjectItem } from '../../../types/studioV2';
import { STUDIO_HOME_ACTIONS, STUDIO_HOME_CATEGORIES, resolveStudioProjectRoute } from './config/studioHomeConfig';

const routeAliases: Record<string, string> = {
  '/app/studio/poster': '/app/studio/tools/ad',
  '/app/studio/ad-builder': '/app/studio/tools/ad',
  '/app/studio/story': '/app/studio/tools/story',
  '/app/studio/photo-editor': '/app/studio/tools/photo-editor',
  '/app/studio/video-editor': '/app/studio/editor/video',
  '/app/studio/caption-generator': '/app/studio/tools/caption',
  '/app/studio/brand': '/app/studio/brand-kit',
};

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

function normalizeStudioRoute(route: string) {
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

  const brandSummary = useMemo(
    () => [
      { label: 'Logos', value: overview.brand_summary.logos_count, icon: Palette },
      { label: 'Templates', value: overview.brand_summary.templates_count, icon: Sparkles },
      { label: 'Paletas', value: overview.brand_summary.palettes_count, icon: Palette },
      { label: 'Assets', value: overview.brand_summary.assets_count, icon: FolderOpen },
    ],
    [overview.brand_summary],
  );

  return (
    <div className="space-y-6">
      <header className="rounded-3xl border border-white/10 bg-white/[0.04] p-6 shadow-soft">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-300">AXI Studio</p>
            <h1 className="mt-3 font-display text-3xl text-white md:text-4xl">Criacao, edicao e biblioteca visual</h1>
            <p className="mt-2 max-w-2xl text-sm text-slate-300">
              Abra ferramentas reais, continue projetos salvos e acompanhe assets conectados ao backend.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            {STUDIO_HOME_ACTIONS.map((action) => (
              <Link
                key={action.id}
                to={normalizeStudioRoute(action.path)}
                className={`inline-flex items-center gap-2 rounded-2xl px-4 py-3 text-sm font-semibold transition ${
                  action.tone === 'primary'
                    ? 'bg-cyan text-ink hover:brightness-110'
                    : 'border border-white/15 bg-white/5 text-white hover:border-cyan/60'
                }`}
              >
                {action.label}
                <ArrowRight size={16} />
              </Link>
            ))}
          </div>
        </div>
      </header>

      {loading ? (
        <div className="flex items-center gap-2 rounded-2xl border border-white/10 bg-black/20 p-4 text-sm text-slate-300">
          <Loader2 className="h-4 w-4 animate-spin text-cyan-300" />
          Carregando Studio...
        </div>
      ) : null}

      {error ? (
        <div className="flex items-center gap-2 rounded-2xl border border-rose-400/30 bg-rose-500/10 p-4 text-sm text-rose-100">
          <AlertTriangle className="h-4 w-4" />
          {error}
        </div>
      ) : null}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {brandSummary.map((item) => {
          const Icon = item.icon;
          return (
            <div key={item.label} className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
              <div className="flex items-center justify-between">
                <p className="text-sm text-slate-300">{item.label}</p>
                <Icon className="h-4 w-4 text-cyan-300" />
              </div>
              <p className="mt-3 text-3xl font-bold text-white">{item.value}</p>
            </div>
          );
        })}
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="space-y-4">
          {STUDIO_HOME_CATEGORIES.map((category) => (
            <div key={category.id} className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
              <div className="mb-4">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-300">{category.label}</p>
                <p className="mt-1 text-sm text-slate-300">{category.description}</p>
              </div>

              <div className="grid gap-3 md:grid-cols-2 2xl:grid-cols-3">
                {category.tools.map((tool) => {
                  const Icon = tool.icon;
                  return (
                    <Link
                      key={tool.id}
                      to={normalizeStudioRoute(tool.path)}
                      className="group min-h-36 rounded-2xl border border-white/10 bg-black/20 p-4 transition hover:-translate-y-0.5 hover:border-cyan/50 hover:bg-white/[0.06]"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <span className="rounded-xl bg-cyan/15 p-2 text-cyan-200">
                          <Icon size={22} />
                        </span>
                        {tool.badge ? (
                          <span className="rounded-full border border-cyan/35 px-2 py-1 text-[11px] font-semibold text-cyan-100">
                            {tool.badge}
                          </span>
                        ) : null}
                      </div>
                      <h3 className="mt-4 text-base font-semibold text-white">{tool.title}</h3>
                      <p className="mt-1 text-sm text-slate-300">{tool.description}</p>
                      <span className="mt-4 inline-flex items-center gap-1 text-xs font-semibold text-cyan-200">
                        Abrir ferramenta <ArrowRight size={13} />
                      </span>
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        <aside className="space-y-4">
          <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-300">Continuar</p>
                <h2 className="mt-1 text-lg font-semibold text-white">Projetos recentes</h2>
              </div>
              <Link to="/app/studio/projects" className="text-xs font-semibold text-cyan-200 hover:text-cyan-100">
                Ver todos
              </Link>
            </div>

            <div className="space-y-3">
              {overview.recent_projects.length > 0 ? (
                overview.recent_projects.map((project) => (
                  <Link
                    key={project.id}
                    to={recentProjectRoute(project)}
                    className="flex items-center gap-3 rounded-2xl border border-white/10 bg-black/20 p-3 transition hover:border-cyan/50 hover:bg-white/[0.06]"
                  >
                    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-cyan/10 text-cyan-200">
                      <FolderOpen size={20} />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-semibold text-white">{project.title}</p>
                      <p className="mt-0.5 flex items-center gap-1 text-xs text-slate-400">
                        <Clock3 size={12} />
                        {project.project_type} - {formatUpdatedAt(project.updated_at)}
                      </p>
                    </div>
                    <ArrowRight className="h-4 w-4 text-slate-500" />
                  </Link>
                ))
              ) : (
                <p className="rounded-2xl border border-dashed border-white/15 p-4 text-sm text-slate-400">
                  Nenhum projeto criado ainda.
                </p>
              )}
            </div>
          </section>

          <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-300">Acoes sugeridas</p>
            <div className="mt-4 space-y-3">
              {overview.suggested_actions.map((action) => (
                <Link
                  key={action.id}
                  to={normalizeStudioRoute(action.route)}
                  className="block rounded-2xl border border-white/10 bg-black/20 p-4 transition hover:border-cyan/50 hover:bg-white/[0.06]"
                >
                  <p className="text-sm font-semibold text-white">{action.label}</p>
                  <p className="mt-1 text-xs text-slate-400">{action.description}</p>
                </Link>
              ))}
              {overview.suggested_actions.length === 0 ? (
                <p className="rounded-2xl border border-dashed border-white/15 p-4 text-sm text-slate-400">
                  As sugestoes aparecem depois que o backend carrega seu contexto.
                </p>
              ) : null}
            </div>
          </section>
        </aside>
      </section>
    </div>
  );
}

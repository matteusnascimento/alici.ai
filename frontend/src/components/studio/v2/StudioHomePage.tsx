import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { useToast } from '../../../hooks/useToast';
import { getStudioOverview } from '../../../services/studio.service';
import type { StudioOverviewResponse } from '../../../types/studioV2';
import { StudioRecentProject } from './cards/StudioRecentProject';
import { STUDIO_HOME_ACTIONS, STUDIO_HOME_CATEGORIES } from './config/studioHomeConfig';

export function StudioHomePage() {
  const navigate = useNavigate();
  const toast = useToast();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [overview, setOverview] = useState<StudioOverviewResponse | null>(null);

  useEffect(() => {
    let mounted = true;

    async function loadOverview() {
      setLoading(true);
      try {
        const data = await getStudioOverview();
        if (mounted) {
          setOverview(data);
          setError(null);
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Falha ao carregar o Studio.');
          toast.error('Falha ao carregar o AXI Studio.');
        }
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
  }, [toast]);

  const recentProjects = useMemo(() => (overview?.recent_projects || []).slice(0, 5), [overview]);

  return (
    <div className="min-h-screen space-y-12 pb-12">
      {/* Hero */}
      <section className="relative overflow-hidden rounded-3xl border border-white/10 p-8 md:p-12">
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 via-transparent to-blue-500/5" />
        <div className="absolute -right-32 -top-32 h-64 w-64 rounded-full bg-cyan-500/10 blur-3xl" />

        <div className="relative z-10">
          <p className="text-xs uppercase tracking-widest text-white/60">AXI Studio</p>
          <h1 className="mt-3 max-w-4xl font-display text-5xl font-bold leading-tight text-white md:text-6xl">
            Crie conteudo visual escalavel
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-white/70">
            Ferramentas profissionais para criar, editar, gerenciar e escalar sua producao visual com fluxo intuitivo.
          </p>

          <div className="mt-8 flex flex-wrap gap-3">
            {STUDIO_HOME_ACTIONS.map((action) => (
              <button
                key={action.id}
                onClick={() => navigate(action.path)}
                className={
                  action.tone === 'primary'
                    ? 'rounded-xl bg-gradient-to-r from-cyan-500 to-blue-500 px-6 py-3 font-semibold text-white transition-all hover:from-cyan-600 hover:to-blue-600 hover:shadow-lg hover:shadow-cyan-500/20'
                    : 'rounded-xl border border-white/20 bg-white/5 px-6 py-3 font-semibold text-white transition-all hover:border-white/30 hover:bg-white/10'
                }
              >
                {action.label}
              </button>
            ))}
            <button
              onClick={() => navigate('/app/studio/projects')}
              className="rounded-xl border border-white/20 bg-white/5 px-6 py-3 font-semibold text-white transition-all hover:border-white/30 hover:bg-white/10"
            >
              Ver projetos
            </button>
          </div>
        </div>
      </section>

      {/* Projetos recentes */}
      {recentProjects.length > 0 && (
        <section className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="max-w-2xl">
              <h2 className="font-display text-3xl font-bold text-white">Continuar</h2>
              <p className="mt-2 text-white/60">Retome seus projetos recentes e continue de onde parou.</p>
            </div>
            <button
              onClick={() => navigate('/app/studio/projects')}
              className="rounded-lg px-4 py-2 text-sm text-white/60 transition-all hover:bg-white/10 hover:text-white"
            >
              Ver todos
            </button>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
            {recentProjects.map((project) => (
              <StudioRecentProject
                key={project.id}
                id={String(project.id)}
                projectKey={String(project.id)}
                title={project.title}
                type={project.project_type}
                lastEdited={project.updated_at}
                thumbnail={project.thumbnail_url ?? undefined}
              />
            ))}
          </div>
        </section>
      )}

      {/* Categorias de ferramentas */}
      {STUDIO_HOME_CATEGORIES.map((category) => (
        <section key={category.id} className="space-y-6">
          <div className="max-w-2xl">
            <h2 className="font-display text-3xl font-bold text-white">{category.label}</h2>
            <p className="mt-2 text-white/60">{category.description}</p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {category.tools.map((tool) => {
              const Icon = tool.icon;
              return (
                <button
                  key={tool.id}
                  onClick={() => navigate(tool.path)}
                  className="group relative overflow-hidden rounded-xl border border-white/10 bg-white/5 p-6 text-left transition-all hover:border-white/20 hover:bg-white/10 hover:shadow-lg"
                >
                  <div className="flex items-start gap-4">
                    <div className="rounded-lg bg-white/10 p-3 transition-transform group-hover:scale-110">
                      <Icon className="h-5 w-5 text-white" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-white">{tool.title}</h3>
                        {tool.badge && (
                          <span className="rounded-full bg-cyan-500/20 px-2 py-0.5 text-xs font-medium text-cyan-300">
                            {tool.badge}
                          </span>
                        )}
                      </div>
                      <p className="mt-1 text-sm text-white/60">{tool.description}</p>
                    </div>
                  </div>
                  <span className="absolute bottom-4 right-4 text-xs font-semibold text-white/30 transition-colors group-hover:text-white/60">
                    Abrir →
                  </span>
                </button>
              );
            })}
          </div>
        </section>
      ))}

      {/* Biblioteca */}
      <section className="space-y-4">
        <h2 className="font-display text-3xl font-bold text-white">Biblioteca</h2>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {[
            { id: 'brand-kit', label: 'Brand Kit', path: '/app/studio/brand-kit' },
            { id: 'templates', label: 'Templates', path: '/app/studio/templates' },
            { id: 'assets', label: 'Assets', path: '/app/studio/assets' },
            { id: 'exports', label: 'Exportacoes', path: '/app/studio/exports' },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => navigate(item.path)}
              className="rounded-xl border border-white/10 bg-white/5 px-5 py-4 text-left font-semibold text-white transition-all hover:border-white/20 hover:bg-white/10"
            >
              {item.label}
            </button>
          ))}
        </div>
      </section>

      {loading && <div className="h-1 w-full animate-pulse rounded-full bg-cyan-400/30" />}
      {error && (
        <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-200">{error}</div>
      )}
    </div>
  );
}

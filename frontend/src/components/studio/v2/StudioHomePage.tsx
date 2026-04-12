import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Zap } from 'lucide-react';

import { useToast } from '../../../hooks/useToast';
import { getStudioOverview } from '../../../services/studio.service';
import type { StudioOverviewResponse } from '../../../types/studioV2';
import { StudioLinkCard } from './cards/StudioLinkCard';
import { StudioRecentProject } from './cards/StudioRecentProject';
import { StudioToolCard } from './cards/StudioToolCard';
import { CREATE_TOOLS, LIBRARY_LINKS, MANAGE_LINKS } from './config/studioToolsConfig';

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
            <button
              onClick={() => navigate('/app/studio/video-editor')}
              className="rounded-xl bg-gradient-to-r from-cyan-500 to-blue-500 px-6 py-3 font-semibold text-white transition-all hover:from-cyan-600 hover:to-blue-600 hover:shadow-lg hover:shadow-cyan-500/20"
            >
              Iniciar criacao
            </button>
            <button
              onClick={() => navigate('/app/studio/projects')}
              className="rounded-xl border border-white/20 bg-white/5 px-6 py-3 font-semibold text-white transition-all hover:border-white/30 hover:bg-white/10"
            >
              Ver projetos
            </button>
          </div>
        </div>
      </section>

      <section className="space-y-6">
        <div className="max-w-2xl">
          <div className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-cyan-400" />
            <h2 className="font-display text-3xl font-bold text-white">Criar</h2>
          </div>
          <p className="mt-2 text-white/60">Escolha uma ferramenta para comecar seu novo criativo.</p>
        </div>

        <div className="grid auto-rows-[minmax(240px,auto)] gap-4 md:grid-cols-2 xl:grid-cols-3">
          {CREATE_TOOLS.map((tool) => (
            <StudioToolCard key={tool.id} {...tool} path={tool.path} />
          ))}
        </div>
      </section>

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

      <section className="space-y-6">
        <div className="max-w-2xl">
          <h2 className="font-display text-3xl font-bold text-white">Gerenciar</h2>
          <p className="mt-2 text-white/60">Acesse areas de organizacao e operacao do Studio.</p>
        </div>

        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {MANAGE_LINKS.map((link) => (
            <StudioLinkCard key={link.id} {...link} color={link.color} variant="manage" />
          ))}
        </div>
      </section>

      <section className="space-y-6">
        <div className="max-w-2xl">
          <h2 className="font-display text-3xl font-bold text-white">Biblioteca</h2>
          <p className="mt-2 text-white/60">Central de ativos e elementos de marca para manter consistencia.</p>
        </div>

        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {LIBRARY_LINKS.map((link) => (
            <StudioLinkCard key={link.id} {...link} color={link.color} variant="library" />
          ))}
        </div>
      </section>

      {loading ? <div className="h-1 w-full animate-pulse rounded-full bg-cyan-400/30" /> : null}

      {error ? (
        <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-200">{error}</div>
      ) : null}
    </div>
  );
}

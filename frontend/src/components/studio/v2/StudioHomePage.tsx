import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Zap } from 'lucide-react';

import { useToast } from '../../../hooks/useToast';
import { getStudioOverview } from '../../../services/studio.service';
import type { StudioOverviewResponse } from '../../../types/studioV2';
import { StudioToolCard } from './cards/StudioToolCard';
import { StudioLinkCard } from './cards/StudioLinkCard';
import { StudioRecentProject } from './cards/StudioRecentProject';
import { CREATE_TOOLS, MANAGE_LINKS, LIBRARY_LINKS } from './config/studioToolsConfig';


const projectRouteByType: Record<string, string> = {
  poster: '/app/studio/poster',
  story: '/app/studio/story',
  ad: '/app/studio/ad-builder',
  banner: '/app/studio/banner',
  video: '/app/studio/video-editor',
  'video-editor': '/app/studio/video-editor',
  'photo-edit': '/app/studio/photo-editor',
  'photo-editor': '/app/studio/photo-editor',
  campaign: '/app/studio/campaign',
};

function resolveProjectRoute(projectType: string): string {
  return projectRouteByType[projectType] || '/app/studio/projects';
}

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
  }, []);

  const recentProjects = useMemo(() => (overview?.recent_projects || []).slice(0, 5), [overview]);

  return (
    <div className="min-h-screen space-y-12 pb-12">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-3xl border border-white/10 p-8 md:p-12">
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 via-transparent to-purple-500/5" />
        <div className="absolute -right-32 -top-32 h-64 w-64 rounded-full bg-cyan-500/10 blur-3xl" />

        <div className="relative z-10">
          <p className="text-xs uppercase tracking-widest text-white/60">AXI Studio</p>
          <h1 className="mt-3 max-w-4xl font-display text-5xl md:text-6xl font-bold leading-tight text-white">
            Crie conteúdo visual escalável
          </h1>
          <p className="mt-4 max-w-2xl text-base text-white/70 leading-relaxed">
            Ferramentas profissionais para criar, editar, gerenciar e escalar sua produção visual com fluxo intuitivo.
          </p>

          <div className="mt-8 flex flex-wrap gap-3">
            <button
              onClick={() => navigate('/app/studio/video-editor')}
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-semibold hover:from-cyan-600 hover:to-blue-600 transition-all hover:shadow-lg hover:shadow-cyan-500/20"
            >
              Iniciar criação
            </button>
            <button
              onClick={() => navigate('/app/studio/projects')}
              className="px-6 py-3 rounded-xl border border-white/20 bg-white/5 text-white font-semibold hover:bg-white/10 hover:border-white/30 transition-all"
            >
              Ver projetos
            </button>
          </div>
        </div>
      </section>

      {/* SECTION 1: CRIAR (CREATE) */}
      <section className="space-y-6">
        <div className="max-w-2xl">
          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-cyan-400" />
            <h2 className="font-display text-3xl font-bold text-white">Criar</h2>
          </div>
          <p className="mt-2 text-white/60">Escolha uma ferramenta para começar seu novo criativo. Cada uma é otimizada para resultados profissionais.</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3 auto-rows-[minmax(240px,auto)]">
          {CREATE_TOOLS.map((tool) => (
            <StudioToolCard
              key={tool.id}
              {...tool}
              path={tool.path}
            />
          ))}
        </div>
      </section>

      {/* SECTION 2: CONTINUAR (CONTINUE) */}
      {recentProjects.length > 0 && (
        <section className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="max-w-2xl">
              <h2 className="font-display text-3xl font-bold text-white">Continuar</h2>
              <p className="mt-2 text-white/60">Retome seus projetos recentes e continue trabalhando de onde parou.</p>
            </div>
            <button
              onClick={() => navigate('/app/studio/projects')}
              className="px-4 py-2 rounded-lg text-sm text-white/60 hover:text-white hover:bg-white/10 transition-all"
            >
              Ver todos →
            </button>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
            {recentProjects.map((project) => (
              <StudioRecentProject
                key={project.id}
                id={project.id}
                projectKey={project.id}
                title={project.title}
                type={project.project_type}
                lastEdited={project.updated_at}
              />
            ))}
          </div>
      </section>
      )}

      {/* SECTION 3: GERENCIAR (MANAGE) */}
      <section className="space-y-6">
        <div className="max-w-2xl">
          <h2 className="font-display text-3xl font-bold text-white">Gerenciar</h2>
          <p className="mt-2 text-white/60">Acesse áreas de organização, monitoramento e operações do Studio.</p>
        </div>

        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {MANAGE_LINKS.map((link) => (
            <StudioLinkCard
              key={link.id}
              {...link}
              color={link.color}
              variant="manage"
            />
          ))}
        </div>
      </section>

      {/* SECTION 4: BIBLIOTECA (LIBRARY) */}
      <section className="space-y-6">
        <div className="max-w-2xl">
          <h2 className="font-display text-3xl font-bold text-white">Biblioteca</h2>
          <p className="mt-2 text-white/60">Central de ativos, templates e brand guidelines para manter consistência.</p>
        </div>

        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {LIBRARY_LINKS.map((link) => (
            <StudioLinkCard
              key={link.id}
              {...link}
              color={link.color}
              variant="library"
            />
          ))}
        </div>
      </section>

      {error && (
        <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-200">
          {error}
        </div>
      )}
    </div>
  );
}

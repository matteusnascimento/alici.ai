import { useNavigate } from 'react-router-dom';

import { getProjects } from '../../../services/projectService';
import { studioNavItems } from '../studioConfig';
import { EmptyState } from '../EmptyState';
import { ProjectCard } from '../ProjectCard';

export function StudioHomePage() {
  const navigate = useNavigate();
  const projects = getProjects().slice(0, 6);

  const categories = ['Create / Generate', 'Photo / Image', 'Video / Content', 'Business / Workspace'] as const;

  function normalizeStudioRoute(route: string) {
    return route.replace('/app/marketing', '/app/studio');
  }

  return (
    <div className="space-y-6">
      {categories.map((category) => (
        <section key={category} className="rounded-3xl border border-white/10 bg-white/[0.02] p-4">
          <h2 className="mb-4 font-display text-2xl text-white">{category}</h2>
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {studioNavItems
              .filter((item) => item.category === category)
              .map((item) => (
                <button
                  key={item.route}
                  type="button"
                  onClick={() => navigate(item.route)}
                  className="rounded-2xl border border-white/10 bg-white/[0.03] p-4 text-left transition hover:border-cyan/35 hover:bg-cyan/5"
                >
                  <span className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-ink/60 text-cyan">
                    <item.icon size={17} />
                  </span>
                  <p className="mt-3 font-semibold text-white">{item.title}</p>
                  <p className="mt-2 text-sm text-slate-300">{item.description}</p>
                </button>
              ))}
          </div>
        </section>
      ))}

      <section className="rounded-3xl border border-white/10 bg-white/[0.02] p-4">
        <h2 className="mb-4 font-display text-2xl text-white">Projetos recentes</h2>
        {!projects.length ? (
          <EmptyState title="Nenhum projeto salvo" description="Comece por uma ferramenta para gerar e salvar seus primeiros projetos." />
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {projects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                onOpen={() => navigate(`${normalizeStudioRoute(project.route)}?projectId=${project.id}`)}
                onDelete={() => {}}
                onDuplicate={() => {}}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

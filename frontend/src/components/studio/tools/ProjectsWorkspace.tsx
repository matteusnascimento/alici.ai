import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { deleteProject, duplicateProject, getProjects } from '../../../services/projectService';
import type { StudioProject } from '../../../types/projects';
import { EmptyState } from '../EmptyState';
import { ProjectCard } from '../ProjectCard';

export function ProjectsWorkspace() {
  const navigate = useNavigate();
  const [filter, setFilter] = useState('all');
  const [refreshKey, setRefreshKey] = useState(0);

  const projects = getProjects();

  const filtered = useMemo(
    () => projects.filter((project) => filter === 'all' || project.type === filter),
    [filter, projects, refreshKey],
  );

  function refresh() {
    setRefreshKey((current) => current + 1);
  }

  function normalizeStudioRoute(route: string) {
    return route.replace('/app/marketing', '/app/studio');
  }

  return (
    <div className="space-y-4">
      <button type="button" onClick={() => navigate('/app/studio')} className="text-sm text-cyan">← Voltar para AXI Studio</button>
      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
        <div className="mb-4 flex flex-wrap items-center gap-2">
          <span className="text-sm text-slate-300">Filtro:</span>
          {['all', 'ads', 'product-photos', 'poster', 'photo-editor', 'marketing-tools', 'captions', 'audio-tools', 'teleprompter'].map((option) => (
            <button key={option} type="button" onClick={() => setFilter(option)} className={[
              'rounded-xl border px-3 py-2 text-xs capitalize',
              filter === option ? 'border-cyan/40 bg-cyan/10 text-cyan' : 'border-white/15 text-slate-200',
            ].join(' ')}>
              {option}
            </button>
          ))}
        </div>

        {!filtered.length ? (
          <EmptyState title="Sem projetos" description="Nao ha projetos para este filtro. Gere e salve em qualquer ferramenta do studio." />
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {filtered.map((project: StudioProject) => (
              <ProjectCard
                key={project.id}
                project={project}
                onOpen={() => navigate(`${normalizeStudioRoute(project.route)}?projectId=${project.id}`)}
                onDelete={() => {
                  deleteProject(project.id);
                  refresh();
                }}
                onDuplicate={() => {
                  const copy = duplicateProject(project.id);
                  if (copy) refresh();
                }}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

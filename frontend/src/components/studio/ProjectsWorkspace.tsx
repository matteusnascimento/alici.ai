import { useState } from 'react';

interface ProjectItem {
  id: string;
  name: string;
  updatedAt: string;
  type: string;
}

const initialProjects: ProjectItem[] = [
  { id: '1', name: 'Campanha Hotel Outono', updatedAt: 'Hoje 14:20', type: 'Anuncio' },
  { id: '2', name: 'Poster Evento Local', updatedAt: 'Ontem 18:05', type: 'Poster' },
  { id: '3', name: 'Fluxo WhatsApp Clinica', updatedAt: '2 dias atras', type: 'Marketing' },
];

interface ProjectsWorkspaceProps {
  onNotify: (msg: string) => void;
}

export function ProjectsWorkspace({ onNotify }: ProjectsWorkspaceProps) {
  const [projects] = useState<ProjectItem[]>(initialProjects);

  return (
    <section className="space-y-4 rounded-3xl border border-white/10 bg-white/[0.03] p-5">
      <div className="flex items-center justify-between">
        <h3 className="font-display text-2xl text-white">Projetos</h3>
        <button
          type="button"
          className="rounded-2xl border border-cyan/35 bg-cyan/10 px-4 py-2 text-sm text-cyan"
          onClick={() => onNotify('Novo projeto criado em modo mock.')}
        >
          Novo projeto
        </button>
      </div>

      {!projects.length ? (
        <div className="rounded-2xl border border-dashed border-white/15 bg-ink/40 p-8 text-center text-sm text-slate-300">
          Nenhum projeto salvo ainda.
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {projects.map((project) => (
            <article key={project.id} className="rounded-2xl border border-white/10 bg-ink/40 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-cyan">{project.type}</p>
              <h4 className="mt-2 font-semibold text-white">{project.name}</h4>
              <p className="mt-2 text-xs text-slate-300">Atualizado em {project.updatedAt}</p>
              <button
                type="button"
                onClick={() => onNotify(`Projeto aberto: ${project.name}`)}
                className="mt-4 rounded-xl border border-white/15 px-3 py-2 text-xs text-slate-100"
              >
                Abrir workspace
              </button>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

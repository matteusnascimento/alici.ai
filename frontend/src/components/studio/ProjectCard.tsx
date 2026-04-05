import type { StudioProject } from '../../types/projects';

interface ProjectCardProps {
  project: StudioProject;
  onOpen: () => void;
  onDelete: () => void;
  onDuplicate: () => void;
}

export function ProjectCard({ project, onOpen, onDelete, onDuplicate }: ProjectCardProps) {
  return (
    <article className="rounded-2xl border border-white/10 bg-ink/40 p-4">
      <p className="text-xs uppercase tracking-[0.2em] text-cyan">{project.type}</p>
      <h3 className="mt-2 font-semibold text-white">{project.title}</h3>
      <p className="mt-2 text-sm text-slate-300">{project.description}</p>
      <p className="mt-3 text-xs text-slate-400">Atualizado: {new Date(project.updated_at).toLocaleString('pt-BR')}</p>
      <div className="mt-4 flex gap-2">
        <button type="button" onClick={onOpen} className="rounded-xl border border-cyan/35 bg-cyan/10 px-3 py-2 text-xs text-cyan">
          Abrir
        </button>
        <button type="button" onClick={onDuplicate} className="rounded-xl border border-white/20 px-3 py-2 text-xs text-slate-200">
          Duplicar
        </button>
        <button type="button" onClick={onDelete} className="rounded-xl border border-white/20 px-3 py-2 text-xs text-slate-200">
          Excluir
        </button>
      </div>
    </article>
  );
}

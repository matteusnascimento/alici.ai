import { Link } from 'react-router-dom';

import { useStudioV2 } from '../../../hooks/useStudioV2';
import { useToast } from '../../../hooks/useToast';

export function ProjectsStudioPage() {
  const { projects } = useStudioV2({ defaultType: 'projects-hub', defaultTitle: 'Projetos Studio' });
  const toast = useToast();

  return (
    <div className="space-y-4">
      <header className="rounded-3xl border border-white/10 bg-white/5 p-5">
        <p className="text-xs uppercase tracking-[0.24em] text-cyan-300">Projects</p>
        <h1 className="mt-2 font-display text-3xl text-white">Projetos, campanhas, exportados e historico</h1>
      </header>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {projects.map((project) => (
          <article key={project.id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="font-semibold text-white">{project.title}</p>
            <p className="text-xs text-slate-400">{project.project_type}</p>
            <p className="mt-2 text-xs text-slate-500">Atualizado em {new Date(project.updated_at).toLocaleString('pt-BR')}</p>
            <div className="mt-3 flex gap-2">
              <Link to="/app/studio/poster" onClick={() => toast.info(`Abrindo projeto ${project.title}.`)} className="rounded-lg border border-cyan-300/40 px-3 py-1 text-xs text-cyan-100">Abrir</Link>
              <Link to="/app/studio/video-editor" onClick={() => toast.info('Abrindo campanha relacionada.')} className="rounded-lg border border-white/20 px-3 py-1 text-xs text-slate-100">Campanha</Link>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}

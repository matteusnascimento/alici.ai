import { Link } from 'react-router-dom';

import { useStudioV2 } from '../../../hooks/useStudioV2';

const quickActions = [
  { label: 'Criar Poster', route: '/app/studio/poster' },
  { label: 'Criar Story', route: '/app/studio/story' },
  { label: 'Editar Foto', route: '/app/studio/photo-editor' },
  { label: 'Criar Video', route: '/app/studio/video-editor' },
  { label: 'Remover Fundo', route: '/app/studio/remove-background' },
  { label: 'Gerar Legenda', route: '/app/studio/legendas' },
  { label: 'Criar Anuncio', route: '/app/studio/banner' },
];

export function StudioHomePage() {
  const { projects, templates, assets } = useStudioV2({ defaultType: 'studio-home', defaultTitle: 'Studio Workspace' });

  return (
    <div className="space-y-6">
      <section className="rounded-3xl border border-cyan-400/20 bg-[radial-gradient(circle_at_20%_0%,rgba(0,212,255,0.22),transparent_48%),linear-gradient(160deg,#051028,#0b2243)] p-8">
        <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">AXI Studio</p>
        <h1 className="mt-3 max-w-3xl font-display text-4xl leading-tight text-white md:text-5xl">Crie campanhas, posts, imagens e videos com IA em um unico workspace.</h1>
      </section>

      <section className="grid gap-3 md:grid-cols-4">
        {quickActions.map((action) => (
          <Link key={action.route} to={action.route} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-4 text-sm font-semibold text-white hover:border-cyan-300/40 hover:bg-cyan-400/10">
            {action.label}
          </Link>
        ))}
      </section>

      <section className="grid gap-4 lg:grid-cols-3">
        <article className="rounded-3xl border border-white/10 bg-white/5 p-4 lg:col-span-2">
          <h3 className="font-display text-2xl text-white">Projetos recentes</h3>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {projects.slice(0, 4).map((project) => (
              <div key={project.id} className="rounded-2xl border border-white/10 bg-black/20 p-3">
                <p className="font-semibold text-white">{project.title}</p>
                <p className="text-xs text-slate-400">{project.project_type}</p>
              </div>
            ))}
            {projects.length === 0 ? <p className="text-sm text-slate-400">Nenhum projeto recente.</p> : null}
          </div>
        </article>

        <article className="rounded-3xl border border-white/10 bg-white/5 p-4">
          <h3 className="font-display text-2xl text-white">Acoes sugeridas</h3>
          <div className="mt-4 space-y-2 text-sm text-slate-200">
            <p className="rounded-xl border border-white/10 bg-black/20 p-3">Crie uma campanha para fim de semana</p>
            <p className="rounded-xl border border-white/10 bg-black/20 p-3">Transforme essa foto em anuncio</p>
            <p className="rounded-xl border border-white/10 bg-black/20 p-3">Gere um video promocional</p>
          </div>
        </article>
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        <article className="rounded-3xl border border-white/10 bg-white/5 p-4">
          <h3 className="font-display text-xl text-white">Brand shortcuts</h3>
          <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
            <p className="rounded-xl border border-white/10 bg-black/20 p-3 text-slate-200">Logos: {assets.length}</p>
            <p className="rounded-xl border border-white/10 bg-black/20 p-3 text-slate-200">Templates: {templates.length}</p>
            <p className="rounded-xl border border-white/10 bg-black/20 p-3 text-slate-200">Paletas</p>
            <p className="rounded-xl border border-white/10 bg-black/20 p-3 text-slate-200">Assets</p>
          </div>
        </article>

        <article className="rounded-3xl border border-white/10 bg-white/5 p-4">
          <h3 className="font-display text-xl text-white">Exportacoes recentes</h3>
          <div className="mt-4 space-y-2 text-sm text-slate-300">
            <p className="rounded-xl border border-white/10 bg-black/20 p-3">PNG campanha primavera</p>
            <p className="rounded-xl border border-white/10 bg-black/20 p-3">MP4 ad vertical 9:16</p>
            <p className="rounded-xl border border-white/10 bg-black/20 p-3">ZIP pacote anuncios</p>
          </div>
        </article>
      </section>
    </div>
  );
}

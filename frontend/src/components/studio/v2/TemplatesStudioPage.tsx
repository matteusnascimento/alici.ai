import { useStudioV2 } from '../../../hooks/useStudioV2';

export function TemplatesStudioPage() {
  const studio = useStudioV2({ defaultType: 'templates', defaultTitle: 'Templates Studio' });

  return (
    <div className="space-y-4">
      <header className="rounded-3xl border border-white/10 bg-white/5 p-5">
        <p className="text-xs uppercase tracking-[0.24em] text-cyan-300">Brand</p>
        <h1 className="mt-2 font-display text-3xl text-white">Templates premium e Brand Kit</h1>
      </header>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {studio.templates.map((template) => (
          <article key={template.id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="font-semibold text-white">{template.name}</p>
            <p className="text-xs text-slate-400">{template.category}</p>
            <button type="button" className="mt-3 rounded-lg border border-cyan-300/40 px-3 py-1 text-xs text-cyan-100" onClick={() => void studio.applyTemplate(template.id)}>
              Aplicar no projeto atual
            </button>
          </article>
        ))}
      </div>
    </div>
  );
}

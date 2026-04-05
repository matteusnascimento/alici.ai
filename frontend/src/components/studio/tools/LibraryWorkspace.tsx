import { useNavigate } from 'react-router-dom';

import { getLibraryTemplates } from '../../../services/studioService';
import { EmptyState } from '../EmptyState';

export function LibraryWorkspace() {
  const navigate = useNavigate();
  const templates = getLibraryTemplates();

  return (
    <div className="space-y-4">
      <button type="button" onClick={() => navigate('/app/studio')} className="text-sm text-cyan">← Voltar para AXI Studio</button>
      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
        <h2 className="font-display text-2xl text-white">Biblioteca</h2>
        <p className="mt-2 text-sm text-slate-300">Templates, estilos e presets reaproveitaveis com prefill de formularios.</p>

        {!templates.length ? (
          <EmptyState title="Sem templates" description="Adicione presets para acelerar workflows por nicho." />
        ) : (
          <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {templates.map((template) => (
              <article key={template.id} className="rounded-2xl border border-white/10 bg-ink/40 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-cyan">{template.category}</p>
                <h3 className="mt-2 font-semibold text-white">{template.title}</h3>
                <p className="mt-2 text-sm text-slate-300">{template.description}</p>
                <div className="mt-4 flex gap-2">
                  <button type="button" onClick={() => navigate(template.targetToolRoute)} className="rounded-xl border border-cyan/35 bg-cyan/10 px-3 py-2 text-xs text-cyan">
                    Usar template
                  </button>
                  <button type="button" className="rounded-xl border border-white/20 px-3 py-2 text-xs text-slate-100">
                    Preview
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

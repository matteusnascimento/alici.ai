import { useState } from 'react';

interface PosterWorkspaceProps {
  onNotify: (msg: string) => void;
}

export function PosterWorkspace({ onNotify }: PosterWorkspaceProps) {
  const [form, setForm] = useState({
    posterType: 'Oferta de produto',
    event: 'Campanha Abril',
    headline: 'Transforme interesse em vendas com AXI Studio',
    subheadline: 'Crie campanhas visuais e copie em minutos',
    cta: 'Solicitar demonstracao',
  });

  return (
    <div className="grid gap-6 xl:grid-cols-[360px_1fr]">
      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
        <h3 className="font-display text-2xl text-white">Poster com IA</h3>
        <p className="mt-2 text-sm text-slate-300">Configure estrutura de poster para oferta, evento ou produto.</p>
        <div className="mt-4 space-y-3">
          {Object.entries(form).map(([key, value]) => (
            <label key={key} className="block space-y-2 text-sm text-slate-300">
              <span className="capitalize">{key}</span>
              <input
                className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white outline-none focus:border-cyan"
                value={value}
                onChange={(event) => setForm((current) => ({ ...current, [key]: event.target.value }))}
              />
            </label>
          ))}
        </div>
        <button
          type="button"
          onClick={() => onNotify('Poster mock atualizado.')}
          className="mt-4 w-full rounded-2xl border border-cyan/35 bg-cyan/10 px-4 py-3 text-sm text-cyan"
        >
          Atualizar preview
        </button>
      </section>

      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
        <div className="mx-auto max-w-xl rounded-3xl border border-white/15 bg-[linear-gradient(140deg,rgba(17,36,59,0.9),rgba(8,17,31,0.95))] p-8">
          <p className="text-xs uppercase tracking-[0.2em] text-cyan">{form.posterType}</p>
          <h4 className="mt-4 font-display text-3xl text-white">{form.headline}</h4>
          <p className="mt-4 text-slate-200">{form.subheadline}</p>
          <p className="mt-6 inline-flex rounded-full border border-white/20 px-4 py-2 text-sm text-slate-100">{form.event}</p>
          <button className="mt-6 rounded-2xl bg-sand px-4 py-3 text-sm font-semibold text-ink" type="button">
            {form.cta}
          </button>
        </div>
      </section>
    </div>
  );
}

import { FormEvent, useState } from 'react';

import { useMarketing } from '../../hooks/useMarketing';

export function MarketingPanel() {
  const { result, loading, error, runCampaign } = useMarketing();
  const [form, setForm] = useState({
    company_name: 'AXI',
    audience: 'times comerciais e operação digital',
    objective: 'gerar reuniões qualificadas',
    offer: 'uma operação AI unificada',
    tone: 'premium',
  });

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await runCampaign(form);
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
      <section className="panel-base">
        <h3 className="font-display text-2xl text-white">Gerar campanha textual</h3>
        <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
          {[
            ['company_name', 'Empresa'],
            ['audience', 'Público'],
            ['objective', 'Objetivo'],
            ['offer', 'Oferta'],
            ['tone', 'Tom'],
          ].map(([key, label]) => (
            <div key={key}>
              <label className="mb-2 block text-sm text-slate-300">{label}</label>
              <input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none focus:border-cyan" value={form[key as keyof typeof form]} onChange={(event) => setForm((current) => ({ ...current, [key]: event.target.value }))} required />
            </div>
          ))}
          <button className="w-full rounded-2xl bg-sand px-4 py-3 font-semibold text-ink transition hover:bg-white disabled:opacity-60" disabled={loading} type="submit">
            {loading ? 'Gerando...' : 'Gerar campanha'}
          </button>
        </form>
        {error ? <p className="mt-4 text-sm text-coral">{error}</p> : null}
      </section>
      <section className="panel-base">
        <h3 className="font-display text-2xl text-white">Saída da campanha</h3>
        {!result ? <p className="mt-6 text-slate-300">Preencha o formulário para gerar campanha, copy, CTA, estrutura de anúncio e sugestão de criativo.</p> : null}
        {result ? (
          <div className="mt-6 grid gap-4">
            {[
              ['Campanha', result.campaign],
              ['Copy', result.copy],
              ['CTA', result.cta],
              ['Estrutura do anúncio', result.ad_structure],
              ['Sugestão de criativo', result.creative_suggestion],
            ].map(([label, value]) => (
              <article key={label} className="rounded-3xl border border-white/10 bg-white/5 p-5">
                <p className="text-sm uppercase tracking-[0.3em] text-cyan">{label}</p>
                <p className="mt-3 whitespace-pre-wrap text-slate-100">{value}</p>
              </article>
            ))}
          </div>
        ) : null}
      </section>
    </div>
  );
}

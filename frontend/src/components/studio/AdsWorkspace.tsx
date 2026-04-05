import { useState } from 'react';

interface AdsWorkspaceProps {
  onNotify: (msg: string) => void;
}

interface AdsResult {
  adCopy: string;
  hook: string;
  cta: string;
  angle: string;
}

export function AdsWorkspace({ onNotify }: AdsWorkspaceProps) {
  const [form, setForm] = useState({
    business: 'AXI Platform',
    audience: 'times comerciais e marketing',
    objective: 'gerar reunioes qualificadas',
    offer: 'AXI Studio',
    tone: 'premium consultivo',
    platform: 'Instagram + WhatsApp',
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AdsResult | null>(null);

  async function generate() {
    setLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 750));
    setResult({
      adCopy: `${form.business} ajuda ${form.audience} a ${form.objective} com ${form.offer}.`,
      hook: `"Seu funil esta pronto para converter mais em ${form.platform}?"`,
      cta: 'Solicitar plano personalizado agora',
      angle: `Posicionamento ${form.tone} com foco em ROI e velocidade de execucao.`,
    });
    setLoading(false);
    onNotify('Anuncios gerados com IA mock.');
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[390px_1fr]">
      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
        <h3 className="font-display text-2xl text-white">Anuncios Inteligentes</h3>
        <p className="mt-2 text-sm text-slate-300">Gere campanhas com copy, hook, CTA e angulo criativo.</p>
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
          onClick={generate}
          disabled={loading}
          className="mt-4 w-full rounded-2xl bg-sand px-4 py-3 text-sm font-semibold text-ink"
        >
          {loading ? 'Gerando ativos...' : 'Gerar ativos'}
        </button>
      </section>

      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
        <h3 className="font-display text-2xl text-white">Output de campanha</h3>
        {!result ? (
          <p className="mt-4 text-sm text-slate-300">Preencha os campos para gerar um pacote de anuncio.</p>
        ) : (
          <div className="mt-4 grid gap-3">
            {[
              ['Ad copy', result.adCopy],
              ['Hook', result.hook],
              ['CTA', result.cta],
              ['Creative angle', result.angle],
            ].map(([label, value]) => (
              <article key={label} className="rounded-2xl border border-white/10 bg-ink/40 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-cyan">{label}</p>
                <p className="mt-2 text-sm text-slate-100">{value}</p>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

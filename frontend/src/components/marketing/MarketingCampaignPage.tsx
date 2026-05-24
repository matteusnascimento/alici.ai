import { Bot, Loader2, Rocket, Sparkles } from 'lucide-react';
import { useState } from 'react';
import type { MarketingCampaignInput, MarketingCampaignResult } from '../../types/marketing';
import { generateCampaign } from '../../services/marketing.service';

const TONES = ['premium', 'casual', 'urgente', 'educativo', 'inspirador'];
const GOALS = ['Gerar leads', 'Vender direto', 'Aumentar seguidores', 'Engajamento', 'Retencao'];
const CHANNELS = ['instagram', 'whatsapp', 'facebook', 'google', 'email'];

function buildCampaignPreview(input: MarketingCampaignInput) {
  const brand = input.business_name.trim() || 'Sua marca';
  const audience = input.target_audience.trim() || 'seu publico-alvo';
  const goal = input.campaign_goal || 'crescimento';
  const offer = input.offer.trim() || 'sua oferta principal';
  const channel = input.channel || 'instagram';

  return {
    title: `${brand}: campanha para ${goal.toLowerCase()}`,
    description: `Campanha focada em ${audience}, com narrativa orientada a conversao e oferta de ${offer}.`,
    strategy: `Top funnel com gancho forte no ${channel}, seguido de prova social e CTA de fechamento em WhatsApp.`,
    channels: [channel, 'whatsapp', 'instagram'].filter((value, index, arr) => arr.indexOf(value) === index),
  };
}

export function MarketingCampaignPage() {
  const [form, setForm] = useState<MarketingCampaignInput>({
    business_name: '',
    market_segment: '',
    target_audience: '',
    campaign_goal: GOALS[0],
    offer: '',
    tone: 'premium',
    channel: 'instagram',
    campaign_type: 'awareness',
    budget_range: '',
    call_to_action: '',
  });
  const [result, setResult] = useState<MarketingCampaignResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const preview = buildCampaignPreview(form);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const r = await generateCampaign(form);
      setResult({
        ...r,
        cta_suggestions: Array.isArray(r?.cta_suggestions) ? r.cta_suggestions : [],
      });
    } catch {
      setError('Erro ao gerar campanha. Verifique as configuracoes de IA.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-7xl px-6 py-8 space-y-8">
      <section className="rounded-3xl border border-cyan-300/20 bg-[radial-gradient(circle_at_10%_20%,rgba(6,182,212,0.22),transparent_40%),linear-gradient(165deg,#06142a,#0b2448)] p-6 md:p-8">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.28em] text-cyan-200">
              <Sparkles size={14} className="animate-pulse" /> Campaign Intelligence
            </p>
            <h1 className="mt-2 font-display text-4xl text-white md:text-5xl">Crie campanhas com IA em minutos</h1>
            <p className="mt-3 max-w-3xl text-sm text-slate-200 md:text-base">
              Defina seu briefing estrategico e acompanhe o resultado da IA em tempo real, com direcao, canal e proposta de campanha.
            </p>
          </div>
          <span className="inline-flex items-center gap-2 rounded-xl border border-cyan-300/35 bg-cyan-500/10 px-3 py-2 text-xs text-cyan-100">
            <Bot size={14} /> IA ativa
          </span>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <form onSubmit={handleSubmit} className="rounded-3xl border border-white/10 bg-[linear-gradient(160deg,rgba(255,255,255,0.07),rgba(255,255,255,0.03))] p-6 grid gap-4 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <p className="text-sm font-semibold text-white">Entrada estrategica</p>
            <p className="mt-1 text-xs text-slate-300">Briefing da campanha com foco em performance e posicionamento.</p>
          </div>

          <label className="space-y-1.5">
            <span className="text-sm font-medium text-slate-100">Marca / Negocio</span>
            <input
              required
              placeholder="Nome da empresa"
              value={form.business_name}
              onChange={(e) => setForm((f) => ({ ...f, business_name: e.target.value }))}
              className="w-full rounded-xl border border-white/15 bg-[#0b1328]/80 px-3 py-2.5 text-sm text-white placeholder-slate-500 transition focus:outline-none focus:border-cyan/50 focus:ring-2 focus:ring-cyan/20"
            />
          </label>

          <label className="space-y-1.5">
            <span className="text-sm font-medium text-slate-100">Segmento</span>
            <input
              placeholder="Ex: Hospitalidade, SaaS, Varejo"
              value={form.market_segment}
              onChange={(e) => setForm((f) => ({ ...f, market_segment: e.target.value }))}
              className="w-full rounded-xl border border-white/15 bg-[#0b1328]/80 px-3 py-2.5 text-sm text-white placeholder-slate-500 transition focus:outline-none focus:border-cyan/50 focus:ring-2 focus:ring-cyan/20"
            />
          </label>

          <label className="space-y-1.5">
            <span className="text-sm font-medium text-slate-100">Publico-alvo</span>
            <input
              required
              placeholder="Quem deve comprar"
              value={form.target_audience}
              onChange={(e) => setForm((f) => ({ ...f, target_audience: e.target.value }))}
              className="w-full rounded-xl border border-white/15 bg-[#0b1328]/80 px-3 py-2.5 text-sm text-white placeholder-slate-500 transition focus:outline-none focus:border-cyan/50 focus:ring-2 focus:ring-cyan/20"
            />
          </label>

          <label className="space-y-1.5">
            <span className="text-sm font-medium text-slate-100">Oferta / Produto</span>
            <input
              required
              placeholder="Oferta principal"
              value={form.offer}
              onChange={(e) => setForm((f) => ({ ...f, offer: e.target.value }))}
              className="w-full rounded-xl border border-white/15 bg-[#0b1328]/80 px-3 py-2.5 text-sm text-white placeholder-slate-500 transition focus:outline-none focus:border-cyan/50 focus:ring-2 focus:ring-cyan/20"
            />
          </label>

          <label className="space-y-1.5">
            <span className="text-sm font-medium text-slate-100">Objetivo</span>
            <select
              value={form.campaign_goal}
              onChange={(e) => setForm((f) => ({ ...f, campaign_goal: e.target.value }))}
              className="w-full rounded-xl border border-white/15 bg-[#0b1328]/80 px-3 py-2.5 text-sm text-white transition focus:outline-none focus:border-cyan/50 focus:ring-2 focus:ring-cyan/20"
            >
              {GOALS.map((g) => <option key={g} value={g}>{g}</option>)}
            </select>
          </label>

          <label className="space-y-1.5">
            <span className="text-sm font-medium text-slate-100">Tom</span>
            <select
              value={form.tone}
              onChange={(e) => setForm((f) => ({ ...f, tone: e.target.value }))}
              className="w-full rounded-xl border border-white/15 bg-[#0b1328]/80 px-3 py-2.5 text-sm text-white transition focus:outline-none focus:border-cyan/50 focus:ring-2 focus:ring-cyan/20"
            >
              {TONES.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </label>

          <label className="space-y-1.5 sm:col-span-2">
            <span className="text-sm font-medium text-slate-100">Canal principal</span>
            <select
              value={form.channel}
              onChange={(e) => setForm((f) => ({ ...f, channel: e.target.value }))}
              className="w-full rounded-xl border border-white/15 bg-[#0b1328]/80 px-3 py-2.5 text-sm text-white transition focus:outline-none focus:border-cyan/50 focus:ring-2 focus:ring-cyan/20"
            >
              {CHANNELS.map((channel) => <option key={channel} value={channel}>{channel}</option>)}
            </select>
          </label>

          <div className="sm:col-span-2 flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-2 rounded-xl bg-cyan px-6 py-2.5 text-sm font-semibold text-ink transition hover:bg-cyan/90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? <Loader2 size={14} className="animate-spin" /> : <Rocket size={14} />}
              Gerar campanha com IA
            </button>
          </div>

          {error ? <p className="sm:col-span-2 text-xs text-rose-300">{error}</p> : null}
        </form>

        <aside className="rounded-3xl border border-cyan-300/20 bg-[linear-gradient(165deg,rgba(7,17,38,0.95),rgba(8,23,49,0.92))] p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Resultado da IA</h2>
            <span className="inline-flex items-center gap-1 rounded-full border border-cyan-300/30 bg-cyan-500/10 px-2.5 py-1 text-xs text-cyan-100">
              <Sparkles size={12} /> Preview dinamico
            </span>
          </div>

          <div className="space-y-3">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-[11px] uppercase tracking-[0.2em] text-cyan-200">Titulo da campanha</p>
              <p className="mt-2 text-base font-semibold text-white">{result?.campaign_headline || preview.title}</p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-[11px] uppercase tracking-[0.2em] text-cyan-200">Descricao</p>
              <p className="mt-2 text-sm text-slate-200">{result?.primary_copy || preview.description}</p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-[11px] uppercase tracking-[0.2em] text-cyan-200">Estrategia</p>
              <p className="mt-2 text-sm text-slate-200">{result?.secondary_copy || preview.strategy}</p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-[11px] uppercase tracking-[0.2em] text-cyan-200">Canais sugeridos</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {(result?.cta_suggestions?.length ? result.cta_suggestions : preview.channels).map((item) => (
                  <span key={item} className="rounded-full border border-white/15 px-3 py-1 text-xs text-slate-200">
                    {item}
                  </span>
                ))}
              </div>
            </div>

            {result?.creative_suggestion ? (
              <div className="rounded-2xl border border-emerald-300/25 bg-emerald-500/10 p-4">
                <p className="text-[11px] uppercase tracking-[0.2em] text-emerald-200">Insight criativo</p>
                <p className="mt-2 text-sm text-emerald-100">{result.creative_suggestion}</p>
              </div>
            ) : null}
          </div>
        </aside>
      </section>
    </div>
  );
}


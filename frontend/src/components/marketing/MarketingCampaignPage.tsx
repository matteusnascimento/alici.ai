import { Loader2, Megaphone, Zap } from 'lucide-react';
import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import type { MarketingCampaignInput, MarketingCampaignResult } from '../../types/marketing';
import { generateCampaign } from '../../services/marketing.service';

const TONES = ['premium', 'casual', 'urgente', 'educativo', 'inspirador'];
const GOALS = ['Gerar leads', 'Vender direto', 'Aumentar seguidores', 'Engajamento', 'Retenção'];

export function MarketingCampaignPage() {
  const [searchParams] = useSearchParams();
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

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const r = await generateCampaign(form);
      setResult(r);
    } catch {
      setError('Erro ao gerar campanha. Verifique as configurações de IA.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-8 space-y-8">
      <div className="flex items-center gap-3">
        <Megaphone size={20} className="text-cyan" />
        <h1 className="text-xl font-semibold text-white">Gerador de Campanha</h1>
      </div>

      <form onSubmit={handleSubmit} className="rounded-2xl border border-white/10 bg-white/5 p-6 grid gap-3 sm:grid-cols-2">
        <input
          required
          placeholder="Nome da empresa / marca"
          value={form.business_name}
          onChange={(e) => setForm((f) => ({ ...f, business_name: e.target.value }))}
          className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan/50"
        />
        <input
          placeholder="Segmento de mercado"
          value={form.market_segment}
          onChange={(e) => setForm((f) => ({ ...f, market_segment: e.target.value }))}
          className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan/50"
        />
        <input
          required
          placeholder="Público-alvo"
          value={form.target_audience}
          onChange={(e) => setForm((f) => ({ ...f, target_audience: e.target.value }))}
          className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan/50"
        />
        <input
          required
          placeholder="Oferta / produto"
          value={form.offer}
          onChange={(e) => setForm((f) => ({ ...f, offer: e.target.value }))}
          className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan/50"
        />
        <select
          value={form.campaign_goal}
          onChange={(e) => setForm((f) => ({ ...f, campaign_goal: e.target.value }))}
          className="rounded-xl border border-white/10 bg-storm px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan/50"
        >
          {GOALS.map((g) => <option key={g} value={g}>{g}</option>)}
        </select>
        <select
          value={form.tone}
          onChange={(e) => setForm((f) => ({ ...f, tone: e.target.value }))}
          className="rounded-xl border border-white/10 bg-storm px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan/50"
        >
          {TONES.map((t) => <option key={t} value={t}>{t}</option>)}
        </select>
        <div className="sm:col-span-2 flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 rounded-xl bg-cyan px-6 py-2.5 text-sm font-semibold text-ink hover:bg-cyan/90 disabled:opacity-50"
          >
            {loading ? <Loader2 size={14} className="animate-spin" /> : <Zap size={14} />}
            Gerar Campanha
          </button>
        </div>
        {error && <p className="sm:col-span-2 text-xs text-red-400">{error}</p>}
      </form>

      {result && (
        <section className="space-y-4">
          <h2 className="text-sm uppercase tracking-[0.25em] text-slate-400">Resultado</h2>
          {[
            { label: 'Headline', value: result.campaign_headline },
            { label: 'Copy Principal', value: result.primary_copy },
            { label: 'Estrutura do Anúncio', value: result.secondary_copy },
            { label: 'CTA', value: result.cta_suggestions.join(', ') },
            { label: 'Sugestão Criativa', value: result.creative_suggestion },
          ].map(({ label, value }) => (
            <div key={label} className="rounded-2xl border border-white/10 bg-white/5 p-5">
              <p className="mb-1 text-xs text-cyan uppercase tracking-wider">{label}</p>
              <p className="text-sm text-slate-200 whitespace-pre-wrap">{value}</p>
            </div>
          ))}
        </section>
      )}
    </div>
  );
}

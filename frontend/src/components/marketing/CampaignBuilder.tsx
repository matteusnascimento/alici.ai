import { useEffect, useMemo, useState } from 'react';

import { generateCampaign } from '../../services/marketingService';
import type { MarketingCampaignInput, MarketingCampaignResult, MarketingTemplateProfile } from '../../types/marketing';
import { EmptyState } from './EmptyState';
import { OutputCard } from './OutputCard';
import { SectionCard } from './SectionCard';

interface CampaignBuilderProps {
  templateProfile: MarketingTemplateProfile | null;
  onNotify: (message: string) => void;
}

const initialForm: MarketingCampaignInput = {
  business_name: 'AXI Platform',
  market_segment: 'SaaS B2B',
  target_audience: 'times comerciais e de marketing',
  campaign_goal: 'gerar reunioes qualificadas',
  offer: 'AXI Growth Studio',
  tone: 'premium consultivo',
  channel: 'Multi-channel',
  campaign_type: 'lead generation',
  budget_range: 'R$ 3.000 - R$ 8.000',
  call_to_action: 'Agendar diagnostico',
};

export function CampaignBuilder({ templateProfile, onNotify }: CampaignBuilderProps) {
  const [form, setForm] = useState<MarketingCampaignInput>(initialForm);
  const [result, setResult] = useState<MarketingCampaignResult | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!templateProfile) return;
    setForm((current) => ({
      ...current,
      business_name: templateProfile.businessName,
      market_segment: templateProfile.marketSegment,
      target_audience: templateProfile.audience,
      offer: templateProfile.offer,
      tone: templateProfile.tone,
      channel: templateProfile.platform,
    }));
  }, [templateProfile]);

  async function handleGenerate() {
    setLoading(true);
    try {
      const generated = await generateCampaign(form);
      setResult(generated);
      onNotify('Campanha gerada com sucesso.');
    } finally {
      setLoading(false);
    }
  }

  function handleClear() {
    setForm(initialForm);
    setResult(null);
    onNotify('Formulario de campanhas limpo.');
  }

  async function handleCopy() {
    if (!result) return;
    const payload = [
      result.campaign_headline,
      result.primary_copy,
      result.secondary_copy,
      `CTAs: ${result.cta_suggestions.join(' | ')}`,
    ].join('\n\n');
    await navigator.clipboard.writeText(payload);
    onNotify('Resultado da campanha copiado.');
  }

  function handleSaveDraft() {
    localStorage.setItem('axi-growth-campaign-draft', JSON.stringify(form));
    onNotify('Rascunho de campanha salvo.');
  }

  const fields: Array<[keyof MarketingCampaignInput, string]> = useMemo(
    () => [
      ['business_name', 'Business name'],
      ['market_segment', 'Market segment'],
      ['target_audience', 'Target audience'],
      ['campaign_goal', 'Campaign goal'],
      ['offer', 'Offer'],
      ['tone', 'Tone'],
      ['channel', 'Channel'],
      ['campaign_type', 'Campaign type'],
      ['budget_range', 'Budget range'],
      ['call_to_action', 'Call to action'],
    ],
    [],
  );

  return (
    <div className="grid gap-6 xl:grid-cols-[1.05fr_1fr]">
      <SectionCard
        title="Campaign Strategy Builder"
        description="Estruture campanha completa com angulo de oferta, copy e estrategia criativa."
      >
        <div className="grid gap-4 md:grid-cols-2">
          {fields.map(([key, label]) => (
            <label key={key} className="space-y-2 text-sm text-slate-300">
              <span>{label}</span>
              <input
                className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white outline-none transition focus:border-cyan"
                value={form[key]}
                onChange={(event) => setForm((current) => ({ ...current, [key]: event.target.value }))}
              />
            </label>
          ))}
        </div>
        <div className="mt-5 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={handleGenerate}
            className="rounded-2xl bg-sand px-4 py-2 text-sm font-semibold text-ink transition hover:bg-white disabled:opacity-60"
            disabled={loading}
          >
            {loading ? 'Gerando campanha...' : 'Gerar campanha'}
          </button>
          <button type="button" onClick={handleClear} className="rounded-2xl border border-white/20 px-4 py-2 text-sm text-slate-100">
            Limpar
          </button>
          <button type="button" onClick={handleCopy} className="rounded-2xl border border-white/20 px-4 py-2 text-sm text-slate-100">
            Copiar resultado
          </button>
          <button
            type="button"
            onClick={handleSaveDraft}
            className="rounded-2xl border border-cyan/30 bg-cyan/10 px-4 py-2 text-sm text-cyan"
          >
            Salvar draft
          </button>
        </div>
      </SectionCard>

      <SectionCard
        title="Campaign Output"
        description="Resumo pronto para campanha, criativos e operacao comercial."
      >
        {!result ? (
          <EmptyState
            title="Sem campanha gerada"
            description="Preencha os dados e clique em Gerar campanha para montar headline, copys, dores, objecoes e CTA."
          />
        ) : (
          <div className="grid gap-3">
            <OutputCard label="Campaign headline" value={result.campaign_headline} />
            <OutputCard label="Primary copy" value={result.primary_copy} />
            <OutputCard label="Secondary copy" value={result.secondary_copy} />
            <OutputCard label="CTA suggestions" list={result.cta_suggestions} />
            <OutputCard label="Offer angle" value={result.offer_angle} />
            <OutputCard label="Pain points" list={result.pain_points} />
            <OutputCard label="Objections" list={result.objections} />
            <OutputCard label="Positioning summary" value={result.positioning_summary} />
            <OutputCard label="Creative suggestion" value={result.creative_suggestion} />
          </div>
        )}
      </SectionCard>
    </div>
  );
}

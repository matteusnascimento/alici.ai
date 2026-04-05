import { useEffect, useState } from 'react';

import { generateContentPlan } from '../../services/marketingService';
import type { ContentPlanInput, ContentPlanResult, MarketingTemplateProfile } from '../../types/marketing';
import { EmptyState } from './EmptyState';
import { OutputCard } from './OutputCard';
import { SectionCard } from './SectionCard';

interface ContentPlannerProps {
  templateProfile: MarketingTemplateProfile | null;
  onNotify: (message: string) => void;
}

const initialForm: ContentPlanInput = {
  business_type: 'SaaS',
  target_audience: 'gestores de crescimento',
  goal: 'gerar pipeline qualificado',
  frequency_per_week: '4',
  content_pillars: 'educacao, prova social, oferta, retencao',
  timeframe: 'Maio 2026',
  platform: 'Instagram + LinkedIn',
};

export function ContentPlanner({ templateProfile, onNotify }: ContentPlannerProps) {
  const [form, setForm] = useState<ContentPlanInput>(initialForm);
  const [result, setResult] = useState<ContentPlanResult | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!templateProfile) return;
    setForm((current) => ({
      ...current,
      business_type: templateProfile.marketSegment,
      target_audience: templateProfile.audience,
      goal: `vender ${templateProfile.offer}`,
      platform: templateProfile.platform,
    }));
  }, [templateProfile]);

  async function handleGenerate() {
    setLoading(true);
    try {
      const generated = await generateContentPlan(form);
      setResult(generated);
      onNotify('Planejamento de conteudo gerado.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[390px_1fr]">
      <SectionCard title="Content Planner" description="Planejamento semanal e mensal com pilares e distribuicao por objetivo.">
        <div className="space-y-3">
          {[
            ['business_type', 'Business type'],
            ['target_audience', 'Target audience'],
            ['goal', 'Goal'],
            ['frequency_per_week', 'Frequency per week'],
            ['content_pillars', 'Content pillars'],
            ['timeframe', 'Month or timeframe'],
            ['platform', 'Platform'],
          ].map(([key, label]) => (
            <label key={key} className="block space-y-2 text-sm text-slate-300">
              <span>{label}</span>
              <input
                className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white outline-none focus:border-cyan"
                value={form[key as keyof ContentPlanInput]}
                onChange={(event) => setForm((current) => ({ ...current, [key]: event.target.value }))}
              />
            </label>
          ))}
        </div>
        <div className="mt-5 flex flex-wrap gap-3">
          <button type="button" onClick={handleGenerate} className="rounded-2xl bg-sand px-4 py-2 text-sm font-semibold text-ink" disabled={loading}>
            {loading ? 'Gerando planner...' : 'Gerar planner'}
          </button>
          <button
            type="button"
            onClick={() => {
              setResult(null);
              onNotify('Planner limpo.');
            }}
            className="rounded-2xl border border-white/20 px-4 py-2 text-sm text-slate-100"
          >
            Limpar
          </button>
        </div>
      </SectionCard>

      <SectionCard title="Planner Output" description="Calendario operacional por etapa do funil de conteudo.">
        {!result ? (
          <EmptyState title="Sem plano de conteudo" description="Gere o plano para visualizar semana a semana, pilares e ideias por fase do funil." />
        ) : (
          <div className="grid gap-3 md:grid-cols-2">
            <OutputCard label="Weekly plan" list={result.weekly_plan} />
            <OutputCard label="Monthly plan" list={result.monthly_plan} />
            <OutputCard label="Content pillars" list={result.content_pillar_breakdown} />
            <OutputCard label="Posting suggestions" list={result.posting_suggestions} />
            <OutputCard label="Campaign dates" list={result.campaign_dates} />
            <OutputCard label="Attraction" list={result.grouped_ideas.attraction} />
            <OutputCard label="Authority" list={result.grouped_ideas.authority} />
            <OutputCard label="Conversion" list={result.grouped_ideas.conversion} />
            <OutputCard label="Retention" list={result.grouped_ideas.retention} />
          </div>
        )}
      </SectionCard>
    </div>
  );
}

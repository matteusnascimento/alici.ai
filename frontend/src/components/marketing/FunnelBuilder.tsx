import { useEffect, useState } from 'react';

import { generateFunnel } from '../../services/marketingService';
import type { FunnelInput, FunnelResult, MarketingTemplateProfile } from '../../types/marketing';
import { EmptyState } from './EmptyState';
import { SectionCard } from './SectionCard';

interface FunnelBuilderProps {
  templateProfile: MarketingTemplateProfile | null;
  onNotify: (message: string) => void;
}

const initialForm: FunnelInput = {
  business: 'AXI Platform',
  offer: 'Growth Studio',
  target_audience: 'times de crescimento',
  acquisition_channel: 'Instagram + WhatsApp',
  funnel_objective: 'reunioes qualificadas',
};

export function FunnelBuilder({ templateProfile, onNotify }: FunnelBuilderProps) {
  const [form, setForm] = useState<FunnelInput>(initialForm);
  const [result, setResult] = useState<FunnelResult | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!templateProfile) return;
    setForm((current) => ({
      ...current,
      business: templateProfile.businessName,
      offer: templateProfile.offer,
      target_audience: templateProfile.audience,
      acquisition_channel: templateProfile.platform,
    }));
  }, [templateProfile]);

  async function handleGenerate() {
    setLoading(true);
    try {
      const generated = await generateFunnel(form);
      setResult(generated);
      onNotify('Funil gerado com sucesso.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[380px_1fr]">
      <SectionCard title="Funnel Builder" description="Top, middle, bottom, remarketing e sequencia de conversao com mensagem por etapa.">
        <div className="space-y-3">
          {[
            ['business', 'Business'],
            ['offer', 'Offer'],
            ['target_audience', 'Target audience'],
            ['acquisition_channel', 'Acquisition channel'],
            ['funnel_objective', 'Funnel objective'],
          ].map(([key, label]) => (
            <label key={key} className="block space-y-2 text-sm text-slate-300">
              <span>{label}</span>
              <input
                className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white outline-none focus:border-cyan"
                value={form[key as keyof FunnelInput]}
                onChange={(event) => setForm((current) => ({ ...current, [key]: event.target.value }))}
              />
            </label>
          ))}
        </div>
        <div className="mt-5 flex gap-3">
          <button type="button" onClick={handleGenerate} className="rounded-2xl bg-sand px-4 py-2 text-sm font-semibold text-ink" disabled={loading}>
            {loading ? 'Gerando funil...' : 'Gerar funil'}
          </button>
          <button
            type="button"
            onClick={() => {
              setResult(null);
              onNotify('Funil resetado.');
            }}
            className="rounded-2xl border border-white/20 px-4 py-2 text-sm text-slate-100"
          >
            Limpar
          </button>
        </div>
      </SectionCard>

      <SectionCard title="Funnel Stages" description="Mapa acionavel de conteudo, mensagens e objeções por etapa.">
        {!result ? (
          <EmptyState title="Sem funil montado" description="Gere o funil para visualizar estagios e copy de conversao por fase." />
        ) : (
          <div className="grid gap-3">
            {result.stages.map((stage) => (
              <article key={stage.stage} className="rounded-2xl border border-white/10 bg-ink/40 p-4">
                <h4 className="font-display text-lg text-white">{stage.stage}</h4>
                <p className="mt-2 text-sm text-slate-100">Conteudo: {stage.content}</p>
                <p className="mt-1 text-sm text-slate-100">Objetivo da mensagem: {stage.messaging_goal}</p>
                <p className="mt-1 text-sm text-cyan">CTA: {stage.cta}</p>
                <p className="mt-1 text-sm text-slate-300">Objecao: {stage.objections}</p>
                <p className="mt-1 text-sm text-slate-300">Nurturing: {stage.nurturing}</p>
              </article>
            ))}
          </div>
        )}
      </SectionCard>
    </div>
  );
}

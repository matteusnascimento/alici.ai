import { useEffect, useState } from 'react';

import { generateWhatsAppFlow } from '../../services/marketingService';
import type { MarketingTemplateProfile, WhatsAppFlowInput, WhatsAppFlowResult } from '../../types/marketing';
import { EmptyState } from './EmptyState';
import { OutputCard } from './OutputCard';
import { SectionCard } from './SectionCard';

interface WhatsAppFlowsProps {
  templateProfile: MarketingTemplateProfile | null;
  onNotify: (message: string) => void;
}

const initialForm: WhatsAppFlowInput = {
  business_type: 'servicos locais',
  customer_stage: 'primeiro contato',
  objective: 'qualificar e converter',
  tone: 'humano consultivo',
  offer: 'diagnostico com plano de acao',
};

export function WhatsAppFlows({ templateProfile, onNotify }: WhatsAppFlowsProps) {
  const [form, setForm] = useState<WhatsAppFlowInput>(initialForm);
  const [result, setResult] = useState<WhatsAppFlowResult | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!templateProfile) return;
    setForm((current) => ({
      ...current,
      business_type: templateProfile.marketSegment,
      objective: `vender ${templateProfile.offer}`,
      tone: templateProfile.tone,
      offer: templateProfile.offer,
    }));
  }, [templateProfile]);

  async function handleGenerate() {
    setLoading(true);
    try {
      const generated = await generateWhatsAppFlow(form);
      setResult(generated);
      onNotify('Fluxo de WhatsApp gerado.');
    } finally {
      setLoading(false);
    }
  }

  async function handleCopy() {
    if (!result) return;
    await navigator.clipboard.writeText(result.sequence.join('\n'));
    onNotify('Sequencia de WhatsApp copiada.');
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[390px_1fr]">
      <SectionCard
        title="WhatsApp Revenue Flows"
        description="Fluxos para primeiro contato, qualificacao, follow-up, reserva, recuperacao, fechamento e pos-venda."
      >
        <div className="space-y-3">
          {[
            ['business_type', 'Business type'],
            ['customer_stage', 'Customer stage'],
            ['objective', 'Objective'],
            ['tone', 'Tone'],
            ['offer', 'Offer'],
          ].map(([key, label]) => (
            <label key={key} className="block space-y-2 text-sm text-slate-300">
              <span>{label}</span>
              <input
                className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white outline-none focus:border-cyan"
                value={form[key as keyof WhatsAppFlowInput]}
                onChange={(event) => setForm((current) => ({ ...current, [key]: event.target.value }))}
              />
            </label>
          ))}
        </div>
        <div className="mt-5 flex flex-wrap gap-3">
          <button type="button" onClick={handleGenerate} className="rounded-2xl bg-sand px-4 py-2 text-sm font-semibold text-ink" disabled={loading}>
            {loading ? 'Gerando fluxo...' : 'Gerar fluxo'}
          </button>
          <button type="button" onClick={handleCopy} className="rounded-2xl border border-white/20 px-4 py-2 text-sm text-slate-100">
            Copiar resultado
          </button>
          <button
            type="button"
            onClick={() => {
              localStorage.setItem('axi-growth-whatsapp-draft', JSON.stringify(form));
              onNotify('Draft de WhatsApp salvo.');
            }}
            className="rounded-2xl border border-cyan/30 bg-cyan/10 px-4 py-2 text-sm text-cyan"
          >
            Salvar draft
          </button>
        </div>
      </SectionCard>

      <SectionCard title="Flow Output" description="Sequencia completa com timing, variacoes, versao humanizada e versao direta.">
        {!result ? (
          <EmptyState
            title="Fluxo nao gerado"
            description="Monte seu roteiro de WhatsApp com mensagens prontas para acelerar vendas e follow-up."
          />
        ) : (
          <div className="grid gap-3 md:grid-cols-2">
            <OutputCard label="Message sequence" list={result.sequence} />
            <OutputCard label="Follow-up timing" list={result.follow_up_timing} />
            <OutputCard label="Variations" list={result.variations} />
            <OutputCard label="More human version" value={result.human_version} />
            <OutputCard label="More direct version" value={result.direct_version} />
          </div>
        )}
      </SectionCard>
    </div>
  );
}

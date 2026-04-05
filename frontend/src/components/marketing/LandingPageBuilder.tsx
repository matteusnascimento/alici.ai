import { useEffect, useState } from 'react';

import { generateLandingPage } from '../../services/marketingService';
import type { LandingPageInput, LandingPageResult, MarketingTemplateProfile } from '../../types/marketing';
import { EmptyState } from './EmptyState';
import { OutputCard } from './OutputCard';
import { SectionCard } from './SectionCard';

interface LandingPageBuilderProps {
  templateProfile: MarketingTemplateProfile | null;
  onNotify: (message: string) => void;
}

const initialForm: LandingPageInput = {
  business: 'AXI Platform',
  audience: 'times de marketing e vendas',
  offer: 'Growth Studio',
  promise: 'mais pipeline com menos dispersao',
  tone: 'premium consultivo',
  cta_objective: 'Solicitar demo estrategica',
};

export function LandingPageBuilder({ templateProfile, onNotify }: LandingPageBuilderProps) {
  const [form, setForm] = useState<LandingPageInput>(initialForm);
  const [result, setResult] = useState<LandingPageResult | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!templateProfile) return;
    setForm((current) => ({
      ...current,
      business: templateProfile.businessName,
      audience: templateProfile.audience,
      offer: templateProfile.offer,
      tone: templateProfile.tone,
    }));
  }, [templateProfile]);

  async function handleGenerate() {
    setLoading(true);
    try {
      const generated = await generateLandingPage(form);
      setResult(generated);
      onNotify('Estrutura de landing page gerada.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[390px_1fr]">
      <SectionCard title="Landing Page Builder" description="Arquitetura de copy para hero, beneficios, objecoes, FAQ e CTA final.">
        <div className="space-y-3">
          {[
            ['business', 'Business'],
            ['audience', 'Audience'],
            ['offer', 'Offer'],
            ['promise', 'Promise'],
            ['tone', 'Tone'],
            ['cta_objective', 'CTA objective'],
          ].map(([key, label]) => (
            <label key={key} className="block space-y-2 text-sm text-slate-300">
              <span>{label}</span>
              <input
                className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white outline-none focus:border-cyan"
                value={form[key as keyof LandingPageInput]}
                onChange={(event) => setForm((current) => ({ ...current, [key]: event.target.value }))}
              />
            </label>
          ))}
        </div>
        <div className="mt-5 flex gap-3">
          <button type="button" onClick={handleGenerate} className="rounded-2xl bg-sand px-4 py-2 text-sm font-semibold text-ink" disabled={loading}>
            {loading ? 'Gerando landing...' : 'Gerar landing page'}
          </button>
          <button
            type="button"
            onClick={() => {
              localStorage.setItem('axi-growth-landing-draft', JSON.stringify(form));
              onNotify('Draft de landing salvo.');
            }}
            className="rounded-2xl border border-cyan/30 bg-cyan/10 px-4 py-2 text-sm text-cyan"
          >
            Salvar draft
          </button>
        </div>
      </SectionCard>

      <SectionCard title="Landing Output" description="Conteudo pronto para pagina de conversao e testes de oferta.">
        {!result ? (
          <EmptyState title="Sem estrutura de landing" description="Gere uma estrutura de copy completa para sua pagina de conversao." />
        ) : (
          <div className="grid gap-3 md:grid-cols-2">
            <OutputCard label="Hero title" value={result.hero_title} />
            <OutputCard label="Subtitle" value={result.subtitle} />
            <OutputCard label="Benefit bullets" list={result.benefit_bullets} />
            <OutputCard label="Offer section" value={result.offer_section} />
            <OutputCard label="Objections section" list={result.objections_section} />
            <OutputCard label="FAQ" list={result.faq} />
            <OutputCard label="Final CTA" value={result.final_cta} />
            <OutputCard label="Proof section" value={result.proof_section} />
          </div>
        )}
      </SectionCard>
    </div>
  );
}

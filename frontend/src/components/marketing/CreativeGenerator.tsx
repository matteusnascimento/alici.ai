import { useEffect, useState } from 'react';

import { generateCreativeIdeas } from '../../services/marketingService';
import type { CreativeIdea, CreativeIdeasInput, MarketingTemplateProfile } from '../../types/marketing';
import { EmptyState } from './EmptyState';
import { SectionCard } from './SectionCard';

interface CreativeGeneratorProps {
  templateProfile: MarketingTemplateProfile | null;
  onNotify: (message: string) => void;
}

const initialForm: CreativeIdeasInput = {
  niche: 'servicos locais',
  audience: 'gestores e donos',
  objective: 'atrair leads qualificados',
  platform: 'Instagram',
  tone: 'premium direto',
};

export function CreativeGenerator({ templateProfile, onNotify }: CreativeGeneratorProps) {
  const [form, setForm] = useState<CreativeIdeasInput>(initialForm);
  const [ideas, setIdeas] = useState<CreativeIdea[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!templateProfile) return;
    setForm((current) => ({
      ...current,
      niche: templateProfile.marketSegment,
      audience: templateProfile.audience,
      objective: `vender ${templateProfile.offer}`,
      platform: templateProfile.platform,
      tone: templateProfile.tone,
    }));
  }, [templateProfile]);

  async function handleGenerate() {
    setLoading(true);
    try {
      const generated = await generateCreativeIdeas(form);
      setIdeas(generated);
      onNotify('Ideias criativas geradas.');
    } finally {
      setLoading(false);
    }
  }

  function handleSaveDraft() {
    localStorage.setItem('axi-growth-creatives-draft', JSON.stringify(form));
    onNotify('Rascunho de criativos salvo.');
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[380px_1fr]">
      <SectionCard title="Creative Generator" description="Reels, stories, carrossel, hooks e angulos de criativos com qualidade de campanha.">
        <div className="space-y-3">
          {[
            ['niche', 'Niche'],
            ['audience', 'Audience'],
            ['objective', 'Objective'],
            ['platform', 'Platform'],
            ['tone', 'Tone'],
          ].map(([key, label]) => (
            <label key={key} className="block space-y-2 text-sm text-slate-300">
              <span>{label}</span>
              <input
                className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white outline-none focus:border-cyan"
                value={form[key as keyof CreativeIdeasInput]}
                onChange={(event) => setForm((current) => ({ ...current, [key]: event.target.value }))}
              />
            </label>
          ))}
        </div>
        <div className="mt-5 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={handleGenerate}
            className="rounded-2xl bg-sand px-4 py-2 text-sm font-semibold text-ink"
            disabled={loading}
          >
            {loading ? 'Gerando ideias...' : 'Gerar ideias'}
          </button>
          <button type="button" onClick={handleSaveDraft} className="rounded-2xl border border-cyan/30 bg-cyan/10 px-4 py-2 text-sm text-cyan">
            Salvar draft
          </button>
        </div>
      </SectionCard>

      <SectionCard title="Creative Output" description="Blocos prontos para equipe de conteudo, design e performance.">
        {!ideas.length ? (
          <EmptyState
            title="Nenhuma ideia ainda"
            description="Gere de 5 a 10 conceitos com hook e CTA para acelerar seu backlog de criativos."
          />
        ) : (
          <div className="grid gap-3 md:grid-cols-2">
            {ideas.map((idea) => (
              <article key={idea.title} className="rounded-2xl border border-white/10 bg-ink/40 p-4">
                <p className="font-semibold text-white">{idea.title}</p>
                <p className="mt-2 text-sm text-slate-200">{idea.concept}</p>
                <p className="mt-3 text-sm text-cyan">Hook: {idea.hook}</p>
                <p className="mt-2 text-sm text-slate-100">CTA: {idea.cta}</p>
              </article>
            ))}
          </div>
        )}
      </SectionCard>
    </div>
  );
}

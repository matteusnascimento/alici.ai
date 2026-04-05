import { useEffect, useState } from 'react';

import { generatePostCopy } from '../../services/marketingService';
import type { MarketingTemplateProfile, PostCopyInput, PostCopyResult } from '../../types/marketing';
import { EmptyState } from './EmptyState';
import { OutputCard } from './OutputCard';
import { SectionCard } from './SectionCard';

interface CopyStudioProps {
  templateProfile: MarketingTemplateProfile | null;
  onNotify: (message: string) => void;
}

const initialForm: PostCopyInput = {
  content_type: 'Instagram caption generator',
  audience: 'gestores e times comerciais',
  goal: 'gerar conversas comerciais',
  product_service: 'AXI Growth Studio',
  tone: 'premium direto',
  cta: 'Clique para solicitar diagnostico',
};

export function CopyStudio({ templateProfile, onNotify }: CopyStudioProps) {
  const [form, setForm] = useState<PostCopyInput>(initialForm);
  const [result, setResult] = useState<PostCopyResult | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!templateProfile) return;
    setForm((current) => ({
      ...current,
      audience: templateProfile.audience,
      product_service: templateProfile.offer,
      tone: templateProfile.tone,
    }));
  }, [templateProfile]);

  async function handleGenerate() {
    setLoading(true);
    try {
      const generated = await generatePostCopy(form);
      setResult(generated);
      onNotify('Copy gerada para postagem.');
    } finally {
      setLoading(false);
    }
  }

  async function handleCopy() {
    if (!result) return;
    await navigator.clipboard.writeText(result.main_copy);
    onNotify('Copy principal copiada.');
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[390px_1fr]">
      <SectionCard title="Posts & Copy Studio" description="Gerador para caption, carrossel, promo, institucional, oferta, ad curto e copy longa.">
        <div className="space-y-3">
          {[
            ['content_type', 'Content type'],
            ['audience', 'Audience'],
            ['goal', 'Goal'],
            ['product_service', 'Product or service'],
            ['tone', 'Tone'],
            ['cta', 'CTA'],
          ].map(([key, label]) => (
            <label key={key} className="block space-y-2 text-sm text-slate-300">
              <span>{label}</span>
              <input
                className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white outline-none focus:border-cyan"
                value={form[key as keyof PostCopyInput]}
                onChange={(event) => setForm((current) => ({ ...current, [key]: event.target.value }))}
              />
            </label>
          ))}
        </div>
        <div className="mt-5 flex flex-wrap gap-3">
          <button type="button" onClick={handleGenerate} className="rounded-2xl bg-sand px-4 py-2 text-sm font-semibold text-ink" disabled={loading}>
            {loading ? 'Gerando copy...' : 'Gerar copy'}
          </button>
          <button type="button" onClick={handleCopy} className="rounded-2xl border border-white/20 px-4 py-2 text-sm text-slate-100">
            Copiar resultado
          </button>
          <button
            type="button"
            onClick={() => {
              localStorage.setItem('axi-growth-copy-draft', JSON.stringify(form));
              onNotify('Draft de copy salvo.');
            }}
            className="rounded-2xl border border-cyan/30 bg-cyan/10 px-4 py-2 text-sm text-cyan"
          >
            Salvar draft
          </button>
        </div>
      </SectionCard>

      <SectionCard title="Copy Output" description="Texto principal, variacoes, hashtags e hooks prontos para deploy.">
        {!result ? (
          <EmptyState title="Nenhuma copy gerada" description="Use os campos ao lado para montar um ativo completo de copywriting." />
        ) : (
          <div className="grid gap-3 md:grid-cols-2">
            <OutputCard label="Main copy" value={result.main_copy} />
            <OutputCard label="Variations" list={result.variations} />
            <OutputCard label="CTA lines" list={result.cta_lines} />
            <OutputCard label="Hashtags" list={result.hashtags} />
            <OutputCard label="Hook suggestion" value={result.hook_suggestion} />
          </div>
        )}
      </SectionCard>
    </div>
  );
}

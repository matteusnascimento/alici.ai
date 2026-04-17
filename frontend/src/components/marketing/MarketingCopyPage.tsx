import { Loader2, Sparkles, Copy } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { generateCopy, listProjects } from '../../services/marketing.service';
import type { MarketingProject } from '../../types/marketing';

const COPY_TYPES = [
  { id: 'social_post', label: 'Post Redes Sociais' },
  { id: 'email', label: 'E-mail Marketing' },
  { id: 'whatsapp', label: 'WhatsApp' },
  { id: 'ad', label: 'Anúncio' },
  { id: 'headline', label: 'Headline / CTA' },
];

export function MarketingCopyPage() {
  const [searchParams] = useSearchParams();
  const defaultProjectId = searchParams.get('project') ? Number(searchParams.get('project')) : undefined;

  const [projects, setProjects] = useState<MarketingProject[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<number | undefined>(defaultProjectId);
  const [context, setContext] = useState('');
  const [copyType, setCopyType] = useState('social_post');
  const [result, setResult] = useState<{ copies: string[]; cta: string; hook: string; hashtags: string[] } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<number | null>(null);

  useEffect(() => {
    listProjects()
      .then((rows) => setProjects(Array.isArray(rows) ? rows : []))
      .catch(() => setProjects([]));
  }, []);

  async function handleGenerate(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedProjectId) { setError('Selecione um projeto'); return; }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const r = await generateCopy(selectedProjectId, context, copyType);
      setResult({
        copies: Array.isArray(r?.copies) ? r.copies : [],
        cta: r?.cta ?? '',
        hook: r?.hook ?? '',
        hashtags: Array.isArray(r?.hashtags) ? r.hashtags : [],
      });
    } catch {
      setError('Erro ao gerar copy. Verifique a configuração de IA.');
    } finally {
      setLoading(false);
    }
  }

  function handleCopy(text: string, idx: number) {
    navigator.clipboard.writeText(text);
    setCopied(idx);
    setTimeout(() => setCopied(null), 1500);
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-8 space-y-8">
      <div className="flex items-center gap-3">
        <Sparkles size={20} className="text-cyan" />
        <h1 className="text-xl font-semibold text-white">Gerador de Copy com IA</h1>
      </div>

      <form onSubmit={handleGenerate} className="rounded-2xl border border-white/10 bg-white/5 p-6 space-y-3">
        <select
          required
          value={selectedProjectId ?? ''}
          onChange={(e) => setSelectedProjectId(Number(e.target.value))}
          className="w-full rounded-xl border border-white/10 bg-storm px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan/50"
        >
          <option value="">Selecione um projeto de marketing...</option>
          {projects.map((p) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>

        <select
          value={copyType}
          onChange={(e) => setCopyType(e.target.value)}
          className="w-full rounded-xl border border-white/10 bg-storm px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan/50"
        >
          {COPY_TYPES.map((t) => <option key={t.id} value={t.id}>{t.label}</option>)}
        </select>

        <textarea
          placeholder="Contexto adicional (lançamento, promoção, tema especial...)"
          value={context}
          onChange={(e) => setContext(e.target.value)}
          rows={3}
          className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan/50 resize-none"
        />

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 rounded-xl bg-cyan px-6 py-2.5 text-sm font-semibold text-ink hover:bg-cyan/90 disabled:opacity-50"
          >
            {loading ? <Loader2 size={14} className="animate-spin" /> : <Sparkles size={14} />}
            Gerar Variações
          </button>
        </div>
        {error && <p className="text-xs text-red-400">{error}</p>}
      </form>

      {result && (
        <section className="space-y-4">
          {result.hook && (
            <div className="rounded-2xl border border-cyan/20 bg-cyan/5 p-4">
              <p className="text-xs text-cyan uppercase tracking-wider mb-1">Hook</p>
              <p className="text-sm text-white">{result.hook}</p>
            </div>
          )}

          <h2 className="text-sm uppercase tracking-[0.25em] text-slate-400">Variações de Copy</h2>
          {result.copies.map((copy, i) => (
            <div key={i} className="rounded-2xl border border-white/10 bg-white/5 p-5 relative group">
              <p className="text-sm text-slate-200 whitespace-pre-wrap pr-8">{copy}</p>
              <button
                onClick={() => handleCopy(copy, i)}
                className="absolute right-4 top-4 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg p-1.5 hover:bg-white/10 text-slate-400"
              >
                {copied === i ? <span className="text-xs text-cyan">✓</span> : <Copy size={13} />}
              </button>
            </div>
          ))}

          {result.cta && (
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">CTA</p>
              <p className="text-sm text-white">{result.cta}</p>
            </div>
          )}

          {result.hashtags?.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {result.hashtags.map((h) => (
                <span key={h} className="rounded-full border border-white/15 px-3 py-1 text-xs text-slate-300">
                  {h.startsWith('#') ? h : `#${h}`}
                </span>
              ))}
            </div>
          )}
        </section>
      )}
    </div>
  );
}

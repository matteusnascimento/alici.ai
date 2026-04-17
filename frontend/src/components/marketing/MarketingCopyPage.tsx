import { Bot, Copy, Loader2, RefreshCcw, SendHorizontal, Sparkles, User2 } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';

import { generateCopy, listProjects } from '../../services/marketing.service';
import type { MarketingProject } from '../../types/marketing';

const COPY_TYPES = [
  { id: 'social_post', label: 'Post redes sociais' },
  { id: 'email', label: 'Email marketing' },
  { id: 'whatsapp', label: 'WhatsApp' },
  { id: 'ad', label: 'Anuncio' },
  { id: 'headline', label: 'Headline / CTA' },
];

interface CopyHistoryEntry {
  id: string;
  prompt: string;
  copies: string[];
  cta: string;
  hook: string;
  hashtags: string[];
}

export function MarketingCopyPage() {
  const [searchParams] = useSearchParams();
  const defaultProjectId = searchParams.get('project') ? Number(searchParams.get('project')) : undefined;

  const [projects, setProjects] = useState<MarketingProject[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<number | undefined>(defaultProjectId);
  const [prompt, setPrompt] = useState('');
  const [copyType, setCopyType] = useState('social_post');
  const [history, setHistory] = useState<CopyHistoryEntry[]>([]);
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
    if (!selectedProjectId) {
      setError('Selecione um projeto');
      return;
    }
    if (!prompt.trim()) {
      setError('Descreva o que deseja gerar para a IA.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await generateCopy(selectedProjectId, prompt, copyType);
      const entry: CopyHistoryEntry = {
        id: `${Date.now()}`,
        prompt,
        copies: Array.isArray(response?.copies) ? response.copies : [],
        cta: response?.cta ?? '',
        hook: response?.hook ?? '',
        hashtags: Array.isArray(response?.hashtags) ? response.hashtags : [],
      };
      setHistory((current) => [entry, ...current]);
      setPrompt('');
    } catch {
      setError('Erro ao gerar copy. Verifique a configuracao de IA.');
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerateMore() {
    if (!selectedProjectId || history.length === 0) return;

    setLoading(true);
    setError(null);
    try {
      const last = history[0];
      const response = await generateCopy(
        selectedProjectId,
        `${last.prompt}. Gere novas variacoes com angulo diferente.`,
        copyType,
      );
      const entry: CopyHistoryEntry = {
        id: `${Date.now()}`,
        prompt: `Gerar mais: ${last.prompt}`,
        copies: Array.isArray(response?.copies) ? response.copies : [],
        cta: response?.cta ?? '',
        hook: response?.hook ?? '',
        hashtags: Array.isArray(response?.hashtags) ? response.hashtags : [],
      };
      setHistory((current) => [entry, ...current]);
    } catch {
      setError('Nao foi possivel gerar mais variacoes agora.');
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
    <div className="mx-auto max-w-7xl px-6 py-8 space-y-6">
      <section className="rounded-3xl border border-cyan-300/20 bg-[radial-gradient(circle_at_10%_25%,rgba(6,182,212,0.22),transparent_42%),linear-gradient(165deg,#051329,#0a2245)] p-6 md:p-8">
        <p className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.28em] text-cyan-200">
          <Sparkles size={14} className="animate-pulse" /> Copy AI Assistant
        </p>
        <h1 className="mt-2 font-display text-4xl text-white md:text-5xl">Gere copy como conversa com IA</h1>
        <p className="mt-3 max-w-3xl text-sm text-slate-200 md:text-base">
          Interface no estilo chat com historico de geracoes, variacoes de copy e acao de gerar mais.
        </p>
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.92fr_1.08fr]">
        <aside className="rounded-3xl border border-white/10 bg-white/5 p-5 space-y-4">
          <p className="text-sm font-semibold text-white">Configuracao da geracao</p>
          <label className="space-y-1.5 block">
            <span className="text-xs uppercase tracking-[0.18em] text-slate-300">Projeto</span>
            <select
              required
              value={selectedProjectId ?? ''}
              onChange={(e) => setSelectedProjectId(Number(e.target.value))}
              className="w-full rounded-xl border border-white/15 bg-[#0b1328]/85 px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan/50"
            >
              <option value="">Selecione um projeto...</option>
              {projects.map((project) => (
                <option key={project.id} value={project.id}>{project.name}</option>
              ))}
            </select>
          </label>

          <label className="space-y-1.5 block">
            <span className="text-xs uppercase tracking-[0.18em] text-slate-300">Formato</span>
            <select
              value={copyType}
              onChange={(e) => setCopyType(e.target.value)}
              className="w-full rounded-xl border border-white/15 bg-[#0b1328]/85 px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan/50"
            >
              {COPY_TYPES.map((type) => <option key={type.id} value={type.id}>{type.label}</option>)}
            </select>
          </label>

          <button
            type="button"
            onClick={() => void handleGenerateMore()}
            disabled={loading || history.length === 0 || !selectedProjectId}
            className="inline-flex items-center gap-2 rounded-xl border border-white/20 px-3 py-2 text-xs font-semibold text-slate-100 hover:bg-white/10 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RefreshCcw size={13} /> Gerar mais
          </button>

          <p className="text-xs text-slate-400">
            Use prompts com contexto de publico, dor e oferta para obter respostas melhores.
          </p>
        </aside>

        <div className="rounded-3xl border border-white/10 bg-[linear-gradient(170deg,rgba(255,255,255,0.08),rgba(255,255,255,0.03))] p-5">
          <div className="space-y-4 max-h-[58vh] overflow-y-auto pr-1">
            {history.length === 0 ? (
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-300">
                Digite uma solicitacao e gere sua primeira copy.
                Exemplo: Quero vender pousada em Morro de SP para casais no fim de semana.
              </div>
            ) : null}

            {history.map((entry, blockIndex) => (
              <div key={entry.id} className="space-y-3">
                <div className="flex justify-end">
                  <div className="max-w-[85%] rounded-2xl border border-cyan-300/30 bg-cyan-500/10 px-4 py-3 text-sm text-cyan-100">
                    <p className="mb-1 inline-flex items-center gap-1 text-[11px] uppercase tracking-[0.16em] text-cyan-200"><User2 size={12} /> Voce</p>
                    <p>{entry.prompt}</p>
                  </div>
                </div>

                <div className="flex justify-start">
                  <div className="w-full max-w-[95%] rounded-2xl border border-white/15 bg-[#0b1328]/85 px-4 py-4 text-sm text-slate-100">
                    <p className="mb-2 inline-flex items-center gap-1 text-[11px] uppercase tracking-[0.16em] text-cyan-200"><Bot size={12} /> IA</p>
                    {entry.hook ? <p className="mb-2 text-xs text-cyan-100">Hook: {entry.hook}</p> : null}

                    <div className="space-y-2">
                      {entry.copies.map((copy, index) => {
                        const absoluteIndex = blockIndex * 100 + index;
                        return (
                          <div key={`${entry.id}-${index}`} className="group rounded-xl border border-white/10 bg-white/5 px-3 py-3">
                            <div className="flex items-start justify-between gap-3">
                              <p className="whitespace-pre-wrap text-sm text-slate-100">{index + 1}. {copy}</p>
                              <button
                                type="button"
                                onClick={() => handleCopy(copy, absoluteIndex)}
                                className="opacity-0 transition group-hover:opacity-100 rounded-lg p-1.5 hover:bg-white/10 text-slate-400"
                              >
                                {copied === absoluteIndex ? <span className="text-xs text-cyan">copiado</span> : <Copy size={13} />}
                              </button>
                            </div>
                          </div>
                        );
                      })}
                    </div>

                    <div className="mt-3 flex flex-wrap gap-2 text-xs">
                      {entry.cta ? <span className="rounded-full border border-cyan-300/30 px-2.5 py-1 text-cyan-100">CTA: {entry.cta}</span> : null}
                      {entry.hashtags.map((tag) => (
                        <span key={`${entry.id}-${tag}`} className="rounded-full border border-white/15 px-2.5 py-1 text-slate-300">
                          {tag.startsWith('#') ? tag : `#${tag}`}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <form onSubmit={handleGenerate} className="mt-4 rounded-2xl border border-white/15 bg-[#0b1328]/80 p-3">
            <div className="flex gap-2">
              <textarea
                placeholder="Descreva o que voce quer gerar..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={3}
                className="w-full rounded-xl border border-white/15 bg-white/5 px-3 py-2 text-sm text-white placeholder-slate-500 resize-none focus:outline-none focus:border-cyan/50"
              />
              <button
                type="submit"
                disabled={loading}
                className="h-fit inline-flex items-center gap-2 rounded-xl bg-cyan px-4 py-2.5 text-sm font-semibold text-ink hover:bg-cyan/90 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? <Loader2 size={14} className="animate-spin" /> : <SendHorizontal size={14} />}
                Gerar
              </button>
            </div>
            {error ? <p className="mt-2 text-xs text-rose-300">{error}</p> : null}
          </form>
        </div>
      </section>
    </div>
  );
}

import {
  ArrowLeft,
  BarChart2,
  Bot,
  Check,
  ClipboardCopy,
  Edit2,
  FileText,
  LayoutGrid,
  Loader2,
  Megaphone,
  Rocket,
  Send,
  Sparkles,
  Trash2,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import type {
  MarketingCampaignInput,
  MarketingCampaignResult,
  MarketingProject,
} from '../../types/marketing';
import {
  deleteProject,
  generateCampaign,
  generateCopy,
  getProject,
} from '../../services/marketing.service';

// ─── types ────────────────────────────────────────────────────────────────────

type TabId = 'overview' | 'campaign' | 'copy' | 'brief' | 'results';

interface CopyEntry {
  id: number;
  prompt: string;
  copies: string[];
  cta: string;
  hook: string;
  hashtags: string[];
}

interface BriefModel {
  objetivo: string;
  publico: string;
  tom: string;
  mensagem: string;
  estrategia: string;
}

// ─── constants ────────────────────────────────────────────────────────────────

const TABS: { id: TabId; label: string; icon: LucideIcon }[] = [
  { id: 'overview', label: 'Visão Geral', icon: LayoutGrid },
  { id: 'campaign', label: 'Campanha', icon: Megaphone },
  { id: 'copy', label: 'Copy IA', icon: Sparkles },
  { id: 'brief', label: 'Briefing', icon: FileText },
  { id: 'results', label: 'Resultados', icon: BarChart2 },
];

const TONES = ['premium', 'casual', 'urgente', 'educativo', 'inspirador'];
const GOALS = ['Gerar leads', 'Vender direto', 'Aumentar seguidores', 'Engajamento', 'Retencao'];
const CHANNELS = ['instagram', 'whatsapp', 'facebook', 'google', 'email'];

const INPUT_CLS =
  'w-full rounded-xl border border-white/15 bg-[#0b1328]/80 px-3 py-2.5 text-sm text-white placeholder:text-slate-500 transition focus:border-cyan/50 focus:outline-none focus:ring-2 focus:ring-cyan/20';

// ─── helpers ──────────────────────────────────────────────────────────────────

function toneLabel(t: string) {
  const map: Record<string, string> = {
    premium: 'Premium',
    casual: 'Casual',
    urgente: 'Urgente',
    educativo: 'Educativo',
    inspirador: 'Inspirador',
  };
  return map[t] ?? t;
}

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' });
}

function mapProjectToCampaignInput(p: MarketingProject): MarketingCampaignInput {
  return {
    business_name: p.name,
    market_segment: p.notes ?? '',
    target_audience: p.audience,
    campaign_goal: p.objective,
    offer: p.offer,
    tone: p.tone,
    channel: 'instagram',
    campaign_type: 'awareness',
    budget_range: '',
    call_to_action: '',
  };
}

function mapCampaignToBrief(project: MarketingProject, result: MarketingCampaignResult): BriefModel {
  return {
    objetivo: project.objective,
    publico: project.audience,
    tom: toneLabel(project.tone),
    mensagem: result.primary_copy,
    estrategia: result.secondary_copy || result.positioning_summary || '',
  };
}

// ─── sub-panels ───────────────────────────────────────────────────────────────

interface OverviewPanelProps {
  project: MarketingProject;
  campaignResult: MarketingCampaignResult | null;
  copyHistory: CopyEntry[];
  briefResult: BriefModel | null;
  onGoTo: (tab: TabId) => void;
}

function OverviewPanel({ project, campaignResult, copyHistory, briefResult, onGoTo }: OverviewPanelProps) {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {[
          { label: 'Público-alvo', value: project.audience },
          { label: 'Objetivo', value: project.objective },
          { label: 'Oferta', value: project.offer },
          { label: 'Tom', value: toneLabel(project.tone) },
        ].map(({ label, value }) => (
          <div
            key={label}
            className="rounded-2xl border border-white/10 bg-white/5 p-4"
          >
            <p className="text-[11px] uppercase tracking-[0.2em] text-cyan-200">{label}</p>
            <p className="mt-2 text-sm font-medium text-white">{value}</p>
          </div>
        ))}
      </div>

      {project.notes ? (
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="text-[11px] uppercase tracking-[0.2em] text-cyan-200">Contexto adicional</p>
          <p className="mt-2 text-sm text-slate-300">{project.notes}</p>
        </div>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-3">
        <StatusCard
          title="Campanha"
          icon={<Megaphone size={16} className="text-cyan" />}
          done={!!campaignResult}
          cta="Gerar campanha"
          onCta={() => onGoTo('campaign')}
          preview={campaignResult?.campaign_headline}
        />
        <StatusCard
          title="Copy IA"
          icon={<Sparkles size={16} className="text-cyan" />}
          done={copyHistory.length > 0}
          cta="Criar copies"
          onCta={() => onGoTo('copy')}
          preview={copyHistory.length > 0 ? `${copyHistory.length} variação(ões) gerada(s)` : undefined}
        />
        <StatusCard
          title="Briefing"
          icon={<FileText size={16} className="text-cyan" />}
          done={!!briefResult}
          cta="Gerar briefing"
          onCta={() => onGoTo('brief')}
          preview={briefResult?.objetivo}
        />
      </div>
    </div>
  );
}

interface StatusCardProps {
  title: string;
  icon: React.ReactNode;
  done: boolean;
  cta: string;
  onCta: () => void;
  preview?: string;
}

function StatusCard({ title, icon, done, cta, onCta, preview }: StatusCardProps) {
  return (
    <div className="flex flex-col gap-3 rounded-2xl border border-white/10 bg-white/5 p-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {icon}
          <span className="text-sm font-semibold text-white">{title}</span>
        </div>
        <span
          className={[
            'rounded-full px-2 py-0.5 text-[11px] font-medium',
            done
              ? 'bg-emerald-500/15 text-emerald-300'
              : 'bg-white/8 text-slate-400',
          ].join(' ')}
        >
          {done ? 'Pronto' : 'Pendente'}
        </span>
      </div>
      {preview ? (
        <p className="text-xs text-slate-300 line-clamp-2">{preview}</p>
      ) : (
        <p className="text-xs text-slate-500">Nenhum conteúdo gerado ainda.</p>
      )}
      <button
        type="button"
        onClick={onCta}
        className="mt-auto inline-flex items-center gap-1.5 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs font-medium text-slate-200 transition hover:border-cyan/40 hover:bg-cyan/10 hover:text-cyan"
      >
        <Rocket size={12} />
        {cta}
      </button>
    </div>
  );
}

// ─── Campaign Panel ───────────────────────────────────────────────────────────

interface CampaignPanelProps {
  project: MarketingProject;
  result: MarketingCampaignResult | null;
  onResult: (r: MarketingCampaignResult) => void;
}

function CampaignPanel({ project, result, onResult }: CampaignPanelProps) {
  const [form, setForm] = useState<MarketingCampaignInput>(() => mapProjectToCampaignInput(project));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const r = await generateCampaign(form);
      onResult({
        ...r,
        cta_suggestions: Array.isArray(r?.cta_suggestions) ? r.cta_suggestions : [],
      });
    } catch {
      setError('Erro ao gerar campanha. Verifique as configurações de IA.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-2">
      <form
        onSubmit={handleSubmit}
        className="rounded-3xl border border-white/10 bg-white/[0.04] p-6 grid gap-4 sm:grid-cols-2"
      >
        <div className="sm:col-span-2">
          <p className="text-sm font-semibold text-white">Briefing da campanha</p>
          <p className="mt-1 text-xs text-slate-400">Pré-preenchido com os dados do projeto. Ajuste se necessário.</p>
        </div>

        <label className="space-y-1.5">
          <span className="text-xs font-medium text-slate-300">Marca / Negócio</span>
          <input
            required
            placeholder="Nome da empresa"
            value={form.business_name}
            onChange={(e) => setForm((f) => ({ ...f, business_name: e.target.value }))}
            className={INPUT_CLS}
          />
        </label>
        <label className="space-y-1.5">
          <span className="text-xs font-medium text-slate-300">Segmento</span>
          <input
            placeholder="Ex: Hospitalidade, SaaS, Varejo"
            value={form.market_segment}
            onChange={(e) => setForm((f) => ({ ...f, market_segment: e.target.value }))}
            className={INPUT_CLS}
          />
        </label>
        <label className="space-y-1.5">
          <span className="text-xs font-medium text-slate-300">Público-alvo</span>
          <input
            required
            placeholder="Quem deve comprar"
            value={form.target_audience}
            onChange={(e) => setForm((f) => ({ ...f, target_audience: e.target.value }))}
            className={INPUT_CLS}
          />
        </label>
        <label className="space-y-1.5">
          <span className="text-xs font-medium text-slate-300">Oferta / Produto</span>
          <input
            required
            placeholder="Oferta principal"
            value={form.offer}
            onChange={(e) => setForm((f) => ({ ...f, offer: e.target.value }))}
            className={INPUT_CLS}
          />
        </label>
        <label className="space-y-1.5">
          <span className="text-xs font-medium text-slate-300">Objetivo</span>
          <select
            value={form.campaign_goal}
            onChange={(e) => setForm((f) => ({ ...f, campaign_goal: e.target.value }))}
            className={INPUT_CLS}
          >
            {GOALS.map((g) => <option key={g} value={g}>{g}</option>)}
          </select>
        </label>
        <label className="space-y-1.5">
          <span className="text-xs font-medium text-slate-300">Tom</span>
          <select
            value={form.tone}
            onChange={(e) => setForm((f) => ({ ...f, tone: e.target.value }))}
            className={INPUT_CLS}
          >
            {TONES.map((t) => <option key={t} value={t}>{toneLabel(t)}</option>)}
          </select>
        </label>
        <label className="space-y-1.5">
          <span className="text-xs font-medium text-slate-300">Canal principal</span>
          <select
            value={form.channel}
            onChange={(e) => setForm((f) => ({ ...f, channel: e.target.value }))}
            className={INPUT_CLS}
          >
            {CHANNELS.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        </label>
        <label className="space-y-1.5">
          <span className="text-xs font-medium text-slate-300">CTA desejado</span>
          <input
            placeholder="Ex: Fale conosco agora"
            value={form.call_to_action}
            onChange={(e) => setForm((f) => ({ ...f, call_to_action: e.target.value }))}
            className={INPUT_CLS}
          />
        </label>

        <div className="sm:col-span-2 flex items-center justify-between">
          {error ? <p className="text-xs text-rose-300">{error}</p> : <span />}
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-xl bg-cyan px-5 py-2.5 text-sm font-semibold text-ink transition hover:bg-cyan/90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? <Loader2 size={14} className="animate-spin" /> : <Rocket size={14} />}
            {result ? 'Regerar campanha' : 'Gerar campanha com IA'}
          </button>
        </div>
      </form>

      <aside className="rounded-3xl border border-cyan-300/20 bg-[linear-gradient(165deg,rgba(7,17,38,0.96),rgba(8,23,49,0.93))] p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-white">Resultado da IA</h3>
          {loading ? (
            <span className="inline-flex items-center gap-1 text-xs text-cyan-300">
              <Loader2 size={12} className="animate-spin" /> Gerando…
            </span>
          ) : result ? (
            <span className="inline-flex items-center gap-1 rounded-full border border-emerald-400/30 bg-emerald-500/10 px-2.5 py-1 text-[11px] text-emerald-300">
              <Check size={10} /> Pronto
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 rounded-full border border-white/15 bg-white/5 px-2.5 py-1 text-[11px] text-slate-400">
              <Bot size={10} /> Aguardando
            </span>
          )}
        </div>

        {result ? (
          <div className="space-y-3">
            {[
              { label: 'Headline', value: result.campaign_headline },
              { label: 'Copy principal', value: result.primary_copy },
              { label: 'Estrutura do anúncio', value: result.secondary_copy },
              { label: 'Sugestão criativa', value: result.creative_suggestion },
            ].map(({ label, value }) =>
              value ? (
                <div key={label} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p className="text-[11px] uppercase tracking-[0.2em] text-cyan-200">{label}</p>
                  <p className="mt-2 text-sm text-slate-200">{value}</p>
                </div>
              ) : null
            )}
            {result.cta_suggestions?.length > 0 && (
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <p className="text-[11px] uppercase tracking-[0.2em] text-cyan-200">CTAs sugeridos</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {result.cta_suggestions.map((cta, i) => (
                    <span
                      key={i}
                      className="rounded-lg bg-cyan/10 px-3 py-1 text-xs font-medium text-cyan-100"
                    >
                      {cta}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex h-48 flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-white/10">
            <Bot size={28} className="text-slate-600" />
            <p className="text-xs text-slate-500">Preencha o briefing e gere a campanha.</p>
          </div>
        )}
      </aside>
    </div>
  );
}

// ─── Copy Panel ───────────────────────────────────────────────────────────────

interface CopyPanelProps {
  project: MarketingProject;
  history: CopyEntry[];
  onHistory: (entries: CopyEntry[]) => void;
}

function CopyPanel({ project, history, onHistory }: CopyPanelProps) {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  async function submit(text: string) {
    if (!text.trim() || loading) return;
    setLoading(true);
    setError(null);
    try {
      const res = await generateCopy(project.id, text.trim());
      const entry: CopyEntry = {
        id: Date.now(),
        prompt: text.trim(),
        copies: Array.isArray(res.copies) ? res.copies : [],
        cta: res.cta ?? '',
        hook: res.hook ?? '',
        hashtags: Array.isArray(res.hashtags) ? res.hashtags : [],
      };
      onHistory([...history, entry]);
      setPrompt('');
    } catch {
      setError('Erro ao gerar copies.');
    } finally {
      setLoading(false);
      setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: 'smooth' }), 80);
    }
  }

  function handleCopy(text: string) {
    navigator.clipboard.writeText(text);
    setCopied(text);
    setTimeout(() => setCopied(null), 1800);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submit(prompt);
    }
  }

  const lastPrompt = history.length > 0 ? history[history.length - 1].prompt : null;

  return (
    <div className="flex h-[calc(100vh-18rem)] flex-col gap-4">
      <div className="flex-1 overflow-y-auto rounded-2xl border border-white/10 bg-white/[0.03] p-4 space-y-4">
        {history.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
            <Sparkles size={28} className="text-slate-600" />
            <p className="text-sm text-slate-400">
              Descreva o que precisa. A IA gerará variações de copy prontas para usar.
            </p>
            <p className="text-xs text-slate-600">
              Ex: "Crie 3 copies para Story do Instagram promovendo {project.offer}"
            </p>
          </div>
        ) : (
          history.map((entry) => (
            <div key={entry.id} className="space-y-3">
              <div className="flex justify-end">
                <div className="max-w-[80%] rounded-2xl rounded-tr-sm bg-cyan/15 px-4 py-3 text-sm text-white">
                  {entry.prompt}
                </div>
              </div>
              <div className="space-y-2">
                {entry.copies.map((copy, idx) => (
                  <div
                    key={idx}
                    className="group relative rounded-2xl border border-white/10 bg-white/5 px-4 py-3"
                  >
                    <p className="text-[11px] font-semibold uppercase tracking-widest text-cyan-200 mb-2">
                      Variação {idx + 1}
                    </p>
                    <p className="text-sm text-slate-200 whitespace-pre-wrap">{copy}</p>
                    <button
                      type="button"
                      onClick={() => handleCopy(copy)}
                      className="absolute right-3 top-3 rounded-lg border border-white/10 bg-white/5 p-1.5 opacity-0 transition group-hover:opacity-100"
                    >
                      {copied === copy ? (
                        <Check size={12} className="text-emerald-400" />
                      ) : (
                        <ClipboardCopy size={12} className="text-slate-400" />
                      )}
                    </button>
                  </div>
                ))}
                {entry.cta && (
                  <div className="flex flex-wrap gap-2">
                    <span className="rounded-lg border border-cyan-300/30 bg-cyan-500/10 px-3 py-1 text-xs text-cyan-200">
                      CTA: {entry.cta}
                    </span>
                  </div>
                )}
                {entry.hashtags.length > 0 && (
                  <div className="flex flex-wrap gap-1.5">
                    {entry.hashtags.map((tag, i) => (
                      <span key={i} className="rounded-md bg-white/8 px-2 py-0.5 text-[11px] text-slate-400">
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>

      <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-3 space-y-2">
        {error ? <p className="text-xs text-rose-300 px-1">{error}</p> : null}
        <div className="flex gap-2">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={2}
            placeholder="Ex: 3 copies para Story do Instagram sobre meu produto..."
            className="flex-1 resize-none rounded-xl border border-white/15 bg-[#0b1328]/80 px-3 py-2.5 text-sm text-white placeholder:text-slate-500 transition focus:border-cyan/50 focus:outline-none focus:ring-2 focus:ring-cyan/20"
          />
          <div className="flex flex-col gap-2">
            <button
              type="button"
              onClick={() => submit(prompt)}
              disabled={loading || !prompt.trim()}
              className="rounded-xl bg-cyan px-3 py-2 transition hover:bg-cyan/90 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {loading ? <Loader2 size={16} className="animate-spin text-ink" /> : <Send size={16} className="text-ink" />}
            </button>
            {lastPrompt && (
              <button
                type="button"
                onClick={() => submit(lastPrompt)}
                disabled={loading}
                title="Gerar mais variações do último prompt"
                className="rounded-xl border border-white/15 bg-white/5 px-3 py-2 text-[11px] text-slate-400 transition hover:border-cyan/30 hover:text-cyan disabled:opacity-40"
              >
                +
              </button>
            )}
          </div>
        </div>
        <p className="text-[11px] text-slate-600 px-1">Enter para enviar · Shift+Enter para nova linha</p>
      </div>
    </div>
  );
}

// ─── Brief Panel ──────────────────────────────────────────────────────────────

interface BriefPanelProps {
  project: MarketingProject;
  brief: BriefModel | null;
  onBrief: (b: BriefModel) => void;
}

function BriefPanel({ project, brief, onBrief }: BriefPanelProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState<keyof BriefModel | null>(null);
  const [localBrief, setLocalBrief] = useState<BriefModel | null>(brief);
  const [saved, setSaved] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setLocalBrief(brief);
  }, [brief]);

  async function handleGenerate() {
    setLoading(true);
    setError(null);
    try {
      const result = await generateCampaign(mapProjectToCampaignInput(project));
      const mapped = mapCampaignToBrief(project, result);
      onBrief(mapped);
      setLocalBrief(mapped);
    } catch {
      setError('Erro ao gerar briefing.');
    } finally {
      setLoading(false);
    }
  }

  function handleSave() {
    if (!localBrief) return;
    onBrief(localBrief);
    localStorage.setItem(`axi_brief_${project.id}`, JSON.stringify(localBrief));
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  function handleCopyAll() {
    if (!localBrief) return;
    const text = Object.entries(localBrief)
      .map(([k, v]) => `${k.toUpperCase()}\n${v}`)
      .join('\n\n');
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  }

  const BRIEF_LABELS: { key: keyof BriefModel; label: string }[] = [
    { key: 'objetivo', label: 'Objetivo' },
    { key: 'publico', label: 'Público-alvo' },
    { key: 'tom', label: 'Tom de comunicação' },
    { key: 'mensagem', label: 'Mensagem principal' },
    { key: 'estrategia', label: 'Estratégia de execução' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-white">Briefing estruturado</h3>
          <p className="mt-0.5 text-xs text-slate-400">
            Gerado automaticamente com base nos dados do projeto. Edite e salve.
          </p>
        </div>
        <div className="flex gap-2">
          {localBrief && (
            <>
              <button
                type="button"
                onClick={handleCopyAll}
                className="inline-flex items-center gap-1.5 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-300 transition hover:border-cyan/30 hover:text-cyan"
              >
                {copied ? <Check size={12} className="text-emerald-400" /> : <ClipboardCopy size={12} />}
                Copiar tudo
              </button>
              <button
                type="button"
                onClick={handleSave}
                className="inline-flex items-center gap-1.5 rounded-lg border border-emerald-400/30 bg-emerald-500/10 px-3 py-2 text-xs text-emerald-300 transition hover:bg-emerald-500/20"
              >
                {saved ? <Check size={12} /> : <Edit2 size={12} />}
                {saved ? 'Salvo!' : 'Salvar'}
              </button>
            </>
          )}
          <button
            type="button"
            onClick={handleGenerate}
            disabled={loading}
            className="inline-flex items-center gap-1.5 rounded-lg bg-cyan px-4 py-2 text-xs font-semibold text-ink transition hover:bg-cyan/90 disabled:opacity-50"
          >
            {loading ? <Loader2 size={12} className="animate-spin" /> : <Rocket size={12} />}
            {localBrief ? 'Regenerar' : 'Gerar briefing'}
          </button>
        </div>
      </div>

      {error ? <p className="text-xs text-rose-300">{error}</p> : null}

      {localBrief ? (
        <div className="grid gap-4 sm:grid-cols-2">
          {BRIEF_LABELS.map(({ key, label }) => (
            <div
              key={key}
              className={[
                'rounded-2xl border border-white/10 bg-white/5 p-4',
                key === 'mensagem' || key === 'estrategia' ? 'sm:col-span-2' : '',
              ].join(' ')}
            >
              <div className="flex items-center justify-between mb-2">
                <p className="text-[11px] uppercase tracking-[0.2em] text-cyan-200">{label}</p>
                <button
                  type="button"
                  onClick={() => setEditing(editing === key ? null : key)}
                  className="rounded p-1 text-slate-500 transition hover:text-slate-300"
                >
                  <Edit2 size={12} />
                </button>
              </div>
              {editing === key ? (
                <textarea
                  value={localBrief[key]}
                  onChange={(e) =>
                    setLocalBrief((prev) => prev ? { ...prev, [key]: e.target.value } : prev)
                  }
                  onBlur={() => setEditing(null)}
                  rows={3}
                  autoFocus
                  className="w-full resize-none rounded-lg border border-cyan/30 bg-[#0b1328]/80 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-cyan/20"
                />
              ) : (
                <p className="text-sm text-slate-200">{localBrief[key]}</p>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="flex h-48 flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-white/10">
          <FileText size={28} className="text-slate-600" />
          <p className="text-sm text-slate-500">Clique em "Gerar briefing" para estruturar o projeto.</p>
        </div>
      )}
    </div>
  );
}

// ─── Results Panel ────────────────────────────────────────────────────────────

interface ResultsPanelProps {
  campaignResult: MarketingCampaignResult | null;
  copyHistory: CopyEntry[];
  briefResult: BriefModel | null;
}

function ResultsPanel({ campaignResult, copyHistory, briefResult }: ResultsPanelProps) {
  const totalCopies = copyHistory.reduce((acc, e) => acc + e.copies.length, 0);

  if (!campaignResult && copyHistory.length === 0 && !briefResult) {
    return (
      <div className="flex h-64 flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-white/10">
        <BarChart2 size={28} className="text-slate-600" />
        <p className="text-sm text-slate-500">
          Nenhum conteúdo gerado ainda. Complete as seções Campanha, Copy e Briefing.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-3">
        {[
          { label: 'Campanhas', value: campaignResult ? 1 : 0, icon: <Megaphone size={16} className="text-cyan" /> },
          { label: 'Copies geradas', value: totalCopies, icon: <Sparkles size={16} className="text-cyan" /> },
          { label: 'Briefing', value: briefResult ? 1 : 0, icon: <FileText size={16} className="text-cyan" /> },
        ].map(({ label, value, icon }) => (
          <div key={label} className="rounded-2xl border border-white/10 bg-white/5 p-5 text-center">
            <div className="mb-2 flex justify-center">{icon}</div>
            <p className="text-3xl font-bold text-white">{value}</p>
            <p className="mt-1 text-xs text-slate-400">{label}</p>
          </div>
        ))}
      </div>

      {campaignResult && (
        <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
          <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-cyan-200">
            Campanha gerada
          </p>
          <p className="font-semibold text-white">{campaignResult.campaign_headline}</p>
          <p className="mt-2 text-sm text-slate-300">{campaignResult.primary_copy}</p>
        </div>
      )}

      {copyHistory.length > 0 && (
        <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
          <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-cyan-200">
            Histórico de copies
          </p>
          <div className="space-y-3">
            {copyHistory.map((entry) => (
              <div key={entry.id} className="rounded-xl bg-white/5 p-3">
                <p className="text-xs text-slate-400 mb-1">{entry.prompt}</p>
                <p className="text-sm text-white">{entry.copies[0]}</p>
                {entry.copies.length > 1 && (
                  <p className="mt-1 text-xs text-slate-500">+{entry.copies.length - 1} variação(ões)</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Main workspace ───────────────────────────────────────────────────────────

export function MarketingProjectWorkspace() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  const [project, setProject] = useState<MarketingProject | null>(null);
  const [loadingProject, setLoadingProject] = useState(true);
  const [projectError, setProjectError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabId>('overview');

  const [campaignResult, setCampaignResult] = useState<MarketingCampaignResult | null>(null);
  const [copyHistory, setCopyHistory] = useState<CopyEntry[]>([]);
  const [briefResult, setBriefResult] = useState<BriefModel | null>(null);

  useEffect(() => {
    if (!projectId) return;
    setLoadingProject(true);
    getProject(Number(projectId))
      .then((p) => {
        setProject(p);
        const savedBrief = localStorage.getItem(`axi_brief_${p.id}`);
        if (savedBrief) {
          try {
            setBriefResult(JSON.parse(savedBrief));
          } catch {
            /* ignore */
          }
        }
      })
      .catch(() => setProjectError('Projeto não encontrado.'))
      .finally(() => setLoadingProject(false));
  }, [projectId]);

  async function handleDeleteProject() {
    if (!project) return;
    if (!confirm(`Remover o projeto "${project.name}"? Essa ação não pode ser desfeita.`)) return;
    await deleteProject(project.id);
    navigate('/app/marketing');
  }

  if (loadingProject) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 size={24} className="animate-spin text-cyan" />
      </div>
    );
  }

  if (projectError || !project) {
    return (
      <div className="flex h-64 flex-col items-center justify-center gap-4">
        <p className="text-sm text-rose-300">{projectError ?? 'Projeto não encontrado.'}</p>
        <button
          type="button"
          onClick={() => navigate('/app/marketing')}
          className="inline-flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-300 hover:text-white"
        >
          <ArrowLeft size={14} /> Voltar a projetos
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* ── Workspace Header ── */}
      <header className="shrink-0 border-b border-white/10 bg-[#05101f]/80 px-6 py-4 backdrop-blur">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            <button
              type="button"
              onClick={() => navigate('/app/marketing')}
              className="mt-0.5 rounded-lg border border-white/10 bg-white/5 p-1.5 text-slate-400 transition hover:text-white"
            >
              <ArrowLeft size={14} />
            </button>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-semibold text-white">{project.name}</h1>
                <span className="rounded-full bg-cyan/15 px-2.5 py-0.5 text-[11px] font-medium text-cyan">
                  Ativo
                </span>
              </div>
              <p className="mt-0.5 text-xs text-slate-500">
                Criado em {fmtDate(project.created_at)} · {project.audience}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={handleDeleteProject}
            className="inline-flex items-center gap-1.5 rounded-lg border border-rose-400/20 bg-rose-500/10 px-3 py-1.5 text-xs text-rose-300 transition hover:bg-rose-500/20"
          >
            <Trash2 size={12} /> Remover
          </button>
        </div>

        {/* Tabs */}
        <div className="mt-4 flex gap-1 overflow-x-auto">
          {TABS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              type="button"
              onClick={() => setActiveTab(id)}
              className={[
                'inline-flex shrink-0 items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm transition',
                activeTab === id
                  ? 'bg-cyan/15 text-cyan'
                  : 'text-slate-400 hover:bg-white/5 hover:text-white',
              ].join(' ')}
            >
              <Icon size={14} />
              {label}
            </button>
          ))}
        </div>
      </header>

      {/* ── Tab Content ── */}
      <div className="flex-1 overflow-y-auto px-6 py-6">
        {activeTab === 'overview' && (
          <OverviewPanel
            project={project}
            campaignResult={campaignResult}
            copyHistory={copyHistory}
            briefResult={briefResult}
            onGoTo={setActiveTab}
          />
        )}
        {activeTab === 'campaign' && (
          <CampaignPanel
            project={project}
            result={campaignResult}
            onResult={setCampaignResult}
          />
        )}
        {activeTab === 'copy' && (
          <CopyPanel
            project={project}
            history={copyHistory}
            onHistory={setCopyHistory}
          />
        )}
        {activeTab === 'brief' && (
          <BriefPanel
            project={project}
            brief={briefResult}
            onBrief={setBriefResult}
          />
        )}
        {activeTab === 'results' && (
          <ResultsPanel
            campaignResult={campaignResult}
            copyHistory={copyHistory}
            briefResult={briefResult}
          />
        )}
      </div>
    </div>
  );
}

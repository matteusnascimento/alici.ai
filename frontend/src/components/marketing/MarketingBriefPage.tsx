import { Bot, Check, Copy, Edit3, FileText, Loader2, Save, Sparkles, Zap } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { listProjects } from '../../services/marketing.service';
import { generateCampaign } from '../../services/marketing.service';
import type { MarketingProject, MarketingCampaignResult } from '../../types/marketing';

interface BriefModel {
  objetivo: string;
  publico: string;
  tom: string;
  mensagem: string;
  estrategia: string;
}

function mapCampaignToBrief(project: MarketingProject, result: MarketingCampaignResult): BriefModel {
  return {
    objetivo: project.objective || 'Definir objetivo de campanha',
    publico: project.audience || 'Publico a definir',
    tom: project.tone || 'premium',
    mensagem: result.primary_copy || result.campaign_headline || 'Mensagem principal nao definida',
    estrategia: result.secondary_copy || result.positioning_summary || 'Estrategia nao definida',
  };
}

export function MarketingBriefPage() {
  const [searchParams] = useSearchParams();
  const defaultId = searchParams.get('project') ? Number(searchParams.get('project')) : undefined;

  const [projects, setProjects] = useState<MarketingProject[]>([]);
  const [selectedId, setSelectedId] = useState<number | undefined>(defaultId);
  const [result, setResult] = useState<MarketingCampaignResult | null>(null);
  const [brief, setBrief] = useState<BriefModel | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const [saved, setSaved] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    listProjects()
      .then((rows) => setProjects(Array.isArray(rows) ? rows : []))
      .catch(() => setProjects([]));
  }, []);

  const selectedProject = projects.find((p) => p.id === selectedId);

  async function handleGenerate() {
    if (!selectedProject) { setError('Selecione um projeto'); return; }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const r = await generateCampaign({
        business_name: selectedProject.name,
        market_segment: selectedProject.objective,
        target_audience: selectedProject.audience,
        campaign_goal: selectedProject.objective,
        offer: selectedProject.offer,
        tone: selectedProject.tone,
        channel: 'instagram',
        campaign_type: 'awareness',
        budget_range: '',
        call_to_action: '',
      });
      setResult({
        ...r,
        cta_suggestions: Array.isArray(r?.cta_suggestions) ? r.cta_suggestions : [],
      });
      setBrief(mapCampaignToBrief(selectedProject, {
        ...r,
        cta_suggestions: Array.isArray(r?.cta_suggestions) ? r.cta_suggestions : [],
      }));
      setEditing(false);
      setSaved(false);
    } catch {
      setError('Erro ao gerar briefing.');
    } finally {
      setLoading(false);
    }
  }

  function toBriefText(value: BriefModel) {
    return [
      'Briefing gerado',
      '',
      `Objetivo: ${value.objetivo}`,
      `Publico: ${value.publico}`,
      `Tom: ${value.tom}`,
      `Mensagem: ${value.mensagem}`,
      `Estrategia: ${value.estrategia}`,
    ].join('\n');
  }

  function handleCopyBrief() {
    if (!brief) return;
    navigator.clipboard.writeText(toBriefText(brief));
    setCopied(true);
    setTimeout(() => setCopied(false), 1200);
  }

  function handleSaveBrief() {
    if (!brief || !selectedProject) return;
    localStorage.setItem(`axi_marketing_brief_${selectedProject.id}`, JSON.stringify(brief));
    setSaved(true);
    setTimeout(() => setSaved(false), 1500);
  }

  return (
    <div className="mx-auto max-w-7xl px-6 py-8 space-y-8">
      <section className="rounded-3xl border border-cyan-300/20 bg-[radial-gradient(circle_at_12%_25%,rgba(6,182,212,0.2),transparent_40%),linear-gradient(165deg,#051329,#0a2245)] p-6 md:p-8">
        <p className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.28em] text-cyan-200">
          <Sparkles size={14} className="animate-pulse" /> Briefing AI Engine
        </p>
        <h1 className="mt-2 font-display text-4xl text-white md:text-5xl">Briefing estruturado com IA</h1>
        <p className="mt-3 max-w-3xl text-sm text-slate-200 md:text-base">
          Gere um briefing completo com objetivo, publico, tom, mensagem e estrategia para orientar execucao de marketing.
        </p>
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <div className="rounded-3xl border border-white/10 bg-white/5 p-6 space-y-4">
          <p className="text-sm font-semibold text-white">Entrada do briefing</p>
          <select
            value={selectedId ?? ''}
            onChange={(e) => setSelectedId(Number(e.target.value))}
            className="w-full rounded-xl border border-white/10 bg-storm px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan/50"
          >
            <option value="">Selecione um projeto...</option>
            {projects.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>

          {selectedProject ? (
            <div className="rounded-xl border border-white/10 bg-white/5 p-4 text-sm space-y-1">
              <p className="text-slate-400">Publico: <span className="text-white">{selectedProject.audience}</span></p>
              <p className="text-slate-400">Objetivo: <span className="text-white">{selectedProject.objective}</span></p>
              <p className="text-slate-400">Oferta: <span className="text-white">{selectedProject.offer}</span></p>
              <p className="text-slate-400">Tom: <span className="text-white">{selectedProject.tone}</span></p>
              {selectedProject.notes ? <p className="text-slate-400">Notas: <span className="text-white">{selectedProject.notes}</span></p> : null}
            </div>
          ) : null}

          <button
            disabled={!selectedId || loading}
            onClick={handleGenerate}
            className="flex items-center gap-2 rounded-xl bg-cyan px-6 py-2.5 text-sm font-semibold text-ink hover:bg-cyan/90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? <Loader2 size={14} className="animate-spin" /> : <Zap size={14} />}
            Gerar briefing com IA
          </button>
          {error ? <p className="text-xs text-rose-300">{error}</p> : null}
        </div>

        <aside className="rounded-3xl border border-white/10 bg-[linear-gradient(170deg,rgba(255,255,255,0.08),rgba(255,255,255,0.03))] p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Briefing gerado</h2>
            <span className="inline-flex items-center gap-1 rounded-full border border-cyan-300/30 bg-cyan-500/10 px-2.5 py-1 text-xs text-cyan-100">
              <Bot size={12} /> Estruturado
            </span>
          </div>

          {brief ? (
            <>
              <div className="grid gap-3">
                {([
                  ['Objetivo', 'objetivo'],
                  ['Publico', 'publico'],
                  ['Tom de voz', 'tom'],
                  ['Mensagem', 'mensagem'],
                  ['Estrategia', 'estrategia'],
                ] as Array<[string, keyof BriefModel]>).map(([label, field]) => (
                  <div key={field} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                    <p className="text-[11px] uppercase tracking-[0.2em] text-cyan-200">{label}</p>
                    {editing ? (
                      <textarea
                        value={brief[field]}
                        onChange={(e) => setBrief((current) => (current ? { ...current, [field]: e.target.value } : current))}
                        rows={field === 'mensagem' || field === 'estrategia' ? 4 : 2}
                        className="mt-2 w-full rounded-xl border border-white/15 bg-[#0b1328]/80 px-3 py-2 text-sm text-white resize-none focus:outline-none focus:border-cyan/50"
                      />
                    ) : (
                      <p className="mt-2 text-sm text-slate-200 whitespace-pre-wrap">{brief[field]}</p>
                    )}
                  </div>
                ))}
              </div>

              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={handleCopyBrief}
                  className="inline-flex items-center gap-2 rounded-xl border border-white/20 px-3 py-2 text-xs font-semibold text-slate-100 hover:bg-white/10"
                >
                  {copied ? <Check size={13} /> : <Copy size={13} />} Copiar
                </button>
                <button
                  type="button"
                  onClick={() => setEditing((value) => !value)}
                  className="inline-flex items-center gap-2 rounded-xl border border-white/20 px-3 py-2 text-xs font-semibold text-slate-100 hover:bg-white/10"
                >
                  <Edit3 size={13} /> {editing ? 'Finalizar edicao' : 'Editar'}
                </button>
                <button
                  type="button"
                  onClick={handleSaveBrief}
                  className="inline-flex items-center gap-2 rounded-xl bg-cyan px-3 py-2 text-xs font-semibold text-ink hover:bg-cyan/90"
                >
                  {saved ? <Check size={13} /> : <Save size={13} />} {saved ? 'Salvo' : 'Salvar'}
                </button>
              </div>
            </>
          ) : (
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-300">
              Selecione um projeto e gere o briefing para visualizar a estrutura completa.
            </div>
          )}

          {result?.creative_suggestion ? (
            <div className="rounded-2xl border border-emerald-300/20 bg-emerald-500/10 p-4">
              <p className="text-[11px] uppercase tracking-[0.2em] text-emerald-200">Insight criativo</p>
              <p className="mt-2 text-sm text-emerald-100">{result.creative_suggestion}</p>
            </div>
          ) : null}
        </aside>
      </section>
    </div>
  );
}

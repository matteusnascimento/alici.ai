import { FileText, Loader2, Zap } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { listProjects } from '../../services/marketing.service';
import { generateCampaign } from '../../services/marketing.service';
import type { MarketingProject, MarketingCampaignResult } from '../../types/marketing';

export function MarketingBriefPage() {
  const [searchParams] = useSearchParams();
  const defaultId = searchParams.get('project') ? Number(searchParams.get('project')) : undefined;

  const [projects, setProjects] = useState<MarketingProject[]>([]);
  const [selectedId, setSelectedId] = useState<number | undefined>(defaultId);
  const [result, setResult] = useState<MarketingCampaignResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
    } catch {
      setError('Erro ao gerar briefing.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-8 space-y-8">
      <div className="flex items-center gap-3">
        <FileText size={20} className="text-cyan" />
        <h1 className="text-xl font-semibold text-white">Gerador de Briefing</h1>
      </div>

      <div className="rounded-2xl border border-white/10 bg-white/5 p-6 space-y-4">
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

        {selectedProject && (
          <div className="rounded-xl border border-white/10 bg-white/5 p-4 text-sm space-y-1">
            <p className="text-slate-400">Público: <span className="text-white">{selectedProject.audience}</span></p>
            <p className="text-slate-400">Objetivo: <span className="text-white">{selectedProject.objective}</span></p>
            <p className="text-slate-400">Oferta: <span className="text-white">{selectedProject.offer}</span></p>
            <p className="text-slate-400">Tom: <span className="text-white">{selectedProject.tone}</span></p>
            {selectedProject.notes && <p className="text-slate-400">Notas: <span className="text-white">{selectedProject.notes}</span></p>}
          </div>
        )}

        <button
          disabled={!selectedId || loading}
          onClick={handleGenerate}
          className="flex items-center gap-2 rounded-xl bg-cyan px-6 py-2.5 text-sm font-semibold text-ink hover:bg-cyan/90 disabled:opacity-50"
        >
          {loading ? <Loader2 size={14} className="animate-spin" /> : <Zap size={14} />}
          Gerar Briefing Completo
        </button>
        {error && <p className="text-xs text-red-400">{error}</p>}
      </div>

      {result && (
        <section className="space-y-4">
          <h2 className="text-sm uppercase tracking-[0.25em] text-slate-400">Briefing Gerado</h2>
          {[
            { label: 'Proposta de Campanha', value: result.campaign_headline },
            { label: 'Copy Principal', value: result.primary_copy },
            { label: 'Estrutura do Anúncio', value: result.secondary_copy },
            { label: 'CTAs Sugeridos', value: result.cta_suggestions.join(' | ') },
            { label: 'Posicionamento', value: result.positioning_summary },
            { label: 'Ângulo da Oferta', value: result.offer_angle },
            { label: 'Sugestão Criativa', value: result.creative_suggestion },
          ].map(({ label, value }) => value ? (
            <div key={label} className="rounded-2xl border border-white/10 bg-white/5 p-5">
              <p className="mb-1 text-xs text-cyan uppercase tracking-wider">{label}</p>
              <p className="text-sm text-slate-200 whitespace-pre-wrap">{value}</p>
            </div>
          ) : null)}
        </section>
      )}
    </div>
  );
}

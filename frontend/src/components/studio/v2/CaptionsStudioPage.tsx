import { useState } from 'react';

import { useStudioV2 } from '../../../hooks/useStudioV2';
import { useToast } from '../../../hooks/useToast';
import { studioCaptionGenerate, studioCopyGenerate, studioCtaGenerate } from '../../../services/studio.service';
import { StudioCanvas } from './StudioCanvas';
import { StudioInspectorPanel } from './StudioInspectorPanel';
import { StudioShell } from './StudioShell';

interface CaptionsStudioPageProps {
  mode?: 'caption' | 'cta' | 'promo';
}

export function CaptionsStudioPage({ mode = 'caption' }: CaptionsStudioPageProps) {
  const workspaceTitle = mode === 'cta' ? 'Gerador de CTA' : mode === 'promo' ? 'Texto Promocional' : 'Gerar Legenda';
  const studioType = mode === 'cta' ? 'cta-generator' : mode === 'promo' ? 'promo-copy' : 'caption-generator';
  const studio = useStudioV2({ defaultType: studioType, defaultTitle: workspaceTitle });
  const { pushToast } = useToast();
  const [campaignContext, setCampaignContext] = useState('Campanha de lancamento de curso online para iniciantes em IA.');
  const [channel, setChannel] = useState('instagram');
  const [tone, setTone] = useState('persuasivo');
  const [variations, setVariations] = useState(3);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ captions: string[]; cta: string; hashtags: string[] } | null>(null);
  const [status, setStatus] = useState<string | null>(null);

  async function handleGenerate() {
    if (!campaignContext.trim()) {
      pushToast('Informe um contexto de campanha antes de gerar.', 'warning');
      return;
    }

    setLoading(true);
    setStatus('Processando IA...');
    pushToast('Geracao iniciada. Aguarde o processamento.', 'info');
    try {
      const payload = {
        project_id: studio.currentProject?.id,
        campaign_context: campaignContext,
        channel,
        tone,
        include_cta: true,
        include_hashtags: true,
        variations,
      };
      const response = mode === 'cta' ? await studioCtaGenerate(payload) : mode === 'promo' ? await studioCopyGenerate(payload) : await studioCaptionGenerate(payload);
      setResult({
        captions: (response.result.captions as string[]) || [],
        cta: (response.result.cta as string) || '',
        hashtags: (response.result.hashtags as string[]) || [],
      });
      setStatus('Conteudo gerado com sucesso.');
      studio.setSaveState('dirty');
      pushToast('Conteudo gerado com IA.', 'success');
    } catch (err) {
      setStatus(err instanceof Error ? err.message : 'Falha ao gerar conteudo.');
      pushToast('Falha ao gerar conteudo com IA.', 'error');
    } finally {
      setLoading(false);
    }
  }

  return (
    <StudioShell
      projectName={studio.projectName}
      saveState={loading ? 'saving' : studio.saveState}
      onSave={() => void studio.saveProject({ status: 'saved', metadata: { campaignContext, channel, tone, variations } })}
      onExport={() => void studio.exportProject('pdf')}
      center={(
        <StudioCanvas title={workspaceTitle} subtitle="Formulario de contexto com IA para texto principal, CTA, hashtags e variacoes">
          <div className="space-y-3 rounded-2xl border border-white/10 bg-black/25 p-4">
            <button type="button" onClick={() => void handleGenerate()} disabled={loading} className="rounded-xl bg-cyan px-4 py-2 text-sm font-semibold text-ink disabled:opacity-70" title="Gera conteudo no backend com IA">
              {loading ? 'Gerando copy...' : 'Gerar conteudo'}
            </button>
            {status ? <p className="text-xs text-cyan-100">{status}</p> : null}
            {!result && !loading ? (
              <div className="rounded-xl border border-dashed border-white/20 bg-black/20 p-3 text-xs text-slate-300">
                <p className="font-semibold text-white">Fluxo sugerido</p>
                <p className="mt-1">1. Defina contexto, canal, tom e variacoes.</p>
                <p>2. Gere a primeira versao e refine no prompt.</p>
                <p>3. Salve e exporte para manter historico do workspace.</p>
              </div>
            ) : null}
            <div className="space-y-2">
              {(result?.captions || []).map((caption, index) => (
                <p key={`${caption}-${index}`} className="rounded-xl border border-white/10 bg-black/20 p-3 text-sm text-slate-200">{caption}</p>
              ))}
            </div>
            {result?.cta ? <p className="rounded-xl border border-white/10 bg-black/20 p-3 text-sm text-white">CTA: {result.cta}</p> : null}
            {result?.hashtags && result.hashtags.length > 0 ? <p className="rounded-xl border border-white/10 bg-black/20 p-3 text-sm text-slate-300">{result.hashtags.join(' ')}</p> : null}
          </div>
        </StudioCanvas>
      )}
      right={(
        <StudioInspectorPanel title="Contexto da campanha">
          <label className="text-xs text-slate-400">Contexto</label>
          <textarea value={campaignContext} onChange={(event) => setCampaignContext(event.target.value)} className="min-h-32 w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white" />
          <label className="text-xs text-slate-400">Canal</label>
          <input value={channel} onChange={(event) => setChannel(event.target.value)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white" />
          <label className="text-xs text-slate-400">Tom</label>
          <input value={tone} onChange={(event) => setTone(event.target.value)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white" />
          <label className="text-xs text-slate-400">Variacoes</label>
          <input type="number" min={1} max={6} value={variations} onChange={(event) => setVariations(Number(event.target.value) || 1)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white" />
        </StudioInspectorPanel>
      )}
    />
  );
}

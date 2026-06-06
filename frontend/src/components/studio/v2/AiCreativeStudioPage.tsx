import { Clock3, Image, Sparkles } from 'lucide-react';
import { useState } from 'react';

import { useStudioV2 } from '../../../hooks/useStudioV2';
import { useToast } from '../../../hooks/useToast';
import { studioAICreativeGenerate } from '../../../services/studio.service';
import { StudioCanvas } from './StudioCanvas';
import { StudioInspectorPanel } from './StudioInspectorPanel';
import { StudioShell } from './StudioShell';

const creativeActions = ['Campanha', 'Headline', 'CTA', 'Legenda', 'Copy Promocional', 'Formato de Criativo'];
const promptExamples = [
  'Gerar campanha para produto premium com criativo vertical 9:16.',
  'Criar headline curta para oferta relampago de consultoria.',
  'Transformar briefing em roteiro UGC com gancho nos 3 primeiros segundos.',
];

export function AiCreativeStudioPage() {
  const studio = useStudioV2({ defaultType: 'ai-creative', defaultTitle: 'IA Criativa' });
  const toast = useToast();
  const [briefing, setBriefing] = useState('Produto: consultoria para e-commerce local. Objetivo: gerar mais leads em 14 dias.');
  const [action, setAction] = useState(creativeActions[0]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<Array<{ action: string; briefing: string }>>([]);

  async function runCreativeAssistant() {
    if (!briefing.trim()) {
      toast.warning('Preencha o briefing antes de gerar.');
      return;
    }

    setLoading(true);
    toast.info('Geracao criativa iniciada.');
    try {
      const response = await studioAICreativeGenerate({
        project_id: studio.currentProject?.id,
        action,
        briefing,
      });
      setResult(response.result);
      setHistory((current) => [{ action, briefing }, ...current].slice(0, 5));
      setError(null);
      studio.setSaveState('dirty');
      toast.success('Conteudo de IA criativa gerado com sucesso.');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao executar IA criativa.');
      toast.error('Falha de API ao executar IA criativa.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <StudioShell
      projectName={studio.projectName}
      saveState={loading ? 'saving' : studio.saveState}
      onSave={() => void studio.saveProject({ status: 'saved', metadata: { action, briefing }, canvas_data: { result } })}
      onExport={() => void studio.exportProject('pdf')}
      center={(
        <StudioCanvas title="IA Criativa" subtitle="Transforme briefing em ideia, copy e estrutura de criativo sem expor chaves no frontend.">
          <div className="grid h-full gap-4 lg:grid-cols-[220px_minmax(0,1fr)]">
            <aside className="rounded-2xl border border-white/10 bg-black/25 p-4">
              <p className="text-[11px] font-bold uppercase tracking-[0.22em] text-cyan-300">Historico</p>
              <div className="mt-4 space-y-2">
                {(history.length ? history : [{ action: 'Sem geracoes', briefing: 'Execute a IA para salvar o historico desta sessao.' }]).map((item, index) => (
                  <div key={`${item.action}-${index}`} className="rounded-xl border border-white/10 bg-white/[0.035] p-3 text-xs text-slate-300">
                    <div className="flex items-center gap-2 text-white">
                      <Clock3 size={13} /> {item.action}
                    </div>
                    <p className="mt-1 line-clamp-2">{item.briefing}</p>
                  </div>
                ))}
              </div>
            </aside>
            <div className="space-y-3 rounded-2xl border border-white/10 bg-black/25 p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <p className="text-sm text-slate-300">A IA sugere estrategia, headline, CTA e formatos de criativo com base no briefing.</p>
                <button type="button" onClick={() => void runCreativeAssistant()} disabled={loading} className="inline-flex items-center gap-2 rounded-xl bg-[var(--studio-gradient)] px-4 py-2 text-sm font-bold text-white disabled:opacity-70" title="Executa a IA criativa no backend">
                  <Sparkles size={16} /> {loading ? 'Gerando...' : 'Executar IA'}
                </button>
              </div>
            {error ? <p className="text-sm text-coral">{error}</p> : null}
            {result ? (
              <div className="grid gap-3 md:grid-cols-[minmax(0,1fr)_220px]">
                <pre className="max-h-[330px] overflow-auto rounded-xl border border-white/10 bg-black/30 p-3 text-xs text-slate-200">{JSON.stringify(result, null, 2)}</pre>
                <div className="grid grid-cols-2 gap-2 md:grid-cols-1">
                  {[1, 2].map((item) => (
                    <div key={item} className="flex min-h-[120px] items-center justify-center rounded-xl border border-white/10 bg-[radial-gradient(circle_at_20%_10%,rgba(192,38,211,0.34),transparent_38%),linear-gradient(135deg,rgba(34,211,238,0.18),rgba(255,255,255,0.04))]">
                      <Image className="h-8 w-8 text-white/70" />
                    </div>
                  ))}
                </div>
              </div>
            ) : null}
            {!result && !loading ? (
              <div className="rounded-xl border border-dashed border-fuchsia-300/25 bg-black/20 p-5 text-xs text-slate-400">
                <p className="font-semibold text-white">Sem geracao ainda</p>
                <p className="mt-1">1. Defina acao e briefing.</p>
                <p>2. Execute a IA e revise o resultado.</p>
                <p>3. Salve e exporte para distribuir.</p>
              </div>
            ) : null}
            </div>
          </div>
        </StudioCanvas>
      )}
      right={(
        <StudioInspectorPanel title="Assistente Interno">
          <label className="text-xs text-slate-400">Acao</label>
          <select value={action} onChange={(event) => setAction(event.target.value)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white">
            {creativeActions.map((item) => (
              <option key={item} value={item}>{item}</option>
            ))}
          </select>
          <label className="text-xs text-slate-400">Briefing</label>
          <textarea value={briefing} onChange={(event) => setBriefing(event.target.value)} className="min-h-48 w-full rounded-xl border border-white/10 bg-black/30 px-3 py-2 text-sm text-white outline-none focus:border-cyan-300/45" />
          <div className="space-y-2">
            {promptExamples.map((example) => (
              <button key={example} type="button" onClick={() => setBriefing(example)} className="w-full rounded-xl border border-white/10 bg-white/[0.035] px-3 py-2 text-left text-xs text-slate-300 hover:border-cyan-300/35 hover:text-white">
                {example}
              </button>
            ))}
          </div>
        </StudioInspectorPanel>
      )}
      bottom={<div className="rounded-2xl border border-white/10 bg-white/5 p-3 text-xs text-slate-400">Dica: quanto mais claro o briefing, melhor a qualidade das sugestoes da IA.</div>}
    />
  );
}

import { useState } from 'react';

import { useToast } from '../../../hooks/useToast';
import { studioAICreativeGenerate } from '../../../services/studio.service';
import { StudioCanvas } from './StudioCanvas';
import { StudioInspectorPanel } from './StudioInspectorPanel';
import { StudioShell } from './StudioShell';

const creativeActions = ['Campanha', 'Headline', 'CTA', 'Legenda', 'Copy Promocional', 'Formato de Criativo'];

export function AiCreativeStudioPage() {
  const toast = useToast();
  const [briefing, setBriefing] = useState('Produto: consultoria para e-commerce local. Objetivo: gerar mais leads em 14 dias.');
  const [action, setAction] = useState(creativeActions[0]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function runCreativeAssistant() {
    setLoading(true);
    try {
      const response = await studioAICreativeGenerate({
        action,
        briefing,
      });
      setResult(response.result);
      setError(null);
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
      projectName="IA Criativa"
      saveState={loading ? 'saving' : 'saved'}
      onSave={() => undefined}
      onExport={() => undefined}
      center={(
        <StudioCanvas title="IA Criativa" subtitle="Transforme briefing em ideia, copy e estrutura de criativo sem expor chaves no frontend.">
          <div className="space-y-3 rounded-2xl border border-white/10 bg-black/25 p-4">
            <p className="text-sm text-slate-300">A IA sugere estrategia, headline, CTA e formatos de criativo com base no briefing.</p>
            <button type="button" onClick={() => void runCreativeAssistant()} disabled={loading} className="rounded-xl bg-cyan px-4 py-2 text-sm font-semibold text-ink disabled:opacity-70" title="Executa a IA criativa no backend">
              {loading ? 'Gerando...' : 'Executar IA Criativa'}
            </button>
            {error ? <p className="text-sm text-coral">{error}</p> : null}
            {result ? <pre className="overflow-auto rounded-xl border border-white/10 bg-black/30 p-3 text-xs text-slate-200">{JSON.stringify(result, null, 2)}</pre> : null}
            {!result && !loading ? <p className="text-xs text-slate-400">Descreva seu briefing e clique em executar para comecar.</p> : null}
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
          <textarea value={briefing} onChange={(event) => setBriefing(event.target.value)} className="min-h-40 w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white" />
        </StudioInspectorPanel>
      )}
      bottom={<div className="rounded-2xl border border-white/10 bg-white/5 p-3 text-xs text-slate-400">Dica: quanto mais claro o briefing, melhor a qualidade das sugestoes da IA.</div>}
    />
  );
}

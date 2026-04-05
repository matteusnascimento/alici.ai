import { useNavigate } from 'react-router-dom';

import { useStudioWorkspace } from '../../../hooks/useStudioWorkspace';
import { generateTeleprompter } from '../../../services/studioService';
import type { TeleprompterInput, TeleprompterOutput } from '../../../types/studio';
import { EmptyState } from '../EmptyState';
import { OutputPanel } from '../OutputPanel';
import { ToolFormSection } from '../ToolFormSection';
import { ToolResultSection } from '../ToolResultSection';
import { WorkspaceActions } from '../WorkspaceActions';

const defaultInput: TeleprompterInput = {
  scriptText: '',
  readingSpeedWpm: 130,
  sections: 'intro, desenvolvimento, fechamento',
  recordingMode: 'camera frontal',
};

export function TeleprompterWorkspace() {
  const navigate = useNavigate();
  const { input, setInput, output, setOutput, loading, beginLoading, endLoading, error, markError, saveCurrentProject, resetWorkspace } =
    useStudioWorkspace<TeleprompterInput, TeleprompterOutput>({
      toolType: 'teleprompter',
      route: '/app/studio/teleprompter',
      emptyInput: defaultInput,
      emptyOutput: null,
    });

  async function run() {
    if (!input.scriptText.trim()) {
      markError('Informe o texto do roteiro.');
      return;
    }
    beginLoading();
    try {
      setOutput(await generateTeleprompter(input));
    } finally {
      endLoading();
    }
  }

  return (
    <div className="space-y-4">
      <button type="button" onClick={() => navigate('/app/studio')} className="text-sm text-cyan">← Voltar para AXI Studio</button>
      <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
        <ToolFormSection title="Teleprompter" subtitle="Edite roteiro, velocidade e modo de gravacao.">
          <label className="block space-y-2 text-sm text-slate-300">
            <span>Script text</span>
            <textarea value={input.scriptText} onChange={(e) => setInput((c) => ({ ...c, scriptText: e.target.value }))} className="h-48 w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white" />
          </label>
          <label className="block space-y-2 text-sm text-slate-300">
            <span>Reading speed (wpm)</span>
            <input type="number" min={80} max={220} value={input.readingSpeedWpm} onChange={(e) => setInput((c) => ({ ...c, readingSpeedWpm: Number(e.target.value) }))} className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white" />
          </label>
          <label className="block space-y-2 text-sm text-slate-300">
            <span>Sections</span>
            <input value={input.sections} onChange={(e) => setInput((c) => ({ ...c, sections: e.target.value }))} className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white" />
          </label>
          <label className="block space-y-2 text-sm text-slate-300">
            <span>Recording mode</span>
            <input value={input.recordingMode} onChange={(e) => setInput((c) => ({ ...c, recordingMode: e.target.value }))} className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white" />
          </label>
          <WorkspaceActions onGenerate={run} onRegenerate={run} onSave={() => saveCurrentProject('Teleprompter', input.recordingMode, output?.formattedScriptBlocks[0] || 'Teleprompter')} onReset={resetWorkspace} loading={loading} />
          {error ? <p className="text-sm text-coral">{error}</p> : null}
        </ToolFormSection>
        <ToolResultSection title="Teleprompter output" subtitle="Script formatado, blocos segmentados e estimativa de tempo.">
          {!output ? <EmptyState title="Sem output" description="Gere o teleprompter para visualizar os blocos de leitura." /> : <div className="grid gap-3"><OutputPanel title="Formatted script" lines={output.formattedScriptBlocks} /><OutputPanel title="Segmented reading" lines={output.segmentedReadingBlocks} /><OutputPanel title="Timing estimate" lines={[`${output.timingEstimateMinutes} min`]} /></div>}
        </ToolResultSection>
      </div>
    </div>
  );
}

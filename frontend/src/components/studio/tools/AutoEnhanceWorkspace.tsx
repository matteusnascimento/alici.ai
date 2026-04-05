import { useNavigate } from 'react-router-dom';

import { useStudioWorkspace } from '../../../hooks/useStudioWorkspace';
import { autoEnhanceImage } from '../../../services/studioService';
import type { AutoEnhanceInput, AutoEnhanceOutput } from '../../../types/studio';
import { EmptyState } from '../EmptyState';
import { OutputPanel } from '../OutputPanel';
import { ToolFormSection } from '../ToolFormSection';
import { ToolResultSection } from '../ToolResultSection';
import { UploadZone } from '../UploadZone';
import { WorkspaceActions } from '../WorkspaceActions';

const defaultInput: AutoEnhanceInput = {
  uploads: [],
  enhancementMode: 'balanced',
  outputSize: '1080x1080',
};

export function AutoEnhanceWorkspace() {
  const navigate = useNavigate();
  const { input, setInput, output, setOutput, loading, beginLoading, endLoading, error, markError, saveCurrentProject, resetWorkspace } =
    useStudioWorkspace<AutoEnhanceInput, AutoEnhanceOutput>({
      toolType: 'auto-enhance',
      route: '/app/studio/auto-enhance',
      emptyInput: defaultInput,
      emptyOutput: null,
    });

  async function run() {
    if (!input.uploads.length) {
      markError('Envie uma imagem para aprimorar.');
      return;
    }
    beginLoading();
    try {
      setOutput(await autoEnhanceImage(input));
    } finally {
      endLoading();
    }
  }

  return (
    <div className="space-y-4">
      <button type="button" onClick={() => navigate('/app/studio')} className="text-sm text-cyan">← Voltar para AXI Studio</button>
      <div className="grid gap-6 xl:grid-cols-[360px_1fr]">
        <ToolFormSection title="Aprimorar Automaticamente" subtitle="One-click enhancement com comparativo de resultado.">
          <UploadZone label="Upload de imagem para aprimorar" onSelect={(files) => setInput((c) => ({ ...c, uploads: Array.from(files || []).map((f) => ({ name: f.name, size: f.size, type: f.type })) }))} />
          <label className="block space-y-2 text-sm text-slate-300">
            <span>Enhancement mode</span>
            <input value={input.enhancementMode} onChange={(e) => setInput((c) => ({ ...c, enhancementMode: e.target.value }))} className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white" />
          </label>
          <label className="block space-y-2 text-sm text-slate-300">
            <span>Output size</span>
            <input value={input.outputSize} onChange={(e) => setInput((c) => ({ ...c, outputSize: e.target.value }))} className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white" />
          </label>
          <WorkspaceActions onGenerate={run} onRegenerate={run} onSave={() => saveCurrentProject('Auto Enhance', input.enhancementMode, output?.processedPreview || 'Auto enhance')} onReset={resetWorkspace} loading={loading} />
          {error ? <p className="text-sm text-coral">{error}</p> : null}
        </ToolFormSection>

        <ToolResultSection title="Enhancement result" subtitle="Resumo de melhorias aplicadas e comparativo visual.">
          {!output ? (
            <EmptyState title="Sem resultado" description="Execute o aprimoramento para visualizar o resultado." />
          ) : (
            <div className="grid gap-3">
              <div className="grid gap-3 md:grid-cols-2">
                <div className="min-h-[240px] rounded-2xl border border-white/10 bg-ink/50 p-4">Before</div>
                <div className="min-h-[240px] rounded-2xl border border-cyan/30 bg-cyan/10 p-4 text-cyan">After: {output.processedPreview}</div>
              </div>
              <OutputPanel title="Enhancements applied" lines={output.enhancementsApplied} />
            </div>
          )}
        </ToolResultSection>
      </div>
    </div>
  );
}

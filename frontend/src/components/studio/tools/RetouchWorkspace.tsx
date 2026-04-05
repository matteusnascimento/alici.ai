import { useNavigate } from 'react-router-dom';

import { useStudioWorkspace } from '../../../hooks/useStudioWorkspace';
import { retouchImage } from '../../../services/studioService';
import type { RetouchInput, RetouchOutput } from '../../../types/studio';
import { EmptyState } from '../EmptyState';
import { ToolFormSection } from '../ToolFormSection';
import { ToolResultSection } from '../ToolResultSection';
import { UploadZone } from '../UploadZone';
import { WorkspaceActions } from '../WorkspaceActions';

const defaultInput: RetouchInput = {
  uploads: [],
  retouchMode: 'skin polish',
  intensity: 40,
  cleanupMode: 'general polish',
};

export function RetouchWorkspace() {
  const navigate = useNavigate();
  const { input, setInput, output, setOutput, loading, beginLoading, endLoading, error, markError, saveCurrentProject, resetWorkspace } =
    useStudioWorkspace<RetouchInput, RetouchOutput>({
      toolType: 'retouch',
      route: '/app/studio/retouch',
      emptyInput: defaultInput,
      emptyOutput: null,
    });

  async function run() {
    if (!input.uploads.length) {
      markError('Envie uma imagem para retoque.');
      return;
    }
    beginLoading();
    try {
      setOutput(await retouchImage(input));
    } finally {
      endLoading();
    }
  }

  return (
    <div className="space-y-4">
      <button type="button" onClick={() => navigate('/app/studio')} className="text-sm text-cyan">← Voltar para AXI Studio</button>
      <div className="grid gap-6 xl:grid-cols-[360px_1fr]">
        <ToolFormSection title="Retoque" subtitle="Ajuste modo de retoque, intensidade e limpeza.">
          <UploadZone
            label="Upload de imagem para retoque"
            onSelect={(files) => setInput((current) => ({ ...current, uploads: Array.from(files || []).map((f) => ({ name: f.name, size: f.size, type: f.type })) }))}
          />
          <label className="block space-y-2 text-sm text-slate-300">
            <span>Retouch mode</span>
            <input value={input.retouchMode} onChange={(e) => setInput((c) => ({ ...c, retouchMode: e.target.value }))} className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white" />
          </label>
          <label className="block space-y-2 text-sm text-slate-300">
            <span>Intensity ({input.intensity})</span>
            <input type="range" min={0} max={100} value={input.intensity} onChange={(e) => setInput((c) => ({ ...c, intensity: Number(e.target.value) }))} className="w-full" />
          </label>
          <label className="block space-y-2 text-sm text-slate-300">
            <span>Cleanup mode</span>
            <input value={input.cleanupMode} onChange={(e) => setInput((c) => ({ ...c, cleanupMode: e.target.value }))} className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white" />
          </label>
          <WorkspaceActions onGenerate={run} onRegenerate={run} onSave={() => saveCurrentProject('Retouch', input.retouchMode, output?.beforeAfterSummary || 'Retoque')} onReset={resetWorkspace} loading={loading} />
          {error ? <p className="text-sm text-coral">{error}</p> : null}
        </ToolFormSection>

        <ToolResultSection title="Before / After" subtitle="Comparativo de retoque e historico de ajustes.">
          {!output ? (
            <EmptyState title="Sem comparativo" description="Aplique o retoque para gerar resultado before/after." />
          ) : (
            <div className="grid gap-3 md:grid-cols-2">
              <div className="min-h-[260px] rounded-2xl border border-white/10 bg-ink/50 p-4 text-slate-200">Before</div>
              <div className="min-h-[260px] rounded-2xl border border-cyan/30 bg-cyan/10 p-4 text-cyan">After: {output.processedPreview}</div>
              <div className="md:col-span-2 rounded-2xl border border-white/10 bg-ink/40 p-4 text-sm text-slate-100">{output.beforeAfterSummary}</div>
            </div>
          )}
        </ToolResultSection>
      </div>
    </div>
  );
}

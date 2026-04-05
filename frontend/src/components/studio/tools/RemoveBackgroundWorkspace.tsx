import { useNavigate } from 'react-router-dom';

import { useStudioWorkspace } from '../../../hooks/useStudioWorkspace';
import { removeBackground } from '../../../services/studioService';
import type { RemoveBackgroundInput, RemoveBackgroundOutput } from '../../../types/studio';
import { EmptyState } from '../EmptyState';
import { ToolFormSection } from '../ToolFormSection';
import { ToolResultSection } from '../ToolResultSection';
import { UploadZone } from '../UploadZone';
import { WorkspaceActions } from '../WorkspaceActions';

const defaultInput: RemoveBackgroundInput = { uploads: [] };

export function RemoveBackgroundWorkspace() {
  const navigate = useNavigate();
  const { input, setInput, output, setOutput, loading, beginLoading, endLoading, error, markError, saveCurrentProject, resetWorkspace } =
    useStudioWorkspace<RemoveBackgroundInput, RemoveBackgroundOutput>({
      toolType: 'remove-background',
      route: '/app/studio/remove-background',
      emptyInput: defaultInput,
      emptyOutput: null,
    });

  async function run() {
    if (!input.uploads.length) {
      markError('Envie ao menos uma imagem.');
      return;
    }
    beginLoading();
    try {
      setOutput(await removeBackground(input));
    } finally {
      endLoading();
    }
  }

  return (
    <div className="space-y-4">
      <button type="button" onClick={() => navigate('/app/studio')} className="text-sm text-cyan">← Voltar para AXI Studio</button>
      <div className="grid gap-6 xl:grid-cols-[360px_1fr]">
        <ToolFormSection title="Remover Fundo" subtitle="Fluxo rapido para recorte e export com fundo transparente.">
          <UploadZone
            label="Upload de imagem"
            onSelect={(files) =>
              setInput({ uploads: Array.from(files || []).map((file) => ({ name: file.name, size: file.size, type: file.type })) })
            }
          />
          <p className="text-xs text-slate-400">Arquivos: {input.uploads.map((item) => item.name).join(', ') || 'nenhum'}</p>
          <WorkspaceActions
            onGenerate={run}
            onRegenerate={run}
            onSave={() => saveCurrentProject('Remove Background', 'Fluxo de recorte', output?.summary || 'Recorte')}
            onExport={() => output && navigator.clipboard.writeText(output.summary)}
            onReset={resetWorkspace}
            loading={loading}
          />
          {error ? <p className="text-sm text-coral">{error}</p> : null}
        </ToolFormSection>

        <ToolResultSection title="Resultado" subtitle="Preview original, preview processado e estado de exportacao.">
          {!output ? (
            <EmptyState title="Sem processamento" description="Carregue uma imagem e execute o processamento para visualizar o resultado." />
          ) : (
            <div className="grid gap-3 md:grid-cols-2">
              <div className="min-h-[260px] rounded-2xl border border-white/10 bg-ink/50 p-4 text-sm text-slate-200">Preview original</div>
              <div className="min-h-[260px] rounded-2xl border border-cyan/30 bg-cyan/10 p-4 text-sm text-cyan">{output.processedPreview}</div>
            </div>
          )}
        </ToolResultSection>
      </div>
    </div>
  );
}

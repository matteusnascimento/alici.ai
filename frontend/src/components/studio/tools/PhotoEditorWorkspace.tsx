import { useNavigate } from 'react-router-dom';

import { useStudioWorkspace } from '../../../hooks/useStudioWorkspace';
import { applyPhotoEdit } from '../../../services/studioService';
import type { PhotoEditorInput, PhotoEditorOutput } from '../../../types/studio';
import { EmptyState } from '../EmptyState';
import { OutputPanel } from '../OutputPanel';
import { ToolFormSection } from '../ToolFormSection';
import { ToolResultSection } from '../ToolResultSection';
import { UploadZone } from '../UploadZone';
import { WorkspaceActions } from '../WorkspaceActions';

const tools = ['remove background', 'crop', 'resize', 'enhance', 'retouch', 'lighting', 'cleanup'];

const defaultInput: PhotoEditorInput = {
  uploads: [],
  selectedTool: tools[0],
  settings: { intensity: 50, size: '1080x1080', keepRatio: true },
};

export function PhotoEditorWorkspace() {
  const navigate = useNavigate();
  const { input, setInput, output, setOutput, loading, beginLoading, endLoading, error, markError, saveCurrentProject, resetWorkspace } =
    useStudioWorkspace<PhotoEditorInput, PhotoEditorOutput>({
      toolType: 'photo-editor',
      route: '/app/studio/photo-editor',
      emptyInput: defaultInput,
      emptyOutput: null,
    });

  async function run() {
    if (!input.uploads.length) {
      markError('Envie pelo menos uma imagem para editar.');
      return;
    }
    beginLoading();
    try {
      setOutput(await applyPhotoEdit(input));
    } finally {
      endLoading();
    }
  }

  return (
    <div className="space-y-4">
      <button type="button" onClick={() => navigate('/app/studio')} className="text-sm text-cyan">← Voltar para AXI Studio</button>
      <div className="grid gap-6 xl:grid-cols-[280px_1fr_320px]">
        <ToolFormSection title="Ferramentas" subtitle="Selecione acao e ajuste parametros.">
          <UploadZone
            label="Upload de imagem para edicao"
            onSelect={(files) =>
              setInput((current) => ({
                ...current,
                uploads: Array.from(files || []).map((file) => ({ name: file.name, size: file.size, type: file.type })),
              }))
            }
          />
          <div className="grid gap-2">
            {tools.map((tool) => (
              <button
                key={tool}
                type="button"
                onClick={() => setInput((current) => ({ ...current, selectedTool: tool }))}
                className={[
                  'rounded-xl border px-3 py-2 text-left text-sm',
                  input.selectedTool === tool ? 'border-cyan/40 bg-cyan/10 text-cyan' : 'border-white/10 text-slate-200',
                ].join(' ')}
              >
                {tool}
              </button>
            ))}
          </div>
        </ToolFormSection>

        <ToolResultSection title="Canvas preview" subtitle="Preview central da edicao selecionada.">
          {!output ? (
            <EmptyState title="Sem preview editado" description="Selecione ferramenta e clique em Gerar para aplicar a edicao." />
          ) : (
            <div className="grid gap-3">
              <div className="min-h-[340px] rounded-2xl border border-white/10 bg-gradient-to-br from-storm/60 to-ink/80 p-4 text-sm text-slate-200">
                {output.processedPreview}
              </div>
              <WorkspaceActions
                onGenerate={run}
                onRegenerate={run}
                onSave={() => saveCurrentProject('Photo Editor', `Tool: ${input.selectedTool}`, output.processedPreview)}
                onReset={resetWorkspace}
                loading={loading}
              />
            </div>
          )}
          {error ? <p className="mt-3 text-sm text-coral">{error}</p> : null}
        </ToolResultSection>

        <ToolResultSection title="History / Settings" subtitle="Historico de acoes e metadata de output.">
          {!output ? <EmptyState title="Historico vazio" description="Aplicacoes de edicao aparecerao aqui." /> : <OutputPanel title="History" lines={output.history} />}
        </ToolResultSection>
      </div>
    </div>
  );
}

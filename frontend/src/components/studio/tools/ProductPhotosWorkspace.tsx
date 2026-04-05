import { useNavigate } from 'react-router-dom';

import { useStudioWorkspace } from '../../../hooks/useStudioWorkspace';
import { generateProductPhotos } from '../../../services/studioService';
import type { ProductPhotosInput, ProductPhotosOutput } from '../../../types/studio';
import { EmptyState } from '../EmptyState';
import { OutputPanel } from '../OutputPanel';
import { ToolFormSection } from '../ToolFormSection';
import { ToolResultSection } from '../ToolResultSection';
import { UploadZone } from '../UploadZone';
import { WorkspaceActions } from '../WorkspaceActions';

const defaultInput: ProductPhotosInput = {
  productType: '',
  visualStyle: 'premium',
  backgroundStyle: 'studio soft',
  outputFormat: '1080x1080',
  platformDestination: 'Instagram',
  prompt: '',
  uploads: [],
};

export function ProductPhotosWorkspace() {
  const navigate = useNavigate();
  const {
    input,
    setInput,
    output,
    setOutput,
    loading,
    beginLoading,
    endLoading,
    error,
    markError,
    clearError,
    saveCurrentProject,
    resetWorkspace,
  } = useStudioWorkspace<ProductPhotosInput, ProductPhotosOutput>({
    toolType: 'product-photos',
    route: '/app/studio/product-photos',
    emptyInput: defaultInput,
    emptyOutput: null,
  });

  async function runGeneration() {
    if (!input.uploads.length || !input.productType || !input.prompt) {
      markError('Adicione imagem, tipo de produto e prompt.');
      return;
    }
    clearError();
    beginLoading();
    try {
      setOutput(await generateProductPhotos(input));
    } catch {
      markError('Falha ao gerar variacoes de fotos.');
    } finally {
      endLoading();
    }
  }

  function handleFiles(files: FileList | null) {
    const uploads = Array.from(files || []).map((file) => ({ name: file.name, size: file.size, type: file.type }));
    setInput((current) => ({ ...current, uploads }));
  }

  function saveProjectNow() {
    const project = saveCurrentProject(
      `Fotos - ${input.productType || 'Produto'}`,
      `Variacoes ${input.visualStyle} para ${input.platformDestination}`,
      output?.previews[0] || 'Fotos do produto',
    );
    if (project) navigate(`/app/studio/product-photos?projectId=${project.id}`, { replace: true });
  }

  return (
    <div className="space-y-4">
      <button type="button" onClick={() => navigate('/app/studio')} className="text-sm text-cyan">← Voltar para AXI Studio</button>
      <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
        <ToolFormSection title="Fotos do Produto" subtitle="Upload, prompt e configuracao de estilo visual.">
          <UploadZone label="Clique para carregar imagens do produto" onSelect={handleFiles} />
          <p className="text-xs text-slate-400">Arquivos: {input.uploads.map((item) => item.name).join(', ') || 'nenhum'}</p>
          {[
            ['productType', 'Product type'],
            ['visualStyle', 'Visual style'],
            ['backgroundStyle', 'Background style'],
            ['outputFormat', 'Output format'],
            ['platformDestination', 'Platform destination'],
            ['prompt', 'Prompt / instructions'],
          ].map(([key, label]) => (
            <label key={key} className="block space-y-2 text-sm text-slate-300">
              <span>{label}</span>
              <input
                value={input[key as keyof ProductPhotosInput] as string}
                onChange={(event) => setInput((current) => ({ ...current, [key]: event.target.value }))}
                className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white outline-none focus:border-cyan"
              />
            </label>
          ))}
          <WorkspaceActions onGenerate={runGeneration} onRegenerate={runGeneration} onSave={saveProjectNow} onReset={resetWorkspace} loading={loading} />
          {error ? <p className="text-sm text-coral">{error}</p> : null}
        </ToolFormSection>

        <ToolResultSection title="Preview e variacoes" subtitle="Saidas mockadas para fluxo de criacao e exportacao.">
          {!output ? (
            <EmptyState title="Sem variacoes geradas" description="Gere resultados para visualizar cards de preview e estilos." />
          ) : (
            <div className="grid gap-3 md:grid-cols-2">
              <OutputPanel title="Previews" lines={output.previews} />
              <OutputPanel title="Style variations" lines={output.styleVariations} />
              <OutputPanel title="Export formats" lines={output.exportFormats} />
            </div>
          )}
        </ToolResultSection>
      </div>
    </div>
  );
}

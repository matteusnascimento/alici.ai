import { useNavigate } from 'react-router-dom';

import { useStudioWorkspace } from '../../../hooks/useStudioWorkspace';
import { generatePoster } from '../../../services/studioService';
import type { PosterInput, PosterOutput } from '../../../types/studio';
import { EmptyState } from '../EmptyState';
import { OutputPanel } from '../OutputPanel';
import { ToolFormSection } from '../ToolFormSection';
import { ToolResultSection } from '../ToolResultSection';
import { WorkspaceActions } from '../WorkspaceActions';

const defaultInput: PosterInput = {
  title: '',
  subtitle: '',
  offer: '',
  eventOrProduct: '',
  cta: '',
  style: 'premium dark',
  targetAudience: '',
  sizeFormat: '1080x1350',
};

export function PosterWorkspace() {
  const navigate = useNavigate();
  const { input, setInput, output, setOutput, loading, beginLoading, endLoading, error, markError, saveCurrentProject, resetWorkspace } =
    useStudioWorkspace<PosterInput, PosterOutput>({
      toolType: 'poster',
      route: '/app/studio/poster',
      emptyInput: defaultInput,
      emptyOutput: null,
    });

  async function run() {
    if (!input.title || !input.offer || !input.cta) {
      markError('Preencha titulo, oferta e CTA.');
      return;
    }
    beginLoading();
    try {
      setOutput(await generatePoster(input));
    } finally {
      endLoading();
    }
  }

  return (
    <div className="space-y-4">
      <button type="button" onClick={() => navigate('/app/studio')} className="text-sm text-cyan">← Voltar para AXI Studio</button>
      <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
        <ToolFormSection title="Poster com IA" subtitle="Construa o pacote textual e visual para poster de campanha.">
          {[
            ['title', 'Title'],
            ['subtitle', 'Subtitle'],
            ['offer', 'Offer'],
            ['eventOrProduct', 'Event/product/service'],
            ['cta', 'CTA'],
            ['style', 'Style'],
            ['targetAudience', 'Target audience'],
            ['sizeFormat', 'Size/format'],
          ].map(([key, label]) => (
            <label key={key} className="block space-y-2 text-sm text-slate-300">
              <span>{label}</span>
              <input
                value={input[key as keyof PosterInput] as string}
                onChange={(event) => setInput((current) => ({ ...current, [key]: event.target.value }))}
                className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white outline-none focus:border-cyan"
              />
            </label>
          ))}
          <WorkspaceActions
            onGenerate={run}
            onRegenerate={run}
            onSave={() => saveCurrentProject(`Poster - ${input.title || 'Sem titulo'}`, input.subtitle || 'Poster IA', output?.posterBrief || 'Poster')}
            onExport={() => output && navigator.clipboard.writeText(output.exportBlock)}
            onReset={resetWorkspace}
            loading={loading}
          />
          {error ? <p className="text-sm text-coral">{error}</p> : null}
        </ToolFormSection>

        <ToolResultSection title="Poster package" subtitle="Brief, hierarquia, recomendacao de estilo e bloco de exportacao.">
          {!output ? (
            <EmptyState title="Sem poster gerado" description="Gere o pacote para visualizar sugestao de layout e bloco final." />
          ) : (
            <div className="grid gap-3">
              <OutputPanel title="Poster brief" lines={[output.posterBrief]} />
              <OutputPanel title="Layout suggestion" lines={[output.layoutSuggestion]} />
              <OutputPanel title="Headline hierarchy" lines={output.headlineHierarchy} />
              <OutputPanel title="Color/style recommendation" lines={[output.colorStyleRecommendation]} />
              <OutputPanel title="Export block" lines={[output.exportBlock]} />
            </div>
          )}
        </ToolResultSection>
      </div>
    </div>
  );
}

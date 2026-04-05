import { useNavigate } from 'react-router-dom';

import { useStudioWorkspace } from '../../../hooks/useStudioWorkspace';
import { generateAds } from '../../../services/studioService';
import type { AdsInput, AdsOutput } from '../../../types/studio';
import { EmptyState } from '../EmptyState';
import { OutputPanel } from '../OutputPanel';
import { ToolFormSection } from '../ToolFormSection';
import { ToolResultSection } from '../ToolResultSection';
import { WorkspaceActions } from '../WorkspaceActions';

const defaultInput: AdsInput = {
  businessName: '',
  segment: '',
  targetAudience: '',
  productService: '',
  offer: '',
  objective: '',
  tone: 'premium',
  platform: 'Instagram',
  campaignType: 'lead generation',
  budgetRange: '',
  cta: '',
};

export function AdsWorkspace() {
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
  } = useStudioWorkspace<AdsInput, AdsOutput>({
    toolType: 'ads',
    route: '/app/studio/ads',
    emptyInput: defaultInput,
    emptyOutput: null,
  });

  async function runGeneration() {
    if (!input.businessName || !input.segment || !input.targetAudience || !input.offer || !input.objective || !input.cta) {
      markError('Preencha os campos obrigatorios para gerar anuncios.');
      return;
    }
    clearError();
    beginLoading();
    try {
      const result = await generateAds(input);
      setOutput(result);
    } catch {
      markError('Falha ao gerar anuncios.');
    } finally {
      endLoading();
    }
  }

  function saveProjectNow() {
    const project = saveCurrentProject(
      `Ads - ${input.businessName || 'Sem nome'}`,
      `Campanha ${input.campaignType} em ${input.platform}`,
      output?.campaignHeadline || 'Campanha de anuncios',
    );
    if (project) navigate(`/app/studio/ads?projectId=${project.id}`, { replace: true });
  }

  return (
    <div className="space-y-4">
      <button type="button" onClick={() => navigate('/app/studio')} className="text-sm text-cyan">
        ← Voltar para AXI Studio
      </button>
      <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
        <ToolFormSection title="Anuncios Inteligentes" subtitle="Estruture campanha completa com narrativa, copy e angulo criativo.">
          {[
            ['businessName', 'Business name'],
            ['segment', 'Segment / niche'],
            ['targetAudience', 'Target audience'],
            ['productService', 'Product/service'],
            ['offer', 'Offer'],
            ['objective', 'Objective'],
            ['tone', 'Tone'],
            ['platform', 'Platform'],
            ['campaignType', 'Campaign type'],
            ['budgetRange', 'Budget range'],
            ['cta', 'CTA'],
          ].map(([key, label]) => (
            <label key={key} className="block space-y-2 text-sm text-slate-300">
              <span>{label}</span>
              <input
                value={input[key as keyof AdsInput] as string}
                onChange={(event) => setInput((current) => ({ ...current, [key]: event.target.value }))}
                className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white outline-none focus:border-cyan"
              />
            </label>
          ))}
          <WorkspaceActions
            onGenerate={runGeneration}
            onRegenerate={runGeneration}
            onSave={saveProjectNow}
            onExport={() => output && navigator.clipboard.writeText(JSON.stringify(output, null, 2))}
            onReset={resetWorkspace}
            loading={loading}
          />
          {error ? <p className="text-sm text-coral">{error}</p> : null}
        </ToolFormSection>

        <ToolResultSection title="Resultado" subtitle="Headline, copys, hooks, dores e objecoes da campanha.">
          {!output ? (
            <EmptyState title="Nenhum resultado" description="Preencha os campos e clique em Gerar para montar os ativos da campanha." />
          ) : (
            <div className="grid gap-3">
              <OutputPanel title="Headline" lines={[output.campaignHeadline]} />
              <OutputPanel title="Main copy" lines={[output.mainCopy, output.shortCopyVariation, output.positioningSummary]} />
              <OutputPanel title="CTA" lines={output.ctaSuggestions} />
              <OutputPanel title="Creative angle" lines={[output.creativeAngle]} />
              <OutputPanel title="Hooks" lines={output.hookIdeas} />
              <OutputPanel title="Pain points" lines={output.painPoints} />
              <OutputPanel title="Objections" lines={output.objections} />
            </div>
          )}
        </ToolResultSection>
      </div>
    </div>
  );
}

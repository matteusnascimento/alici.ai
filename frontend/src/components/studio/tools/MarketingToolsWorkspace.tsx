import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { useStudioWorkspace } from '../../../hooks/useStudioWorkspace';
import { generateMarketingAsset } from '../../../services/studioService';
import type { MarketingToolsInput, MarketingToolsOutput } from '../../../types/studio';
import { EmptyState } from '../EmptyState';
import { OutputPanel } from '../OutputPanel';
import { ToolFormSection } from '../ToolFormSection';
import { ToolResultSection } from '../ToolResultSection';
import { WorkspaceActions } from '../WorkspaceActions';

const tabs: MarketingToolsInput['tab'][] = ['campaigns', 'copy', 'funnels', 'whatsapp', 'content-planner'];

const defaultInput: MarketingToolsInput = {
  tab: 'campaigns',
  context: '',
};

export function MarketingToolsWorkspace() {
  const navigate = useNavigate();
  const { input, setInput, output, setOutput, loading, beginLoading, endLoading, error, markError, saveCurrentProject, resetWorkspace } =
    useStudioWorkspace<MarketingToolsInput, MarketingToolsOutput>({
      toolType: 'marketing-tools',
      route: '/app/studio/marketing-tools',
      emptyInput: defaultInput,
      emptyOutput: null,
    });
  const [tab, setTab] = useState<MarketingToolsInput['tab']>(input.tab);

  async function run() {
    if (!input.context.trim()) {
      markError('Descreva contexto da acao de marketing.');
      return;
    }
    beginLoading();
    try {
      const generated = await generateMarketingAsset({ ...input, tab });
      setInput((current) => ({ ...current, tab }));
      setOutput(generated);
    } finally {
      endLoading();
    }
  }

  return (
    <div className="space-y-4">
      <button type="button" onClick={() => navigate('/app/studio')} className="text-sm text-cyan">← Voltar para AXI Studio</button>
      <div className="grid gap-6 xl:grid-cols-[390px_1fr]">
        <ToolFormSection title="Ferramentas de Marketing" subtitle="Campanhas, copy, funis, WhatsApp e content planner em tabs operacionais.">
          <div className="flex flex-wrap gap-2">
            {tabs.map((tabId) => (
              <button
                key={tabId}
                type="button"
                onClick={() => setTab(tabId)}
                className={[
                  'rounded-2xl border px-3 py-2 text-sm capitalize',
                  tab === tabId ? 'border-cyan/40 bg-cyan/10 text-cyan' : 'border-white/15 text-slate-200',
                ].join(' ')}
              >
                {tabId}
              </button>
            ))}
          </div>
          <label className="block space-y-2 text-sm text-slate-300">
            <span>Context</span>
            <textarea value={input.context} onChange={(e) => setInput((c) => ({ ...c, context: e.target.value }))} className="h-40 w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white" />
          </label>
          <WorkspaceActions
            onGenerate={run}
            onRegenerate={run}
            onSave={() => saveCurrentProject(`Marketing - ${tab}`, 'Workspace de marketing central', output?.lines[0] || 'Marketing tools')}
            onReset={resetWorkspace}
            loading={loading}
          />
          {error ? <p className="text-sm text-coral">{error}</p> : null}
        </ToolFormSection>

        <ToolResultSection title="Output por tab" subtitle="Resultados estruturados por subferramenta selecionada.">
          {!output ? <EmptyState title="Sem output" description="Gere ativos por tab para exibir plano estruturado." /> : <OutputPanel title={`Tab ${tab}`} lines={output.lines} />}
        </ToolResultSection>
      </div>
    </div>
  );
}

import { useNavigate } from 'react-router-dom';

import { useStudioWorkspace } from '../../../hooks/useStudioWorkspace';
import { generateCaptions } from '../../../services/studioService';
import type { CaptionsInput, CaptionsOutput } from '../../../types/studio';
import { EmptyState } from '../EmptyState';
import { OutputPanel } from '../OutputPanel';
import { ToolFormSection } from '../ToolFormSection';
import { ToolResultSection } from '../ToolResultSection';
import { WorkspaceActions } from '../WorkspaceActions';

const defaultInput: CaptionsInput = {
  mediaName: '',
  language: 'pt-BR',
  tone: 'direto',
  captionType: 'social',
  outputFormat: 'SRT',
};

export function CaptionsWorkspace() {
  const navigate = useNavigate();
  const { input, setInput, output, setOutput, loading, beginLoading, endLoading, error, markError, saveCurrentProject, resetWorkspace } =
    useStudioWorkspace<CaptionsInput, CaptionsOutput>({
      toolType: 'captions',
      route: '/app/studio/captions',
      emptyInput: defaultInput,
      emptyOutput: null,
    });

  async function run() {
    if (!input.mediaName) {
      markError('Informe o arquivo de audio/video.');
      return;
    }
    beginLoading();
    try {
      setOutput(await generateCaptions(input));
    } finally {
      endLoading();
    }
  }

  return (
    <div className="space-y-4">
      <button type="button" onClick={() => navigate('/app/studio')} className="text-sm text-cyan">← Voltar para AXI Studio</button>
      <div className="grid gap-6 xl:grid-cols-[390px_1fr]">
        <ToolFormSection title="Legendas Automaticas" subtitle="Gere blocos de subtitulo e caption social editavel.">
          {[
            ['mediaName', 'Media upload placeholder'],
            ['language', 'Language'],
            ['tone', 'Tone'],
            ['captionType', 'Caption type'],
            ['outputFormat', 'Output format'],
          ].map(([key, label]) => (
            <label key={key} className="block space-y-2 text-sm text-slate-300">
              <span>{label}</span>
              <input value={input[key as keyof CaptionsInput] as string} onChange={(e) => setInput((c) => ({ ...c, [key]: e.target.value }))} className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white" />
            </label>
          ))}
          <WorkspaceActions onGenerate={run} onRegenerate={run} onSave={() => saveCurrentProject('Captions', input.mediaName, output?.captionText || 'Captions')} onExport={() => output && navigator.clipboard.writeText(output.exportText)} onReset={resetWorkspace} loading={loading} />
          {error ? <p className="text-sm text-coral">{error}</p> : null}
        </ToolFormSection>
        <ToolResultSection title="Output" subtitle="Blocos de legenda, texto social e export.">
          {!output ? <EmptyState title="Sem legenda gerada" description="Preencha os dados e gere a estrutura de legendas." /> : <div className="grid gap-3"><OutputPanel title="Subtitle blocks" lines={output.subtitleBlocks} /><OutputPanel title="Caption" lines={[output.captionText, output.socialCaptionSuggestion]} /><OutputPanel title="Export" lines={[output.exportText]} /></div>}
        </ToolResultSection>
      </div>
    </div>
  );
}

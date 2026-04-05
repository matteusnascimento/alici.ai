import { useNavigate } from 'react-router-dom';

import { useStudioWorkspace } from '../../../hooks/useStudioWorkspace';
import { generateAudioScript } from '../../../services/studioService';
import type { AudioToolsInput, AudioToolsOutput } from '../../../types/studio';
import { EmptyState } from '../EmptyState';
import { OutputPanel } from '../OutputPanel';
import { ToolFormSection } from '../ToolFormSection';
import { ToolResultSection } from '../ToolResultSection';
import { WorkspaceActions } from '../WorkspaceActions';

const defaultInput: AudioToolsInput = {
  objective: '',
  audience: '',
  duration: '45s',
  tone: 'energetico',
  platform: 'Instagram Reels',
};

export function AudioToolsWorkspace() {
  const navigate = useNavigate();
  const { input, setInput, output, setOutput, loading, beginLoading, endLoading, error, markError, saveCurrentProject, resetWorkspace } =
    useStudioWorkspace<AudioToolsInput, AudioToolsOutput>({
      toolType: 'audio-tools',
      route: '/app/studio/audio-tools',
      emptyInput: defaultInput,
      emptyOutput: null,
    });

  async function run() {
    if (!input.objective || !input.audience) {
      markError('Informe objetivo e audiencia.');
      return;
    }
    beginLoading();
    try {
      setOutput(await generateAudioScript(input));
    } finally {
      endLoading();
    }
  }

  return (
    <div className="space-y-4">
      <button type="button" onClick={() => navigate('/app/studio')} className="text-sm text-cyan">← Voltar para AXI Studio</button>
      <div className="grid gap-6 xl:grid-cols-[390px_1fr]">
        <ToolFormSection title="Ferramentas de Audio" subtitle="Estruture script, narracao e guia de fala para conteudo em video.">
          {[
            ['objective', 'Objective'],
            ['audience', 'Audience'],
            ['duration', 'Duration'],
            ['tone', 'Tone'],
            ['platform', 'Platform'],
          ].map(([key, label]) => (
            <label key={key} className="block space-y-2 text-sm text-slate-300">
              <span>{label}</span>
              <input value={input[key as keyof AudioToolsInput] as string} onChange={(e) => setInput((c) => ({ ...c, [key]: e.target.value }))} className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white" />
            </label>
          ))}
          <WorkspaceActions onGenerate={run} onRegenerate={run} onSave={() => saveCurrentProject('Audio Tools', input.objective, output?.audioScript || 'Audio script')} onDuplicate={run} onReset={resetWorkspace} loading={loading} />
          {error ? <p className="text-sm text-coral">{error}</p> : null}
        </ToolFormSection>
        <ToolResultSection title="Audio script output" subtitle="Roteiro principal, sequencia de narracao e fechamento CTA.">
          {!output ? <EmptyState title="Sem roteiro" description="Gere um roteiro para visualizar estrutura de narracao." /> : <div className="grid gap-3"><OutputPanel title="Script" lines={[output.audioScript]} /><OutputPanel title="Narration sequence" lines={output.narrationSequence} /><OutputPanel title="CTA ending" lines={[output.ctaEnding]} /><OutputPanel title="Speaking guide" lines={[output.speakingGuide]} /></div>}
        </ToolResultSection>
      </div>
    </div>
  );
}

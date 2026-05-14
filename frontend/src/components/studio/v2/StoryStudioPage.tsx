import { useState } from 'react';

import { useStudioV2 } from '../../../hooks/useStudioV2';
import { useToast } from '../../../hooks/useToast';
import { studioCreateStory } from '../../../services/studio.service';
import { StudioCanvas } from './StudioCanvas';
import { StudioInspectorPanel } from './StudioInspectorPanel';
import { StudioShell } from './StudioShell';

export function StoryStudioPage() {
  const studio = useStudioV2({ defaultType: 'story', defaultTitle: 'Story com IA' });
  const { pushToast } = useToast();
  const [prompt, setPrompt] = useState('Story 9:16 para oferta relampago com foco em clique no link.');
  const [template, setTemplate] = useState('story-premium');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

  async function handleGenerate() {
    setLoading(true);
    try {
      const result = await studioCreateStory({
        title: 'Story 9:16',
        prompt,
        metadata: { ratio: '9:16', template },
      });
      setStatus(result.message);
      await studio.reload();
      pushToast('Story gerado com sucesso.', 'success');
    } catch (err) {
      setStatus(err instanceof Error ? err.message : 'Falha ao gerar story.');
      pushToast('Falha ao gerar story.', 'error');
    } finally {
      setLoading(false);
    }
  }

  return (
    <StudioShell
      projectName={studio.projectName}
      saveState={loading ? 'saving' : studio.saveState}
      onSave={() => void studio.saveProject({ status: 'saved', metadata: { prompt, template } })}
      onExport={() => void studio.exportProject('png')}
      center={(
        <StudioCanvas title="Story Canvas 9:16" subtitle="Templates verticais com geracao opcional por IA e salvamento automatico no projeto">
          <div className="mx-auto flex h-full max-w-sm flex-col justify-center rounded-2xl border border-dashed border-cyan-300/35 bg-black/25 p-4 text-center">
            <p className="font-display text-2xl text-white">Story 9:16</p>
            <p className="mt-2 text-sm text-slate-300">Template: {template}</p>
            <p className="mt-2 text-xs text-slate-400">{prompt}</p>
            <button type="button" onClick={() => void handleGenerate()} disabled={loading} className="mt-4 rounded-xl bg-cyan px-4 py-2 text-sm font-semibold text-ink disabled:opacity-70">
              {loading ? 'Gerando story...' : 'Gerar story por IA'}
            </button>
            {status ? <p className="mt-3 text-xs text-cyan-100">{status}</p> : null}
          </div>
        </StudioCanvas>
      )}
      right={(
        <StudioInspectorPanel title="Story Wizard">
          <label className="text-xs text-slate-400">Template</label>
          <select value={template} onChange={(event) => setTemplate(event.target.value)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white">
            <option value="story-premium">Story Premium</option>
            <option value="story-clean">Story Clean</option>
            <option value="story-product">Story Produto</option>
          </select>
          <label className="text-xs text-slate-400">Prompt</label>
          <textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} className="min-h-28 w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white" />
        </StudioInspectorPanel>
      )}
    />
  );
}

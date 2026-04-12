import { useState } from 'react';

import { useStudioV2 } from '../../../hooks/useStudioV2';
import { useToast } from '../../../hooks/useToast';
import { studioVideoCaptions, studioVideoGenerate, studioVideoVoiceover } from '../../../services/studio.service';
import { StudioBottomDock } from './StudioBottomDock';
import { StudioCanvas } from './StudioCanvas';
import { StudioExportModal } from './StudioExportModal';
import { StudioInspectorPanel } from './StudioInspectorPanel';
import { StudioShell } from './StudioShell';
import { StudioTimeline } from './StudioTimeline';
import { StudioToolContextPanel } from './StudioToolContextPanel';
import { StudioToolRail } from './StudioToolRail';

const tools = ['Upload', 'AI Video', 'Cortes', 'Texto', 'Legendas', 'Audio', 'Voz IA', 'Transicoes', 'Filtros', 'Proporcao', 'Avatar IA', 'AI Media'];

export function VideoEditorStudioPage() {
  const studio = useStudioV2({ defaultType: 'video-editor', defaultTitle: 'Editor de Video IA' });
  const { pushToast } = useToast();
  const [activeTool, setActiveTool] = useState(tools[0]);
  const [openExport, setOpenExport] = useState(false);
  const [prompt, setPrompt] = useState('Video promocional de 15 segundos para produto premium no formato reel');

  async function runTool() {
    if (!studio.currentProject) return;
    try {
      if (activeTool === 'Legendas') {
        await studioVideoCaptions({ project_id: studio.currentProject.id, prompt, options: { style: 'bold-modern' } });
      } else if (activeTool === 'Voz IA') {
        await studioVideoVoiceover({ project_id: studio.currentProject.id, prompt, options: { voice: 'pt-BR-female-pro' } });
      } else {
        await studioVideoGenerate({ project_id: studio.currentProject.id, prompt, options: { ratio: '9:16', duration: 15 } });
      }
      studio.setSaveState('dirty');
      pushToast('Processamento de video concluido.', 'success');
    } catch {
      pushToast('Falha ao processar video.', 'error');
    }
  }

  return (
    <>
      <StudioShell
        projectName={studio.projectName}
        saveState={studio.saveState}
        onSave={() => void studio.saveProject({ status: 'saved', metadata: { tool: activeTool, prompt } })}
        onExport={() => setOpenExport(true)}
        leftRail={<StudioToolRail tools={tools} activeTool={activeTool} onSelect={setActiveTool} />}
        center={(
          <StudioCanvas title="Video Preview" subtitle="Canvas central com preview, composicao e foco no corte">
            <div className="flex h-full items-center justify-center rounded-2xl border border-dashed border-cyan-300/30 bg-black/30 text-center">
              <div>
                <p className="font-display text-2xl text-white">Preview do video</p>
                <p className="mt-2 text-slate-300">Ferramenta ativa: {activeTool}</p>
                <button type="button" onClick={() => void runTool()} className="mt-4 rounded-xl bg-cyan px-4 py-2 text-sm font-semibold text-ink">
                  Gerar video a partir do prompt
                </button>
              </div>
            </div>
          </StudioCanvas>
        )}
        right={(
          <StudioInspectorPanel title="Propriedades do clipe">
            <StudioToolContextPanel activeTool={activeTool} />
            <label className="text-xs text-slate-400">Prompt</label>
            <textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} className="min-h-24 w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white" />
            <button type="button" className="w-full rounded-xl border border-cyan-300/40 px-3 py-2 text-sm text-cyan-100">Create vertical ad</button>
            <button type="button" className="w-full rounded-xl border border-white/20 px-3 py-2 text-sm text-white">Create story version</button>
            <button type="button" className="w-full rounded-xl border border-white/20 px-3 py-2 text-sm text-white">Create reel version</button>
            <button type="button" className="w-full rounded-xl border border-white/20 px-3 py-2 text-sm text-white" onClick={() => void studio.saveVersion(`Video ${new Date().toLocaleTimeString('pt-BR')}`, { timeline_data: { prompt, activeTool } })}>
              Save version
            </button>
          </StudioInspectorPanel>
        )}
        bottom={(
          <StudioBottomDock>
            <StudioTimeline clips={[{ id: 'v1', label: 'Clip principal', length: 6 }, { id: 'v2', label: 'Texto overlay', length: 4 }, { id: 'v3', label: 'CTA final', length: 5 }]} />
          </StudioBottomDock>
        )}
      />
      <StudioExportModal
        open={openExport}
        onClose={() => setOpenExport(false)}
        onExport={(format) => {
          setOpenExport(false);
          void studio.exportProject(format);
        }}
      />
    </>
  );
}

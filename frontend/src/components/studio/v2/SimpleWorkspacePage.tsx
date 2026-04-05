import { useState } from 'react';

import { useStudioV2 } from '../../../hooks/useStudioV2';
import { StudioBottomDock } from './StudioBottomDock';
import { StudioCanvas } from './StudioCanvas';
import { StudioExportModal } from './StudioExportModal';
import { StudioInspectorPanel } from './StudioInspectorPanel';
import { StudioPromptBar } from './StudioPromptBar';
import { StudioShell } from './StudioShell';
import { StudioTimeline } from './StudioTimeline';
import { StudioToolRail } from './StudioToolRail';

interface SimpleWorkspacePageProps {
  type: string;
  title: string;
  subtitle: string;
  tools: string[];
  promptPlaceholder: string;
}

export function SimpleWorkspacePage({ type, title, subtitle, tools, promptPlaceholder }: SimpleWorkspacePageProps) {
  const studio = useStudioV2({ defaultType: type, defaultTitle: title });
  const [activeTool, setActiveTool] = useState(tools[0] || 'tool');
  const [prompt, setPrompt] = useState('');
  const [openExport, setOpenExport] = useState(false);

  return (
    <>
      <StudioShell
        projectName={studio.projectName}
        saveState={studio.saveState}
        onSave={() => void studio.saveProject({ status: 'saved' })}
        onExport={() => setOpenExport(true)}
        leftRail={<StudioToolRail tools={tools} activeTool={activeTool} onSelect={setActiveTool} />}
        center={(
          <div className="space-y-4">
            <StudioPromptBar value={prompt} onChange={setPrompt} onGenerate={() => studio.setSaveState('dirty')} placeholder={promptPlaceholder} />
            <StudioCanvas title={title} subtitle={subtitle}>
              <div className="flex h-full items-center justify-center text-center text-slate-300">
                <div>
                  <p className="font-display text-2xl text-white">Workspace ativo: {activeTool}</p>
                  <p className="mt-2 text-sm">Preview-first, canvas-first, pronto para edicao visual.</p>
                  {studio.error ? <p className="mt-2 text-coral">{studio.error}</p> : null}
                </div>
              </div>
            </StudioCanvas>
          </div>
        )}
        right={(
          <StudioInspectorPanel title="Propriedades">
            <label className="block text-xs text-slate-400">Ferramenta ativa</label>
            <input value={activeTool} readOnly className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white" />
            <button type="button" className="w-full rounded-xl border border-cyan-300/40 px-3 py-2 text-sm text-cyan-100" onClick={() => void studio.duplicateProject()}>
              Duplicar projeto
            </button>
            <button type="button" className="w-full rounded-xl border border-white/20 px-3 py-2 text-sm text-white" onClick={() => void studio.saveVersion(`Versao ${studio.versions.length + 1}`, {})}>
              Salvar versao
            </button>
          </StudioInspectorPanel>
        )}
        bottom={(
          <StudioBottomDock>
            <StudioTimeline clips={[{ id: 'c1', label: 'Cena 01', length: 3 }, { id: 'c2', label: 'Cena 02', length: 5 }, { id: 'c3', label: 'Cena 03', length: 4 }]} />
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

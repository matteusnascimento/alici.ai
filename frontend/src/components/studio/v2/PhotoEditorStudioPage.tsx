import { Upload, Wand2 } from 'lucide-react';
import { useRef, useState } from 'react';

import { useStudioV2 } from '../../../hooks/useStudioV2';
import { useToast } from '../../../hooks/useToast';
import { studioImageEnhance, studioImageFilter, studioImageRemoveBackground, studioImageResize, studioImageRetouch } from '../../../services/studio.service';
import { StudioBottomDock } from './StudioBottomDock';
import { StudioCanvas } from './StudioCanvas';
import { StudioExportModal } from './StudioExportModal';
import { StudioInspectorPanel } from './StudioInspectorPanel';
import { StudioShell } from './StudioShell';
import { StudioToolContextPanel } from './StudioToolContextPanel';
import { StudioToolRail } from './StudioToolRail';

const tools = [
  'Crop / Cortar',
  'Redimensionar',
  'Remover Fundo',
  'Rotacionar',
  'Brilho',
  'Contraste',
  'Saturacao',
  'Nitidez',
  'Temperatura',
  'Sombras',
  'Desfoque',
  'Texto',
  'Logo',
  'CTA Visual',
  'Molduras',
  'Ajustes IA',
  'Filtros',
  'Preparar para Anuncio',
  'Preparar para Story',
  'Preparar para Feed',
];

export function PhotoEditorStudioPage() {
  const studio = useStudioV2({ defaultType: 'photo-editor', defaultTitle: 'Editor de Fotos IA' });
  const { pushToast } = useToast();
  const uploadInputRef = useRef<HTMLInputElement | null>(null);
  const [activeTool, setActiveTool] = useState(tools[0]);
  const [openExport, setOpenExport] = useState(false);
  const [uploadedMedia, setUploadedMedia] = useState<string | null>(null);
  const [adjustments, setAdjustments] = useState({ brightness: 40, contrast: 55, saturation: 50, exposure: 45, temperature: 52, sharpness: 48, vignette: 8 });

  async function applyAiAction() {
    if (!studio.currentProject) return;
    try {
      if (activeTool === 'Crop / Cortar') {
        await studioImageRetouch({ project_id: studio.currentProject.id, options: { crop: '1:1', source: uploadedMedia } });
      } else if (activeTool === 'Remover Fundo') {
        await studioImageRemoveBackground({ project_id: studio.currentProject.id, options: { softness: 0.5 } });
      } else if (activeTool === 'Redimensionar') {
        await studioImageResize({ project_id: studio.currentProject.id, options: { ratio: '9:16', source: uploadedMedia } });
      } else if (activeTool === 'Filtros') {
        await studioImageFilter({ project_id: studio.currentProject.id, options: { preset: 'cinematic', source: uploadedMedia } });
      } else if (activeTool === 'Ajustes IA') {
        await studioImageRetouch({ project_id: studio.currentProject.id, options: { detail: 0.7 } });
      } else {
        await studioImageEnhance({ project_id: studio.currentProject.id, options: { ...adjustments, source: uploadedMedia, tool: activeTool } });
      }
      pushToast('Ajuste aplicado com sucesso.', 'success');
      studio.setSaveState('dirty');
    } catch {
      pushToast('Falha ao aplicar ajuste da imagem.', 'error');
    }
  }

  return (
    <>
      <StudioShell
        projectName={studio.projectName}
        saveState={studio.saveState}
        onSave={() => void studio.saveProject({ status: 'saved', metadata: { tool: activeTool, adjustments } })}
        onExport={() => setOpenExport(true)}
        leftRail={<StudioToolRail tools={tools} activeTool={activeTool} onSelect={setActiveTool} />}
        center={(
          <StudioCanvas title="Preview de imagem" subtitle="Canvas de composicao com zoom, compare e ajustes em tempo real." onUpload={() => uploadInputRef.current?.click()}>
            <div className="flex h-full items-center justify-center rounded-2xl border border-white/10 bg-black/35 text-center">
              <div>
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-[var(--studio-gradient)] text-white shadow-[0_0_34px_rgba(192,38,211,0.34)]">
                  <Upload size={26} />
                </div>
                <p className="mt-5 font-display text-2xl font-bold text-white">Imagem em foco</p>
                <p className="mt-2 text-slate-300">Ferramenta ativa: {activeTool}</p>
                <label className="mx-auto mt-4 block w-fit cursor-pointer rounded-2xl bg-[var(--studio-gradient)] px-5 py-3 text-sm font-bold text-white shadow-[0_0_26px_rgba(34,211,238,0.22)]" title="Faca upload da imagem para comecar">
                  Upload de imagem
                  <input
                    ref={uploadInputRef}
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={(event) => {
                      const file = event.target.files?.[0];
                      if (!file) return;
                      setUploadedMedia(file.name);
                      studio.setSaveState('dirty');
                      pushToast(`Upload concluido: ${file.name}.`, 'info');
                    }}
                  />
                </label>
                {uploadedMedia ? <p className="mt-2 text-xs text-cyan-100">Arquivo carregado: {uploadedMedia}</p> : <p className="mt-2 text-xs text-slate-400">Faca upload da sua imagem para comecar.</p>}
                <button type="button" onClick={() => void applyAiAction()} className="mt-4 inline-flex items-center gap-2 rounded-xl border border-cyan-300/35 bg-cyan-300/10 px-4 py-2 text-sm font-semibold text-cyan-50" title="Aplica ajuste usando a ferramenta ativa">
                  <Wand2 size={15} /> Aplicar preset IA
                </button>
              </div>
            </div>
          </StudioCanvas>
        )}
        right={(
          <StudioInspectorPanel title={`Propriedades: ${activeTool}`}>
            <StudioToolContextPanel activeTool={activeTool} />
            {Object.entries(adjustments).map(([key, value]) => (
              <label key={key} className="block text-xs text-slate-300">
                <span className="mb-1 block capitalize">{key}</span>
                <input
                  type="range"
                  min={0}
                  max={100}
                  value={value}
                  onChange={(event) => setAdjustments((current) => ({ ...current, [key]: Number(event.target.value) }))}
                  className="studio-range w-full"
                />
              </label>
            ))}
            <button type="button" className="w-full rounded-xl border border-white/20 px-3 py-2 text-sm text-white" onClick={() => void studio.saveVersion(`Photo ${new Date().toLocaleTimeString('pt-BR')}`, { canvas_data: { adjustments } })}>
              Save version
            </button>
            <button type="button" className="w-full rounded-xl border border-white/20 px-3 py-2 text-sm text-white" title="Comparar resultado com original">Compare before/after</button>
            <p className="text-xs text-slate-400">Fluxo recomendado: upload, ajuste, preview em tempo real, salvar e exportar.</p>
          </StudioInspectorPanel>
        )}
        bottom={(
          <StudioBottomDock>
            <p className="text-sm text-slate-300">Ferramentas rapidas: reset tool, save version, export e aplicar presets.</p>
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

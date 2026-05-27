import { useEffect, useState } from 'react';

import { useStudioV2 } from '../../../hooks/useStudioV2';
import { useToast } from '../../../hooks/useToast';
import { studioImageEnhance, studioImageRemoveBackground, studioImageRetouch } from '../../../services/studio.service';
import { StudioBottomDock } from './StudioBottomDock';
import { StudioCanvas } from './StudioCanvas';
import { StudioContextToolbar } from './StudioContextToolbar';
import { StudioExportModal } from './StudioExportModal';
import { StudioInspectorPanel } from './StudioInspectorPanel';
import { StudioShell } from './StudioShell';
import { StudioToolContextPanel } from './StudioToolContextPanel';
import { StudioToolRail } from './StudioToolRail';

const tools = [
  'Editar',
  'Remover Fundo',
  'Borracha',
  'Crop / Cortar',
  'Redimensionar',
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
  const [activeTool, setActiveTool] = useState(tools[0]);
  const [openExport, setOpenExport] = useState(false);
  const [uploadedMedia, setUploadedMedia] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [selectionActive, setSelectionActive] = useState(false);
  const [zoom, setZoom] = useState(39);
  const [adjustments, setAdjustments] = useState({ brightness: 40, contrast: 55, saturation: 50, exposure: 45, temperature: 52, sharpness: 48, vignette: 8 });

  useEffect(() => () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
  }, [previewUrl]);

  async function applyAiAction(toolOverride?: string) {
    const tool = toolOverride || activeTool;
    if (!studio.currentProject) {
      pushToast('Projeto ainda nao foi preparado. Tente novamente em alguns segundos.', 'error');
      return;
    }
    if (!uploadedMedia && !previewUrl) {
      pushToast('Selecione uma imagem antes de aplicar a ferramenta.', 'error');
      return;
    }
    try {
      if (tool === 'Crop / Cortar') {
        await studioImageRetouch({ project_id: studio.currentProject.id, options: { crop: '1:1', source: uploadedMedia } });
      } else if (tool === 'Remover Fundo') {
        await studioImageRemoveBackground({ project_id: studio.currentProject.id, options: { softness: 0.5, source: uploadedMedia } });
      } else if (tool === 'Borracha') {
        await studioImageRetouch({ project_id: studio.currentProject.id, options: { eraser: true, source: uploadedMedia } });
      } else if (tool === 'Ajustes IA') {
        await studioImageRetouch({ project_id: studio.currentProject.id, options: { detail: 0.7, source: uploadedMedia } });
      } else {
        await studioImageEnhance({ project_id: studio.currentProject.id, options: { ...adjustments, source: uploadedMedia, tool } });
      }
      pushToast(`Ferramenta aplicada: ${tool}.`, 'success');
      studio.setSaveState('dirty');
    } catch {
      pushToast(`Falha ao aplicar ${tool}.`, 'error');
    }
  }

  function toolbarToTool(actionId: string) {
    const map: Record<string, string> = {
      edit: 'Editar',
      'remove-background': 'Remover Fundo',
      eraser: 'Borracha',
      crop: 'Crop / Cortar',
      flip: 'Rotacionar',
      transparency: 'Desfoque',
      animate: 'Preparar para Story',
      position: 'Redimensionar',
      style: 'Filtros',
      color: 'Saturacao',
    };
    const next = map[actionId] || 'Editar';
    setActiveTool(next);
    if (['remove-background', 'eraser', 'crop', 'color', 'transparency', 'style'].includes(actionId)) {
      void applyAiAction(next);
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
          <StudioCanvas
            title="Editor de imagem"
            subtitle="Selecione a imagem para liberar a barra contextual, ajustes, corte, fundo e posição."
            selected={Boolean(previewUrl && selectionActive)}
            toolbar={previewUrl && selectionActive ? <StudioContextToolbar selectionKind="image" activeAction={activeTool === 'Remover Fundo' ? 'remove-background' : undefined} onAction={toolbarToTool} /> : null}
            footer={(
              <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-white/10 bg-black/25 px-4 py-3 text-sm text-slate-300">
                <span>{uploadedMedia || 'Nenhuma imagem selecionada'}</span>
                <label className="flex min-w-48 items-center gap-3">
                  Zoom
                  <input type="range" min={25} max={160} value={zoom} onChange={(event) => setZoom(Number(event.target.value))} className="w-32" />
                  <span>{zoom}%</span>
                </label>
              </div>
            )}
          >
            <div className="flex min-h-[470px] items-center justify-center rounded-2xl border border-dashed border-cyan-300/30 bg-[#eef2f7]/5 p-6 text-center">
              {previewUrl ? (
                <button
                  type="button"
                  onClick={() => setSelectionActive((value) => !value)}
                  className="relative flex h-full min-h-[420px] w-full items-center justify-center overflow-hidden rounded-2xl bg-slate-100/95 p-8 text-left"
                  title={selectionActive ? 'Clique para remover selecao' : 'Clique para selecionar imagem'}
                >
                  <img
                    src={previewUrl}
                    alt={uploadedMedia || 'Imagem selecionada'}
                    className="max-h-full max-w-full rounded-lg object-contain shadow-2xl"
                    style={{ transform: `scale(${zoom / 100})` }}
                  />
                </button>
              ) : (
                <div>
                  <p className="font-display text-2xl text-white">Imagem em foco</p>
                  <p className="mt-2 text-slate-300">Faça upload para ativar seleção, handles e barra contextual.</p>
                  <label className="mx-auto mt-4 block w-fit cursor-pointer rounded-xl border border-white/20 px-4 py-2 text-sm text-white" title="Faça upload da imagem para começar">
                    Upload de imagem
                    <input
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={(event) => {
                        const file = event.target.files?.[0];
                        if (!file) return;
                        if (previewUrl) URL.revokeObjectURL(previewUrl);
                        setPreviewUrl(URL.createObjectURL(file));
                        setUploadedMedia(file.name);
                        setSelectionActive(true);
                        studio.setSaveState('dirty');
                        pushToast(`Upload concluído: ${file.name}.`, 'info');
                      }}
                    />
                  </label>
                </div>
              )}
            </div>
          </StudioCanvas>
        )}
        right={(
          <StudioInspectorPanel title="Propriedades contextuais">
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
                  className="w-full"
                />
              </label>
            ))}
            <button type="button" onClick={() => void applyAiAction()} className="w-full rounded-xl bg-cyan px-3 py-2 text-sm font-semibold text-ink">
              Aplicar ferramenta ativa
            </button>
            <button type="button" className="w-full rounded-xl border border-white/20 px-3 py-2 text-sm text-white" onClick={() => void studio.saveVersion(`Photo ${new Date().toLocaleTimeString('pt-BR')}`, { canvas_data: { adjustments, activeTool } })}>
              Salvar versão
            </button>
            <button type="button" className="w-full rounded-xl border border-white/20 px-3 py-2 text-sm text-white" title="Comparar resultado com original">Compare before/after</button>
            <p className="text-xs text-slate-400">Fluxo recomendado: upload, ajuste, preview em tempo real, salvar e exportar.</p>
          </StudioInspectorPanel>
        )}
        bottom={(
          <StudioBottomDock>
            <p className="text-sm text-slate-300">Fluxo rápido: selecione imagem, use a barra contextual, ajuste no painel e salve versões antes de exportar.</p>
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

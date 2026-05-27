import { type ElementType, useEffect, useMemo, useState } from 'react';
import { Image as KonvaImage, Layer, Rect, Stage, Text } from 'react-konva';
import {
  Captions,
  Download,
  Eraser,
  Film,
  FolderOpen,
  ImagePlus,
  Layers3,
  MousePointer2,
  Palette,
  Search,
  Scissors,
  Shapes,
  SlidersHorizontal,
  SmilePlus,
  Sparkles,
  Split,
  Type,
  UploadCloud,
  Wand2,
  Zap,
} from 'lucide-react';

import { useToast } from '../../../hooks/useToast';
import { useAxiStudioAutosave } from '../../../hooks/useAxiStudioAutosave';
import { useStudioV2 } from '../../../hooks/useStudioV2';
import {
  searchStudioWebImages,
  studioAICreativeGenerate,
  studioImageRemoveBackground,
  studioImageRetouch,
  studioVideoCaptions,
  uploadStudioAsset,
} from '../../../services/studio.service';
import type { AxiLayerKind, AxiStudioLayer } from '../../../store/axiStudioStore';
import type { StudioWebImage } from '../../../types/studioV2';
import { getAxiStudioSnapshot, useAxiStudioStore } from '../../../store/axiStudioStore';
import { StudioExportModal } from './StudioExportModal';
import { StudioTopbar } from './StudioTopbar';

type StudioToolId =
  | 'select'
  | 'assets'
  | 'upload'
  | 'text'
  | 'templates'
  | 'effects'
  | 'emoji'
  | 'web-images'
  | 'photo-ai'
  | 'video'
  | 'captions'
  | 'export';

const leftTools: Array<{ id: StudioToolId; label: string; icon: ElementType<{ size?: string | number }> }> = [
  { id: 'select', label: 'Selecionar', icon: MousePointer2 },
  { id: 'assets', label: 'Assets', icon: FolderOpen },
  { id: 'upload', label: 'Upload', icon: UploadCloud },
  { id: 'text', label: 'Texto', icon: Type },
  { id: 'templates', label: 'Templates', icon: LayoutIcon },
  { id: 'effects', label: 'Efeitos', icon: Palette },
  { id: 'emoji', label: 'Emojis', icon: SmilePlus },
  { id: 'web-images', label: 'Web', icon: Search },
  { id: 'photo-ai', label: 'Foto IA', icon: Wand2 },
  { id: 'video', label: 'Video', icon: Film },
  { id: 'captions', label: 'Legendas', icon: Captions },
  { id: 'export', label: 'Exportar', icon: Download },
];

const textPresets = [
  { label: 'Titulo forte', text: 'Digite seu titulo', size: 44, color: '#07111f' },
  { label: 'Subtitulo', text: 'Texto de apoio claro', size: 26, color: '#111827' },
  { label: 'CTA', text: 'Clique e saiba mais', size: 30, color: '#A020F0' },
];

const emojiSet = ['✨', '🔥', '🚀', '💎', '✅', '⚡', '📌', '💬', '🎯', '❤️', '⭐', '📈', '🛒', '🎬', '🎨'];

const effectPresets = [
  { id: 'cinematic', label: 'Cinematic', color: '#1f2937', opacity: 0.16 },
  { id: 'neon', label: 'Neon AXI', color: '#00F0FF', opacity: 0.14 },
  { id: 'purple-glow', label: 'Roxo Glow', color: '#A020F0', opacity: 0.16 },
  { id: 'warm', label: 'Quente', color: '#FF6A00', opacity: 0.12 },
  { id: 'contrast', label: 'Contraste', color: '#000000', opacity: 0.1 },
  { id: 'clean', label: 'Limpo', color: '#ffffff', opacity: 0.08 },
];

const templatePresets = [
  {
    id: 'social-launch',
    title: 'Post de lancamento',
    type: 'Social',
    prompt: 'Post quadrado para lancamento com titulo forte, prova social e CTA.',
    layers: [
      { name: 'Titulo lancamento', text: 'LANCAMENTO', x: 160, y: 120, width: 360, height: 68, color: '#07111f' },
      { name: 'CTA', text: 'Garanta sua vaga', x: 190, y: 390, width: 300, height: 54, color: '#A020F0' },
    ],
  },
  {
    id: 'story-offer',
    title: 'Story oferta',
    type: 'Stories',
    prompt: 'Story vertical com oferta, beneficio principal e chamada para WhatsApp.',
    layers: [
      { name: 'Oferta', text: 'OFERTA ESPECIAL', x: 130, y: 140, width: 420, height: 62, color: '#00F0FF' },
      { name: 'Mensagem', text: 'Fale conosco hoje', x: 165, y: 360, width: 360, height: 52, color: '#111827' },
    ],
  },
  {
    id: 'reels-hook',
    title: 'Reels hook',
    type: 'Video',
    prompt: 'Video vertical de 15 segundos com hook nos 3 primeiros segundos e CTA final.',
    layers: [
      { name: 'Hook', text: 'PARE DE PERDER CLIENTES', x: 105, y: 130, width: 500, height: 70, color: '#07111f' },
      { name: 'CTA final', text: 'Conecte suas redes na AXI', x: 110, y: 400, width: 500, height: 54, color: '#A020F0' },
    ],
  },
];

function LayoutIcon({ size = 20 }: { size?: string | number }) {
  return <Shapes size={size} />;
}

function kindColor(kind: AxiLayerKind) {
  if (kind === 'text') return '#111827';
  if (kind === 'shape') return '#a99b92';
  if (kind === 'image') return '#dbeafe';
  if (kind === 'video') return '#082f49';
  if (kind === 'audio') return '#4c1d95';
  return '#13313a';
}

function formatTime(seconds: number) {
  return `${seconds.toFixed(1)}s`;
}

function CanvasImageLayer({
  layer,
  selected,
  onSelect,
  onChange,
}: {
  layer: AxiStudioLayer;
  selected: boolean;
  onSelect: () => void;
  onChange: (patch: Partial<AxiStudioLayer>) => void;
}) {
  const [image, setImage] = useState<HTMLImageElement | null>(null);

  useEffect(() => {
    if (!layer.src) {
      setImage(null);
      return;
    }
    const next = new window.Image();
    next.crossOrigin = 'anonymous';
    next.onload = () => setImage(next);
    next.onerror = () => setImage(null);
    next.src = layer.src;
  }, [layer.src]);

  if (!image) {
    return (
      <Rect
        x={layer.x}
        y={layer.y}
        width={layer.width}
        height={layer.height}
        fill="#dbeafe"
        opacity={layer.opacity}
        cornerRadius={12}
        stroke={selected ? '#A020F0' : undefined}
        strokeWidth={selected ? 2 : 0}
        draggable={!layer.locked}
        onClick={onSelect}
        onTap={onSelect}
        onDragEnd={(event) => onChange({ x: event.target.x(), y: event.target.y() })}
      />
    );
  }

  return (
    <KonvaImage
      image={image}
      x={layer.x}
      y={layer.y}
      width={layer.width}
      height={layer.height}
      opacity={layer.opacity}
      cornerRadius={10}
      draggable={!layer.locked}
      onClick={onSelect}
      onTap={onSelect}
      onDragEnd={(event) => onChange({ x: event.target.x(), y: event.target.y() })}
    />
  );
}

export function UnifiedStudioEditorPage() {
  const studio = useStudioV2({ defaultType: 'unified-editor', defaultTitle: 'Axi Studio Web' });
  const { pushToast } = useToast();
  const autosave = useAxiStudioAutosave('axi_studio_unified_autosave');
  const [openExport, setOpenExport] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [webQuery, setWebQuery] = useState('marketing brasil');
  const [webImages, setWebImages] = useState<StudioWebImage[]>([]);
  const [webImagesLoading, setWebImagesLoading] = useState(false);
  const [webImagesError, setWebImagesError] = useState<string | null>(null);

  const {
    activeTool,
    selectedLayerId,
    zoom,
    layers,
    clips,
    mode,
    prompt,
    setActiveTool,
    selectLayer,
    setZoom,
    setPrompt,
    addLayer,
    updateLayer,
    removeLayer,
    reorderLayer,
    addClip,
    splitClip,
    trimClip,
    setMode,
  } = useAxiStudioStore();

  const activeToolId = (activeTool || 'select') as StudioToolId;
  const selectedLayer = useMemo(() => layers.find((layer) => layer.id === selectedLayerId) ?? null, [layers, selectedLayerId]);
  const activeEffects = useMemo(() => layers.filter((layer) => layer.kind === 'effect'), [layers]);
  const totalDuration = useMemo(() => clips.reduce((total, clip) => Math.max(total, clip.start + clip.duration), 0), [clips]);

  async function saveUnifiedProject() {
    await studio.saveProject({
      status: 'saved',
      metadata: { editor: 'unified', mode, activeTool },
      canvas_data: getAxiStudioSnapshot(),
      layers: layers as unknown as Array<Record<string, unknown>>,
      timeline_data: { clips, duration: totalDuration },
    });
  }

  function addTextLayer(preset = textPresets[0]) {
    const id = addLayer({
      name: preset.label,
      kind: 'text',
      visible: true,
      locked: false,
      opacity: 1,
      blendMode: 'normal',
      x: 190,
      y: 210,
      width: 340,
      height: 76,
      rotation: 0,
      text: preset.text,
      color: preset.color,
      start: 0,
      duration: 8,
    });
    addClip({ layerId: id, track: 'text', label: preset.label, start: 0, duration: 8 });
  }

  function addEmojiLayer(emoji: string) {
    const id = addLayer({
      name: `Emoji ${emoji}`,
      kind: 'text',
      visible: true,
      locked: false,
      opacity: 1,
      blendMode: 'normal',
      x: 310,
      y: 220,
      width: 96,
      height: 96,
      rotation: 0,
      text: emoji,
      color: '#111827',
      start: 0,
      duration: 8,
    });
    addClip({ layerId: id, track: 'overlay', label: emoji, start: 0, duration: 8 });
  }

  function addShapeLayer(color = '#00F0FF') {
    const id = addLayer({
      name: 'Forma',
      kind: 'shape',
      visible: true,
      locked: false,
      opacity: 0.9,
      blendMode: 'normal',
      x: 230,
      y: 180,
      width: 180,
      height: 130,
      rotation: 0,
      color,
      start: 0,
      duration: 8,
    });
    addClip({ layerId: id, track: 'overlay', label: 'Forma', start: 0, duration: 8 });
  }

  function addWebImage(url: string, label: string) {
    const id = addLayer({
      name: label,
      kind: 'image',
      visible: true,
      locked: false,
      opacity: 1,
      blendMode: 'normal',
      x: 145,
      y: 100,
      width: 430,
      height: 320,
      rotation: 0,
      src: url,
      color: '#dbeafe',
      start: 0,
      duration: 8,
    });
    addClip({ layerId: id, track: 'overlay', label, start: 0, duration: 8 });
  }

  function applyEffect(effect: (typeof effectPresets)[number]) {
    const id = addLayer({
      name: `Efeito ${effect.label}`,
      kind: 'effect',
      visible: true,
      locked: false,
      opacity: effect.opacity,
      blendMode: 'screen',
      x: 0,
      y: 0,
      width: 720,
      height: 540,
      rotation: 0,
      color: effect.color,
      start: 0,
      duration: totalDuration || 8,
    });
    addClip({ layerId: id, track: 'effect', label: effect.label, start: 0, duration: totalDuration || 8 });
    pushToast(`Efeito "${effect.label}" aplicado.`, 'success');
  }

  function applyTemplate(template: (typeof templatePresets)[number]) {
    setPrompt(template.prompt);
    template.layers.forEach((layer) => addTextLayer({ label: layer.name, text: layer.text, size: 34, color: layer.color }));
    pushToast(`Template "${template.title}" aplicado.`, 'success');
  }

  async function handleUpload(file: File) {
    if (!studio.currentProject) {
      pushToast('Aguarde o projeto carregar antes de enviar midia.', 'error');
      return;
    }
    if (file.size / 1024 / 1024 > 500) {
      pushToast('Arquivo acima de 500MB. Use um arquivo menor para manter o navegador estavel.', 'error');
      return;
    }
    try {
      const asset = await uploadStudioAsset({
        file,
        projectId: studio.currentProject.id,
        assetType: file.type.startsWith('video') ? 'video' : file.type.startsWith('audio') ? 'audio' : 'image',
      });
      const kind: AxiLayerKind = file.type.startsWith('video') ? 'video' : file.type.startsWith('audio') ? 'audio' : 'image';
      const id = addLayer({
        name: asset.name,
        kind,
        visible: true,
        locked: false,
        opacity: 1,
        blendMode: 'normal',
        x: 145,
        y: 105,
        width: 430,
        height: kind === 'audio' ? 72 : 360,
        rotation: 0,
        src: asset.file_url,
        color: kindColor(kind),
        start: 0,
        duration: kind === 'audio' ? 15 : 8,
      });
      addClip({ layerId: id, track: kind === 'audio' ? 'audio' : kind === 'video' ? 'video' : 'overlay', label: asset.name, start: 0, duration: kind === 'audio' ? 15 : 8 });
      pushToast('Midia enviada e adicionada ao canvas.', 'success');
    } catch {
      pushToast('Falha ao enviar midia.', 'error');
    }
  }

  async function runAiAction(action: string) {
    if (!studio.currentProject) return;
    setProcessing(true);
    try {
      if (action === 'captions') {
        await studioVideoCaptions({ project_id: studio.currentProject.id, prompt, options: { style: 'animated-bold' } });
      } else if (action === 'remove-background') {
        await studioImageRemoveBackground({ project_id: studio.currentProject.id, options: { layer_id: selectedLayer?.id, source: selectedLayer?.src } });
      } else if (action === 'magic-eraser') {
        await studioImageRetouch({ project_id: studio.currentProject.id, options: { eraser: true, layer_id: selectedLayer?.id, source: selectedLayer?.src } });
      } else {
        await studioAICreativeGenerate({ project_id: studio.currentProject.id, action, briefing: prompt });
      }
      pushToast('Acao concluida pelo backend.', 'success');
    } catch {
      pushToast('Falha ao executar. Nenhuma chave fica exposta no navegador.', 'error');
    } finally {
      setProcessing(false);
    }
  }

  function handleToolClick(toolId: StudioToolId) {
    setActiveTool(toolId);
    if (toolId === 'export') setOpenExport(true);
  }

  useEffect(() => {
    const query = webQuery.trim();
    if (query.length < 2) {
      setWebImages([]);
      setWebImagesError(null);
      return;
    }

    const controller = new AbortController();
    const timer = window.setTimeout(() => {
      setWebImagesLoading(true);
      setWebImagesError(null);
      searchStudioWebImages(query, 12)
        .then((images) => {
          if (!controller.signal.aborted) setWebImages(images);
        })
        .catch((error) => {
          if (!controller.signal.aborted) {
            setWebImages([]);
            setWebImagesError(error instanceof Error ? error.message : 'Busca de imagens indisponivel.');
          }
        })
        .finally(() => {
          if (!controller.signal.aborted) setWebImagesLoading(false);
        });
    }, 450);

    return () => {
      controller.abort();
      window.clearTimeout(timer);
    };
  }, [webQuery]);

  return (
    <>
      <div className="min-h-[calc(100vh-2rem)] bg-[linear-gradient(180deg,#030711,#07111f)] px-3 py-3 text-white md:px-4">
        <div className="mx-auto flex min-h-[calc(100vh-2rem)] w-full max-w-none flex-col gap-3">
          <StudioTopbar
            projectName={studio.projectName}
            saveState={processing ? 'saving' : studio.saveState}
            onSave={() => void saveUnifiedProject()}
            onExport={() => setOpenExport(true)}
            onDuplicate={() => void studio.duplicateProject()}
            onBackHome={() => window.history.back()}
          />

          <div className="grid min-h-0 flex-1 gap-3 lg:grid-cols-[minmax(0,1fr)_320px_76px] 2xl:grid-cols-[minmax(0,1fr)_360px_82px]">
            <main className="min-h-0 space-y-3">
              <div className="rounded-[1.75rem] border border-white/10 bg-white/[0.035] p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="text-xs font-black uppercase tracking-[0.24em] text-cyan">Axi Studio Web</p>
                    <h1 className="font-display text-2xl font-black">Editor Unificado</h1>
                    <p className="mt-1 text-sm text-slate-400">Clique em uma ferramenta para abrir suas opcoes. Nada fica fixo ocupando a tela.</p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {(['photo', 'video', 'ai'] as const).map((item) => (
                      <button
                        key={item}
                        type="button"
                        onClick={() => setMode(item)}
                        className={mode === item ? 'rounded-full bg-cyan px-4 py-2 text-sm font-black text-ink' : 'rounded-full border border-white/10 px-4 py-2 text-sm font-bold text-slate-300 hover:bg-white/[0.06]'}
                      >
                        {item === 'photo' ? 'Foto' : item === 'video' ? 'Video' : 'IA'}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <div className="relative overflow-hidden rounded-[2rem] border border-cyan/20 bg-[#eef2f7] p-4 shadow-[0_30px_90px_rgba(0,0,0,0.28)]">
                {selectedLayer ? (
                  <div className="absolute left-1/2 top-4 z-10 flex -translate-x-1/2 items-center gap-1 rounded-full border border-slate-300 bg-white px-3 py-2 text-sm font-bold text-slate-900 shadow-xl">
                    <button type="button" onClick={() => removeLayer(selectedLayer.id)} className="rounded-lg px-2 py-1 hover:bg-slate-100">Excluir</button>
                    <button type="button" onClick={() => reorderLayer(selectedLayer.id, 'up')} className="rounded-lg px-2 py-1 hover:bg-slate-100">Subir</button>
                    <button type="button" onClick={() => reorderLayer(selectedLayer.id, 'down')} className="rounded-lg px-2 py-1 hover:bg-slate-100">Descer</button>
                  </div>
                ) : null}

                <div className="flex min-h-[460px] items-center justify-center pt-12 xl:min-h-[540px]">
                  <Stage width={720} height={540} scaleX={zoom} scaleY={zoom} className="rounded-2xl bg-white shadow-2xl">
                    <Layer>
                      {[...layers].reverse().filter((layer) => layer.visible).map((layer) => {
                        const selected = selectedLayerId === layer.id;
                        if (layer.kind === 'image') {
                          return (
                            <CanvasImageLayer
                              key={layer.id}
                              layer={layer}
                              selected={selected}
                              onSelect={() => selectLayer(layer.id)}
                              onChange={(patch) => updateLayer(layer.id, patch)}
                            />
                          );
                        }
                        if (layer.kind === 'text') {
                          return (
                            <Text
                              key={layer.id}
                              x={layer.x}
                              y={layer.y}
                              text={layer.text || layer.name}
                              fontSize={layer.text && emojiSet.includes(layer.text) ? 72 : 36}
                              fontStyle="bold"
                              fill={layer.color || '#111827'}
                              opacity={layer.opacity}
                              draggable={!layer.locked}
                              onClick={() => selectLayer(layer.id)}
                              onTap={() => selectLayer(layer.id)}
                              onDragEnd={(event) => updateLayer(layer.id, { x: event.target.x(), y: event.target.y() })}
                            />
                          );
                        }
                        return (
                          <Rect
                            key={layer.id}
                            x={layer.x}
                            y={layer.y}
                            width={layer.width}
                            height={layer.height}
                            fill={layer.color || kindColor(layer.kind)}
                            opacity={layer.opacity}
                            cornerRadius={layer.kind === 'shape' ? 12 : 6}
                            stroke={selected ? '#A020F0' : undefined}
                            strokeWidth={selected ? 2 : 0}
                            draggable={!layer.locked && layer.kind !== 'effect'}
                            onClick={() => selectLayer(layer.id)}
                            onTap={() => selectLayer(layer.id)}
                            onDragEnd={(event) => updateLayer(layer.id, { x: event.target.x(), y: event.target.y() })}
                          />
                        );
                      })}
                    </Layer>
                  </Stage>
                </div>
              </div>

              <div className="rounded-[1.5rem] border border-white/10 bg-[#050a16]/95 p-4 backdrop-blur">
                <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-2 text-cyan">
                    <Film size={16} />
                    <p className="text-sm font-black">Timeline multi-track</p>
                    <span className="text-xs text-slate-500">{formatTime(totalDuration)}</span>
                  </div>
                  <div className="flex gap-2">
                    <button type="button" onClick={() => selectedLayerId && splitClip(clips.find((clip) => clip.layerId === selectedLayerId)?.id || '')} className="inline-flex items-center gap-2 rounded-xl border border-white/10 px-3 py-2 text-xs font-bold text-slate-200 hover:bg-white/[0.06]">
                      <Split size={14} /> Split
                    </button>
                    <button type="button" onClick={() => selectedLayerId && trimClip(clips.find((clip) => clip.layerId === selectedLayerId)?.id || '', -0.5)} className="inline-flex items-center gap-2 rounded-xl border border-white/10 px-3 py-2 text-xs font-bold text-slate-200 hover:bg-white/[0.06]">
                      <Scissors size={14} /> Trim
                    </button>
                    <button type="button" onClick={() => void runAiAction('captions')} className="inline-flex items-center gap-2 rounded-xl border border-cyan/30 bg-cyan/10 px-3 py-2 text-xs font-bold text-cyan">
                      <Zap size={14} /> Auto Captions
                    </button>
                    <button type="button" onClick={() => setOpenExport(true)} className="inline-flex items-center gap-2 rounded-xl bg-cyan px-3 py-2 text-xs font-black text-ink">
                      <Download size={14} /> Exportar
                    </button>
                  </div>
                </div>
                <div className="space-y-2 overflow-x-auto pb-1">
                  {(['video', 'overlay', 'text', 'audio', 'effect'] as const).map((track) => (
                    <div key={track} className="grid min-w-[720px] grid-cols-[80px_1fr] items-center gap-3">
                      <span className="text-xs font-bold uppercase text-slate-500">{track}</span>
                      <div className="relative h-11 rounded-2xl border border-white/10 bg-white/[0.035]">
                        {clips.filter((clip) => clip.track === track).map((clip) => (
                          <button
                            key={clip.id}
                            type="button"
                            onClick={() => selectLayer(clip.layerId)}
                            style={{ left: `${(clip.start / Math.max(1, totalDuration)) * 100}%`, width: `${Math.max(8, (clip.duration / Math.max(1, totalDuration)) * 100)}%` }}
                            className="absolute top-1 h-9 rounded-xl border border-cyan/30 bg-cyan/15 px-3 text-left text-xs font-bold text-cyan hover:bg-cyan/20"
                          >
                            {clip.label}
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <EditStatusBar
                selectedLayer={selectedLayer}
                activeTool={activeToolId}
                effects={activeEffects}
                zoom={zoom}
                autosaveStatus={autosave.status}
                onZoomChange={setZoom}
              />
            </main>

            <aside className="order-first min-h-0 overflow-hidden rounded-[1.75rem] border border-white/10 bg-white/[0.035] lg:order-none">
              <ToolPanel
                activeTool={activeToolId}
                layers={layers}
                selectedLayer={selectedLayer}
                selectedLayerId={selectedLayerId}
                webQuery={webQuery}
                webImages={webImages}
                webImagesLoading={webImagesLoading}
                webImagesError={webImagesError}
                onSetWebQuery={setWebQuery}
                onSelectLayer={selectLayer}
                onUpload={handleUpload}
                onAddText={addTextLayer}
                onAddEmoji={addEmojiLayer}
                onAddShape={addShapeLayer}
                onAddWebImage={addWebImage}
                onApplyEffect={applyEffect}
                onApplyTemplate={applyTemplate}
                onRunAiAction={(action) => void runAiAction(action)}
              />
            </aside>

            <aside className="rounded-[1.75rem] border border-white/10 bg-white/[0.035] p-2">
              <div className="flex gap-1 overflow-x-auto lg:block lg:space-y-1">
                {leftTools.map((tool) => {
                  const Icon = tool.icon;
                  const active = activeToolId === tool.id;
                  return (
                    <button
                      key={tool.id}
                      type="button"
                      onClick={() => handleToolClick(tool.id)}
                      className={[
                        'flex min-w-[68px] flex-col items-center gap-1 rounded-2xl px-2 py-3 text-[10px] font-bold transition lg:w-full lg:min-w-0',
                        active ? 'bg-cyan text-ink shadow-[0_0_24px_rgba(0,240,255,0.25)]' : 'text-slate-300 hover:bg-white/[0.07] hover:text-white',
                      ].join(' ')}
                      title={tool.label}
                    >
                      <Icon size={19} />
                      <span className="max-w-full truncate">{tool.label}</span>
                    </button>
                  );
                })}
              </div>
            </aside>
          </div>
        </div>
      </div>

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

function ToolPanel({
  activeTool,
  layers,
  selectedLayer,
  selectedLayerId,
  webQuery,
  webImages,
  webImagesLoading,
  webImagesError,
  onSetWebQuery,
  onSelectLayer,
  onUpload,
  onAddText,
  onAddEmoji,
  onAddShape,
  onAddWebImage,
  onApplyEffect,
  onApplyTemplate,
  onRunAiAction,
}: {
  activeTool: StudioToolId;
  layers: AxiStudioLayer[];
  selectedLayer: AxiStudioLayer | null;
  selectedLayerId: string | null;
  webQuery: string;
  webImages: StudioWebImage[];
  webImagesLoading: boolean;
  webImagesError: string | null;
  onSetWebQuery: (value: string) => void;
  onSelectLayer: (layerId: string | null) => void;
  onUpload: (file: File) => void | Promise<void>;
  onAddText: (preset?: (typeof textPresets)[number]) => void;
  onAddEmoji: (emoji: string) => void;
  onAddShape: (color?: string) => void;
  onAddWebImage: (url: string, label: string) => void;
  onApplyEffect: (effect: (typeof effectPresets)[number]) => void;
  onApplyTemplate: (template: (typeof templatePresets)[number]) => void;
  onRunAiAction: (action: string) => void;
}) {
  return (
    <div className="flex h-full max-h-[calc(100vh-8rem)] min-h-[520px] flex-col">
      <div className="border-b border-white/10 p-4">
        <p className="text-xs font-black uppercase tracking-[0.24em] text-cyan">{leftTools.find((tool) => tool.id === activeTool)?.label}</p>
        <p className="mt-1 text-sm text-slate-400">Painel contextual. Escolha uma acao para aplicar no projeto.</p>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto p-4">
        {activeTool === 'select' || activeTool === 'assets' ? (
          <div className="space-y-3">
            {layers.map((layer) => (
              <button
                key={layer.id}
                type="button"
                onClick={() => onSelectLayer(layer.id)}
                className={[
                  'flex w-full items-center gap-3 rounded-2xl border px-3 py-3 text-left transition',
                  selectedLayerId === layer.id ? 'border-cyan/50 bg-cyan/10' : 'border-white/10 bg-black/20 hover:border-white/20',
                ].join(' ')}
              >
                <Layers3 size={17} className="text-cyan" />
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-sm font-bold text-white">{layer.name}</span>
                  <span className="text-xs text-slate-500">{layer.kind} - {Math.round(layer.opacity * 100)}%</span>
                </span>
              </button>
            ))}
          </div>
        ) : null}

        {activeTool === 'upload' ? (
          <label className="flex min-h-56 cursor-pointer flex-col items-center justify-center gap-3 rounded-3xl border border-dashed border-cyan/35 bg-cyan/10 p-6 text-center text-cyan hover:bg-cyan/15">
            <ImagePlus size={34} />
            <span className="text-lg font-black">Enviar midia ate 500MB</span>
            <span className="text-sm text-cyan/80">Imagem, video ou audio. O arquivo entra no canvas e na timeline.</span>
            <input
              type="file"
              accept="image/*,video/*,audio/*"
              className="hidden"
              onChange={(event) => {
                const file = event.target.files?.[0];
                if (file) void onUpload(file);
                event.currentTarget.value = '';
              }}
            />
          </label>
        ) : null}

        {activeTool === 'text' ? (
          <div className="space-y-3">
            {textPresets.map((preset) => (
              <button key={preset.label} type="button" onClick={() => onAddText(preset)} className="w-full rounded-2xl border border-white/10 bg-white/[0.04] p-4 text-left hover:border-cyan/40">
                <span className="block text-lg font-black text-white">{preset.label}</span>
                <span className="text-sm text-slate-400">{preset.text}</span>
              </button>
            ))}
          </div>
        ) : null}

        {activeTool === 'templates' ? (
          <div className="grid gap-3">
            {templatePresets.map((template) => (
              <button key={template.id} type="button" onClick={() => onApplyTemplate(template)} className="min-h-32 rounded-3xl border border-white/10 bg-[radial-gradient(circle_at_top_left,rgba(0,240,255,0.18),transparent_45%),rgba(255,255,255,0.04)] p-4 text-left hover:border-cyan/40">
                <span className="rounded-full bg-black/30 px-2 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-cyan">{template.type}</span>
                <span className="mt-8 block text-lg font-black text-white">{template.title}</span>
                <span className="text-xs text-slate-400">{template.prompt}</span>
              </button>
            ))}
          </div>
        ) : null}

        {activeTool === 'effects' ? (
          <div className="grid grid-cols-2 gap-3">
            {effectPresets.map((effect) => (
              <button key={effect.id} type="button" onClick={() => onApplyEffect(effect)} className="rounded-2xl border border-white/10 bg-white/[0.04] p-3 text-left hover:border-cyan/40">
                <span className="mb-3 block h-16 rounded-xl" style={{ background: `linear-gradient(135deg, ${effect.color}, #07111f)` }} />
                <span className="text-sm font-black text-white">{effect.label}</span>
              </button>
            ))}
          </div>
        ) : null}

        {activeTool === 'emoji' ? (
          <div className="grid grid-cols-5 gap-2">
            {emojiSet.map((emoji) => (
              <button key={emoji} type="button" onClick={() => onAddEmoji(emoji)} className="grid aspect-square place-items-center rounded-2xl border border-white/10 bg-white/[0.04] text-2xl hover:border-cyan/40">
                {emoji}
              </button>
            ))}
          </div>
        ) : null}

        {activeTool === 'web-images' ? (
          <div className="space-y-4">
            <label className="block text-sm font-bold text-slate-300">
              Pesquisar imagens na web
              <input value={webQuery} onChange={(event) => onSetWebQuery(event.target.value)} className="mt-2 w-full rounded-2xl border border-white/10 bg-black/25 px-4 py-3 text-white outline-none focus:border-cyan/40" placeholder="ex: hotel, beleza, comida, marketing" />
            </label>
            {webImagesLoading ? <p className="rounded-2xl border border-cyan/20 bg-cyan/10 px-3 py-2 text-xs text-cyan">Buscando imagens reais...</p> : null}
            {webImagesError ? <p className="rounded-2xl border border-amber-400/25 bg-amber-400/10 px-3 py-2 text-xs text-amber-100">{webImagesError}</p> : null}
            <div className="grid grid-cols-2 gap-3">
              {webImages.map((image, index) => (
                <button key={`${image.id}-${index}`} type="button" onClick={() => onAddWebImage(image.image_url, image.title)} className="overflow-hidden rounded-2xl border border-white/10 bg-white/[0.04] text-left hover:border-cyan/40">
                  <img src={image.thumb_url} alt={image.title} className="h-28 w-full object-cover" loading="lazy" />
                  <span className="block truncate px-3 pt-2 text-xs font-bold text-white">{image.title}</span>
                  <span className="block truncate px-3 pb-2 text-[10px] text-slate-500">{image.provider}{image.author_name ? ` - ${image.author_name}` : ''}</span>
                </button>
              ))}
            </div>
            {!webImagesLoading && !webImagesError && webImages.length === 0 ? (
              <p className="text-xs text-slate-500">Digite um termo para buscar em providers reais configurados no backend.</p>
            ) : null}
          </div>
        ) : null}

        {activeTool === 'photo-ai' ? (
          <div className="space-y-3">
            {[
              ['text-to-image', 'Gerar imagem', 'Cria imagem com IA a partir do briefing.'],
              ['remove-background', 'Remover fundo', 'Usa backend para recorte real.'],
              ['magic-eraser', 'Borracha magica', 'Remove ou retoca area selecionada.'],
              ['inpainting', 'Substituir area', 'Troca partes com prompt.'],
              ['outpainting', 'Expandir imagem', 'Estende bordas mantendo estilo.'],
              ['upscale', 'Melhorar qualidade', 'Aumenta nitidez e resolucao.'],
            ].map(([id, title, desc]) => (
              <button key={id} type="button" onClick={() => onRunAiAction(id)} className="flex w-full items-start gap-3 rounded-2xl border border-white/10 bg-white/[0.04] px-3 py-3 text-left transition hover:border-cyan/35">
                <Sparkles size={16} className="mt-0.5 text-cyan" />
                <span>
                  <span className="block text-sm font-black text-white">{title}</span>
                  <span className="text-xs text-slate-500">{desc}</span>
                </span>
              </button>
            ))}
          </div>
        ) : null}

        {activeTool === 'video' || activeTool === 'captions' ? (
          <div className="space-y-3">
            <button type="button" onClick={() => onRunAiAction('captions')} className="w-full rounded-2xl border border-cyan/30 bg-cyan/10 px-4 py-3 text-left font-black text-cyan">Gerar legendas automaticas</button>
            <button type="button" onClick={() => onRunAiAction('text-to-video')} className="w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-left font-black text-white">Text-to-Video</button>
            <button type="button" onClick={() => onRunAiAction('image-to-video')} className="w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-left font-black text-white">Image-to-Video</button>
          </div>
        ) : null}

        {selectedLayer ? (
          <div className="mt-4 rounded-2xl border border-white/10 bg-black/20 p-3">
            <p className="text-sm font-black text-white">Selecionado: {selectedLayer.name}</p>
            <p className="mt-1 text-xs text-slate-500">{selectedLayer.kind} - {Math.round(selectedLayer.opacity * 100)}% opacidade</p>
          </div>
        ) : null}
      </div>
    </div>
  );
}

function EditStatusBar({
  selectedLayer,
  activeTool,
  effects,
  zoom,
  autosaveStatus,
  onZoomChange,
}: {
  selectedLayer: AxiStudioLayer | null;
  activeTool: string;
  effects: AxiStudioLayer[];
  zoom: number;
  autosaveStatus: string;
  onZoomChange: (zoom: number) => void;
}) {
  return (
    <div className="rounded-[1.25rem] border border-white/10 bg-white/[0.035] px-4 py-3">
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-slate-400">
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded-full bg-cyan/10 px-3 py-1 font-bold text-cyan">Ferramenta: {activeTool}</span>
          <span className="rounded-full bg-white/[0.06] px-3 py-1">Camada: {selectedLayer?.name ?? 'nenhuma'}</span>
          <span className="rounded-full bg-white/[0.06] px-3 py-1">Efeitos: {effects.length ? effects.map((effect) => effect.name.replace('Efeito ', '')).join(', ') : 'nenhum'}</span>
          <span className="rounded-full bg-white/[0.06] px-3 py-1">Autosave: {autosaveStatus}</span>
        </div>
        <label className="flex items-center gap-2 font-bold text-slate-300">
          Zoom {Math.round(zoom * 100)}%
          <input type="range" min={20} max={200} value={Math.round(zoom * 100)} onChange={(event) => onZoomChange(Number(event.target.value) / 100)} className="w-40" />
        </label>
      </div>
    </div>
  );
}


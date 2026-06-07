import { type CSSProperties, type DragEvent, type ElementType, type ReactNode, useEffect, useMemo, useState } from 'react';
import {
  Captions,
  Download,
  Eraser,
  Film,
  FolderOpen,
  ImagePlus,
  Layers3,
  Maximize2,
  MousePointer2,
  Palette,
  Pause,
  Play,
  Plus,
  Search,
  Scissors,
  Shapes,
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
  listStudioTemplateCatalog,
  uploadStudioAsset,
} from '../../../services/studio.service';
import type { AxiLayerKind, AxiStudioClip, AxiStudioLayer } from '../../../store/axiStudioStore';
import type { StudioWebImage } from '../../../types/studioV2';
import { getAxiStudioSnapshot, useAxiStudioStore } from '../../../store/axiStudioStore';
import { StudioExportModal } from './StudioExportModal';
import { StudioTopbar } from './StudioTopbar';
import { catalogItemToTemplate, templateToStudioSnapshot, type AxiTemplateDefinition } from './templates/axiStudioTemplates';

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

const workspaces = [
  { id: 'editing', label: 'Editing' },
  { id: 'color', label: 'Color' },
  { id: 'audio', label: 'Audio' },
  { id: 'graphics', label: 'Graphics' },
  { id: 'ai', label: 'IA Generate' },
];

const trackMeta: Record<AxiStudioClip['track'], { label: string; accent: string; bg: string }> = {
  video: { label: 'V1 Video', accent: '#38bdf8', bg: 'rgba(56, 189, 248, 0.16)' },
  overlay: { label: 'V2 Overlay', accent: '#f97316', bg: 'rgba(249, 115, 22, 0.14)' },
  text: { label: 'T1 Texto', accent: '#c026d3', bg: 'rgba(192, 38, 211, 0.16)' },
  audio: { label: 'A1 Audio', accent: '#22c55e', bg: 'rgba(34, 197, 94, 0.14)' },
  effect: { label: 'FX Efeitos', accent: '#fb923c', bg: 'rgba(251, 146, 60, 0.14)' },
};

function LayoutIcon({ size = 20 }: { size?: string | number }) {
  return <Shapes size={size} />;
}

interface StudioDragEvent {
  target: {
    x: () => number;
    y: () => number;
  };
}

interface CanvasNodeProps {
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  opacity?: number;
  fill?: string;
  stroke?: string;
  strokeWidth?: number;
  cornerRadius?: number;
  draggable?: boolean;
  children?: ReactNode;
  onClick?: () => void;
  onTap?: () => void;
  onDragEnd?: (event: StudioDragEvent) => void;
}

function canvasNodeStyle(props: CanvasNodeProps): CSSProperties {
  return {
    position: 'absolute',
    left: props.x ?? 0,
    top: props.y ?? 0,
    width: props.width,
    height: props.height,
    opacity: props.opacity,
    borderRadius: props.cornerRadius,
    border: props.stroke ? `${props.strokeWidth ?? 1}px solid ${props.stroke}` : undefined,
    cursor: props.draggable ? 'move' : 'default',
    userSelect: 'none',
  };
}

function emitCanvasDrag(event: DragEvent<HTMLElement>, onDragEnd?: (event: StudioDragEvent) => void) {
  if (!onDragEnd) return;
  const parent = event.currentTarget.parentElement?.getBoundingClientRect();
  const x = parent ? event.clientX - parent.left : event.currentTarget.offsetLeft;
  const y = parent ? event.clientY - parent.top : event.currentTarget.offsetTop;
  onDragEnd({ target: { x: () => x, y: () => y } });
}

function Stage({
  width,
  height,
  scaleX = 1,
  scaleY = 1,
  className,
  children,
}: {
  width: number;
  height: number;
  scaleX?: number;
  scaleY?: number;
  className?: string;
  children: ReactNode;
}) {
  return (
    <div
      className={className}
      style={{
        position: 'relative',
        width,
        height,
        transform: `scale(${scaleX}, ${scaleY})`,
        transformOrigin: 'top left',
      }}
    >
      {children}
    </div>
  );
}

function Layer({ children }: { children: ReactNode }) {
  return <>{children}</>;
}

function Rect(props: CanvasNodeProps) {
  return (
    <div
      draggable={props.draggable}
      onClick={props.onClick}
      onDragEnd={(event) => emitCanvasDrag(event, props.onDragEnd)}
      style={{ ...canvasNodeStyle(props), background: props.fill }}
    />
  );
}

function Text(props: CanvasNodeProps & { text: string; fontSize?: number; fontFamily?: string; fontStyle?: string }) {
  return (
    <div
      draggable={props.draggable}
      onClick={props.onClick}
      onDragEnd={(event) => emitCanvasDrag(event, props.onDragEnd)}
      style={{
        ...canvasNodeStyle(props),
        color: props.fill,
        fontSize: props.fontSize,
        fontFamily: props.fontFamily,
        fontWeight: props.fontStyle === 'bold' ? 700 : 500,
        display: 'flex',
        alignItems: 'center',
        whiteSpace: 'pre-wrap',
      }}
    >
      {props.text}
    </div>
  );
}

function KonvaImage(props: CanvasNodeProps & { image: HTMLImageElement }) {
  return (
    <img
      src={props.image.src}
      draggable={props.draggable}
      onClick={props.onClick}
      onDragEnd={(event) => emitCanvasDrag(event, props.onDragEnd)}
      style={{ ...canvasNodeStyle(props), objectFit: 'cover', display: 'block' }}
      alt=""
    />
  );
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
  const [workspace, setWorkspace] = useState('editing');
  const [isPlaying, setIsPlaying] = useState(false);
  const [timelineZoom, setTimelineZoom] = useState(1);
  const [templates, setTemplates] = useState<AxiTemplateDefinition[]>([]);
  const [templatesLoading, setTemplatesLoading] = useState(false);
  const [templatesError, setTemplatesError] = useState<string | null>(null);

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
    loadTemplate,
    setMode,
  } = useAxiStudioStore();

  const activeToolId = (activeTool || 'select') as StudioToolId;
  const selectedLayer = useMemo(() => layers.find((layer) => layer.id === selectedLayerId) ?? null, [layers, selectedLayerId]);
  const activeEffects = useMemo(() => layers.filter((layer) => layer.kind === 'effect'), [layers]);
  const totalDuration = useMemo(() => clips.reduce((total, clip) => Math.max(total, clip.start + clip.duration), 0), [clips]);
  const hasMedia = useMemo(() => layers.some((layer) => ['image', 'video', 'audio'].includes(layer.kind)), [layers]);

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

  function applyTemplate(template: AxiTemplateDefinition) {
    loadTemplate(templateToStudioSnapshot(template));
    setZoom(1);
    pushToast(`Template "${template.name}" aplicado como composicao editavel.`, 'success');
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
    setTemplatesLoading(true);
    setTemplatesError(null);
    listStudioTemplateCatalog()
      .then((items) => setTemplates(items.map(catalogItemToTemplate)))
      .catch((error) => {
        setTemplates([]);
        setTemplatesError(error instanceof Error ? error.message : 'Catalogo de templates indisponivel.');
      })
      .finally(() => setTemplatesLoading(false));
  }, []);

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
                    <p className="mt-1 text-sm text-slate-400">Workspace profissional para campanha, video, foto, assets e IA em um fluxo unico.</p>
                  </div>
                  <div className="flex flex-wrap items-center gap-2">
                    <div className="flex rounded-2xl border border-white/10 bg-black/20 p-1">
                      {workspaces.map((item) => (
                        <button
                          key={item.id}
                          type="button"
                          onClick={() => setWorkspace(item.id)}
                          className={workspace === item.id ? 'rounded-xl bg-white px-3 py-1.5 text-xs font-black text-ink' : 'rounded-xl px-3 py-1.5 text-xs font-bold text-slate-400 hover:text-white'}
                        >
                          {item.label}
                        </button>
                      ))}
                    </div>
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

              <div className="relative overflow-hidden rounded-[2rem] border border-cyan/20 bg-[radial-gradient(circle_at_50%_0%,rgba(34,211,238,0.15),transparent_34%),#eef2f7] p-4 shadow-[0_30px_90px_rgba(0,0,0,0.28)]">
                <div className="absolute left-4 top-4 z-10 flex flex-wrap gap-2">
                  <span className="rounded-full bg-slate-950/80 px-3 py-1 text-xs font-bold text-cyan shadow-lg">1080x1920</span>
                  <span className="rounded-full bg-slate-950/80 px-3 py-1 text-xs font-bold text-white shadow-lg">30 FPS</span>
                  <span className="rounded-full bg-slate-950/80 px-3 py-1 text-xs font-bold text-white shadow-lg">{formatTime(totalDuration || 15)}</span>
                </div>
                {selectedLayer ? (
                  <div className="absolute left-1/2 top-4 z-20 flex -translate-x-1/2 items-center gap-1 rounded-full border border-slate-300 bg-white px-3 py-2 text-sm font-bold text-slate-900 shadow-xl">
                    <button type="button" onClick={() => removeLayer(selectedLayer.id)} className="rounded-lg px-2 py-1 hover:bg-slate-100">Excluir</button>
                    <button type="button" onClick={() => reorderLayer(selectedLayer.id, 'up')} className="rounded-lg px-2 py-1 hover:bg-slate-100">Subir</button>
                    <button type="button" onClick={() => reorderLayer(selectedLayer.id, 'down')} className="rounded-lg px-2 py-1 hover:bg-slate-100">Descer</button>
                  </div>
                ) : null}

                <div className="flex min-h-[460px] items-center justify-center pt-12 xl:min-h-[540px]">
                  <div className="relative">
                    {!hasMedia ? (
                      <div className="absolute inset-10 z-10 grid place-items-center rounded-3xl border border-dashed border-slate-400/70 bg-white/65 text-center text-slate-700 backdrop-blur-sm">
                        <div>
                          <UploadCloud className="mx-auto mb-3 text-slate-500" size={34} />
                          <p className="text-lg font-black">Arraste uma mídia ou clique em Upload</p>
                          <p className="mt-1 text-sm">Depois corte, aplique efeitos, legendas e exporte a campanha.</p>
                        </div>
                      </div>
                    ) : null}
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
                              fontSize={layer.text && emojiSet.includes(layer.text) ? 72 : layer.fontSize ?? 36}
                              fontFamily={layer.fontFamily ?? 'Inter'}
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

                <div className="absolute bottom-4 left-1/2 z-20 flex -translate-x-1/2 items-center gap-2 rounded-full border border-slate-300 bg-white/95 px-3 py-2 text-slate-900 shadow-xl">
                  <button type="button" onClick={() => setIsPlaying((value) => !value)} className="grid h-9 w-9 place-items-center rounded-full bg-cyan text-ink shadow-md" title="Play/Pause">
                    {isPlaying ? <Pause size={16} /> : <Play size={16} />}
                  </button>
                  <button type="button" onClick={() => setZoom(1)} className="rounded-full px-3 py-1.5 text-xs font-black hover:bg-slate-100">Fit</button>
                  <button type="button" className="grid h-9 w-9 place-items-center rounded-full hover:bg-slate-100" title="Tela cheia">
                    <Maximize2 size={16} />
                  </button>
                </div>
              </div>

              <TimelinePanel
                clips={clips}
                totalDuration={totalDuration}
                selectedLayerId={selectedLayerId}
                timelineZoom={timelineZoom}
                onTimelineZoomChange={setTimelineZoom}
                onSelectLayer={selectLayer}
                onSplitClip={splitClip}
                onTrimClip={trimClip}
                onCaptions={() => void runAiAction('captions')}
                onExport={() => setOpenExport(true)}
                onAddTrack={() => addShapeLayer('#00F0FF')}
              />

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
                templates={templates}
                templatesLoading={templatesLoading}
                templatesError={templatesError}
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
  templates,
  templatesLoading,
  templatesError,
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
  onApplyTemplate: (template: AxiTemplateDefinition) => void;
  templates: AxiTemplateDefinition[];
  templatesLoading: boolean;
  templatesError: string | null;
  onRunAiAction: (action: string) => void;
}) {
  return (
    <div className="flex h-full max-h-[calc(100vh-8rem)] min-h-[520px] flex-col">
      <div className="border-b border-white/10 p-4">
        <p className="text-xs font-black uppercase tracking-[0.24em] text-cyan">Painel contextual</p>
        <h2 className="mt-1 text-xl font-black text-white">{leftTools.find((tool) => tool.id === activeTool)?.label}</h2>
        <p className="mt-1 text-sm text-slate-400">
          {selectedLayer ? `Ajustes de ${selectedLayer.name}.` : 'Escolha uma ferramenta ou selecione uma camada.'} Nada fica fixo ocupando a tela.
        </p>
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
            <p className="text-xs text-slate-500">Templates sao composicoes editaveis: camadas, timeline, assets, animacoes e regioes dinamicas.</p>
            {templatesLoading ? <p className="rounded-2xl border border-cyan/20 bg-cyan/10 px-3 py-2 text-xs text-cyan">Carregando templates do banco...</p> : null}
            {templatesError ? <p className="rounded-2xl border border-amber-400/25 bg-amber-400/10 px-3 py-2 text-xs text-amber-100">{templatesError}</p> : null}
            {!templatesLoading && !templatesError && templates.length === 0 ? (
              <p className="rounded-2xl border border-white/10 bg-black/20 px-3 py-2 text-xs text-slate-400">Nenhum template ativo cadastrado no banco.</p>
            ) : null}
            {templates.map((template) => (
              <button key={template.id} type="button" onClick={() => onApplyTemplate(template)} className="overflow-hidden rounded-3xl border border-white/10 bg-white/[0.04] text-left hover:border-cyan/40">
                <span className="block h-24 border-b border-white/10" style={{ background: template.thumbnailGradient }} />
                <span className="block p-4">
                  <span className="flex items-center justify-between gap-2">
                    <span className="rounded-full bg-black/30 px-2 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-cyan">{template.category}</span>
                    <span className={template.premium ? 'rounded-full bg-amber-400/15 px-2 py-1 text-[10px] font-black text-amber-200' : 'rounded-full bg-emerald-400/10 px-2 py-1 text-[10px] font-black text-emerald-200'}>
                      {template.premium ? 'PRO' : 'Livre'}
                    </span>
                  </span>
                  <span className="mt-3 block text-lg font-black text-white">{template.name}</span>
                  <span className="text-xs text-slate-400">{template.previewLabel} - {template.templateJson.layers.length} layers - {template.templateJson.clips.length} clips</span>
                </span>
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
          <div className="mt-4 space-y-3">
            <div className="rounded-2xl border border-cyan/20 bg-cyan/10 p-3">
              <p className="text-sm font-black text-white">Selecionado: {selectedLayer.name}</p>
              <p className="mt-1 text-xs text-cyan/80">{selectedLayer.kind} - {Math.round(selectedLayer.opacity * 100)}% opacidade</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-black/20 p-3">
              <p className="text-xs font-black uppercase tracking-[0.2em] text-slate-500">Transformacao</p>
              <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                <span className="rounded-xl bg-white/[0.04] px-3 py-2 text-slate-300">X {Math.round(selectedLayer.x)}</span>
                <span className="rounded-xl bg-white/[0.04] px-3 py-2 text-slate-300">Y {Math.round(selectedLayer.y)}</span>
                <span className="rounded-xl bg-white/[0.04] px-3 py-2 text-slate-300">W {Math.round(selectedLayer.width)}</span>
                <span className="rounded-xl bg-white/[0.04] px-3 py-2 text-slate-300">H {Math.round(selectedLayer.height)}</span>
              </div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-black/20 p-3">
              <p className="text-xs font-black uppercase tracking-[0.2em] text-slate-500">Aparencia</p>
              <div className="mt-3 space-y-2 text-xs text-slate-300">
                <div className="flex items-center justify-between rounded-xl bg-white/[0.04] px-3 py-2">
                  <span>Visibilidade</span>
                  <span className={selectedLayer.visible ? 'text-emerald-300' : 'text-red-300'}>{selectedLayer.visible ? 'Ativa' : 'Oculta'}</span>
                </div>
                <div className="flex items-center justify-between rounded-xl bg-white/[0.04] px-3 py-2">
                  <span>Bloqueio</span>
                  <span>{selectedLayer.locked ? 'Bloqueada' : 'Editavel'}</span>
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

function TimelinePanel({
  clips,
  totalDuration,
  selectedLayerId,
  timelineZoom,
  onTimelineZoomChange,
  onSelectLayer,
  onSplitClip,
  onTrimClip,
  onCaptions,
  onExport,
  onAddTrack,
}: {
  clips: AxiStudioClip[];
  totalDuration: number;
  selectedLayerId: string | null;
  timelineZoom: number;
  onTimelineZoomChange: (value: number) => void;
  onSelectLayer: (layerId: string) => void;
  onSplitClip: (clipId: string) => void;
  onTrimClip: (clipId: string, seconds: number) => void;
  onCaptions: () => void;
  onExport: () => void;
  onAddTrack: () => void;
}) {
  const trackOrder: Array<AxiStudioClip['track']> = ['video', 'overlay', 'text', 'audio', 'effect'];
  const activeClip = clips.find((clip) => clip.layerId === selectedLayerId) ?? clips[0] ?? null;
  const duration = Math.max(totalDuration, 15);
  const timelineWidth = Math.max(920, Math.round(980 * timelineZoom));

  function clipLeft(clip: AxiStudioClip) {
    return `${Math.min(94, Math.max(0, (clip.start / duration) * 100))}%`;
  }

  function clipWidth(clip: AxiStudioClip) {
    return `${Math.max(8, Math.min(100, (clip.duration / duration) * 100))}%`;
  }

  return (
    <section className="rounded-[1.75rem] border border-white/10 bg-[linear-gradient(135deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] p-4">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <Film size={18} className="text-cyan" />
            <h2 className="font-display text-xl font-black text-white">Timeline profissional</h2>
            <span className="rounded-full bg-white/[0.06] px-2 py-1 text-xs font-bold text-slate-400">{formatTime(duration)}</span>
          </div>
          <p className="mt-1 text-xs text-slate-500">Faixas por tipo, keyframes visuais, zoom e acoes somente quando fazem sentido.</p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <label className="flex items-center gap-2 rounded-full border border-white/10 bg-black/20 px-3 py-2 text-xs font-bold text-slate-300">
            Zoom
            <input
              type="range"
              min={70}
              max={180}
              value={Math.round(timelineZoom * 100)}
              onChange={(event) => onTimelineZoomChange(Number(event.target.value) / 100)}
              className="w-28"
            />
          </label>
          <button type="button" onClick={onAddTrack} className="inline-flex items-center gap-2 rounded-full border border-white/10 px-3 py-2 text-xs font-black text-white hover:bg-white/[0.06]">
            <Plus size={14} /> Faixa
          </button>
          <button
            type="button"
            disabled={!activeClip}
            onClick={() => activeClip && onSplitClip(activeClip.id)}
            className="inline-flex items-center gap-2 rounded-full border border-white/10 px-3 py-2 text-xs font-black text-white hover:bg-white/[0.06] disabled:cursor-not-allowed disabled:opacity-40"
          >
            <Split size={14} /> Split
          </button>
          <button
            type="button"
            disabled={!activeClip}
            onClick={() => activeClip && onTrimClip(activeClip.id, Math.max(1, activeClip.duration - 1))}
            className="inline-flex items-center gap-2 rounded-full border border-white/10 px-3 py-2 text-xs font-black text-white hover:bg-white/[0.06] disabled:cursor-not-allowed disabled:opacity-40"
          >
            <Scissors size={14} /> Trim
          </button>
          <button type="button" onClick={onCaptions} className="inline-flex items-center gap-2 rounded-full border border-cyan/30 bg-cyan/10 px-3 py-2 text-xs font-black text-cyan hover:bg-cyan/15">
            <Zap size={14} /> Auto Captions
          </button>
          <button type="button" onClick={onExport} className="inline-flex items-center gap-2 rounded-full bg-cyan px-4 py-2 text-xs font-black text-ink shadow-[0_0_24px_rgba(0,240,255,0.25)]">
            <Download size={14} /> Exportar
          </button>
        </div>
      </div>

      <div className="overflow-x-auto rounded-3xl border border-white/10 bg-black/20 p-3">
        <div className="relative" style={{ width: timelineWidth }}>
          <div className="pointer-events-none absolute bottom-0 left-[22%] top-0 z-20 w-px bg-cyan/80 shadow-[0_0_18px_rgba(0,240,255,0.8)]">
            <span className="absolute -left-2 -top-2 h-4 w-4 rotate-45 rounded-[4px] bg-cyan" />
          </div>

          <div className="mb-2 grid grid-cols-[96px_1fr] gap-3 text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">
            <span>Track</span>
            <div className="grid grid-cols-6">
              {Array.from({ length: 6 }).map((_, index) => (
                <span key={index}>{formatTime((duration / 5) * index)}</span>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            {trackOrder.map((track) => {
              const meta = trackMeta[track];
              const trackClips = clips.filter((clip) => clip.track === track);

              return (
                <div key={track} className="grid min-h-[58px] grid-cols-[96px_1fr] gap-3">
                  <div className="flex items-center rounded-2xl border border-white/10 bg-white/[0.03] px-3">
                    <span className="text-xs font-black" style={{ color: meta.accent }}>{meta.label}</span>
                  </div>
                  <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-slate-950/55">
                    <div className="absolute inset-y-0 left-0 right-0 grid grid-cols-6">
                      {Array.from({ length: 6 }).map((_, index) => (
                        <span key={index} className="border-l border-white/[0.04]" />
                      ))}
                    </div>
                    {trackClips.map((clip) => {
                      const active = clip.layerId === selectedLayerId;
                      return (
                        <button
                          key={clip.id}
                          type="button"
                          onClick={() => onSelectLayer(clip.layerId)}
                          className={[
                            'absolute top-2 h-[40px] overflow-hidden rounded-xl border px-3 text-left text-xs font-black transition',
                            active ? 'shadow-[0_0_0_2px_rgba(0,240,255,0.22)]' : 'hover:brightness-125',
                          ].join(' ')}
                          style={{
                            left: clipLeft(clip),
                            width: clipWidth(clip),
                            background: meta.bg,
                            borderColor: active ? '#00F0FF' : meta.accent,
                            color: meta.accent,
                          }}
                        >
                          <span className="relative z-10 block truncate">{clip.label}</span>
                          {track === 'audio' ? (
                            <span className="absolute bottom-1 left-2 right-2 flex h-4 items-end gap-[2px] opacity-70">
                              {Array.from({ length: 18 }).map((_, index) => (
                                <span
                                  key={index}
                                  className="w-1 rounded-full bg-current"
                                  style={{ height: `${4 + ((index * 7) % 13)}px` }}
                                />
                              ))}
                            </span>
                          ) : null}
                          <span className="absolute left-1/4 top-1/2 h-2 w-2 -translate-y-1/2 rotate-45 rounded-[2px] bg-white/80" />
                          <span className="absolute left-2/3 top-1/2 h-2 w-2 -translate-y-1/2 rotate-45 rounded-[2px] bg-white/80" />
                        </button>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
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


import {
  Bot,
  Captions,
  Film,
  FolderOpen,
  Grip,
  Image,
  Layers,
  LayoutTemplate,
  Loader2,
  MessageSquareText,
  Music,
  Palette,
  PlayCircle,
  Plus,
  Shapes,
  SlidersHorizontal,
  Sparkles,
  Upload,
  Video,
  Wand2,
  Zap,
} from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';

import { useStudioV2 } from '../../../hooks/useStudioV2';
import { FALLBACK_STUDIO_TEMPLATES } from '../../../hooks/useStudioV2';
import { useToast } from '../../../hooks/useToast';
import { studioVideoCaptions, studioVideoGenerate, studioVideoVoiceover, uploadStudioAsset } from '../../../services/studio.service';
import { StudioCanvas } from './StudioCanvas';
import { StudioExportModal } from './StudioExportModal';
import { StudioTimeline } from './StudioTimeline';
import { StudioTopbar } from './StudioTopbar';
import { StudioVideoContextPanel } from './StudioVideoContextPanel';

type EditorTool = 'Modelos' | 'Uploads' | 'Texto' | 'Midia' | 'Legendas' | 'Ajustes' | 'Efeitos' | 'Audio' | 'Camadas' | 'Marca' | 'Projetos' | 'Apps' | 'Midia Magica / IA';

type TimelineClip = {
  id: string;
  label: string;
  length: number;
  kind: string;
  assetUrl?: string;
};

const editorTools: Array<{ label: EditorTool; icon: typeof LayoutTemplate }> = [
  { label: 'Modelos', icon: LayoutTemplate },
  { label: 'Uploads', icon: Upload },
  { label: 'Texto', icon: MessageSquareText },
  { label: 'Midia', icon: Film },
  { label: 'Legendas', icon: Captions },
  { label: 'Ajustes', icon: SlidersHorizontal },
  { label: 'Efeitos', icon: Zap },
  { label: 'Audio', icon: Music },
  { label: 'Camadas', icon: Layers },
  { label: 'Marca', icon: Palette },
  { label: 'Projetos', icon: FolderOpen },
  { label: 'Apps', icon: Shapes },
  { label: 'Midia Magica / IA', icon: Bot },
];

const defaultClips: TimelineClip[] = [
  { id: 'intro', label: 'Intro hook', length: 3, kind: 'video' },
  { id: 'main', label: 'Cena principal', length: 8, kind: 'video' },
  { id: 'cta', label: 'CTA final', length: 4, kind: 'overlay' },
];

const templateGradients = [
  'linear-gradient(135deg,#2e1065,#c026d3 54%,#22d3ee)',
  'linear-gradient(135deg,#064e3b,#0891b2 52%,#f97316)',
  'linear-gradient(135deg,#082f49,#0ea5e9 48%,#a855f7)',
  'linear-gradient(135deg,#18181b,#16a34a 48%,#22d3ee)',
];

const effectGroups = [
  { group: 'Transicoes', items: ['Fade', 'Slide', 'Zoom', 'Blur', 'Flash'] },
  { group: 'Movimento', items: ['Pan', 'Zoom In', 'Zoom Out', 'Shake'] },
  { group: 'Texto', items: ['Digitacao', 'Fade Up', 'Neon', 'Glow'] },
  { group: 'Filtros', items: ['Warm', 'Cinematic', 'Clean', 'Vintage', 'Contrast'] },
];

const assetSections = [
  { label: 'Uploads', kind: 'upload', icon: Upload },
  { label: 'Imagens', kind: 'image', icon: Image },
  { label: 'Videos', kind: 'video', icon: Video },
  { label: 'Audios', kind: 'audio', icon: Music },
  { label: 'Stickers', kind: 'sticker', icon: Sparkles },
  { label: 'Icones', kind: 'icon', icon: Shapes },
  { label: 'Formas', kind: 'shape', icon: Shapes },
  { label: 'Fundos', kind: 'background', icon: Palette },
  { label: 'Brand Kit', kind: 'brand', icon: Palette },
];

function reorderClips(clips: TimelineClip[], sourceId: string, targetId: string) {
  const sourceIndex = clips.findIndex((clip) => clip.id === sourceId);
  const targetIndex = clips.findIndex((clip) => clip.id === targetId);
  if (sourceIndex === -1 || targetIndex === -1) return clips;
  const next = [...clips];
  const [moved] = next.splice(sourceIndex, 1);
  next.splice(targetIndex, 0, moved);
  return next;
}

function contextTool(activeTool: EditorTool): 'Editar' | 'Cortar' | 'Redimensionar' | 'Remover fundo' | 'Audio' | 'Texto' | 'Efeitos' | 'Camadas' | 'Legendas' | 'Filtros' {
  if (activeTool === 'Texto') return 'Texto';
  if (activeTool === 'Audio') return 'Audio';
  if (activeTool === 'Legendas') return 'Legendas';
  if (activeTool === 'Efeitos') return 'Efeitos';
  if (activeTool === 'Camadas') return 'Camadas';
  if (activeTool === 'Ajustes') return 'Filtros';
  return 'Editar';
}

export function VideoEditorStudioPage() {
  const navigate = useNavigate();
  const params = useParams();
  const [searchParams] = useSearchParams();
  const { pushToast } = useToast();
  const mediaInputRef = useRef<HTMLInputElement | null>(null);
  const projectId = params.projectId ? Number(params.projectId) : null;
  const forceNew = searchParams.get('mode') === 'new';
  const templateKey = searchParams.get('template');
  const routeMode = window.location.pathname.includes('/design') ? 'design' : 'video';

  const studio = useStudioV2({
    defaultType: routeMode === 'design' ? 'design-editor' : 'video-editor',
    defaultTitle: routeMode === 'design' ? 'Design sem titulo' : 'Editor de Video',
    projectId,
    forceNew,
  });

  const [activeTool, setActiveTool] = useState<EditorTool>('Modelos');
  const [openExport, setOpenExport] = useState(false);
  const [prompt, setPrompt] = useState('Video vertical de 15 segundos para lancamento premium com hook forte e CTA direto.');
  const [processing, setProcessing] = useState(false);
  const [clips, setClips] = useState<TimelineClip[]>(defaultClips);
  const [selectedClipId, setSelectedClipId] = useState<string | null>(defaultClips[0].id);
  const [uploadedMediaLabel, setUploadedMediaLabel] = useState<string | null>(null);
  const [selectedTemplateName, setSelectedTemplateName] = useState<string | null>(null);
  const [selectedEffect, setSelectedEffect] = useState<string | null>(null);

  useEffect(() => {
    const timelineData = studio.currentProject?.timeline_data;
    if (!timelineData || typeof timelineData !== 'object') return;
    const projectClips = Array.isArray((timelineData as { clips?: unknown }).clips)
      ? ((timelineData as { clips: TimelineClip[] }).clips)
      : null;
    if (projectClips && projectClips.length > 0) {
      setClips(projectClips);
      setSelectedClipId(projectClips[0]?.id || null);
    }
  }, [studio.currentProject?.id]);

  useEffect(() => {
    if (!templateKey || selectedTemplateName) return;
    const templates = studio.templates.length > 0 ? studio.templates : FALLBACK_STUDIO_TEMPLATES;
    const selectedTemplate = templates.find((template) => {
      const route = typeof template.template_data.route === 'string' ? template.template_data.route : '';
      return route.includes(`template=${templateKey}`) || String(template.id) === templateKey;
    });
    if (!selectedTemplate) return;
    applyTemplateToTimeline(selectedTemplate.name, selectedTemplate.template_data.clips);
  }, [templateKey, studio.templates.length, selectedTemplateName]);

  const selectedClip = useMemo(
    () => clips.find((clip) => clip.id === selectedClipId) || clips[0] || null,
    [clips, selectedClipId],
  );

  const totalDuration = useMemo(
    () => clips.reduce((total, clip) => total + clip.length, 0),
    [clips],
  );

  async function persistTimeline(nextClips: TimelineClip[], nextTool = activeTool) {
    await studio.saveProject({
      status: 'saved',
      metadata: { tool: nextTool, prompt, template: selectedTemplateName, selectedEffect },
      timeline_data: {
        clips: nextClips,
        activeTool: nextTool,
        selectedClipId,
      },
      canvas_data: {
        prompt,
        selectedClipId,
        selectedEffect,
      },
    });
  }

  async function handleRunAiAction(action: 'captions' | 'voiceover' | 'generate') {
    if (!studio.currentProject) return;
    setProcessing(true);
    try {
      if (action === 'captions') {
        await studioVideoCaptions({ project_id: studio.currentProject.id, prompt, options: { style: 'bold-modern' } });
      } else if (action === 'voiceover') {
        await studioVideoVoiceover({ project_id: studio.currentProject.id, prompt, options: { voice: 'pt-BR-female-pro' } });
      } else {
        await studioVideoGenerate({ project_id: studio.currentProject.id, prompt, options: { ratio: routeMode === 'video' ? '9:16' : '1080:1350', duration: 15, entry: routeMode } });
      }
      studio.setSaveState('dirty');
      pushToast('Acao de IA concluida no editor.', 'success');
    } catch {
      pushToast('Falha ao executar a acao de IA.', 'error');
    } finally {
      setProcessing(false);
    }
  }

  async function handleUploadMedia(file: File) {
    if (!studio.currentProject) return;
    try {
      const asset = await uploadStudioAsset({
        file,
        projectId: studio.currentProject.id,
        assetType: file.type.startsWith('video') ? 'video' : file.type.startsWith('image') ? 'image' : 'file',
      });
      const nextClip: TimelineClip = {
        id: `asset-${asset.id}`,
        label: asset.name,
        length: 6,
        kind: asset.asset_type,
        assetUrl: asset.file_url,
      };
      const nextClips = [...clips, nextClip];
      setClips(nextClips);
      setSelectedClipId(nextClip.id);
      setUploadedMediaLabel(asset.name);
      studio.setSaveState('dirty');
      pushToast('Midia adicionada ao projeto.', 'success');
    } catch {
      pushToast('Falha ao enviar midia para o projeto.', 'error');
    }
  }

  async function handleUploadAudio(file: File) {
    if (!studio.currentProject) return;
    try {
      const asset = await uploadStudioAsset({
        file,
        projectId: studio.currentProject.id,
        assetType: 'audio',
      });
      const nextClip: TimelineClip = {
        id: `audio-${asset.id}`,
        label: asset.name,
        length: 8,
        kind: 'audio',
      };
      setClips((current) => [...current, nextClip]);
      studio.setSaveState('dirty');
      pushToast('Audio enviado e vinculado ao projeto.', 'success');
    } catch {
      pushToast('Falha ao enviar audio.', 'error');
    }
  }

  function handleAddTextClip(text: string) {
    const nextClip: TimelineClip = {
      id: `text-${Date.now()}`,
      label: text.slice(0, 24) || 'Texto',
      length: 3,
      kind: 'text',
    };
    setClips((current) => [...current, nextClip]);
    setSelectedClipId(nextClip.id);
    studio.setSaveState('dirty');
    pushToast('Camada de texto adicionada.', 'success');
  }

  function applyTemplateToTimeline(templateName: string, templateClips: unknown) {
    const labels = Array.isArray(templateClips) && templateClips.length > 0
      ? templateClips.map((item) => String(item))
      : ['Hook', 'Cena principal', 'Oferta', 'CTA'];
    const nextClips = labels.map((label, index) => ({
      id: `template-${Date.now()}-${index}`,
      label,
      length: index === 0 ? 3 : index === labels.length - 1 ? 4 : 5,
      kind: index === labels.length - 1 ? 'overlay' : 'video',
    }));
    setClips(nextClips);
    setSelectedClipId(nextClips[0]?.id || null);
    setSelectedTemplateName(templateName);
    studio.setSaveState('dirty');
  }

  function handleSelectEffect(effect: string) {
    setSelectedEffect(effect);
    setActiveTool('Efeitos');
    studio.setSaveState('dirty');
  }

  return (
    <>
      <div className="min-h-screen bg-[radial-gradient(circle_at_14%_0%,rgba(192,38,211,0.2),transparent_34%),radial-gradient(circle_at_86%_4%,rgba(34,211,238,0.16),transparent_32%),linear-gradient(180deg,#050507,#0a0a12)] text-white">
        <div className="flex min-h-screen flex-col">
          <StudioTopbar
            projectName={studio.projectName}
            designType={routeMode === 'design' ? 'Design 1080 x 1350' : 'Video 9:16'}
            saveState={processing ? 'saving' : studio.saveState}
            onSave={() => void persistTimeline(clips)}
            onExport={() => setOpenExport(true)}
            onDuplicate={() => void studio.duplicateProject()}
            onBackHome={() => navigate('/app/studio')}
          />

          <div className="grid min-h-0 flex-1 grid-cols-[82px_minmax(0,1fr)] xl:grid-cols-[82px_minmax(0,1fr)_360px]">
            <aside className="border-r border-white/10 bg-black/25 px-2 py-3">
              <nav className="flex flex-col gap-1" aria-label="Ferramentas do editor">
                {editorTools.map((tool) => {
                  const Icon = tool.icon;
                  return (
                    <button
                      key={tool.label}
                      type="button"
                      onClick={() => setActiveTool(tool.label)}
                      className={activeTool === tool.label
                        ? 'flex h-[62px] flex-col items-center justify-center gap-1 rounded-xl border border-cyan-300/35 bg-cyan-300/15 text-[11px] font-bold text-cyan-50'
                        : 'flex h-[62px] flex-col items-center justify-center gap-1 rounded-xl border border-transparent text-[11px] font-semibold text-slate-300 transition hover:border-white/10 hover:bg-white/[0.055] hover:text-white'}
                    >
                      <Icon size={18} />
                      <span className="w-full truncate px-1 text-center">{tool.label}</span>
                    </button>
                  );
                })}
              </nav>
            </aside>

            <main className="min-h-0 px-4 py-4">
              <div className="mb-3 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-300">
                <div className="flex flex-wrap items-center gap-2">
                  {selectedTemplateName ? <span className="rounded-full border border-fuchsia-300/35 bg-fuchsia-300/10 px-3 py-1 text-fuchsia-100">Template: {selectedTemplateName}</span> : null}
                  {selectedEffect ? <span className="rounded-full border border-cyan-300/35 bg-cyan-300/10 px-3 py-1 text-cyan-100">Efeito: {selectedEffect}</span> : null}
                </div>
                <div className="flex items-center gap-2">
                  <span className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1">{clips.length} clips</span>
                  <span className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1">{totalDuration}s</span>
                  <span className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1">{routeMode === 'video' ? '9:16' : '1080 x 1350'}</span>
                </div>
              </div>

              <StudioCanvas title="Canvas" subtitle="Editor visual" onUpload={() => mediaInputRef.current?.click()} showHeader={false}>
                <div className="flex h-full min-h-[420px] items-center justify-center rounded-[1.5rem] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.03),rgba(0,0,0,0.18))] p-4">
                  {selectedClip?.assetUrl ? (
                    selectedClip.kind === 'image' ? (
                      <img src={selectedClip.assetUrl} alt={selectedClip.label} className="max-h-full max-w-full rounded-[1.25rem] object-contain" />
                    ) : (
                      <video src={selectedClip.assetUrl} controls className="max-h-full max-w-full rounded-[1.25rem]" />
                    )
                  ) : (
                    <div className={`flex ${routeMode === 'video' ? 'aspect-[9/16] h-full max-h-[480px]' : 'aspect-[4/5] h-[82%] max-h-[470px]'} flex-col items-center justify-center rounded-[1.75rem] border border-dashed border-fuchsia-300/30 bg-black/35 px-6 py-10 text-center shadow-[0_30px_80px_rgba(0,0,0,0.34)]`}>
                      <PlayCircle className="h-12 w-12 text-cyan-200 drop-shadow-[0_0_18px_rgba(34,211,238,0.45)]" />
                      <p className="mt-4 text-lg font-semibold text-white">{selectedClip?.label || 'Projeto pronto para editar'}</p>
                      <p className="mt-2 text-sm leading-6 text-slate-300">Use a barra lateral para templates, efeitos, assets e IA.</p>
                      <button type="button" onClick={() => mediaInputRef.current?.click()} className="mt-5 inline-flex items-center gap-2 rounded-xl bg-[var(--studio-gradient)] px-5 py-3 text-sm font-bold text-white shadow-[0_0_26px_rgba(192,38,211,0.24)]">
                        <Upload size={16} /> Inserir midia
                      </button>
                    </div>
                  )}
                </div>
              </StudioCanvas>

              <div className="mt-4 rounded-2xl border border-white/10 bg-[linear-gradient(180deg,rgba(12,12,18,0.95),rgba(5,5,7,0.98))] p-4 shadow-[0_-18px_60px_rgba(0,0,0,0.24)] backdrop-blur-xl">
                <div className="mb-3 flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2 text-cyan-100">
                    <Grip size={16} />
                    <p className="text-sm font-semibold">Timeline</p>
                    <span className="text-xs text-slate-400">Notas - 00:00 - Zoom 100% - Paginas</span>
                  </div>
                  <label className="inline-flex cursor-pointer items-center gap-2 rounded-xl border border-white/15 bg-white/[0.03] px-3 py-2 text-xs text-slate-200 transition hover:border-cyan/40 hover:text-white">
                    <Plus size={14} /> Inserir midia
                    <input
                      ref={mediaInputRef}
                      type="file"
                      accept="video/*,image/*"
                      className="hidden"
                      onChange={(event) => {
                        const file = event.target.files?.[0];
                        if (file) {
                          void handleUploadMedia(file);
                          event.currentTarget.value = '';
                        }
                      }}
                    />
                  </label>
                </div>

                <StudioTimeline
                  clips={clips}
                  activeClipId={selectedClipId}
                  onSelectClip={setSelectedClipId}
                  onReorderClips={(sourceId, targetId) => {
                    const next = reorderClips(clips, sourceId, targetId);
                    setClips(next);
                    studio.setSaveState('dirty');
                  }}
                />

                <div className="mt-3 flex gap-2 overflow-x-auto">
                  <button type="button" onClick={() => void handleRunAiAction('generate')} className="inline-flex items-center gap-2 rounded-xl border border-cyan/40 bg-cyan/10 px-4 py-3 text-sm font-semibold text-cyan-100">
                    <Wand2 size={15} /> Gerar variacao
                  </button>
                  {selectedClip ? (
                    <span className="rounded-xl border border-white/10 bg-white/[0.035] px-4 py-3 text-sm text-slate-300">Selecionado: {selectedClip.label}</span>
                  ) : null}
                </div>
              </div>
            </main>

            <aside className="hidden max-h-[calc(100vh-68px)] overflow-y-auto border-l border-white/10 bg-white/[0.045] p-4 backdrop-blur-xl xl:block">
              <div>
                <p className="text-[11px] uppercase tracking-[0.24em] text-cyan-300">{activeTool}</p>
                <h2 className="mt-1 font-display text-xl text-white">Painel contextual</h2>
                <p className="mt-1 text-sm text-slate-300">Ajustes aparecem conforme a ferramenta ou elemento selecionado.</p>
              </div>

              {(activeTool === 'Modelos' || activeTool === 'Projetos') ? (
                <section className="mt-4 rounded-2xl border border-white/10 bg-black/20 p-3">
                  <div className="mb-3 flex items-center gap-2 text-cyan-100">
                    <LayoutTemplate size={16} />
                    <p className="text-sm font-semibold">Templates</p>
                  </div>
                  <div className="space-y-3">
                    {(studio.templates.length > 0 ? studio.templates : FALLBACK_STUDIO_TEMPLATES).slice(0, 6).map((template, index) => (
                      <button
                        key={template.id}
                        type="button"
                        onClick={() => applyTemplateToTimeline(template.name, template.template_data.clips)}
                        className="w-full overflow-hidden rounded-xl border border-white/10 bg-white/[0.04] text-left transition hover:border-fuchsia-300/40"
                      >
                        <div className="h-20" style={{ background: template.preview_url ? undefined : templateGradients[index % templateGradients.length] }}>
                          {template.preview_url ? <img src={template.preview_url} alt={template.name} className="h-full w-full object-cover" /> : null}
                        </div>
                        <div className="p-3">
                          <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-cyan-300">{template.category}</p>
                          <p className="mt-1 text-sm font-bold text-white">{template.name}</p>
                        </div>
                      </button>
                    ))}
                  </div>
                </section>
              ) : null}

              {(activeTool === 'Uploads' || activeTool === 'Midia') ? (
                <section className="mt-4 rounded-2xl border border-white/10 bg-black/20 p-4">
                  <div className="mb-3 flex items-center gap-2 text-cyan-100">
                    <FolderOpen size={16} />
                    <p className="text-sm font-semibold">Biblioteca de assets</p>
                  </div>
                  <div className="grid gap-2 sm:grid-cols-2">
                    {assetSections.map((asset) => {
                      const Icon = asset.icon;
                      return (
                        <button key={asset.kind} type="button" onClick={() => asset.kind === 'upload' && mediaInputRef.current?.click()} className="rounded-xl border border-white/10 bg-white/[0.035] p-3 text-left hover:border-cyan-300/40">
                          <Icon size={17} className="text-cyan-200" />
                          <p className="mt-2 text-xs font-bold text-white">{asset.label}</p>
                          <p className="text-[10px] uppercase tracking-[0.14em] text-slate-500">Inserir midia</p>
                        </button>
                      );
                    })}
                  </div>
                  {uploadedMediaLabel ? <p className="mt-3 text-xs text-slate-300">Ultima midia: {uploadedMediaLabel}</p> : null}
                </section>
              ) : null}

              {activeTool === 'Efeitos' ? (
                <section className="mt-4 rounded-2xl border border-white/10 bg-black/20 p-4">
                  <div className="mb-3 flex items-center gap-2 text-cyan-100">
                    <Zap size={16} />
                    <p className="text-sm font-semibold">Biblioteca de efeitos</p>
                  </div>
                  <div className="space-y-3">
                    {effectGroups.map((group) => (
                      <div key={group.group}>
                        <p className="mb-2 text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">{group.group}</p>
                        <div className="flex flex-wrap gap-2">
                          {group.items.map((effect) => (
                            <button key={effect} type="button" onClick={() => handleSelectEffect(effect)} className={selectedEffect === effect ? 'rounded-xl border border-cyan-300/45 bg-cyan-300/15 px-3 py-2 text-xs font-bold text-cyan-50' : 'rounded-xl border border-white/10 bg-white/[0.035] px-3 py-2 text-xs text-slate-200 hover:border-cyan-300/40 hover:text-white'}>
                              {effect}
                            </button>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              ) : null}

              <div className={activeTool === 'Modelos' || activeTool === 'Uploads' || activeTool === 'Midia' || activeTool === 'Efeitos' ? 'mt-4' : 'mt-4'}>
                <label className="block text-xs text-slate-300">
                  <span className="mb-1 block">Prompt do projeto</span>
                  <textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} className="min-h-28 w-full rounded-xl border border-white/10 bg-black/30 px-3 py-2 text-sm text-white outline-none focus:border-cyan-300/45" />
                </label>
              </div>

              <div className="mt-4">
                <StudioVideoContextPanel
                  activeTool={contextTool(activeTool)}
                  onAddTextClip={handleAddTextClip}
                  onUploadAudio={handleUploadAudio}
                  onRunAiAction={handleRunAiAction}
                />
              </div>

              <section className="mt-4 rounded-2xl border border-white/10 bg-black/20 p-4">
                <div className="mb-3 flex items-center gap-2 text-cyan-100">
                  <Layers size={16} />
                  <p className="text-sm font-semibold">Camadas</p>
                </div>
                <div className="space-y-2">
                  {clips.slice(0, 6).map((clip) => (
                    <button
                      key={clip.id}
                      type="button"
                      onClick={() => setSelectedClipId(clip.id)}
                      className="flex w-full items-center justify-between rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2 text-left text-sm text-slate-200 transition hover:border-cyan/40 hover:text-white"
                    >
                      <span>{clip.label}</span>
                      <span className="text-xs text-slate-500">{clip.kind}</span>
                    </button>
                  ))}
                </div>
              </section>
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

      {studio.loading ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/80 backdrop-blur">
          <div className="inline-flex items-center gap-3 rounded-2xl border border-white/10 bg-black/40 px-4 py-3 text-sm text-white">
            <Loader2 className="h-4 w-4 animate-spin" /> Preparando editor...
          </div>
        </div>
      ) : null}
    </>
  );
}

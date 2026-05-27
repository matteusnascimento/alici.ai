import { Captions, FolderOpen, Grip, Image as ImageIcon, LayoutTemplate, Loader2, Mic2, PlayCircle, Plus, SlidersHorizontal, Type, UploadCloud, Wand2, type LucideIcon } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';

import { useStudioV2 } from '../../../hooks/useStudioV2';
import { useToast } from '../../../hooks/useToast';
import { studioVideoCaptions, studioVideoGenerate, studioVideoVoiceover, uploadStudioAsset } from '../../../services/studio.service';
import { StudioCanvas } from './StudioCanvas';
import { StudioContextToolbar } from './StudioContextToolbar';
import { StudioExportModal } from './StudioExportModal';
import { StudioTimeline } from './StudioTimeline';
import { StudioTopbar } from './StudioTopbar';
import { StudioVideoContextPanel } from './StudioVideoContextPanel';

type EditorTool = 'Editar' | 'Audio' | 'Texto' | 'Efeitos' | 'Camadas' | 'Legendas' | 'Filtros';
type SideTool = 'modelos' | 'uploads' | 'texto' | 'midia' | 'legendas' | 'ajustes' | 'projetos';

type TimelineClip = {
  id: string;
  label: string;
  length: number;
  kind: string;
  assetUrl?: string;
};

const editorTools: EditorTool[] = ['Editar', 'Audio', 'Texto', 'Efeitos', 'Camadas', 'Legendas', 'Filtros'];
const sideRailTools = [
  { id: 'modelos', label: 'Modelos', icon: LayoutTemplate },
  { id: 'uploads', label: 'Uploads', icon: UploadCloud },
  { id: 'texto', label: 'Texto', icon: Type },
  { id: 'midia', label: 'Midia', icon: ImageIcon },
  { id: 'legendas', label: 'Legendas', icon: Captions },
  { id: 'ajustes', label: 'Ajustes', icon: SlidersHorizontal },
  { id: 'projetos', label: 'Projetos', icon: FolderOpen },
] satisfies Array<{ id: SideTool; label: string; icon: LucideIcon }>;

const templateCards = [
  {
    title: 'Reels venda direta',
    type: '9:16',
    tone: 'bg-cyan/15',
    clips: [
      { id: 'tpl-hook', label: 'Hook de venda', length: 3, kind: 'video' },
      { id: 'tpl-benefit', label: 'Beneficio principal', length: 7, kind: 'video' },
      { id: 'tpl-cta', label: 'CTA direto', length: 4, kind: 'overlay' },
    ],
  },
  {
    title: 'Antes e depois',
    type: 'video',
    tone: 'bg-fuchsia-400/15',
    clips: [
      { id: 'tpl-before', label: 'Antes', length: 4, kind: 'video' },
      { id: 'tpl-transition', label: 'Transicao', length: 2, kind: 'effect' },
      { id: 'tpl-after', label: 'Depois', length: 5, kind: 'video' },
    ],
  },
  {
    title: 'Depoimento curto',
    type: 'social',
    tone: 'bg-emerald-400/15',
    clips: [
      { id: 'tpl-proof', label: 'Prova social', length: 5, kind: 'video' },
      { id: 'tpl-caption', label: 'Legenda de destaque', length: 3, kind: 'text' },
      { id: 'tpl-offer', label: 'Oferta final', length: 4, kind: 'overlay' },
    ],
  },
  {
    title: 'Oferta relampago',
    type: 'ads',
    tone: 'bg-orange-400/15',
    clips: [
      { id: 'tpl-urgency', label: 'Urgencia', length: 3, kind: 'video' },
      { id: 'tpl-price', label: 'Preco e bonus', length: 5, kind: 'text' },
      { id: 'tpl-action', label: 'Chamar no WhatsApp', length: 4, kind: 'overlay' },
    ],
  },
];
const defaultClips: TimelineClip[] = [
  { id: 'intro', label: 'Intro hook', length: 3, kind: 'video' },
  { id: 'main', label: 'Cena principal', length: 8, kind: 'video' },
  { id: 'cta', label: 'CTA final', length: 4, kind: 'overlay' },
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

export function VideoEditorStudioPage() {
  const navigate = useNavigate();
  const params = useParams();
  const [searchParams] = useSearchParams();
  const { pushToast } = useToast();
  const projectId = params.projectId ? Number(params.projectId) : null;
  const forceNew = searchParams.get('mode') === 'new';
  const entryMode = searchParams.get('entry') || 'editor';

  const studio = useStudioV2({
    defaultType: 'video-editor',
    defaultTitle: 'Editor de Video',
    projectId,
    forceNew,
  });

  const [activeTool, setActiveTool] = useState<EditorTool>('Editar');
  const [openExport, setOpenExport] = useState(false);
  const [prompt, setPrompt] = useState('Video vertical de 15 segundos para lancamento premium com hook forte e CTA direto.');
  const [processing, setProcessing] = useState(false);
  const [clips, setClips] = useState<TimelineClip[]>(defaultClips);
  const [selectedClipId, setSelectedClipId] = useState<string | null>(null);
  const [uploadedMediaLabel, setUploadedMediaLabel] = useState<string | null>(null);
  const [activeSideTool, setActiveSideTool] = useState<SideTool | null>('modelos');

  useEffect(() => {
    const timelineData = studio.currentProject?.timeline_data;
    if (!timelineData || typeof timelineData !== 'object') return;
    const projectClips = Array.isArray((timelineData as { clips?: unknown }).clips)
      ? ((timelineData as { clips: TimelineClip[] }).clips)
      : null;
    if (projectClips && projectClips.length > 0) {
      setClips(projectClips);
      setSelectedClipId(null);
    }
  }, [studio.currentProject?.id]);

  const selectedClip = useMemo(
    () => clips.find((clip) => clip.id === selectedClipId) || null,
    [clips, selectedClipId],
  );

  async function persistTimeline(nextClips: TimelineClip[], nextTool = activeTool) {
    await studio.saveProject({
      status: 'saved',
      metadata: { tool: nextTool, prompt, entryMode },
      timeline_data: {
        clips: nextClips,
        activeTool: nextTool,
        selectedClipId,
      },
      canvas_data: {
        prompt,
        selectedClipId,
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
        await studioVideoGenerate({ project_id: studio.currentProject.id, prompt, options: { ratio: '9:16', duration: 15, entry: entryMode } });
      }
      studio.setSaveState('dirty');
      pushToast('Acao de IA concluida no editor.', 'success');
    } catch {
      pushToast('Falha ao executar a acao de IA.', 'error');
    } finally {
      setProcessing(false);
    }
  }

  function handleToolbarAction(actionId: string) {
    if (!selectedClip) {
      pushToast('Selecione um clip na timeline antes de usar esta ferramenta.', 'error');
      return;
    }
    const map: Record<string, EditorTool> = {
      split: 'Editar',
      trim: 'Editar',
      speed: 'Editar',
      audio: 'Audio',
      captions: 'Legendas',
      animate: 'Efeitos',
      position: 'Camadas',
      ai: 'Efeitos',
    };
    setActiveTool(map[actionId] || 'Editar');
    if (actionId === 'split') {
      const nextClips = clips.flatMap((clip) => clip.id === selectedClip.id
        ? [
            { ...clip, id: `${clip.id}-a`, label: `${clip.label} A`, length: Math.max(1, Math.ceil(clip.length / 2)) },
            { ...clip, id: `${clip.id}-b`, label: `${clip.label} B`, length: Math.max(1, Math.floor(clip.length / 2)) },
          ]
        : [clip]);
      setClips(nextClips);
      setSelectedClipId(`${selectedClip.id}-a`);
      studio.setSaveState('dirty');
      pushToast('Clip dividido na timeline.', 'success');
      return;
    }
    if (actionId === 'trim') {
      setClips((current) => current.map((clip) => clip.id === selectedClip.id ? { ...clip, length: Math.max(1, clip.length - 1) } : clip));
      studio.setSaveState('dirty');
      pushToast('Clip cortado em 1 segundo.', 'success');
      return;
    }
    if (actionId === 'speed') {
      setClips((current) => current.map((clip) => clip.id === selectedClip.id ? { ...clip, length: Math.max(1, Math.round(clip.length * 0.75)) } : clip));
      studio.setSaveState('dirty');
      pushToast('Velocidade ajustada no clip.', 'success');
      return;
    }
    if (actionId === 'captions') void handleRunAiAction('captions');
    if (actionId === 'audio') setActiveTool('Audio');
    if (actionId === 'ai') void handleRunAiAction('generate');
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

  const totalDuration = useMemo(
    () => clips.reduce((total, clip) => total + clip.length, 0),
    [clips],
  );

  function selectSideTool(tool: SideTool) {
    setActiveSideTool((current) => (current === tool ? null : tool));
    const map: Partial<Record<SideTool, EditorTool>> = {
      texto: 'Texto',
      legendas: 'Legendas',
      ajustes: 'Filtros',
      uploads: 'Editar',
      modelos: 'Editar',
    };
    if (map[tool]) setActiveTool(map[tool]);
  }

  function applyTemplate(template: (typeof templateCards)[number]) {
    const nextClips = template.clips.map((clip) => ({
      ...clip,
      id: `${clip.id}-${Date.now()}`,
    }));
    setClips(nextClips);
    setSelectedClipId(nextClips[0]?.id ?? null);
    setPrompt(`${template.title}: video curto com narrativa clara, texto objetivo e CTA forte.`);
    studio.setSaveState('dirty');
    pushToast(`Template "${template.title}" aplicado na timeline.`, 'success');
  }

  function renderSidePanel() {
    if (!activeSideTool) return null;
    if (activeSideTool === 'modelos') {
      return (
        <div className="space-y-4">
          <div className="rounded-2xl border border-white/10 bg-black/20 p-3">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-cyan">Modelos</p>
            <input placeholder="Buscar modelos" className="mt-3 h-11 w-full rounded-2xl border border-white/10 bg-white/[0.04] px-3 text-sm text-white outline-none placeholder:text-slate-500 focus:border-cyan/40" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            {templateCards.map((template) => (
              <button key={template.title} type="button" onClick={() => applyTemplate(template)} className={`min-h-36 rounded-2xl border border-white/10 ${template.tone} p-3 text-left transition hover:border-cyan/40`}>
                <span className="rounded-full bg-black/30 px-2 py-1 text-[10px] font-bold text-slate-300">{template.type}</span>
                <p className="mt-12 text-sm font-black text-white">{template.title}</p>
              </button>
            ))}
          </div>
        </div>
      );
    }
    if (activeSideTool === 'uploads') {
      return (
        <div className="space-y-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-cyan">Uploads</p>
            <p className="mt-1 text-sm text-slate-400">Envie video, imagem ou audio para editar no canvas.</p>
          </div>
          <label className="flex min-h-44 cursor-pointer flex-col items-center justify-center rounded-3xl border border-dashed border-cyan/30 bg-cyan/10 p-5 text-center text-sm text-cyan transition hover:bg-cyan/15">
            <UploadCloud size={32} />
            <span className="mt-3 font-bold">Fazer upload</span>
            <span className="mt-1 text-xs text-slate-400">MP4, JPG, PNG ou MP3</span>
            <input
              type="file"
              accept="video/*,image/*,audio/*"
              className="hidden"
              onChange={(event) => {
                const file = event.target.files?.[0];
                if (!file) return;
                if (file.type.startsWith('audio')) void handleUploadAudio(file);
                else void handleUploadMedia(file);
                event.currentTarget.value = '';
              }}
            />
          </label>
        </div>
      );
    }
    if (activeSideTool === 'texto') {
      return (
        <div className="space-y-3">
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-cyan">Texto</p>
          {['Adicionar titulo', 'Adicionar subtitulo', 'Adicionar texto curto'].map((label) => (
            <button key={label} type="button" onClick={() => handleAddTextClip(label.replace('Adicionar ', ''))} className="w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-4 text-left text-sm font-bold text-white transition hover:border-cyan/40">
              <Plus size={16} className="mb-2 text-cyan" /> {label}
            </button>
          ))}
        </div>
      );
    }
    if (activeSideTool === 'legendas') {
      return (
        <div className="space-y-3">
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-cyan">Legendas</p>
          <button type="button" onClick={() => void handleRunAiAction('captions')} className="w-full rounded-2xl border border-cyan/30 bg-cyan/10 px-4 py-3 text-sm font-bold text-cyan hover:bg-cyan/15">
            Gerar legendas com IA
          </button>
          <p className="text-xs leading-5 text-slate-500">A legenda usa o prompt do projeto e salva o resultado no projeto.</p>
        </div>
      );
    }
    if (activeSideTool === 'ajustes') {
      const adjustmentActions: Array<{ label: string; action: string }> = [
        { label: 'Cortar', action: 'trim' },
        { label: 'Dividir', action: 'split' },
        { label: 'Velocidade', action: 'speed' },
        { label: 'Animar', action: 'animate' },
        { label: 'Posicao', action: 'position' },
      ];
      return (
        <div className="space-y-3">
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-cyan">Ajustes</p>
          {adjustmentActions.map((item) => (
            <button key={item.action} type="button" onClick={() => handleToolbarAction(item.action)} className="w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-left text-sm font-bold text-white hover:border-cyan/40">
              {item.label}
            </button>
          ))}
        </div>
      );
    }
    if (activeSideTool === 'midia') {
      return (
        <div className="space-y-3">
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-cyan">Midia IA</p>
          <button type="button" onClick={() => void handleRunAiAction('generate')} className="w-full rounded-2xl border border-cyan/30 bg-cyan/10 px-4 py-3 text-sm font-bold text-cyan hover:bg-cyan/15">
            Gerar variacao visual
          </button>
          <button type="button" onClick={() => void handleRunAiAction('voiceover')} className="inline-flex w-full items-center gap-2 rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-bold text-white hover:border-cyan/40">
            <Mic2 size={16} /> Criar voiceover
          </button>
        </div>
      );
    }
    return (
      <div className="space-y-3">
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-cyan">Projetos</p>
        <p className="text-sm leading-6 text-slate-400">Use Salvar para manter este projeto na biblioteca do Studio.</p>
      </div>
    );
  }

  return (
    <>
      <div className="min-h-screen bg-[linear-gradient(180deg,#040813,#091324)] px-4 py-4 md:px-6">
        <div className="mx-auto flex min-h-[calc(100vh-2rem)] max-w-[1600px] flex-col gap-4">
          <StudioTopbar
            projectName={studio.projectName}
            saveState={processing ? 'saving' : studio.saveState}
            onSave={() => void persistTimeline(clips)}
            onExport={() => setOpenExport(true)}
            onDuplicate={() => void studio.duplicateProject()}
            onBackHome={() => navigate('/app/studio')}
          />

          <div className={['grid min-h-0 flex-1 gap-4', activeSideTool ? 'xl:grid-cols-[76px_320px_minmax(0,1fr)_340px]' : 'xl:grid-cols-[76px_minmax(0,1fr)_340px]'].join(' ')}>
            <aside className="hidden rounded-[1.75rem] border border-white/10 bg-white/[0.03] p-2 xl:block">
              <div className="space-y-2">
                {sideRailTools.map((tool) => {
                  const Icon = tool.icon;
                  const active = activeSideTool === tool.id;
                  return (
                    <button
                      key={tool.id}
                      type="button"
                      onClick={() => selectSideTool(tool.id)}
                      className={[
                        'flex w-full flex-col items-center gap-1 rounded-2xl px-2 py-3 text-[11px] font-semibold transition',
                        active ? 'bg-cyan text-ink' : 'text-slate-300 hover:bg-white/[0.06] hover:text-white',
                      ].join(' ')}
                      title={tool.label}
                    >
                      <Icon size={20} />
                      <span className="leading-tight">{tool.label}</span>
                    </button>
                  );
                })}
              </div>
            </aside>

            {activeSideTool ? (
              <aside className="hidden min-h-0 overflow-y-auto rounded-[1.75rem] border border-white/10 bg-white/[0.035] p-4 xl:block">
                {renderSidePanel()}
              </aside>
            ) : null}

            <div className="min-h-0 space-y-4">
              <div className="rounded-[1.75rem] border border-white/10 bg-white/[0.03] p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="text-[11px] uppercase tracking-[0.24em] text-cyan-300">Editor de video</p>
                    <h1 className="mt-1 font-display text-2xl text-white">Canvas principal</h1>
                  </div>
                  <div className="flex flex-wrap items-center gap-2 text-xs text-slate-300">
                    <span className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1">{clips.length} clips</span>
                    <span className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1">{totalDuration}s</span>
                    <span className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1">9:16</span>
                  </div>
                </div>
              </div>

              <StudioCanvas
                title="Area de edicao"
                subtitle="Selecione um clip na timeline para liberar a barra de ferramentas contextual."
                selected={Boolean(selectedClipId && selectedClip)}
                toolbar={selectedClipId && selectedClip ? <StudioContextToolbar selectionKind={selectedClip.kind === 'text' ? 'text' : 'video'} activeAction={activeTool === 'Legendas' ? 'captions' : undefined} onAction={handleToolbarAction} /> : null}
                footer={(
                  <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm font-semibold text-slate-700 shadow-sm">
                    <button type="button" className="rounded-xl border border-slate-300 px-4 py-2 hover:bg-slate-50">+ Adicionar pagina</button>
                    <span>{clips.length} clips - {totalDuration}s - 9:16</span>
                  </div>
                )}
              >
                <div className="flex min-h-[500px] items-center justify-center">
                  <div className="relative flex aspect-[9/16] h-[460px] max-h-full items-center justify-center bg-[#a99b92] shadow-[0_22px_70px_rgba(15,23,42,0.22)]">
                    <div className="absolute -top-10 right-0 flex gap-2 text-slate-600">
                      <span className="rounded-lg bg-white/80 px-2 py-1 text-xs">bloquear</span>
                      <span className="rounded-lg bg-white/80 px-2 py-1 text-xs">duplicar</span>
                      <span className="rounded-lg bg-white/80 px-2 py-1 text-xs">+</span>
                    </div>
                    {selectedClip?.assetUrl ? (
                      selectedClip.kind === 'image' ? (
                        <img src={selectedClip.assetUrl} alt={selectedClip.label} className="max-h-full max-w-full object-contain" />
                      ) : (
                        <video src={selectedClip.assetUrl} controls className="max-h-full max-w-full" />
                      )
                    ) : (
                      <div className="mx-8 flex flex-col items-center justify-center rounded-3xl border border-dashed border-slate-700/30 bg-white/18 px-8 py-10 text-center text-slate-900">
                        <PlayCircle className="h-12 w-12 text-cyan" />
                        <p className="mt-4 text-lg font-black">{selectedClip?.label || 'Projeto pronto para editar'}</p>
                        <p className="mt-2 max-w-[260px] text-sm leading-6">Envie uma midia ou selecione um clip na timeline para abrir as ferramentas.</p>
                      </div>
                    )}
                  </div>
                </div>
              </StudioCanvas>
            </div>

            <aside className="space-y-4 rounded-[1.75rem] border border-white/10 bg-white/[0.03] p-4">
              <div>
                <p className="text-[11px] uppercase tracking-[0.24em] text-cyan-300">Painel direito</p>
                <h2 className="mt-1 font-display text-xl text-white">Controles dinamicos</h2>
                <p className="mt-1 text-sm text-slate-300">O painel muda conforme a ferramenta ativa para manter o editor limpo.</p>
              </div>

              <label className="block text-xs text-slate-300">
                <span className="mb-1 block">Prompt do projeto</span>
                <textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} className="min-h-28 w-full rounded-xl border border-white/10 bg-black/25 px-3 py-2 text-sm text-white" />
              </label>

              <div className="rounded-2xl border border-white/10 bg-black/20 p-3 text-sm text-slate-300">
                <p className="text-xs text-slate-500">Ultima midia enviada</p>
                <p className="mt-1 font-semibold text-white">{uploadedMediaLabel || 'Nenhuma midia nesta sessao'}</p>
              </div>

              <StudioVideoContextPanel
                activeTool={activeTool}
                onAddTextClip={handleAddTextClip}
                onUploadAudio={handleUploadAudio}
                onRunAiAction={handleRunAiAction}
              />

              <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
                <div className="mb-3 flex items-center gap-2 text-cyan-100">
                  <LayoutTemplate size={16} />
                  <p className="text-sm font-semibold">Camadas e estrutura</p>
                </div>
                <div className="space-y-2">
                  {clips.slice(0, 5).map((clip) => (
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
              </div>
            </aside>
          </div>

          <div className="sticky bottom-0 z-20 space-y-3 rounded-[1.75rem] border border-white/10 bg-[linear-gradient(180deg,rgba(4,8,19,0.95),rgba(7,13,28,0.98))] p-4 backdrop-blur-xl">
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2 text-cyan-100">
                <Grip size={16} />
                <p className="text-sm font-semibold">Timeline</p>
              </div>
              <label className="inline-flex cursor-pointer items-center rounded-xl border border-white/15 bg-white/[0.03] px-3 py-2 text-xs text-slate-200 transition hover:border-cyan/40 hover:text-white">
                Inserir midia
                <input
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

            <div className="flex gap-2 overflow-x-auto">
              {editorTools.map((tool) => (
                <button
                  key={tool}
                  type="button"
                  onClick={() => setActiveTool(tool)}
                  className={activeTool === tool
                    ? 'rounded-2xl border border-cyan/40 bg-cyan/15 px-4 py-3 text-sm font-semibold text-cyan-50'
                    : 'rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm font-medium text-slate-300 transition hover:border-cyan/35 hover:text-white'}
                >
                  {tool}
                </button>
              ))}
              <button type="button" onClick={() => void handleRunAiAction('generate')} className="inline-flex items-center gap-2 rounded-2xl border border-cyan/40 bg-cyan/10 px-4 py-3 text-sm font-semibold text-cyan-100">
                <Wand2 size={15} /> Gerar variacao
              </button>
            </div>
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

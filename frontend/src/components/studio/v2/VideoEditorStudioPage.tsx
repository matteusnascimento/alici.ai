import { Film, Grip, LayoutTemplate, Loader2, PlayCircle, Wand2 } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';

import { useStudioV2 } from '../../../hooks/useStudioV2';
import { useToast } from '../../../hooks/useToast';
import { studioVideoCaptions, studioVideoGenerate, studioVideoVoiceover, uploadStudioAsset } from '../../../services/studio.service';
import { StudioCanvas } from './StudioCanvas';
import { StudioExportModal } from './StudioExportModal';
import { StudioTimeline } from './StudioTimeline';
import { StudioTopbar } from './StudioTopbar';
import { StudioVideoContextPanel } from './StudioVideoContextPanel';

type EditorTool = 'Editar' | 'Audio' | 'Texto' | 'Efeitos' | 'Camadas' | 'Legendas' | 'Filtros';

type TimelineClip = {
  id: string;
  label: string;
  length: number;
  kind: string;
  assetUrl?: string;
};

const editorTools: EditorTool[] = ['Editar', 'Audio', 'Texto', 'Efeitos', 'Camadas', 'Legendas', 'Filtros'];
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
  const [selectedClipId, setSelectedClipId] = useState<string | null>(defaultClips[0].id);
  const [uploadedMediaLabel, setUploadedMediaLabel] = useState<string | null>(null);

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

  const selectedClip = useMemo(
    () => clips.find((clip) => clip.id === selectedClipId) || clips[0] || null,
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

          <div className="grid min-h-0 flex-1 gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
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

              <StudioCanvas title="Preview do video" subtitle="Workspace focado em composicao, timing e narrativa visual.">
                <div className="grid h-full gap-4 lg:grid-cols-[minmax(0,1fr)_280px]">
                  <div className="flex h-full min-h-[280px] items-center justify-center rounded-[1.5rem] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.03),rgba(0,0,0,0.18))] p-4">
                    {selectedClip?.assetUrl ? (
                      selectedClip.kind === 'image' ? (
                        <img src={selectedClip.assetUrl} alt={selectedClip.label} className="max-h-full max-w-full rounded-[1.25rem] object-contain" />
                      ) : (
                        <video src={selectedClip.assetUrl} controls className="max-h-full max-w-full rounded-[1.25rem]" />
                      )
                    ) : (
                      <div className="flex w-full max-w-[360px] flex-col items-center justify-center rounded-[1.75rem] border border-dashed border-cyan-300/25 bg-black/25 px-6 py-10 text-center">
                        <PlayCircle className="h-12 w-12 text-cyan-200" />
                        <p className="mt-4 text-lg font-semibold text-white">{selectedClip?.label || 'Projeto pronto para editar'}</p>
                        <p className="mt-2 text-sm leading-6 text-slate-300">Envie uma midia, reorganize a timeline e refine o corte no painel lateral.</p>
                      </div>
                    )}
                  </div>

                  <div className="rounded-[1.5rem] border border-white/10 bg-black/20 p-4">
                    <div className="flex items-center gap-2 text-cyan-200">
                      <Film size={16} />
                      <p className="text-xs uppercase tracking-[0.24em]">Resumo do frame</p>
                    </div>
                    <div className="mt-4 space-y-3 text-sm text-slate-300">
                      <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
                        <p className="text-xs text-slate-400">Clip selecionado</p>
                        <p className="mt-1 font-medium text-white">{selectedClip?.label || 'Nenhum clip selecionado'}</p>
                      </div>
                      <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
                        <p className="text-xs text-slate-400">Prompt de criacao</p>
                        <p className="mt-1 line-clamp-4 text-white">{prompt}</p>
                      </div>
                      <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
                        <p className="text-xs text-slate-400">Ultima midia</p>
                        <p className="mt-1 text-white">{uploadedMediaLabel || 'Nenhuma midia enviada nesta sessao'}</p>
                      </div>
                    </div>
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

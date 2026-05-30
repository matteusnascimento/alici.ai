import {
  ArrowLeft,
  Download,
  FileVideo,
  Image,
  Layers3,
  Loader2,
  MousePointer2,
  Redo2,
  Save,
  SlidersHorizontal,
  Sparkles,
  Square,
  Type,
  Undo2,
  Wand2,
} from 'lucide-react';
import type { CSSProperties } from 'react';
import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom';

import { MAGIC_STUDIO_ACTIONS } from '../../../data/studioEffects';
import { getStudioTemplateDefinition } from '../../../services/studioTemplate.service';
import {
  createProjectFromTemplate,
  duplicateLocalStudioProject,
  getLocalStudioProject,
  saveLocalStudioProject,
} from '../../../services/studioTemplate.service';
import { buildCssFilter, listStudioEffects, mergeLayerFilters } from '../../../services/studioEffects.service';
import type { StudioEffectDefinition, StudioProjectFromTemplate, StudioTemplateField, StudioTemplateLayer } from '../../../types/studioTemplate';

type EditorTool = 'select' | 'fields' | 'templates' | 'effects' | 'magic' | 'layers' | 'assets';

const tools: Array<{ id: EditorTool; label: string; icon: typeof MousePointer2 }> = [
  { id: 'select', label: 'Selecionar', icon: MousePointer2 },
  { id: 'fields', label: 'Campos', icon: Type },
  { id: 'effects', label: 'Efeitos', icon: SlidersHorizontal },
  { id: 'magic', label: 'Magic AXI', icon: Wand2 },
  { id: 'layers', label: 'Camadas', icon: Layers3 },
  { id: 'assets', label: 'Assets', icon: Image },
];

function parseFormat(format: string) {
  const [width, height] = format.split('x').map((part) => Number(part));
  return { width: width || 1080, height: height || 1080 };
}

function layerFieldValue(project: StudioProjectFromTemplate, layer: StudioTemplateLayer) {
  return layer.field ? project.fields[layer.field] || '' : '';
}

function resolveAccent(project: StudioProjectFromTemplate, fallback?: string) {
  return project.fields.brand_color || fallback || '#63E6FF';
}

function layerStyle(project: StudioProjectFromTemplate, layer: StudioTemplateLayer, scale: number): CSSProperties {
  const accent = resolveAccent(project, layer.color || layer.fill);
  const isAccent = layer.color === '#63E6FF' || layer.fill === '#63E6FF' || layer.color === '#C026D3' || layer.fill === '#C026D3';
  return {
    position: 'absolute',
    left: layer.x * scale,
    top: layer.y * scale,
    width: (layer.width || 400) * scale,
    height: layer.height ? layer.height * scale : undefined,
    opacity: layer.opacity ?? 1,
    borderRadius: layer.borderRadius ? layer.borderRadius * scale : undefined,
    filter: buildCssFilter(layer.filters),
    color: isAccent ? accent : layer.color,
    fontSize: layer.fontSize ? layer.fontSize * scale : undefined,
    fontWeight: layer.fontWeight,
    lineHeight: 1.04,
  };
}

function renderLayer(project: StudioProjectFromTemplate, layer: StudioTemplateLayer, scale: number, selected: boolean, onSelect: () => void) {
  const base = layerStyle(project, layer, scale);
  const selectedClass = selected ? 'ring-2 ring-cyan-300/80 ring-offset-2 ring-offset-black/70' : 'hover:ring-1 hover:ring-white/30';

  if (layer.type === 'shape') {
    const accent = resolveAccent(project, layer.fill);
    const isAccent = layer.fill === '#63E6FF' || layer.fill === '#C026D3';
    return (
      <button
        key={layer.id}
        type="button"
        aria-label={`Selecionar camada ${layer.id}`}
        onClick={onSelect}
        className={`absolute ${selectedClass}`}
        style={{ ...base, background: isAccent ? accent : layer.fill }}
      />
    );
  }

  if (layer.type === 'image' || layer.type === 'video' || layer.type === 'logo') {
    const value = layerFieldValue(project, layer);
    return (
      <button
        key={layer.id}
        type="button"
        aria-label={`Selecionar camada ${layer.id}`}
        onClick={onSelect}
        className={`absolute overflow-hidden bg-[radial-gradient(circle_at_25%_20%,rgba(34,211,238,0.24),transparent_32%),linear-gradient(135deg,#111827,#312e81_48%,#0e7490)] ${selectedClass}`}
        style={base}
      >
        {value ? <img src={value} alt="" className="h-full w-full object-cover" onError={(event) => { event.currentTarget.style.display = 'none'; }} /> : null}
        <span className="pointer-events-none absolute bottom-3 left-3 rounded-full bg-black/45 px-3 py-1 text-xs font-semibold text-white/80">
          {layer.type === 'video' ? 'Video' : 'Imagem'}
        </span>
      </button>
    );
  }

  return (
    <button
      key={layer.id}
      type="button"
      aria-label={`Selecionar camada ${layer.id}`}
      onClick={onSelect}
      className={`absolute text-left ${selectedClass}`}
      style={base}
    >
      {layerFieldValue(project, layer)}
    </button>
  );
}

function fieldInputType(field: StudioTemplateField) {
  if (field.type === 'color') return 'color';
  if (field.type === 'image' || field.type === 'video' || field.type === 'logo' || field.type === 'background') return 'url';
  return 'text';
}

export function UnifiedEditorPage() {
  const navigate = useNavigate();
  const params = useParams();
  const [searchParams] = useSearchParams();
  const templateId = searchParams.get('templateId') || searchParams.get('template');
  const [project, setProject] = useState<StudioProjectFromTemplate | null>(null);
  const [activeTool, setActiveTool] = useState<EditorTool>('fields');
  const [selectedLayerId, setSelectedLayerId] = useState<string | null>(null);
  const [saveState, setSaveState] = useState<'saved' | 'dirty' | 'saving'>('saved');
  const [magicStatus, setMagicStatus] = useState<string | null>(null);

  const template = useMemo(() => getStudioTemplateDefinition(project?.templateId || templateId), [project?.templateId, templateId]);
  const effects = useMemo(() => listStudioEffects(), []);

  useEffect(() => {
    const existing = getLocalStudioProject(params.projectId || null);
    if (existing) {
      setProject(existing);
      setSelectedLayerId(existing.canvas.layers[0]?.id || null);
      return;
    }

    const selectedTemplate = getStudioTemplateDefinition(templateId) || getStudioTemplateDefinition('hotel_promo_story_001');
    if (selectedTemplate) {
      const next = createProjectFromTemplate(selectedTemplate);
      setProject(next);
      setSelectedLayerId(next.canvas.layers[0]?.id || null);
    }
  }, [params.projectId, templateId]);

  const selectedLayer = project?.canvas.layers.find((layer) => layer.id === selectedLayerId) || null;
  const isVideo = project?.type === 'video' || project?.type === 'reel';
  const canvasSize = project ? parseFormat(project.format) : { width: 1080, height: 1080 };
  const scale = Math.min(0.48, 620 / canvasSize.width, 760 / canvasSize.height);
  const canvasWidth = canvasSize.width * scale;
  const canvasHeight = canvasSize.height * scale;

  function updateProject(mutator: (current: StudioProjectFromTemplate) => StudioProjectFromTemplate) {
    setProject((current) => {
      if (!current) return current;
      const next = mutator(current);
      setSaveState('dirty');
      return next;
    });
  }

  function updateField(fieldId: string, value: string) {
    updateProject((current) => ({
      ...current,
      fields: { ...current.fields, [fieldId]: value },
    }));
  }

  function applyEffect(effect: StudioEffectDefinition) {
    if (!selectedLayer) return;
    if (effect.status === 'coming_soon') {
      setMagicStatus(`${effect.label}: em breve. Nenhum sucesso falso foi simulado.`);
      return;
    }
    updateProject((current) => ({
      ...current,
      selectedEffects: Array.from(new Set([...current.selectedEffects, effect.id])),
      canvas: {
        ...current.canvas,
        layers: current.canvas.layers.map((layer) =>
          layer.id === selectedLayer.id
            ? { ...layer, effect: effect.id, filters: mergeLayerFilters(layer.filters, effect.cssFilters) }
            : layer,
        ),
      },
    }));
  }

  function saveAsNewProject() {
    if (!project) return;
    setSaveState('saving');
    const saved = saveLocalStudioProject(project);
    setProject(saved);
    setSaveState('saved');
    navigate(`/app/studio/editor/${saved.id}`, { replace: true });
  }

  function duplicateProject() {
    if (!project) return;
    const copy = duplicateLocalStudioProject(project);
    navigate(`/app/studio/editor/${copy.id}`);
  }

  if (!project || !template) {
    return (
      <main className="flex min-h-[60vh] items-center justify-center text-white">
        <div className="rounded-2xl border border-white/10 bg-white/[0.05] px-5 py-4 text-sm">
          <Loader2 className="mr-2 inline h-4 w-4 animate-spin text-cyan-300" />
          Preparando editor unificado...
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_14%_0%,rgba(192,38,211,0.18),transparent_34%),radial-gradient(circle_at_84%_0%,rgba(34,211,238,0.12),transparent_32%),linear-gradient(180deg,#050507,#0a0a12)] text-white">
      <header data-testid="studio-editor-topbar" className="sticky top-0 z-30 border-b border-white/10 bg-[#050507]/92 px-4 py-3 backdrop-blur-xl">
        <div className="mx-auto flex max-w-[1680px] flex-wrap items-center justify-between gap-3">
          <div className="flex min-w-0 items-center gap-3">
            <Link to="/app/studio" className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/[0.04] text-slate-200 hover:text-white" aria-label="Voltar">
              <ArrowLeft size={17} />
            </Link>
            <div className="min-w-0">
              <input
                aria-label="Nome do projeto"
                value={project.name}
                onChange={(event) => updateProject((current) => ({ ...current, name: event.target.value }))}
                className="w-full max-w-md bg-transparent font-display text-lg font-bold text-white outline-none"
              />
              <p className="text-xs text-slate-400">{project.type} / {project.format} / {saveState === 'saved' ? 'salvo' : saveState === 'saving' ? 'salvando' : 'alteracoes pendentes'}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button type="button" className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/[0.04] text-slate-300" aria-label="Undo"><Undo2 size={16} /></button>
            <button type="button" className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-white/[0.04] text-slate-300" aria-label="Redo"><Redo2 size={16} /></button>
            <button type="button" onClick={saveAsNewProject} className="inline-flex items-center gap-2 rounded-xl border border-cyan-300/35 bg-cyan-300/10 px-4 py-2.5 text-sm font-bold text-cyan-50">
              <Save size={16} /> Salvar
            </button>
            <button type="button" onClick={duplicateProject} className="hidden rounded-xl border border-white/10 bg-white/[0.04] px-4 py-2.5 text-sm font-bold text-slate-200 sm:inline-flex">
              Duplicar
            </button>
            <button type="button" className="inline-flex items-center gap-2 rounded-xl bg-[var(--studio-gradient)] px-4 py-2.5 text-sm font-bold text-white">
              <Download size={16} /> Exportar
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-[1680px] gap-4 px-4 py-4 lg:grid-cols-[88px_minmax(0,1fr)_360px]">
        <aside className="flex gap-2 overflow-x-auto rounded-2xl border border-white/10 bg-white/[0.045] p-2 lg:flex-col">
          {tools.map((tool) => {
            const Icon = tool.icon;
            return (
              <button
                key={tool.id}
                type="button"
                onClick={() => setActiveTool(tool.id)}
                title={tool.label}
                className={activeTool === tool.id ? 'inline-flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-cyan-300/16 text-cyan-100' : 'inline-flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl border border-white/10 bg-black/20 text-slate-300 hover:text-white'}
              >
                <Icon size={19} />
              </button>
            );
          })}
        </aside>

        <section className="min-h-[calc(100vh-7rem)] rounded-2xl border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] p-4">
          <div className="mb-3 flex items-center justify-between gap-3 text-xs text-slate-400">
            <span>{template.name}</span>
            <span>{canvasSize.width} x {canvasSize.height}</span>
          </div>
          <div className="flex min-h-[680px] items-center justify-center overflow-auto rounded-2xl border border-white/10 bg-black/35 p-6">
            <div
              data-testid="studio-template-canvas"
              className="relative overflow-hidden shadow-[0_30px_90px_rgba(0,0,0,0.45)]"
              style={{ width: canvasWidth, height: canvasHeight, background: project.canvas.background }}
            >
              {project.canvas.layers.map((layer) => renderLayer(project, layer, scale, layer.id === selectedLayerId, () => setSelectedLayerId(layer.id)))}
            </div>
          </div>
          {isVideo ? (
            <div className="mt-4 rounded-2xl border border-white/10 bg-black/30 p-3">
              <div className="mb-3 flex items-center gap-2 text-sm font-bold text-white"><FileVideo size={16} /> Timeline</div>
              <div className="grid grid-cols-4 gap-2">
                {['Intro', 'Cena principal', 'Oferta', 'CTA'].map((clip) => (
                  <button key={clip} type="button" className="h-16 rounded-xl border border-white/10 bg-white/[0.05] text-xs text-slate-200">{clip}</button>
                ))}
              </div>
            </div>
          ) : (
            <div className="mt-4 flex items-center justify-between rounded-2xl border border-white/10 bg-black/30 px-4 py-3 text-sm text-slate-300">
              <span>Pagina 1 / 1</span>
              <span>Zoom {Math.round(scale * 100)}%</span>
            </div>
          )}
        </section>

        <aside className="max-h-[calc(100vh-6rem)] overflow-y-auto rounded-2xl border border-white/10 bg-white/[0.055] p-4">
          {activeTool === 'fields' || activeTool === 'select' ? (
            <section className="space-y-3">
              <h2 className="font-display text-xl font-bold">Campos dinamicos</h2>
              {template.fields.map((field) => (
                <label key={field.id} className="block text-sm text-slate-300">
                  <span className="mb-1 block text-xs font-bold uppercase tracking-[0.16em] text-slate-500">{field.label}</span>
                  <input
                    type={fieldInputType(field)}
                    value={project.fields[field.id] || ''}
                    onChange={(event) => updateField(field.id, event.target.value)}
                    className="w-full rounded-xl border border-white/10 bg-black/25 px-3 py-2.5 text-sm text-white outline-none focus:border-cyan-300/45"
                  />
                </label>
              ))}
            </section>
          ) : null}

          {activeTool === 'effects' ? (
            <section className="space-y-4">
              <h2 className="font-display text-xl font-bold">Efeitos e filtros</h2>
              {(['image-filter', 'image-advanced', 'text-effect', 'video-transition', 'video-motion', 'video-color', 'video-text', 'video-overlay'] as const).map((group) => {
                const groupEffects = effects.filter((effect) => effect.group === group);
                if (groupEffects.length === 0) return null;
                return (
                  <div key={group}>
                    <p className="mb-2 text-xs font-bold uppercase tracking-[0.18em] text-cyan-300">{group.replace('-', ' ')}</p>
                    <div className="grid grid-cols-2 gap-2">
                      {groupEffects.map((effect) => (
                        <button key={effect.id} type="button" onClick={() => applyEffect(effect)} className="rounded-xl border border-white/10 bg-black/25 px-3 py-2 text-left text-xs font-semibold text-slate-200 hover:border-cyan-300/40 hover:text-white">
                          {effect.label}
                        </button>
                      ))}
                    </div>
                  </div>
                );
              })}
            </section>
          ) : null}

          {activeTool === 'magic' ? (
            <section className="space-y-3">
              <div className="flex items-center gap-2">
                <Sparkles size={18} className="text-fuchsia-300" />
                <h2 className="font-display text-xl font-bold">Magic Studio AXI</h2>
              </div>
              {MAGIC_STUDIO_ACTIONS.map((action) => (
                <button
                  key={action}
                  type="button"
                  onClick={() => setMagicStatus(`${action}: em breve. A UI e o contrato estao prontos; sem simular sucesso falso.`)}
                  className="block w-full rounded-xl border border-white/10 bg-black/25 px-3 py-2.5 text-left text-sm font-semibold text-slate-200 hover:border-fuchsia-300/40 hover:text-white"
                >
                  {action}
                </button>
              ))}
              {magicStatus ? <p className="rounded-xl border border-amber-300/25 bg-amber-300/10 px-3 py-2 text-sm text-amber-100">{magicStatus}</p> : null}
            </section>
          ) : null}

          {activeTool === 'layers' ? (
            <section className="space-y-2">
              <h2 className="font-display text-xl font-bold">Camadas</h2>
              {project.canvas.layers.map((layer) => (
                <button key={layer.id} type="button" onClick={() => setSelectedLayerId(layer.id)} className={layer.id === selectedLayerId ? 'flex w-full items-center gap-2 rounded-xl border border-cyan-300/40 bg-cyan-300/10 px-3 py-2 text-left text-sm text-white' : 'flex w-full items-center gap-2 rounded-xl border border-white/10 bg-black/25 px-3 py-2 text-left text-sm text-slate-300'}>
                  {layer.type === 'text' ? <Type size={15} /> : layer.type === 'shape' ? <Square size={15} /> : <Image size={15} />}
                  {layer.id}
                </button>
              ))}
            </section>
          ) : null}

          {activeTool === 'assets' || activeTool === 'templates' ? (
            <section className="space-y-3">
              <h2 className="font-display text-xl font-bold">Uploads recentes</h2>
              <div className="rounded-xl border border-dashed border-white/15 bg-black/25 p-4 text-sm text-slate-300">
                Importacao de PNG/PDF exportados de outras ferramentas sera tratada como upload de arquivo, sem integracao direta.
              </div>
            </section>
          ) : null}

          {selectedLayer ? (
            <section className="mt-5 rounded-xl border border-white/10 bg-black/25 p-3 text-xs text-slate-300">
              <p className="font-bold text-white">Selecionado: {selectedLayer.id}</p>
              <p className="mt-1">Tipo: {selectedLayer.type}</p>
              <p className="mt-1">Efeito: {selectedLayer.effect || 'nenhum'}</p>
            </section>
          ) : null}
        </aside>
      </div>
    </main>
  );
}

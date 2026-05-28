import { create } from 'zustand';

export type AxiStudioMode = 'photo' | 'video' | 'ai';
export type AxiLayerKind = 'image' | 'video' | 'audio' | 'text' | 'shape' | 'effect';

export interface AxiStudioLayer {
  id: string;
  name: string;
  kind: AxiLayerKind;
  visible: boolean;
  locked: boolean;
  opacity: number;
  blendMode: string;
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;
  src?: string;
  text?: string;
  color?: string;
  fontSize?: number;
  fontFamily?: string;
  effects?: string[];
  editable?: boolean;
  animations?: Array<{
    property: 'x' | 'y' | 'opacity' | 'scale' | 'rotation';
    keyframes: Array<{ time: number; value: number }>;
  }>;
  start?: number;
  duration?: number;
}

export interface AxiStudioClip {
  id: string;
  layerId: string;
  track: 'video' | 'audio' | 'text' | 'overlay' | 'effect';
  label: string;
  start: number;
  duration: number;
}

interface AxiStudioState {
  mode: AxiStudioMode;
  activeTool: string;
  selectedLayerId: string | null;
  zoom: number;
  pan: { x: number; y: number };
  duration: number;
  layers: AxiStudioLayer[];
  clips: AxiStudioClip[];
  prompt: string;
  lastSavedAt: string | null;
  dirty: boolean;
  setMode: (mode: AxiStudioMode) => void;
  setActiveTool: (tool: string) => void;
  selectLayer: (layerId: string | null) => void;
  setZoom: (zoom: number) => void;
  setPan: (pan: { x: number; y: number }) => void;
  setPrompt: (prompt: string) => void;
  addLayer: (layer: Omit<AxiStudioLayer, 'id'> & { id?: string }) => string;
  updateLayer: (layerId: string, patch: Partial<AxiStudioLayer>) => void;
  removeLayer: (layerId: string) => void;
  reorderLayer: (layerId: string, direction: 'up' | 'down') => void;
  addClip: (clip: Omit<AxiStudioClip, 'id'> & { id?: string }) => void;
  updateClip: (clipId: string, patch: Partial<AxiStudioClip>) => void;
  splitClip: (clipId: string) => void;
  trimClip: (clipId: string, seconds: number) => void;
  loadTemplate: (snapshot: {
    mode?: AxiStudioMode;
    prompt?: string;
    duration?: number;
    layers: AxiStudioLayer[];
    clips: AxiStudioClip[];
    selectedLayerId?: string | null;
  }) => void;
  markSaved: () => void;
  hydrate: (snapshot: Partial<Pick<AxiStudioState, 'mode' | 'activeTool' | 'selectedLayerId' | 'zoom' | 'pan' | 'duration' | 'layers' | 'clips' | 'prompt'>>) => void;
}

const initialLayers: AxiStudioLayer[] = [
  {
    id: 'background',
    name: 'Canvas base',
    kind: 'shape',
    visible: true,
    locked: false,
    opacity: 1,
    blendMode: 'normal',
    x: 110,
    y: 70,
    width: 460,
    height: 460,
    rotation: 0,
    color: '#a99b92',
    start: 0,
    duration: 15,
  },
  {
    id: 'headline',
    name: 'Texto principal',
    kind: 'text',
    visible: true,
    locked: false,
    opacity: 1,
    blendMode: 'normal',
    x: 180,
    y: 440,
    width: 320,
    height: 70,
    rotation: 0,
    text: 'AXI Studio',
    color: '#111827',
    start: 0,
    duration: 15,
  },
];

const initialClips: AxiStudioClip[] = [
  { id: 'clip-intro', layerId: 'background', track: 'video', label: 'Intro', start: 0, duration: 4 },
  { id: 'clip-main', layerId: 'headline', track: 'text', label: 'Titulo', start: 2, duration: 8 },
  { id: 'clip-cta', layerId: 'background', track: 'overlay', label: 'CTA final', start: 10, duration: 5 },
];

function makeId(prefix: string) {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export const useAxiStudioStore = create<AxiStudioState>((set, get) => ({
  mode: 'video',
  activeTool: 'select',
  selectedLayerId: 'headline',
  zoom: 1,
  pan: { x: 0, y: 0 },
  duration: 15,
  layers: initialLayers,
  clips: initialClips,
  prompt: 'Crie um video vertical de 15 segundos para lancamento premium com hook forte e CTA direto.',
  lastSavedAt: null,
  dirty: false,
  setMode: (mode) => set({ mode, dirty: true }),
  setActiveTool: (activeTool) => set({ activeTool }),
  selectLayer: (selectedLayerId) => set({ selectedLayerId }),
  setZoom: (zoom) => set({ zoom: Math.min(3, Math.max(0.2, zoom)) }),
  setPan: (pan) => set({ pan }),
  setPrompt: (prompt) => set({ prompt, dirty: true }),
  addLayer: (layer) => {
    const id = layer.id ?? makeId(layer.kind);
    set((state) => ({
      layers: [{ ...layer, id }, ...state.layers],
      selectedLayerId: id,
      dirty: true,
    }));
    return id;
  },
  updateLayer: (layerId, patch) => set((state) => ({
    layers: state.layers.map((layer) => (layer.id === layerId ? { ...layer, ...patch } : layer)),
    dirty: true,
  })),
  removeLayer: (layerId) => set((state) => ({
    layers: state.layers.filter((layer) => layer.id !== layerId),
    clips: state.clips.filter((clip) => clip.layerId !== layerId),
    selectedLayerId: state.selectedLayerId === layerId ? null : state.selectedLayerId,
    dirty: true,
  })),
  reorderLayer: (layerId, direction) => set((state) => {
    const index = state.layers.findIndex((layer) => layer.id === layerId);
    const target = direction === 'up' ? index - 1 : index + 1;
    if (index < 0 || target < 0 || target >= state.layers.length) return state;
    const layers = [...state.layers];
    const [item] = layers.splice(index, 1);
    layers.splice(target, 0, item);
    return { layers, dirty: true };
  }),
  addClip: (clip) => set((state) => ({
    clips: [...state.clips, { ...clip, id: clip.id ?? makeId('clip') }],
    dirty: true,
  })),
  updateClip: (clipId, patch) => set((state) => ({
    clips: state.clips.map((clip) => (clip.id === clipId ? { ...clip, ...patch } : clip)),
    dirty: true,
  })),
  splitClip: (clipId) => set((state) => {
    const clip = state.clips.find((item) => item.id === clipId);
    if (!clip || clip.duration <= 1) return state;
    const half = Math.max(0.5, clip.duration / 2);
    return {
      clips: state.clips.flatMap((item) => item.id === clipId
        ? [
            { ...item, id: makeId('clip-a'), duration: half, label: `${item.label} A` },
            { ...item, id: makeId('clip-b'), start: item.start + half, duration: item.duration - half, label: `${item.label} B` },
          ]
        : [item]),
      dirty: true,
    };
  }),
  trimClip: (clipId, seconds) => set((state) => ({
    clips: state.clips.map((clip) => (clip.id === clipId ? { ...clip, duration: Math.max(0.5, clip.duration + seconds) } : clip)),
    dirty: true,
  })),
  loadTemplate: (snapshot) => set((state) => ({
    mode: snapshot.mode ?? state.mode,
    prompt: snapshot.prompt ?? state.prompt,
    duration: snapshot.duration ?? state.duration,
    layers: snapshot.layers,
    clips: snapshot.clips,
    selectedLayerId: snapshot.selectedLayerId ?? snapshot.layers.find((layer) => layer.editable !== false)?.id ?? snapshot.layers[0]?.id ?? null,
    activeTool: 'select',
    dirty: true,
  })),
  markSaved: () => set({ dirty: false, lastSavedAt: new Date().toISOString() }),
  hydrate: (snapshot) => set({
    ...snapshot,
    dirty: false,
    lastSavedAt: new Date().toISOString(),
  }),
}));

export function getAxiStudioSnapshot() {
  const state = useAxiStudioStore.getState();
  return {
    mode: state.mode,
    activeTool: state.activeTool,
    selectedLayerId: state.selectedLayerId,
    zoom: state.zoom,
    pan: state.pan,
    duration: state.duration,
    layers: state.layers,
    clips: state.clips,
    prompt: state.prompt,
  };
}

interface StudioTimelineProps {
  clips: Array<{ id: string; label: string; length: number; kind?: string }>;
  activeClipId?: string | null;
  onSelectClip?: (clipId: string) => void;
  onReorderClips?: (sourceId: string, targetId: string) => void;
}

export function StudioTimeline({ clips, activeClipId = null, onSelectClip, onReorderClips }: StudioTimelineProps) {
  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Timeline</p>
        <p className="text-xs text-slate-500">Arraste para reordenar</p>
      </div>
      <div className="flex gap-2 overflow-x-auto pb-2">
        {clips.map((clip) => (
          <button
            key={clip.id}
            type="button"
            draggable={Boolean(onReorderClips)}
            onClick={() => onSelectClip?.(clip.id)}
            onDragStart={(event) => event.dataTransfer.setData('text/plain', clip.id)}
            onDragOver={(event) => event.preventDefault()}
            onDrop={(event) => {
              const sourceId = event.dataTransfer.getData('text/plain');
              if (sourceId && sourceId !== clip.id) {
                onReorderClips?.(sourceId, clip.id);
              }
            }}
            className={[
              'min-w-44 rounded-xl border px-3 py-2 text-left transition',
              activeClipId === clip.id ? 'border-cyan bg-cyan/15' : 'border-cyan-400/20 bg-cyan-500/10 hover:border-cyan/45',
            ].join(' ')}
          >
            <p className="text-sm font-semibold text-cyan-100">{clip.label}</p>
            <div className="mt-1 flex items-center justify-between text-xs text-cyan-200/80">
              <span>{clip.kind || 'clip'}</span>
              <span>{clip.length}s</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

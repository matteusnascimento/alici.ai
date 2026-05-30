interface StudioTimelineProps {
  clips: Array<{ id: string; label: string; length: number; kind?: string }>;
  activeClipId?: string | null;
  onSelectClip?: (clipId: string) => void;
  onReorderClips?: (sourceId: string, targetId: string) => void;
}

export function StudioTimeline({ clips, activeClipId = null, onSelectClip, onReorderClips }: StudioTimelineProps) {
  const trackTone: Record<string, string> = {
    video: 'from-fuchsia-500/35 to-cyan-400/20 border-fuchsia-300/35',
    image: 'from-emerald-400/25 to-cyan-400/18 border-emerald-300/30',
    audio: 'from-cyan-400/28 to-sky-500/18 border-cyan-300/35',
    text: 'from-amber-300/24 to-fuchsia-400/18 border-amber-200/30',
    overlay: 'from-violet-400/28 to-fuchsia-400/18 border-violet-300/35',
  };

  return (
    <div className="min-h-[96px]">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Timeline multipista</p>
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <button type="button" className="rounded-lg border border-white/10 px-2 py-1 hover:border-cyan-300/40 hover:text-white" title="Diminuir zoom">-</button>
          <span className="rounded-lg border border-white/10 bg-white/[0.03] px-2 py-1">100%</span>
          <button type="button" className="rounded-lg border border-white/10 px-2 py-1 hover:border-cyan-300/40 hover:text-white" title="Aumentar zoom">+</button>
          <span>Arraste para reordenar</span>
        </div>
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
              'min-h-[76px] min-w-48 rounded-2xl border bg-gradient-to-br px-3 py-2 text-left transition',
              trackTone[clip.kind || ''] || 'from-slate-500/22 to-white/5 border-white/15',
              activeClipId === clip.id ? 'ring-2 ring-cyan-300/55 shadow-[0_0_26px_rgba(34,211,238,0.14)]' : 'hover:border-cyan/45',
            ].join(' ')}
          >
            <p className="text-sm font-semibold text-cyan-100">{clip.label}</p>
            <div className="mt-1 flex items-center justify-between text-xs text-cyan-200/80">
              <span>{clip.kind || 'clip'}</span>
              <span>{clip.length}s</span>
            </div>
            {clip.kind === 'audio' ? (
              <div className="mt-3 flex h-5 items-end gap-0.5 opacity-80">
                {Array.from({ length: 22 }).map((_, index) => (
                  <span key={index} className="w-1 rounded-full bg-cyan-200/80" style={{ height: `${6 + ((index * 7) % 16)}px` }} />
                ))}
              </div>
            ) : (
              <div className="mt-3 h-5 rounded-lg bg-black/20">
                <div className="h-full w-2/3 rounded-lg bg-white/12" />
              </div>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}

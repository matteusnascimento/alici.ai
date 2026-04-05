interface StudioTimelineProps {
  clips: Array<{ id: string; label: string; length: number }>;
}

export function StudioTimeline({ clips }: StudioTimelineProps) {
  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Timeline</p>
        <p className="text-xs text-slate-500">Arraste para reordenar</p>
      </div>
      <div className="flex gap-2 overflow-x-auto pb-2">
        {clips.map((clip) => (
          <div key={clip.id} className="min-w-40 rounded-xl border border-cyan-400/20 bg-cyan-500/10 px-3 py-2">
            <p className="text-sm font-semibold text-cyan-100">{clip.label}</p>
            <p className="text-xs text-cyan-200/80">{clip.length}s</p>
          </div>
        ))}
      </div>
    </div>
  );
}

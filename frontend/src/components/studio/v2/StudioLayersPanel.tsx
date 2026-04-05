interface StudioLayersPanelProps {
  layers: Array<{ id: string; name: string; locked?: boolean }>;
}

export function StudioLayersPanel({ layers }: StudioLayersPanelProps) {
  return (
    <div className="rounded-2xl border border-white/10 bg-black/20 p-3">
      <p className="mb-2 text-xs uppercase tracking-[0.16em] text-slate-400">Layers</p>
      <div className="space-y-1">
        {layers.map((layer) => (
          <div key={layer.id} className="flex items-center justify-between rounded-lg border border-white/10 px-2 py-1 text-xs text-slate-200">
            <span>{layer.name}</span>
            <span className="text-slate-500">{layer.locked ? 'Lock' : 'Edit'}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

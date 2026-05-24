import type { StudioVersion } from '../../../types/studioV2';

interface StudioHistoryPanelProps {
  versions: StudioVersion[];
}

export function StudioHistoryPanel({ versions }: StudioHistoryPanelProps) {
  return (
    <div className="rounded-2xl border border-white/10 bg-black/20 p-3">
      <p className="mb-2 text-xs uppercase tracking-[0.16em] text-slate-400">Historico</p>
      <div className="space-y-1">
        {versions.slice(0, 6).map((version) => (
          <div key={version.id} className="rounded-lg border border-white/10 px-2 py-1 text-xs text-slate-200">
            <p>{version.label}</p>
            <p className="text-slate-500">{new Date(version.created_at).toLocaleString('pt-BR')}</p>
          </div>
        ))}
        {versions.length === 0 ? <p className="text-xs text-slate-400">Nenhuma versao salva.</p> : null}
      </div>
    </div>
  );
}

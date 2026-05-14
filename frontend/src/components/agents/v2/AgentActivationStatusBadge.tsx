interface AgentActivationStatusBadgeProps {
  status: string;
}

export function AgentActivationStatusBadge({ status }: AgentActivationStatusBadgeProps) {
  const map: Record<string, string> = {
    active: 'border-emerald-400/45 bg-emerald-500/15 text-emerald-200',
    ready: 'border-cyan-300/45 bg-cyan-500/15 text-cyan-100',
    draft: 'border-slate-400/40 bg-slate-500/10 text-slate-200',
    incomplete: 'border-amber-300/45 bg-amber-500/15 text-amber-100',
    paused: 'border-orange-300/45 bg-orange-500/15 text-orange-100',
    error: 'border-rose-400/45 bg-rose-500/15 text-rose-100',
  };

  return <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${map[status] || map.incomplete}`}>{status}</span>;
}

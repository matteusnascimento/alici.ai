interface AgentStatusBadgeProps {
  status: 'ativo' | 'em teste' | 'pausado' | 'erro' | string;
}

export function AgentStatusBadge({ status }: AgentStatusBadgeProps) {
  const styleMap: Record<string, string> = {
    ativo: 'border-emerald-400/40 bg-emerald-500/10 text-emerald-200',
    'em teste': 'border-cyan-400/40 bg-cyan-500/10 text-cyan-100',
    pausado: 'border-slate-400/40 bg-slate-500/10 text-slate-200',
    erro: 'border-red-400/40 bg-red-500/10 text-red-200',
  };

  return <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${styleMap[status] || styleMap['em teste']}`}>{status}</span>;
}

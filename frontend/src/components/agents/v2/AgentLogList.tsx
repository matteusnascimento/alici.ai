interface AgentLogListProps {
  items: Array<Record<string, unknown>>;
}

export function AgentLogList({ items }: AgentLogListProps) {
  const safeItems = Array.isArray(items) ? items : [];

  return (
    <div className="space-y-2">
      {safeItems.map((item, index) => (
        <article key={index} className="rounded-2xl border border-white/10 bg-white/5 p-3">
          <p className="text-sm font-semibold text-white">{String(item.event_type || 'evento')}</p>
          <p className="mt-1 text-xs text-slate-300">{String(item.summary || '')}</p>
          <p className="mt-1 text-xs text-slate-500">{String(item.created_at || '')}</p>
        </article>
      ))}
      {safeItems.length === 0 ? <p className="text-sm text-slate-400">Nenhum evento encontrado.</p> : null}
    </div>
  );
}

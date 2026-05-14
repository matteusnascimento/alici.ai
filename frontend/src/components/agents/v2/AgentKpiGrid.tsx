interface AgentKpiGridProps {
  kpis: Record<string, number>;
}

export function AgentKpiGrid({ kpis }: AgentKpiGridProps) {
  return (
    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
      {Object.entries(kpis).map(([key, value]) => (
        <div key={key} className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="text-xs uppercase tracking-[0.12em] text-slate-400">{key.replace(/_/g, ' ')}</p>
          <p className="mt-2 text-2xl font-semibold text-white">{value}</p>
        </div>
      ))}
    </div>
  );
}

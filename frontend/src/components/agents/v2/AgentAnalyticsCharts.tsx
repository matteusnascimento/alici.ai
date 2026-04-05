interface AgentAnalyticsChartsProps {
  data: Record<string, unknown>;
}

export function AgentAnalyticsCharts({ data }: AgentAnalyticsChartsProps) {
  const channelDistribution = (data.channel_distribution as Record<string, number> | undefined) || {};
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <p className="font-semibold text-white">Performance por canal</p>
      <div className="mt-3 space-y-2">
        {Object.entries(channelDistribution).map(([channel, value]) => (
          <div key={channel} className="rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm text-slate-200">
            {channel}: {value}
          </div>
        ))}
        {Object.keys(channelDistribution).length === 0 ? <p className="text-sm text-slate-400">Sem dados de canal ainda.</p> : null}
      </div>
    </div>
  );
}

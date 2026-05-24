interface AgentAnalyticsCardsProps {
  data: Record<string, unknown>;
}

const keys = [
  'total_conversations',
  'leads_captured',
  'human_handoffs',
  'average_response_time_ms',
  'total_inbound_messages',
  'total_outbound_messages',
];

export function AgentAnalyticsCards({ data }: AgentAnalyticsCardsProps) {
  return (
    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
      {keys.map((key) => (
        <div key={key} className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="text-xs uppercase tracking-[0.1em] text-slate-400">{key.replace(/_/g, ' ')}</p>
          <p className="mt-2 text-2xl font-semibold text-white">{String(data[key] ?? 0)}</p>
        </div>
      ))}
    </div>
  );
}

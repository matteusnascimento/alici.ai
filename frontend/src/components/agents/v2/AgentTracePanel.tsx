interface AgentTracePanelProps {
  actions: Array<Record<string, unknown>>;
  source: string;
  confidence: string;
}

export function AgentTracePanel({ actions, source, confidence }: AgentTracePanelProps) {
  return (
    <div className="rounded-2xl border border-cyan-300/20 bg-cyan-500/10 p-4 text-sm text-cyan-100">
      <p><strong>Fonte usada:</strong> {source}</p>
      <p className="mt-1"><strong>Nota de decisao:</strong> {confidence}</p>
      <p className="mt-1"><strong>Acoes acionadas:</strong> {actions.length}</p>
    </div>
  );
}

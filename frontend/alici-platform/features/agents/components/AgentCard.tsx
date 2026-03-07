import type { AgentItem } from "../types/agentTypes";
import { Badge } from "@/components/ui/Badge";

interface AgentCardProps {
  agent: AgentItem;
}

export function AgentCard({ agent }: AgentCardProps) {
  return (
    <article className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-100">{agent.name}</h3>
        <Badge tone={agent.status === "online" ? "success" : "warning"}>{agent.status}</Badge>
      </div>
      <p className="mt-2 text-xs text-slate-400">Model: {agent.model}</p>
      <p className="mt-1 text-xs text-slate-300">Requests today: {agent.requestsToday}</p>
    </article>
  );
}

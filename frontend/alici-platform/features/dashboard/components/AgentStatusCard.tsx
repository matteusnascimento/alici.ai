import type { AgentStatus } from "@/types/dashboard";

interface AgentStatusCardProps {
  agents: AgentStatus[];
}

const statusColor: Record<AgentStatus["status"], string> = {
  online: "bg-emerald-400",
  degraded: "bg-amber-400",
  offline: "bg-rose-500"
};

export function AgentStatusCard({ agents }: AgentStatusCardProps) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
      <h3 className="text-sm font-semibold text-slate-200">Agent Status</h3>
      <ul className="mt-4 space-y-3">
        {agents.map((agent) => (
          <li key={agent.id} className="flex items-center justify-between rounded-lg bg-slate-800/60 px-3 py-2">
            <span className="text-sm text-slate-100">{agent.name}</span>
            <span className="inline-flex items-center gap-2 text-xs uppercase text-slate-300">
              <i className={`h-2.5 w-2.5 rounded-full ${statusColor[agent.status]}`} />
              {agent.status}
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}

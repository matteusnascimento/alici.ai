"use client";

import { AgentCard } from "../components/AgentCard";
import { useAgents } from "../hooks/useAgents";

export function AgentsPage() {
  const { loading, agents } = useAgents();

  if (loading) {
    return <div className="text-sm text-slate-300">Loading agents...</div>;
  }

  return (
    <section className="space-y-4">
      <div>
        <p className="text-xs uppercase tracking-widest text-slate-400">Agents</p>
        <h2 className="text-2xl font-semibold">Autonomous Fleet</h2>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {agents.map((agent) => (
          <AgentCard key={agent.id} agent={agent} />
        ))}
      </div>
    </section>
  );
}

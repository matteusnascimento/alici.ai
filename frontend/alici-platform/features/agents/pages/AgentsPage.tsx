"use client";

import Link from "next/link";
import { Bot } from "lucide-react";
import { AgentCard } from "../components/AgentCard";
import { useAgents } from "../hooks/useAgents";

export function AgentsPage() {
  const { loading, agents, deleteAgent } = useAgents();

  if (loading) {
    return <div className="text-sm text-slate-300">Loading agents...</div>;
  }

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-widest text-slate-400">Agents</p>
          <h2 className="text-2xl font-semibold">Autonomous Fleet</h2>
        </div>
        <Link
          href="/agents/create"
          className="flex items-center gap-2 rounded-xl bg-sky-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-sky-400"
        >
          <Bot size={16} />
          Create New Agent
        </Link>
      </div>

      {agents.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/40 p-12 text-center">
          <Bot size={40} className="mx-auto mb-3 text-slate-600" />
          <p className="text-sm text-slate-400">No agents yet. Create your first agent to get started.</p>
          <Link
            href="/agents/create"
            className="mt-4 inline-flex items-center gap-2 rounded-xl bg-sky-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-sky-400"
          >
            <Bot size={16} />
            Create New Agent
          </Link>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {agents.map((agent) => (
            <AgentCard key={agent.id} agent={agent} onDelete={deleteAgent} />
          ))}
        </div>
      )}
    </section>
  );
}

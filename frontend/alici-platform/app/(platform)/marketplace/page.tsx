"use client";

import { useEffect, useState } from "react";
import { Store } from "lucide-react";
import { api } from "@/services/api";

interface AgentTemplate { id: string; name: string; description?: string; model: string; is_public: boolean }

export default function MarketplacePage() {
  const [agents, setAgents] = useState<AgentTemplate[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    void (async () => {
      try {
        const res = await api.get<{ data: { agents: AgentTemplate[] } }>("/agents");
        if (active) setAgents((res.data?.data?.agents ?? []).filter((a) => a.is_public));
      } catch { /* ignore */ } finally { if (active) setLoading(false); }
    })();
    return () => { active = false; };
  }, []);

  return (
    <section className="space-y-6">
      <header className="flex items-center gap-3">
        <Store size={22} className="text-sky-400" />
        <div>
          <p className="text-xs uppercase tracking-widest text-slate-400">Platform</p>
          <h1 className="text-2xl font-semibold">Marketplace</h1>
          <p className="mt-1 text-sm text-slate-400">Agentes públicos disponíveis para uso imediato</p>
        </div>
      </header>
      {loading ? (
        <p className="text-sm text-slate-400">Carregando agentes...</p>
      ) : agents.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-700 p-8 text-center">
          <p className="text-sm text-slate-500">Nenhum agente público disponível ainda.</p>
          <p className="mt-1 text-xs text-slate-600">Publique um agente em "Agent Builder" para vê-lo aqui.</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {agents.map((agent) => (
            <article key={agent.id} className="rounded-xl border border-slate-800 bg-slate-900/70 p-5 space-y-2">
              <div className="flex items-start justify-between gap-2">
                <h3 className="font-semibold text-slate-100">{agent.name}</h3>
                <span className="shrink-0 rounded-full border border-sky-500/30 px-2 py-0.5 text-xs text-sky-400">{agent.model}</span>
              </div>
              {agent.description && <p className="text-sm text-slate-400">{agent.description}</p>}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

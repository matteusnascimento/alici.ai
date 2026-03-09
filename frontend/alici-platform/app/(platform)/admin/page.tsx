"use client";

import { ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "@/services/api";

interface Stats { total_users: number; total_agents: number; total_requests: number; total_knowledge_docs: number }

export default function AdminPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    void (async () => {
      try {
        const res = await api.get<{ data: { stats: Stats } }>("/platform/overview");
        if (active) setStats(res.data?.data?.stats ?? null);
      } catch { /* ignore */ } finally { if (active) setLoading(false); }
    })();
    return () => { active = false; };
  }, []);

  const items = stats ? [
    { label: "Usuários",   value: stats.total_users },
    { label: "Agentes",    value: stats.total_agents },
    { label: "Requests",   value: stats.total_requests },
    { label: "Documentos", value: stats.total_knowledge_docs },
  ] : [];

  return (
    <section className="space-y-6">
      <header className="flex items-center gap-3">
        <ShieldCheck size={22} className="text-sky-400" />
        <div>
          <p className="text-xs uppercase tracking-widest text-slate-400">Sistema</p>
          <h1 className="text-2xl font-semibold">Admin</h1>
        </div>
      </header>
      {loading ? <p className="text-sm text-slate-400">Carregando...</p> : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {items.map((item) => (
            <div key={item.label} className="rounded-xl border border-slate-800 bg-slate-900/70 p-4">
              <p className="text-xs text-slate-400">{item.label}</p>
              <p className="mt-1 text-2xl font-bold text-slate-100">{item.value.toLocaleString()}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

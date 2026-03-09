"use client";

import { useEffect, useState } from "react";
import { BarChart3 } from "lucide-react";
import { api } from "@/services/api";

interface UsageEntry { endpoint: string; tokens_used: number; cost: number; created_at: string }

export default function AnalyticsPage() {
  const [logs, setLogs] = useState<UsageEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    void (async () => {
      try {
        const res = await api.get<{ data: { recent_activity?: UsageEntry[] } }>("/platform/overview");
        if (active) setLogs(res.data?.data?.recent_activity ?? []);
      } catch { /* ignore */ } finally { if (active) setLoading(false); }
    })();
    return () => { active = false; };
  }, []);

  return (
    <section className="space-y-6">
      <header className="flex items-center gap-3">
        <BarChart3 size={22} className="text-sky-400" />
        <div>
          <p className="text-xs uppercase tracking-widest text-slate-400">Insights</p>
          <h1 className="text-2xl font-semibold">Analytics</h1>
        </div>
      </header>

      {loading ? (
        <p className="text-sm text-slate-400">Carregando dados...</p>
      ) : logs.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-700 p-8 text-center">
          <p className="text-sm text-slate-500">Nenhuma atividade registrada ainda.</p>
        </div>
      ) : (
        <div className="rounded-xl border border-slate-800 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="border-b border-slate-800 bg-slate-900/80">
              <tr>
                {["Endpoint", "Tokens", "Custo", "Data"].map((h) => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-400">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {logs.map((log, i) => (
                <tr key={i} className="bg-slate-900/40 hover:bg-slate-800/50">
                  <td className="px-4 py-3 font-mono text-xs text-slate-300">{log.endpoint}</td>
                  <td className="px-4 py-3 text-slate-200">{log.tokens_used}</td>
                  <td className="px-4 py-3 text-slate-200">${Number(log.cost).toFixed(4)}</td>
                  <td className="px-4 py-3 text-slate-400 text-xs">{new Date(log.created_at).toLocaleString("pt-BR")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

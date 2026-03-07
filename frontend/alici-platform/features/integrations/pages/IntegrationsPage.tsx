"use client";

import { Badge } from "@/components/ui/Badge";
import { useIntegrations } from "../hooks/useIntegrations";

export function IntegrationsPage() {
  const { loading, integrations } = useIntegrations();

  if (loading) {
    return <div className="text-sm text-slate-300">Loading integrations...</div>;
  }

  return (
    <section className="space-y-4">
      <div>
        <p className="text-xs uppercase tracking-widest text-slate-400">Integrations</p>
        <h2 className="text-2xl font-semibold">Connected Channels</h2>
      </div>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {integrations.map((item) => (
          <article key={item.id} className="rounded-xl border border-slate-800 bg-slate-900/70 p-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-slate-100">{item.provider}</h3>
              <Badge tone={item.status === "connected" ? "success" : "warning"}>{item.status}</Badge>
            </div>
            <p className="mt-2 text-xs text-slate-400">Last sync: {item.lastSync}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

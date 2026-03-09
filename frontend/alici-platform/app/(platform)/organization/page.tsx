"use client";

import { Building2 } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "@/services/api";

interface OrgInfo { name: string; plan: string; monthly_limit: number; current_usage: number }

export default function OrganizationPage() {
  const [org, setOrg] = useState<OrgInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    void (async () => {
      try {
        const res = await api.get<{ data: { organization: OrgInfo } }>("/platform/overview");
        if (active) setOrg(res.data?.data?.organization ?? null);
      } catch { /* ignore */ } finally { if (active) setLoading(false); }
    })();
    return () => { active = false; };
  }, []);

  return (
    <section className="space-y-6">
      <header className="flex items-center gap-3">
        <Building2 size={22} className="text-sky-400" />
        <div>
          <p className="text-xs uppercase tracking-widest text-slate-400">Conta</p>
          <h1 className="text-2xl font-semibold">Organização</h1>
        </div>
      </header>
      {loading ? <p className="text-sm text-slate-400">Carregando...</p> : !org ? (
        <p className="text-sm text-red-400">Não foi possível carregar os dados da organização.</p>
      ) : (
        <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-5 space-y-4">
          <div><p className="text-xs text-slate-400">Nome</p><p className="text-sm text-slate-100">{org.name}</p></div>
          <div><p className="text-xs text-slate-400">Plano</p><p className="text-sm capitalize text-slate-100">{org.plan}</p></div>
          <div>
            <p className="text-xs text-slate-400">Uso do mês</p>
            <div className="mt-1 h-2 w-full rounded-full bg-slate-800">
              <div className="h-2 rounded-full bg-sky-500" style={{ width: `${Math.min(100, (org.current_usage / org.monthly_limit) * 100)}%` }} />
            </div>
            <p className="mt-1 text-xs text-slate-500">{org.current_usage} / {org.monthly_limit} requests</p>
          </div>
        </div>
      )}
    </section>
  );
}

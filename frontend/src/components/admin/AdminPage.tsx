import { Building2, CreditCard, LockKeyhole, ScrollText, ShieldCheck, Users } from 'lucide-react';
import { useEffect, useState } from 'react';

import { ApiError } from '../../services/api';
import { getAdminOverview, type AdminOverview } from '../../services/admin.service';

function AdminCard({ title, children, icon: Icon }: { title: string; children: React.ReactNode; icon: typeof Building2 }) {
  return (
    <section className="rounded-2xl border border-white/10 bg-slate-950/60 p-5 shadow-[0_18px_55px_rgba(0,0,0,0.22)]">
      <div className="mb-4 flex items-center gap-3">
        <span className="grid h-11 w-11 place-items-center rounded-full bg-violet-500/15 text-violet-200">
          <Icon size={22} />
        </span>
        <h2 className="font-display text-xl text-white">{title}</h2>
      </div>
      {children}
    </section>
  );
}

function EmptyAdminState({ children }: { children: string }) {
  return (
    <div className="rounded-2xl border border-dashed border-white/15 bg-white/[0.03] p-5 text-sm text-slate-400">
      {children}
    </div>
  );
}

export function AdminPage() {
  const [overview, setOverview] = useState<AdminOverview | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void getAdminOverview()
      .then((data) => {
        setOverview(data);
        setError(null);
      })
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : 'Falha ao carregar Administracao');
      });
  }, []);

  if (error) {
    return <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 p-5 text-rose-100">{error}</div>;
  }

  return (
    <div className="space-y-7">
      <header className="rounded-[1.75rem] border border-white/10 bg-[radial-gradient(circle_at_10%_0%,rgba(124,58,237,0.18),transparent_32%),linear-gradient(145deg,rgba(15,23,42,0.88),rgba(2,6,23,0.74))] p-7">
        <p className="text-xs font-semibold uppercase tracking-[0.25em] text-violet-200">Owner only</p>
        <h1 className="mt-2 font-display text-4xl text-white">Administracao</h1>
        <p className="mt-2 max-w-2xl text-sm text-slate-300">
          Controle operacional de empresas, usuarios, permissoes, billing, seguranca e auditoria. A API retorna 403 para usuarios sem role owner.
        </p>
      </header>

      <div className="grid gap-6 xl:grid-cols-2">
        <AdminCard title="Empresas" icon={Building2}>
          {overview?.empresas.length ? (
            <div className="space-y-2">
              {overview.empresas.map((empresa) => (
                <div key={empresa} className="rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-white">{empresa}</div>
              ))}
            </div>
          ) : <EmptyAdminState>Sem empresas reais cadastradas nos perfis atuais.</EmptyAdminState>}
        </AdminCard>

        <AdminCard title="Usuarios e permissoes" icon={Users}>
          {overview?.usuarios.length ? (
            <div className="space-y-2">
              {overview.usuarios.map((user) => (
                <div key={user.id} className="grid gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm md:grid-cols-[1fr_auto] md:items-center">
                  <div>
                    <p className="font-semibold text-white">{user.name}</p>
                    <p className="text-xs text-slate-400">{user.email}</p>
                  </div>
                  <span className="rounded-full border border-cyan-300/20 bg-cyan-300/10 px-3 py-1 text-xs font-semibold text-cyan-200">{user.role}</span>
                </div>
              ))}
            </div>
          ) : <EmptyAdminState>Sem usuarios reais para listar.</EmptyAdminState>}
        </AdminCard>

        <AdminCard title="Billing" icon={CreditCard}>
          <div className="grid gap-3 sm:grid-cols-2">
            {(overview?.billing ?? []).map((item) => (
              <div key={item.label} className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
                <p className="text-xs text-slate-400">{item.label}</p>
                <p className="mt-1 font-display text-3xl text-white">{item.value}</p>
              </div>
            ))}
          </div>
        </AdminCard>

        <AdminCard title="Seguranca" icon={ShieldCheck}>
          <div className="grid gap-3 sm:grid-cols-2">
            {(overview?.seguranca ?? []).map((item) => (
              <div key={item.label} className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
                <p className="text-xs text-slate-400">{item.label}</p>
                <p className="mt-1 font-display text-3xl text-white">{item.value}</p>
              </div>
            ))}
          </div>
        </AdminCard>

        <AdminCard title="Auditoria" icon={ScrollText}>
          <div className="grid gap-3 sm:grid-cols-2">
            {(overview?.auditoria ?? []).map((item) => (
              <div key={item.label} className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
                <p className="text-xs text-slate-400">{item.label}</p>
                <p className="mt-1 font-display text-3xl text-white">{item.value}</p>
              </div>
            ))}
          </div>
        </AdminCard>

        <AdminCard title="Permissoes" icon={LockKeyhole}>
          <div className="flex flex-wrap gap-2">
            {(overview?.permissoes ?? []).map((role) => (
              <span key={role} className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-2 text-sm text-slate-200">{role}</span>
            ))}
          </div>
        </AdminCard>
      </div>
    </div>
  );
}

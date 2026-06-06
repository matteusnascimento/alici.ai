import { CreditCard, Gauge, Loader2, ReceiptText, ShieldCheck, WalletCards } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

import { ApiError } from '../../services/api';
import { getAdminBilling, type AdminBillingResponse } from '../../services/admin.service';
import type { BillingHistoryItem } from '../../types/billing';

function formatCurrency(value: number, currency = 'BRL') {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: currency.toUpperCase() || 'BRL',
    maximumFractionDigits: 2,
  }).format(value);
}

function formatDate(value: string | null | undefined) {
  if (!value) return 'Nao informado';
  return new Date(value).toLocaleDateString('pt-BR');
}

function formatLimit(value: number) {
  return value < 0 ? 'Ilimitado' : value.toLocaleString('pt-BR');
}

function usagePercent(used: number, limit: number) {
  if (limit <= 0) return 0;
  return Math.min(100, Math.round((used / limit) * 100));
}

function BillingCard({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-2xl border border-white/10 bg-slate-950/58 p-5 shadow-[0_22px_70px_rgba(0,0,0,0.25)]">
      <div className="mb-5">
        <h2 className="font-display text-2xl text-white">{title}</h2>
        <p className="mt-1 text-sm text-slate-400">{description}</p>
      </div>
      {children}
    </section>
  );
}

function EmptyState({ children }: { children: string }) {
  return (
    <div className="rounded-2xl border border-dashed border-white/15 bg-white/[0.03] p-5 text-center text-sm text-slate-400">
      {children}
    </div>
  );
}

function EventList({ events }: { events: BillingHistoryItem[] }) {
  if (events.length === 0) {
    return <EmptyState>Nenhum registro real retornado pelo billing.</EmptyState>;
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-white/10">
      <table className="min-w-full text-sm">
        <thead className="bg-white/[0.03] text-left text-slate-400">
          <tr>
            <th className="px-4 py-3">Evento</th>
            <th className="px-4 py-3">Valor</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Data</th>
          </tr>
        </thead>
        <tbody>
          {events.map((event) => (
            <tr key={`${event.id}-${event.event_type}`} className="border-t border-white/10">
              <td className="px-4 py-3">
                <p className="font-semibold text-white">{event.event_type}</p>
                <p className="mt-1 text-xs text-slate-500">{event.description || event.stripe_event_id || 'Sem descricao'}</p>
              </td>
              <td className="px-4 py-3 text-slate-200">{formatCurrency(event.amount, event.currency || 'BRL')}</td>
              <td className="px-4 py-3">
                <span className="rounded-full border border-white/10 bg-white/[0.04] px-2 py-1 text-xs text-slate-300">
                  {event.status || 'registrado'}
                </span>
              </td>
              <td className="px-4 py-3 text-slate-400">{formatDate(event.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function AdminBillingPage() {
  const [billing, setBilling] = useState<AdminBillingResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    void getAdminBilling()
      .then((data) => {
        setBilling(data);
        setError(null);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : 'Falha ao carregar billing administrativo.'))
      .finally(() => setLoading(false));
  }, []);

  const invoiceEvents = useMemo(
    () => (billing?.events ?? []).filter((event) => event.event_type.toLowerCase().includes('invoice')),
    [billing?.events],
  );

  if (loading) {
    return (
      <div className="grid min-h-[360px] place-items-center rounded-2xl border border-white/10 bg-slate-950/58">
        <Loader2 className="animate-spin text-violet-300" size={28} />
      </div>
    );
  }

  if (error) {
    return <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 p-5 text-rose-100">{error}</div>;
  }

  if (!billing) {
    return <EmptyState>Nenhum dado de billing disponivel.</EmptyState>;
  }

  return (
    <div className="space-y-6">
      {billing.message ? (
        <div className="rounded-2xl border border-amber-400/30 bg-amber-500/10 p-4 text-sm text-amber-100">
          {billing.message}
        </div>
      ) : null}

      <section className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <BillingCard title="Plano Atual" description="Assinatura ativa, ciclo e estado operacional da conta.">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
              <div className="mb-3 flex items-center gap-3">
                <span className="grid h-11 w-11 place-items-center rounded-full bg-violet-500/15 text-violet-200">
                  <ShieldCheck size={20} />
                </span>
                <div>
                  <p className="text-sm text-slate-400">Plano</p>
                  <p className="font-display text-2xl text-white">{billing.current.plan_name}</p>
                </div>
              </div>
              <p className="text-sm text-slate-400">Status: <span className="font-semibold text-white">{billing.current.status}</span></p>
              <p className="mt-1 text-sm text-slate-400">Ciclo: <span className="font-semibold text-white">{billing.current.billing_cycle}</span></p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
              <div className="mb-3 flex items-center gap-3">
                <span className="grid h-11 w-11 place-items-center rounded-full bg-cyan-400/12 text-cyan-200">
                  <WalletCards size={20} />
                </span>
                <div>
                  <p className="text-sm text-slate-400">Proxima cobranca</p>
                  <p className="font-display text-2xl text-white">{formatDate(billing.current.next_renewal_at)}</p>
                </div>
              </div>
              <p className="text-sm text-slate-400">Provider: <span className="font-semibold text-white">{billing.current.provider ?? 'Nao informado'}</span></p>
              <p className="mt-1 text-sm text-slate-400">Stripe: <span className="font-semibold text-white">{billing.stripe_configured ? 'Configurado' : 'Pendente'}</span></p>
            </div>
          </div>
        </BillingCard>

        <BillingCard title="Consumo" description="Uso real retornado pelo backend de billing.">
          {billing.usage.length === 0 ? <EmptyState>Sem consumo real retornado.</EmptyState> : (
            <div className="space-y-3">
              {billing.usage.map((item) => {
                const pct = usagePercent(item.used, item.limit);
                return (
                  <div key={item.metric} className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                    <div className="mb-2 flex items-center justify-between gap-3">
                      <span className="font-semibold text-white">{item.metric}</span>
                      <span className="text-sm text-slate-400">{item.used.toLocaleString('pt-BR')} / {formatLimit(item.limit)}</span>
                    </div>
                    <div className="h-2 rounded-full bg-white/10">
                      <div className="h-2 rounded-full bg-cyan-300" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </BillingCard>
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        <BillingCard title="Limites" description="Limites contratados pelo plano atual.">
          {billing.limits.length === 0 ? <EmptyState>Sem limites reais configurados para o plano atual.</EmptyState> : (
            <div className="grid gap-3 md:grid-cols-2">
              {billing.limits.map((limit) => (
                <div key={limit.key} className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                  <div className="mb-3 flex items-center gap-3">
                    <span className="grid h-10 w-10 place-items-center rounded-full bg-violet-500/15 text-violet-200">
                      <Gauge size={18} />
                    </span>
                    <p className="font-semibold text-white">{limit.key}</p>
                  </div>
                  <p className="font-display text-3xl text-white">{formatLimit(limit.value)}</p>
                </div>
              ))}
            </div>
          )}
        </BillingCard>

        <BillingCard title="Resumo Stripe" description="Somente leitura. Alteracoes continuam no fluxo Stripe existente.">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
              <ReceiptText className="mb-3 text-violet-200" size={22} />
              <p className="text-sm text-slate-400">Eventos</p>
              <p className="font-display text-3xl text-white">{billing.events.length}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
              <CreditCard className="mb-3 text-cyan-200" size={22} />
              <p className="text-sm text-slate-400">Faturas</p>
              <p className="font-display text-3xl text-white">{invoiceEvents.length}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
              <WalletCards className="mb-3 text-emerald-200" size={22} />
              <p className="text-sm text-slate-400">Cliente Stripe</p>
              <p className="break-all text-sm font-semibold text-white">{billing.current.stripe_customer_id ?? 'Nao informado'}</p>
            </div>
          </div>
        </BillingCard>
      </section>

      <BillingCard title="Faturas" description="Eventos de invoice pagos ou recusados pelo Stripe.">
        <EventList events={invoiceEvents} />
      </BillingCard>

      <BillingCard title="Historico" description="Registro administrativo de eventos de assinatura e cobranca.">
        <EventList events={billing.events} />
      </BillingCard>
    </div>
  );
}

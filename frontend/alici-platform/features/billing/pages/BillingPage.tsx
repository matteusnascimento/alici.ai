"use client";

import { useBilling } from "../hooks/useBilling";

export function BillingPage() {
  const { loading, actionLoading, error, overview, upgrade, cancelSubscription } = useBilling();

  if (loading) {
    return <div className="text-sm text-slate-300">Loading billing...</div>;
  }

  if (error) {
    return <div className="text-sm text-red-400">{error}</div>;
  }

  if (!overview) {
    return <div className="text-sm text-slate-400">No billing information available</div>;
  }

  return (
    <section className="space-y-4">
      <div>
        <p className="text-xs uppercase tracking-widest text-slate-400">Billing</p>
        <h2 className="text-2xl font-semibold">Revenue and Plan Control</h2>
      </div>
      <article className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
        <p className="text-sm text-slate-400">Current Plan</p>
        <p className="mt-1 text-xl font-semibold text-slate-100">{overview?.plan?.name ?? "No plan"}</p>
        <p className="mt-1 text-sm text-slate-300">
          R$ {overview?.plan?.priceMonthly ?? 0}/month - {overview?.plan?.seats ?? 0} seats
        </p>
        <div className="mt-4 flex gap-2">
          <button
            type="button"
            onClick={() => void upgrade("pro")}
            disabled={actionLoading}
            className="rounded-lg bg-sky-500 px-3 py-2 text-sm font-semibold text-white disabled:opacity-60"
          >
            Upgrade Plan
          </button>
          <button
            type="button"
            onClick={() => void cancelSubscription()}
            disabled={actionLoading}
            className="rounded-lg border border-red-500/40 px-3 py-2 text-sm font-semibold text-red-300 disabled:opacity-60"
          >
            Cancel Subscription
          </button>
        </div>
      </article>
      <div className="space-y-2">
        {overview?.invoices?.length ? (
          overview.invoices.map((invoice) => (
            <div key={invoice.id} className="flex items-center justify-between rounded-lg border border-slate-800 px-4 py-3">
              <span className="text-sm text-slate-100">{invoice.period}</span>
              <span className="text-sm text-slate-300">R$ {invoice.amount}</span>
              <span className="text-xs uppercase text-emerald-300">{invoice.status}</span>
            </div>
          ))
        ) : (
          <p className="text-sm text-slate-400">No invoices yet</p>
        )}
      </div>
    </section>
  );
}

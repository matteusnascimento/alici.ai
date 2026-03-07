"use client";

import { useBilling } from "../hooks/useBilling";

export function BillingPage() {
  const { loading, overview } = useBilling();

  if (loading || !overview) {
    return <div className="text-sm text-slate-300">Loading billing...</div>;
  }

  return (
    <section className="space-y-4">
      <div>
        <p className="text-xs uppercase tracking-widest text-slate-400">Billing</p>
        <h2 className="text-2xl font-semibold">Revenue and Plan Control</h2>
      </div>
      <article className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
        <p className="text-sm text-slate-400">Current Plan</p>
        <p className="mt-1 text-xl font-semibold text-slate-100">{overview.plan.name}</p>
        <p className="mt-1 text-sm text-slate-300">R$ {overview.plan.priceMonthly}/month - {overview.plan.seats} seats</p>
      </article>
      <div className="space-y-2">
        {overview.invoices.map((invoice) => (
          <div key={invoice.id} className="flex items-center justify-between rounded-lg border border-slate-800 px-4 py-3">
            <span className="text-sm text-slate-100">{invoice.period}</span>
            <span className="text-sm text-slate-300">R$ {invoice.amount}</span>
            <span className="text-xs uppercase text-emerald-300">{invoice.status}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

import type { BillingPlan, CurrentSubscription } from '../../types/billing';

interface PlanCardProps {
  current: CurrentSubscription | null;
  plans: BillingPlan[];
  onUpgrade: (planId: string) => void;
}

export function PlanCard({ current, plans, onUpgrade }: PlanCardProps) {
  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
      <h2 className="font-display text-2xl text-white">Subscription / Plan</h2>
      <p className="mt-2 text-sm text-slate-300">
        Atual: <span className="text-white">{current?.plan_name ?? 'free'}</span> ({current?.status ?? 'active'})
      </p>
      <div className="mt-4 grid gap-3 md:grid-cols-3">
        {plans.map((plan) => (
          <article key={plan.id} className="rounded-2xl border border-white/10 bg-ink/40 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-cyan">{plan.name}</p>
            <p className="mt-2 font-display text-2xl text-white">R$ {plan.monthly_price.toFixed(0)}</p>
            <button
              type="button"
              disabled={current?.plan_id === plan.id}
              onClick={() => onUpgrade(plan.id)}
              className="mt-3 w-full rounded-xl border border-white/20 px-3 py-2 text-sm text-slate-100 disabled:opacity-50"
            >
              {current?.plan_id === plan.id ? 'Plano ativo' : 'Upgrade'}
            </button>
          </article>
        ))}
      </div>
    </section>
  );
}

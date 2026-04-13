import type { BillingPlan, CurrentSubscription } from '../../types/billing';

interface PlanCardProps {
  current: CurrentSubscription | null;
  plans: BillingPlan[];
  billingCycle: 'monthly' | 'yearly';
  onBillingCycleChange: (cycle: 'monthly' | 'yearly') => void;
  onUpgrade: (planId: string, billingCycle: 'monthly' | 'yearly') => void;
  onOpenPortal?: () => void;
}

export function PlanCard({
  current,
  plans,
  billingCycle,
  onBillingCycleChange,
  onUpgrade,
  onOpenPortal,
}: PlanCardProps) {
  const activePlanId = current?.plan_id;

  return (
    <section className="rounded-3xl border border-white/10 bg-gradient-to-b from-white/[0.05] to-white/[0.02] p-5 md:p-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h2 className="font-display text-2xl text-white md:text-3xl">Assinatura e planos</h2>
          <p className="mt-2 text-sm text-slate-300">Sua base de cobranca com opcao de upgrade imediato.</p>
        </div>
        <div className="rounded-2xl border border-cyan/25 bg-cyan/10 px-4 py-3">
          <p className="text-[11px] uppercase tracking-[0.2em] text-cyan/90">Plano ativo</p>
          <p className="mt-1 text-base font-semibold text-white">{current?.plan_name ?? 'Free'}</p>
          <p className="text-xs text-slate-300">{current?.status ?? 'active'} • {current?.billing_cycle ?? 'monthly'}</p>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-3">
        <div className="inline-flex rounded-xl border border-white/15 bg-black/20 p-1 text-xs">
          <button
            type="button"
            onClick={() => onBillingCycleChange('monthly')}
            className={`rounded-lg px-3 py-1.5 transition ${billingCycle === 'monthly' ? 'bg-cyan/20 text-cyan' : 'text-slate-300 hover:text-white'}`}
          >
            Mensal
          </button>
          <button
            type="button"
            onClick={() => onBillingCycleChange('yearly')}
            className={`rounded-lg px-3 py-1.5 transition ${billingCycle === 'yearly' ? 'bg-cyan/20 text-cyan' : 'text-slate-300 hover:text-white'}`}
          >
            Anual
          </button>
        </div>
        {onOpenPortal ? (
          <button
            type="button"
            onClick={onOpenPortal}
            className="rounded-xl border border-white/20 px-3 py-2 text-xs font-semibold text-slate-100 transition hover:border-cyan/45 hover:text-cyan"
          >
            Gerenciar assinatura
          </button>
        ) : null}
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-3">
        {plans.map((plan) => (
          <article
            key={plan.id}
            className={`rounded-2xl border p-4 transition ${
              activePlanId === plan.id ? 'border-cyan/35 bg-cyan/10' : 'border-white/10 bg-black/20 hover:border-white/25 hover:bg-white/[0.04]'
            }`}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-cyan">{plan.name}</p>
                <p className="mt-2 font-display text-2xl text-white">
                  R$ {(billingCycle === 'yearly' ? plan.yearly_price ?? plan.monthly_price : plan.monthly_price).toFixed(0)}
                </p>
                <p className="text-xs text-slate-300">{billingCycle === 'yearly' ? 'por ano' : 'por mes'}</p>
              </div>
              {activePlanId === plan.id ? (
                <span className="rounded-full border border-cyan/35 bg-cyan/10 px-2 py-1 text-[10px] uppercase tracking-[0.2em] text-cyan">Ativo</span>
              ) : null}
            </div>

            <ul className="mt-3 space-y-1.5 text-xs text-slate-200">
              {plan.features.slice(0, 3).map((feature) => (
                <li key={feature}>• {feature}</li>
              ))}
            </ul>

            {plan.yearly_price ? <p className="mt-2 text-xs text-slate-400">Anual: R$ {plan.yearly_price.toFixed(0)}</p> : null}

            <button
              type="button"
              disabled={activePlanId === plan.id}
              onClick={() => onUpgrade(plan.id, billingCycle)}
              className="mt-4 w-full rounded-xl border border-white/20 px-3 py-2 text-sm font-semibold text-slate-100 transition hover:border-cyan/45 hover:text-cyan disabled:cursor-not-allowed disabled:opacity-50"
            >
              {activePlanId === plan.id ? 'Plano ativo' : 'Fazer upgrade'}
            </button>
          </article>
        ))}
      </div>
    </section>
  );
}

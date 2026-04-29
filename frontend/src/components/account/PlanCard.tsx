import type { BillingPlan, CurrentSubscription } from '../../types/billing';

interface PlanCardProps {
  current: CurrentSubscription | null;
  plans: BillingPlan[];
  billingCycle: 'monthly' | 'yearly';
  loading?: boolean;
  error?: string | null;
  onBillingCycleChange: (cycle: 'monthly' | 'yearly') => void;
  onUpgrade: (planId: string, billingCycle: 'monthly' | 'yearly') => void;
  onOpenPortal?: () => void;
}

type PlanVisual = {
  accent: string;
  border: string;
  activeBorder: string;
  activeBg: string;
  badge: string;
  badgeText: string;
  ctaClass: string;
};

const PLAN_VISUALS: Record<string, PlanVisual> = {
  free: {
    accent: 'text-slate-300',
    border: 'border-white/10',
    activeBorder: 'border-slate-400/35',
    activeBg: 'bg-slate-400/8',
    badge: 'border-slate-400/35 bg-slate-400/10',
    badgeText: 'text-slate-300',
    ctaClass: 'border-white/15 text-slate-400 hover:border-white/30 hover:text-white',
  },
  pro: {
    accent: 'text-cyan',
    border: 'border-white/10',
    activeBorder: 'border-cyan/40',
    activeBg: 'bg-cyan/8',
    badge: 'border-cyan/40 bg-cyan/10',
    badgeText: 'text-cyan',
    ctaClass: 'bg-cyan text-ink hover:bg-cyan/90',
  },
  business: {
    accent: 'text-violet-300',
    border: 'border-white/10',
    activeBorder: 'border-violet-400/40',
    activeBg: 'bg-violet-500/8',
    badge: 'border-violet-400/35 bg-violet-500/10',
    badgeText: 'text-violet-300',
    ctaClass: 'border-violet-400/45 text-violet-200 hover:bg-violet-500/15 hover:border-violet-300/60',
  },
};

function getVisual(planId: string): PlanVisual {
  return PLAN_VISUALS[planId] ?? PLAN_VISUALS.pro;
}

function planCTA(planId: string, isActive: boolean): string {
  if (isActive) return 'Plano ativo';
  if (planId === 'free') return 'Fazer downgrade';
  if (planId === 'business') return '⚡ Testar Business';
  return '🚀 Fazer upgrade agora';
}

function isRecommended(plan: BillingPlan, plans: BillingPlan[]): boolean {
  if (plan.id === 'pro') return true;
  // fallback: middle plan among paid plans
  const paid = plans.filter((p) => p.monthly_price > 0);
  return paid.length === 1 && paid[0].id === plan.id;
}

function yearlySavings(plan: BillingPlan): number | null {
  if (!plan.yearly_price || plan.monthly_price === 0) return null;
  const annualMonthly = plan.monthly_price * 12;
  const savings = Math.round(((annualMonthly - plan.yearly_price) / annualMonthly) * 100);
  return savings > 0 ? savings : null;
}

export function PlanCard({
  current,
  plans,
  billingCycle,
  loading = false,
  error = null,
  onBillingCycleChange,
  onUpgrade,
  onOpenPortal,
}: PlanCardProps) {
  const activePlanId = current?.plan_id;
  const hasPlans = plans.length > 0;
  const canOpenPortal = Boolean(onOpenPortal && current?.stripe_customer_id && activePlanId !== 'free');

  return (
    <section id="billing-plans" className="rounded-3xl border border-white/10 bg-gradient-to-b from-white/[0.05] to-white/[0.02] p-5 md:p-6">
      {/* Header */}
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h2 className="font-display text-2xl text-white md:text-3xl">
            Escolha o plano ideal para escalar sua operação
          </h2>
          <p className="mt-2 text-sm text-slate-400">
            Plano atual:{' '}
            <span className="font-semibold text-white">{current?.plan_name ?? 'Free'}</span>
            {current?.next_renewal_at ? (
              <span className="ml-2 text-slate-500">
                • renova em {new Date(current.next_renewal_at).toLocaleDateString('pt-BR')}
              </span>
            ) : null}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Ciclo de cobrança */}
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
              <span className="ml-1 rounded-md bg-emerald-500/20 px-1 py-0.5 text-[10px] text-emerald-300">
                -20%
              </span>
            </button>
          </div>

          {canOpenPortal ? (
            <button
              type="button"
              onClick={onOpenPortal}
              className="rounded-xl border border-white/20 px-3 py-2 text-xs font-semibold text-slate-100 transition hover:border-cyan/45 hover:text-cyan"
            >
              Gerenciar assinatura
            </button>
          ) : null}
        </div>
      </div>

      {/* Plan cards */}
      {loading ? (
        <div className="mt-6 grid gap-4 md:grid-cols-3">
          {[0, 1, 2].map((item) => (
            <div key={item} className="min-h-[320px] animate-pulse rounded-3xl border border-white/10 bg-white/[0.04] p-5">
              <div className="h-3 w-24 rounded-full bg-white/10" />
              <div className="mt-6 h-8 w-28 rounded-full bg-white/10" />
              <div className="mt-8 space-y-3">
                <div className="h-3 rounded-full bg-white/10" />
                <div className="h-3 w-10/12 rounded-full bg-white/10" />
                <div className="h-3 w-8/12 rounded-full bg-white/10" />
              </div>
              <div className="mt-10 h-11 rounded-2xl bg-white/10" />
            </div>
          ))}
        </div>
      ) : !hasPlans ? (
        <div className="mt-6 rounded-2xl border border-rose-400/30 bg-rose-500/10 p-4 text-sm text-rose-200">
          {error ?? 'Nao foi possivel carregar os planos reais do billing agora.'}
        </div>
      ) : (
        <div className="mt-6 grid gap-4 md:grid-cols-3">
          {plans.map((plan) => {
          const visual = getVisual(plan.id);
          const isActive = activePlanId === plan.id;
          const recommended = isRecommended(plan, plans);
          const price = billingCycle === 'yearly' ? (plan.yearly_price ?? plan.monthly_price) : plan.monthly_price;
          const savings = billingCycle === 'yearly' ? yearlySavings(plan) : null;
          const isFree = plan.monthly_price === 0;

          return (
            <article
              key={plan.id}
              className={`relative flex flex-col rounded-3xl border p-5 transition ${
                isActive
                  ? `${visual.activeBorder} ${visual.activeBg}`
                  : recommended
                    ? 'border-cyan/25 bg-gradient-to-b from-cyan/[0.07] to-transparent'
                    : `${visual.border} bg-black/20 hover:border-white/20 hover:bg-white/[0.04]`
              }`}
            >
              {/* Badges */}
              <div className="flex items-start justify-between gap-2">
                <span className={`text-[11px] font-bold uppercase tracking-[0.18em] ${visual.accent}`}>
                  {plan.name}
                </span>
                <div className="flex shrink-0 items-center gap-1.5">
                  {recommended && !isActive ? (
                    <span className="rounded-full border border-cyan/35 bg-cyan/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.15em] text-cyan">
                      Recomendado
                    </span>
                  ) : null}
                  {isActive ? (
                    <span className={`rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.15em] ${visual.badge} ${visual.badgeText}`}>
                      Plano ativo
                    </span>
                  ) : null}
                </div>
              </div>

              {/* Preço */}
              <div className="mt-4">
                {isFree ? (
                  <p className="font-display text-3xl text-white">Grátis</p>
                ) : (
                  <>
                    <p className="font-display text-3xl text-white">
                      R$ {price.toFixed(0)}
                      <span className="ml-1 text-sm font-normal text-slate-400">
                        /{billingCycle === 'yearly' ? 'ano' : 'mês'}
                      </span>
                    </p>
                    {savings ? (
                      <p className="mt-1 text-xs text-emerald-400">Você economiza {savings}% no plano anual</p>
                    ) : billingCycle === 'monthly' && plan.yearly_price ? (
                      <p className="mt-1 text-xs text-slate-500">
                        R$ {plan.yearly_price.toFixed(0)}/ano no plano anual
                      </p>
                    ) : null}
                  </>
                )}
              </div>

              {/* Features */}
              <ul className="mt-5 flex-1 space-y-2 text-sm text-slate-300">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-2">
                    <span className={`mt-0.5 shrink-0 text-base leading-none ${visual.accent}`}>✓</span>
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>

              {/* CTA */}
              <button
                type="button"
                disabled={isActive}
                onClick={() => onUpgrade(plan.id, billingCycle)}
                className={`mt-6 w-full rounded-2xl border px-4 py-3 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-50 ${
                  isActive
                    ? 'border-white/10 text-slate-500'
                    : recommended
                      ? 'border-transparent bg-cyan text-ink hover:bg-cyan/90'
                      : `border ${visual.ctaClass}`
                }`}
              >
                {planCTA(plan.id, isActive)}
              </button>
            </article>
            );
          })}
        </div>
      )}

      {/* Cancel warning */}
      {current?.cancel_at_period_end ? (
        <p className="mt-4 rounded-2xl border border-amber-400/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-300">
          Cancelamento agendado ao fim do período vigente. Reactive para continuar.
        </p>
      ) : null}
    </section>
  );
}

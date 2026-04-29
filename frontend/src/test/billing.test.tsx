import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';

import { PlanCard } from '../components/account/PlanCard';
import type { BillingPlan, CurrentSubscription } from '../types/billing';

const plans: BillingPlan[] = [
  {
    id: 'free',
    name: 'Free',
    monthly_price: 0,
    yearly_price: 0,
    features: ['A', 'B', 'C'],
    limits: [{ key: 'messages', value: 500 }],
    active: true,
  },
  {
    id: 'pro',
    name: 'Pro',
    monthly_price: 197,
    yearly_price: 1970,
    features: ['A', 'B', 'C'],
    limits: [{ key: 'messages', value: 5000 }],
    active: true,
  },
];

const current: CurrentSubscription = {
  plan_id: 'free',
  plan_name: 'Free',
  status: 'active',
  billing_cycle: 'monthly',
  monthly_price: 0,
  yearly_price: 0,
  auto_renew: true,
  cancel_at_period_end: false,
  started_at: new Date().toISOString(),
  next_renewal_at: null,
  provider: 'stripe',
  stripe_customer_id: 'cus_test',
};

describe('PlanCard billing real', () => {
  it('destaca plano atual e desabilita botão do plano ativo', () => {
    render(
      <PlanCard
        current={current}
        plans={plans}
        billingCycle="monthly"
        onBillingCycleChange={vi.fn()}
        onUpgrade={vi.fn()}
      />,
    );

    expect(screen.getAllByText(/Plano ativo/i).length).toBeGreaterThan(0);
    const activeButtons = screen.getAllByRole('button', { name: /Plano ativo/i });
    expect(activeButtons[activeButtons.length - 1]).toBeDisabled();
  });

  it('aciona checkout com plano e ciclo selecionado', async () => {
    const user = userEvent.setup();
    const onUpgrade = vi.fn();

    render(
      <PlanCard
        current={current}
        plans={plans}
        billingCycle="yearly"
        onBillingCycleChange={vi.fn()}
        onUpgrade={onUpgrade}
      />,
    );

    await user.click(screen.getByRole('button', { name: /Fazer upgrade/i }));
    expect(onUpgrade).toHaveBeenCalledWith('pro', 'yearly');
  });

  it('aciona abrir portal quando botão estiver disponível', async () => {
    const user = userEvent.setup();
    const onOpenPortal = vi.fn();
    const paidCurrent: CurrentSubscription = {
      ...current,
      plan_id: 'pro',
      plan_name: 'Pro',
      monthly_price: 197,
      yearly_price: 1970,
    };

    render(
      <PlanCard
        current={paidCurrent}
        plans={plans}
        billingCycle="monthly"
        onBillingCycleChange={vi.fn()}
        onUpgrade={vi.fn()}
        onOpenPortal={onOpenPortal}
      />,
    );

    await user.click(screen.getByRole('button', { name: /Gerenciar assinatura/i }));
    expect(onOpenPortal).toHaveBeenCalledTimes(1);
  });

  it('nao mostra portal Stripe para conta free sem assinatura ativa', () => {
    render(
      <PlanCard
        current={current}
        plans={plans}
        billingCycle="monthly"
        onBillingCycleChange={vi.fn()}
        onUpgrade={vi.fn()}
        onOpenPortal={vi.fn()}
      />,
    );

    expect(screen.queryByRole('button', { name: /Gerenciar assinatura/i })).not.toBeInTheDocument();
  });

  it('mostra erro quando a API nao retorna planos reais', () => {
    render(
      <PlanCard
        current={current}
        plans={[]}
        billingCycle="monthly"
        error="Falha ao carregar planos de billing"
        onBillingCycleChange={vi.fn()}
        onUpgrade={vi.fn()}
      />,
    );

    expect(screen.getByText(/Falha ao carregar planos de billing/i)).toBeInTheDocument();
  });
});

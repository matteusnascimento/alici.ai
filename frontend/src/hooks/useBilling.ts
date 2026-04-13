import { useEffect, useState } from 'react';

import {
  cancelSubscription,
  createCheckoutSession,
  createPortalSession,
  getBillingPlans,
  getBillingUsage,
  getCurrentSubscription,
  resumeSubscription,
  upgradeSubscription,
} from '../services/billing.service';
import type { BillingPlan, BillingUsage, CurrentSubscription } from '../types/billing';

export function useBilling() {
  const [plans, setPlans] = useState<BillingPlan[]>([]);
  const [current, setCurrent] = useState<CurrentSubscription | null>(null);
  const [usage, setUsage] = useState<BillingUsage | null>(null);
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadBilling() {
    setLoading(true);
    try {
      const [plansResult, currentResult, usageResult] = await Promise.all([
        getBillingPlans(),
        getCurrentSubscription(),
        getBillingUsage(),
      ]);
      setPlans(plansResult);
      setCurrent(currentResult);
      setUsage(usageResult);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao carregar billing');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadBilling();
  }, []);

  /** @deprecated Fluxo legado/admin. Use startCheckout() para fluxo Stripe real. */
  async function upgrade(planId: string, billingCycle: 'monthly' | 'yearly' = 'monthly') {
    setUpgrading(true);
    try {
      const response = await upgradeSubscription({ plan_id: planId, billing_cycle: billingCycle });
      setCurrent(response.subscription);
      setError(null);
      await loadBilling();
      return response.message;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Falha no upgrade';
      setError(message);
      throw err;
    } finally {
      setUpgrading(false);
    }
  }

  /** Inicia Stripe Checkout Session real. Redireciona o browser para o Stripe. */
  async function startCheckout(planId: string, billingCycle: 'monthly' | 'yearly' = 'monthly') {
    setUpgrading(true);
    try {
      const response = await createCheckoutSession({ plan_id: planId, billing_cycle: billingCycle });
      window.location.href = response.checkout_url;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao iniciar checkout';
      setError(message);
      throw err;
    } finally {
      setUpgrading(false);
    }
  }

  /** Abre o Stripe Billing Portal para gerenciar assinatura. */
  async function openPortal() {
    try {
      const response = await createPortalSession();
      window.location.href = response.portal_url;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao abrir portal';
      setError(message);
      throw err;
    }
  }

  async function cancel() {
    setUpgrading(true);
    try {
      const response = await cancelSubscription();
      setCurrent(response.subscription);
      setError(null);
      return response.message;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao cancelar';
      setError(message);
      throw err;
    } finally {
      setUpgrading(false);
    }
  }

  async function resume() {
    setUpgrading(true);
    try {
      const response = await resumeSubscription();
      setCurrent(response.subscription);
      setError(null);
      return response.message;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao reativar';
      setError(message);
      throw err;
    } finally {
      setUpgrading(false);
    }
  }

  return {
    plans,
    current,
    usage,
    loading,
    upgrading,
    error,
    upgrade,
    startCheckout,
    openPortal,
    cancel,
    resume,
    reload: loadBilling,
  };
}

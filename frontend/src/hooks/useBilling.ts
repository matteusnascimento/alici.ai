import { useEffect, useState } from 'react';

import {
  cancelSubscription,
  createCheckoutSession,
  createPortalSession,
  getBillingHistory,
  getBillingPlans,
  getBillingUsage,
  getCurrentSubscription,
  resumeSubscription,
  upgradeSubscription,
} from '../services/billing.service';
import type { BillingHistory, BillingPlan, BillingUsage, CurrentSubscription } from '../types/billing';

export function useBilling() {
  const [plans, setPlans] = useState<BillingPlan[]>([]);
  const [current, setCurrent] = useState<CurrentSubscription | null>(null);
  const [usage, setUsage] = useState<BillingUsage | null>(null);
  const [history, setHistory] = useState<BillingHistory | null>(null);
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadBilling() {
    setLoading(true);
    try {
      const [plansResult, currentResult, usageResult, historyResult] = await Promise.all([
        getBillingPlans(),
        getCurrentSubscription(),
        getBillingUsage(),
        getBillingHistory(),
      ]);
      setPlans(Array.isArray(plansResult) ? plansResult : []);
      setCurrent(currentResult ?? null);
      setUsage(
        usageResult
          ? { ...usageResult, items: Array.isArray(usageResult.items) ? usageResult.items : [] }
          : null,
      );
      setHistory(
        historyResult
          ? { ...historyResult, events: Array.isArray(historyResult.events) ? historyResult.events : [] }
          : null,
      );
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao carregar billing');
      setPlans([]);
      setCurrent(null);
      setUsage(null);
      setHistory(null);
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
    setError(null);
    try {
      if (planId === 'free') {
        throw new Error('O plano Free nao requer checkout. Escolha Pro ou Business para upgrade.');
      }
      const response = await createCheckoutSession({ plan_id: planId, billing_cycle: billingCycle });
      if (!response.checkout_url) {
        throw new Error('Checkout nao retornou URL de redirecionamento.');
      }
      window.location.assign(response.checkout_url);
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
    setError(null);
    try {
      const response = await createPortalSession();
      if (!response.portal_url) {
        throw new Error('Portal nao retornou URL de redirecionamento.');
      }
      window.location.assign(response.portal_url);
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
    history,
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

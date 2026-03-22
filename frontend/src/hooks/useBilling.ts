import { useEffect, useState } from 'react';

import { getBillingPlans, getBillingUsage, getCurrentSubscription, upgradeSubscription } from '../services/billing.service';
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

  return {
    plans,
    current,
    usage,
    loading,
    upgrading,
    error,
    upgrade,
    reload: loadBilling,
  };
}

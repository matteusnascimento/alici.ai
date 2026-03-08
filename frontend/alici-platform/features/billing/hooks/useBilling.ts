"use client";

import { useEffect } from "react";
import { cancelPlan, fetchBillingOverview, subscribePlan } from "../services/billingService";
import { useBillingStore } from "../store/billingStore";

export function useBilling() {
  const {
    loading,
    actionLoading,
    error,
    overview,
    setLoading,
    setActionLoading,
    setError,
    setOverview
  } = useBillingStore();

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchBillingOverview();
        setOverview(data);
      } catch {
        setError("Failed to load billing data");
        setLoading(false);
      }
    }

    void load();
  }, [setError, setLoading, setOverview]);

  async function upgrade(plan: "pro" | "enterprise" = "pro") {
    setActionLoading(true);
    setError(null);
    try {
      const result = await subscribePlan(plan);
      if (result.checkoutUrl) {
        window.location.href = result.checkoutUrl;
      }
      const data = await fetchBillingOverview();
      setOverview(data);
      return result;
    } catch {
      setError("Failed to start upgrade flow");
      throw new Error("upgrade_failed");
    } finally {
      setActionLoading(false);
    }
  }

  async function cancelSubscription() {
    setActionLoading(true);
    setError(null);
    try {
      const result = await cancelPlan();
      const data = await fetchBillingOverview();
      setOverview(data);
      return result;
    } catch {
      setError("Failed to cancel subscription");
      throw new Error("cancel_failed");
    } finally {
      setActionLoading(false);
    }
  }

  return { loading, actionLoading, error, overview, upgrade, cancelSubscription };
}

"use client";

import { useEffect } from "react";
import { fetchBillingOverview } from "../services/billingService";
import { useBillingStore } from "../store/billingStore";

export function useBilling() {
  const { loading, overview, setOverview } = useBillingStore();

  useEffect(() => {
    async function load() {
      const data = await fetchBillingOverview();
      setOverview(data);
    }

    void load();
  }, [setOverview]);

  return { loading, overview };
}

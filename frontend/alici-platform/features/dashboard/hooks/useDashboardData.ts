"use client";

import { useEffect } from "react";
import { useState } from "react";
import { fetchDashboard } from "@/features/dashboard/services/dashboardService";
import { useDashboardStore } from "@/features/dashboard/store/dashboardStore";

export function useDashboardData() {
  const { usage, costs, agents, activity, setDashboardData } = useDashboardStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchDashboard();
        if (active) setDashboardData(data);
      } catch {
        if (active) setError("Failed to load dashboard data");
      } finally {
        if (active) setLoading(false);
      }
    }

    void load();
    return () => {
      active = false;
    };
  }, [setDashboardData]);

  const data = { usage, costs, agents, activity };

  return {
    data,
    usage,
    costs,
    agents,
    activity,
    loading,
    error
  };
}

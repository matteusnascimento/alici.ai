"use client";

import { useEffect } from "react";
import { fetchDashboard } from "../services/dashboardService";
import { useDashboardStore } from "../store/dashboardStore";

export function useDashboardData() {
  const { usage, costs, agents, activity, loading, setDashboardData } = useDashboardStore();

  useEffect(() => {
    async function load() {
      const data = await fetchDashboard();
      setDashboardData(data);
    }

    void load();
  }, [setDashboardData]);

  return {
    usage,
    costs,
    agents,
    activity,
    loading
  };
}

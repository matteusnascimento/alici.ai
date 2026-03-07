"use client";

import { create } from "zustand";
import type { ActivityItem, AgentStatus, DashboardData, UsageMetric } from "@/types/dashboard";

interface DashboardState {
  usage: {
    tokens?: UsageMetric;
    requests?: UsageMetric;
    storage?: UsageMetric;
    bandwidth?: UsageMetric;
    tokensHistory: number[];
  };
  costs: number[];
  agents: AgentStatus[];
  activity: ActivityItem[];
  loading: boolean;
  setDashboardData: (data: DashboardData) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  usage: { tokensHistory: [] },
  costs: [],
  agents: [],
  activity: [],
  loading: true,
  setDashboardData: (data) =>
    set({
      usage: data.usage,
      costs: data.costs,
      agents: data.agents,
      activity: data.activity,
      loading: false
    })
}));

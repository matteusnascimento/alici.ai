import { api } from "@/services/api";
import type { DashboardData } from "@/types/dashboard";

const fallbackData: DashboardData = {
  usage: {
    tokens: { title: "Tokens", value: "1.2M", change: 11 },
    requests: { title: "Requests", value: "94.3K", change: 7 },
    storage: { title: "Storage", value: "82 GB", change: 4 },
    bandwidth: { title: "Bandwidth", value: "1.4 TB", change: 9 },
    tokensHistory: [12, 19, 17, 28, 30, 44, 48]
  },
  costs: [180, 220, 205, 260, 295, 330, 348],
  agents: [
    { id: "a1", name: "Sales Assistant", status: "online" },
    { id: "a2", name: "Support Triage", status: "degraded" },
    { id: "a3", name: "Ops Monitor", status: "online" }
  ],
  activity: [
    { id: "ev1", description: "Novo workflow publicado", timestamp: "2 min" },
    { id: "ev2", description: "Integracao Slack conectada", timestamp: "21 min" },
    { id: "ev3", description: "Billing cycle fechado", timestamp: "1 h" }
  ]
};

export async function fetchDashboard(): Promise<DashboardData> {
  try {
    const response = await api.get<DashboardData>("/dashboard");
    return response.data;
  } catch {
    return fallbackData;
  }
}

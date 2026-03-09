import { api } from "@/services/api";
import type { ApiEnvelope } from "@/types/api";
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
    const statsResponse = await api.get<ApiEnvelope<Record<string, unknown>>>("/platform/stats");
    const stats = statsResponse.data?.data ?? {};

    return {
      usage: {
        tokens: {
          title: "Tokens",
          value: String(stats?.tokens ?? 0),
          change: 0
        },
        requests: {
          title: "Requests",
          value: String(stats?.chats ?? 0),
          change: 0
        },
        storage: {
          title: "Storage",
          value: "n/a",
          change: 0
        },
        bandwidth: {
          title: "Bandwidth",
          value: "n/a",
          change: 0
        },
        tokensHistory: []
      },
      costs: [],
      agents: [
        {
          id: "active-agents",
          name: "Active agents",
          status: (Number(stats?.agents ?? 0)) > 0 ? "online" : "degraded"
        }
      ],
      activity: [
        {
          id: "stats-documents",
          description: `Documents indexed: ${String(stats?.documents ?? 0)}`,
          timestamp: "now"
        }
      ]
    };
  } catch {
    try {
      const response = await api.get<ApiEnvelope<Record<string, unknown>>>("/platform/overview");
      const payload = response.data?.data ?? {};
      const payloadStats = (payload?.stats ?? {}) as Record<string, unknown>;
      const payloadOrg = (payload?.organization ?? {}) as Record<string, unknown>;
      const recentActivity = Array.isArray(payload?.recent_activity) ? payload.recent_activity : [];

      return {
        usage: {
          tokens: {
            title: "Tokens",
            value: String(payloadStats?.current_month_tokens ?? 0),
            change: 0
          },
          requests: {
            title: "Requests",
            value: String(payloadOrg?.current_usage ?? 0),
            change: 0
          },
          storage: {
            title: "Storage",
            value: "n/a",
            change: 0
          },
          bandwidth: {
            title: "Bandwidth",
            value: "n/a",
            change: 0
          },
          tokensHistory: []
        },
        costs: recentActivity.map((item: { cost?: number }) => Number(item.cost || 0)),
        agents: [
          {
            id: "active-agents",
            name: "Active agents",
            status: Number(payloadStats?.total_agents ?? 0) > 0 ? "online" : "degraded"
          }
        ],
        activity: recentActivity.map((item: { id: string; endpoint?: string; created_at?: string }) => ({
          id: item.id,
          description: item.endpoint || "activity",
          timestamp: item.created_at || ""
        }))
      };
    } catch {
      return fallbackData;
    }
  }
}

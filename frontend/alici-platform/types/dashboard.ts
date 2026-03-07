export interface UsageMetric {
  title: string;
  value: string;
  change?: number;
}

export interface AgentStatus {
  id: string;
  name: string;
  status: "online" | "degraded" | "offline";
}

export interface ActivityItem {
  id: string;
  description: string;
  timestamp: string;
}

export interface DashboardData {
  usage: {
    tokens: UsageMetric;
    requests: UsageMetric;
    storage: UsageMetric;
    bandwidth: UsageMetric;
    tokensHistory: number[];
  };
  costs: number[];
  agents: AgentStatus[];
  activity: ActivityItem[];
}

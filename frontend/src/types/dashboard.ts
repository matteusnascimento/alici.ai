export interface UsageBar {
  label: string;
  value: number;
}

export interface DashboardStats {
  total_messages: number;
  total_agents: number;
  revenue: number;
  conversions: number;
  clicks: number;
  quotes: number;
  usage_bars: UsageBar[];
}

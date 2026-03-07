export interface AgentItem {
  id: string;
  name: string;
  model: string;
  status: "online" | "paused";
  requestsToday: number;
}

export interface AgentListResponse {
  agents: AgentItem[];
}

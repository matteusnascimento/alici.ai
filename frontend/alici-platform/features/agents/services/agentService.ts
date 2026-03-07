import { api } from "@/services/api";
import type { AgentListResponse } from "../types/agentTypes";

const fallback: AgentListResponse = {
  agents: [
    { id: "ag-01", name: "Support AI", model: "gpt-4.1", status: "online", requestsToday: 3210 },
    { id: "ag-02", name: "Sales Closer", model: "r2", status: "online", requestsToday: 1802 },
    { id: "ag-03", name: "Ops Watchdog", model: "gpt-4o-mini", status: "paused", requestsToday: 509 }
  ]
};

export async function fetchAgents(): Promise<AgentListResponse> {
  try {
    const response = await api.get<AgentListResponse>("/agents");
    return response.data;
  } catch {
    return fallback;
  }
}

import { api } from "@/services/api";
import type { ApiEnvelope } from "@/types/api";
import type {
  AgentCreatePayload,
  AgentCreateResponse,
  AgentListResponse
} from "../types/agentTypes";

const fallback: AgentListResponse = {
  agents: [
    { id: "ag-01", name: "Support AI", model: "gpt-4.1", status: "online", requestsToday: 3210 },
    { id: "ag-02", name: "Sales Closer", model: "r2", status: "online", requestsToday: 1802 },
    { id: "ag-03", name: "Ops Watchdog", model: "gpt-4o-mini", status: "paused", requestsToday: 509 }
  ]
};

export async function fetchAgents(): Promise<AgentListResponse> {
  /**
   * Function: fetchAgents
   * Description: Fetch the agents list and normalize the standard backend envelope.
   * Parameters:
   * Returns:
   *   AgentListResponse with an agents array.
   */
  try {
    const response = await api.get<ApiEnvelope<AgentListResponse>>("/agents");
    const envelopeData = response.data?.data ?? fallback;
    const agents = (envelopeData.agents || []).map((item) => ({
      id: item.id,
      name: item.name,
      model: item.model,
      status: item.status ?? (item.is_active ? "online" : "paused"),
      requestsToday: item.requestsToday ?? item.total_requests ?? 0,
      description: item.description,
      instructions: item.instructions,
      tools: item.tools,
      knowledge: item.knowledge,
      memory: item.memory,
    }));
    return { agents };
  } catch {
    return fallback;
  }
}

export async function createAgent(payload: AgentCreatePayload): Promise<AgentCreateResponse> {
  /**
   * Function: createAgent
   * Description: Create a new agent using the standardized backend envelope.
   * Parameters:
   *   payload: AgentCreatePayload data.
   * Returns:
   *   AgentCreateResponse summary.
   */
  const response = await api.post<ApiEnvelope<AgentCreateResponse>>("/agents", payload);
  return response.data.data;
}

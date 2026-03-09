export interface AgentItem {
  id: string;
  name: string;
  description?: string;
  instructions?: string;
  model: string;
  status: "online" | "paused";
  requestsToday: number;
  tools?: string[];
  knowledge?: Record<string, unknown>;
  memory?: Record<string, unknown>;
  total_requests?: number;
  is_active?: boolean;
}

export interface AgentListResponse {
  agents: AgentItem[];
}

export interface AgentCreatePayload {
  name: string;
  description?: string;
  system_prompt?: string;
  instructions?: string;
  model: string;
  tools?: string[];
  knowledge?: Record<string, unknown>;
  memory?: Record<string, unknown>;
  temperature: number;
  max_tokens: number;
  is_public: boolean;
}

export interface AgentCreateResponse {
  id: string;
  name: string;
  description?: string;
  instructions?: string;
  model: string;
  tools?: string[];
  knowledge?: Record<string, unknown>;
  memory?: Record<string, unknown>;
  created_at?: string;
}

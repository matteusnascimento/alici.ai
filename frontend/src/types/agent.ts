export interface Agent {
  id: number;
  user_id: number;
  nome: string;
  funcao: string;
  tipo: string;
  linguagem: string;
  prompt: string;
  whatsapp: string | null;
  instagram: string | null;
  api: string | null;
  outros: string | null;
  outros_nome: string | null;
  ativo: boolean;
  archived?: boolean;
  created_at: string;
  updated_at?: string;
}

export interface AgentInput {
  nome: string;
  funcao: string;
  tipo: string;
  linguagem: string;
  prompt: string;
  whatsapp?: string;
  instagram?: string;
  api?: string;
  outros?: string;
  outros_nome?: string;
  ativo?: boolean;
  archived?: boolean;
}

export interface AgentChannel {
  id: number;
  agent_id: number;
  channel_type: string;
  provider_name: string;
  external_account_id: string | null;
  channel_id: string;
  credential_ref: string | null;
  enabled: boolean;
  test_mode: boolean;
  config: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface AgentKnowledgeItem {
  id: number;
  agent_id: number;
  title: string;
  kind: string;
  content: string;
  tags: string | null;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface AgentAction {
  id: number;
  agent_id: number;
  name: string;
  action_type: string;
  trigger_keywords: string | null;
  config: Record<string, unknown>;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface AgentLog {
  id: number;
  agent_id: number;
  conversation_id: number | null;
  event_type: string;
  status: string;
  summary: string;
  input_text: string | null;
  output_text: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface AgentAnalytics {
  agent_id: number;
  total_inbound_messages: number;
  total_outbound_messages: number;
  total_conversations: number;
  active_conversations: number;
  human_handoffs: number;
  actions_executed: number;
  failed_responses: number;
  average_response_time_ms: number;
  channel_distribution: Record<string, number>;
  leads_captured: number;
}

export interface AgentTestResult {
  conversation_id: number;
  status: string;
  response: string;
  actions: Array<Record<string, unknown>>;
}

export interface AgentSummary {
  id: number;
  user_id: number;
  nome: string;
  funcao: string;
  linguagem: string;
  prompt: string;
  ativo: boolean;
  archived?: boolean;
  created_at: string;
  updated_at?: string;
}

export interface AgentOverview {
  agent: {
    id: number;
    nome: string;
    funcao: string;
    linguagem: string;
    status: string;
    created_at: string;
    updated_at: string;
  };
  kpis: {
    conversas_atendidas: number;
    leads_capturados: number;
    encaminhamentos_humano: number;
    tempo_medio_resposta_ms: number;
  };
  canais_ativos: Array<{ channel_type: string; status: string }>;
  historico_de_atividade: Array<{
    id: number;
    event_type: string;
    status: string;
    summary: string;
    created_at: string;
  }>;
  setup: AgentSetupStatus;
}

export interface AgentSetupChecklistItem {
  key: 'channels_connected' | 'knowledge_added' | 'actions_configured' | 'test_completed' | 'activation_ready' | string;
  label: string;
  completed: boolean;
  detail: string;
  route: string;
  helper_text?: string | null;
}

export interface AgentRecommendedNextStep {
  key: string;
  title: string;
  description: string;
  route: string;
  cta: string;
}

export interface AgentSetupStatus {
  progress_percent: number;
  completed_steps: number;
  total_steps: number;
  activation_ready: boolean;
  summary_message: string;
  recommended_next_step: AgentRecommendedNextStep;
  checklist: AgentSetupChecklistItem[];
}

export interface AgentReadinessStatus {
  activation_ready: boolean;
  status: string;
  progress_percent: number;
  validation_errors: string[];
}

export interface AgentCreateFlowResponse {
  agent: AgentSummary;
  setup: AgentSetupStatus;
}

export interface AgentChannel {
  id: number;
  agent_id: number;
  channel_type: string;
  channel_id?: string;
  status: string;
  is_enabled: boolean;
  enabled: boolean;
  provider_name: string;
  external_account_id: string | null;
  webhook_url: string | null;
  last_sync_at: string | null;
  last_error: string | null;
  conexao_do_agente?: string;
  created_at: string;
  updated_at: string;
}

export interface AgentConnectionActionResult {
  success: boolean;
  message: string;
  data: Record<string, unknown>;
  channel_type: string;
}

export type ChannelProviderStatus = 'connected' | 'pending_setup' | 'auth_required' | 'error' | 'disconnected' | 'coming_soon';

export interface ChannelProviderCatalogItem {
  provider: string;
  title: string;
  description: string;
  status: ChannelProviderStatus;
  helper_text: string;
  connected_accounts: number;
  active_bindings: number;
  supports_activation: boolean;
}

export interface AgentConnectedChannel {
  binding_id: number;
  agent_id: number;
  channel_endpoint_id: number;
  provider: string;
  status: ChannelProviderStatus;
  is_active: boolean;
  fallback_enabled: boolean;
  external_account_id: string | null;
  external_account_name: string | null;
  channel_name: string;
  external_channel_id: string | null;
  phone_number_or_handle: string | null;
  webhook_status: string;
  last_test_at: string | null;
  last_test_status: string | null;
  last_test_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface AgentChannelBindingActionResult {
  success: boolean;
  message: string;
  provider: string;
  channel_binding_id: number;
  data: Record<string, unknown>;
}

export interface AgentKnowledgeSource {
  id: number;
  agent_id?: number;
  title: string;
  kind: string;
  content: string;
  tags?: string | null;
  enabled?: boolean;
  status?: string;
  created_at?: string;
  updated_at?: string;
}

export interface AgentActionItem {
  id: number;
  name: string;
  action_type: string;
  enabled: boolean;
  trigger_keywords?: string | null;
}

export interface AgentTestResult {
  test_id: number;
  scenario: string;
  response: string;
  actions: Array<Record<string, unknown>>;
  source: string;
  confidence_note: string;
  status: string;
}

export interface AgentSettings {
  basic: {
    name: string;
    role: string;
    language: string;
    tone: string | null;
    working_hours: string | null;
    active: boolean;
    fallback_to_human: boolean;
  };
  advanced: {
    instrucoes_principais_do_agente?: string | null;
    modelo?: string | null;
    temperature?: string | null;
    opcoes_avancadas?: Record<string, unknown>;
  };
}

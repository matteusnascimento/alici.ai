// ---------------------------------------------------------------------------
// Core envelope types
// ---------------------------------------------------------------------------

export interface ApiErrorPayload {
  code: string;
  message: string;
}

export interface ApiEnvelope<T> {
  status: "success" | "error";
  data: T;
  error: ApiErrorPayload | string | null;
}

export function unwrapEnvelope<T>(payload: ApiEnvelope<T> | T): T {
  const maybeEnvelope = payload as ApiEnvelope<T>;
  if (maybeEnvelope && typeof maybeEnvelope === "object" && "status" in maybeEnvelope && "data" in maybeEnvelope) {
    return maybeEnvelope.data;
  }
  return payload as T;
}

// ---------------------------------------------------------------------------
// Agent types
// ---------------------------------------------------------------------------

export interface Agent {
  id: string;
  name: string;
  description?: string;
  instructions?: string;
  model: string;
  tools?: string[];
  knowledge?: Record<string, unknown>;
  memory?: Record<string, unknown>;
  temperature?: number;
  max_tokens?: number;
  is_active?: boolean;
  is_public?: boolean;
  total_requests?: number;
  created_at?: string;
  updated_at?: string;
}

export interface AgentListData {
  agents: Agent[];
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
  temperature?: number;
  max_tokens?: number;
  is_public?: boolean;
}

// ---------------------------------------------------------------------------
// Chat types
// ---------------------------------------------------------------------------

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  created_at?: string;
  tokens_used?: number;
}

export interface Conversation {
  id: string;
  title: string;
  agent_id?: string;
  last_message_at?: string;
  created_at?: string;
}

export interface ConversationListData {
  history: Conversation[];
}

export interface ConversationMessagesData {
  messages: ChatMessage[];
}

export interface SendMessageData {
  content?: string;
  message?: string;
  response?: string;
  conversation_id?: string;
}

export interface StreamChunk {
  chunk: string;
}

// ---------------------------------------------------------------------------
// Knowledge types
// ---------------------------------------------------------------------------

export interface KnowledgeDocument {
  id: string;
  title: string;
  filename: string;
  file_type: string;
  total_chunks: number;
  created_at?: string;
}

export interface KnowledgeDocumentListData {
  documents: KnowledgeDocument[];
}

export interface KnowledgeUploadData {
  document_id: string;
  filename: string;
  file_type: string;
  total_chunks: number;
}

export interface KnowledgeReference {
  document_id: string;
  chunk_index: number;
  excerpt: string;
}

export interface KnowledgeQueryData {
  query: string;
  answer: string;
  references: KnowledgeReference[];
}

// ---------------------------------------------------------------------------
// Integration types
// ---------------------------------------------------------------------------

export interface Integration {
  id: string;
  provider: string;
  status: "connected" | "disconnected";
  lastSync: string;
}

export interface IntegrationListData {
  integrations: Integration[];
}

// ---------------------------------------------------------------------------
// Platform / Dashboard types
// ---------------------------------------------------------------------------

export interface PlatformStats {
  chats: number;
  agents: number;
  documents: number;
  tokens: number;
}

export interface PlatformOverviewStats {
  total_agents: number;
  total_documents: number;
  total_conversations: number;
  current_month_tokens: number;
}

export interface PlatformOverview {
  organization: Record<string, unknown>;
  stats: PlatformOverviewStats;
  recent_activity: Array<{ id: string; endpoint?: string; cost?: number; created_at?: string }>;
}

// ---------------------------------------------------------------------------
// Workflow types
// ---------------------------------------------------------------------------

export interface Workflow {
  id: string;
  name: string;
  trigger: string;
  runsToday: number;
  successRate: number;
}

export interface WorkflowListData {
  workflows: Workflow[];
}

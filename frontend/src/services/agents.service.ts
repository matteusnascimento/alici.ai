import { apiFetch } from './api';
import type {
  Agent,
  AgentAction,
  AgentAnalytics,
  AgentChannel,
  AgentInput,
  AgentKnowledgeItem,
  AgentLog,
  AgentTestResult,
} from '../types/agent';

export function listAgents() {
  return apiFetch<Agent[]>('/agents');
}

export function createAgent(payload: AgentInput) {
  return apiFetch<Agent>('/agents', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function toggleAgent(agentId: number) {
  return apiFetch<{ id: number; ativo: boolean }>(`/agents/${agentId}/toggle`, {
    method: 'POST',
  });
}

export function listAgentChannels(agentId: number) {
  return apiFetch<AgentChannel[]>(`/agents/${agentId}/channels/registry`);
}

export function createAgentChannel(
  agentId: number,
  payload: {
    channel_type: string;
    provider_name: string;
    channel_id: string;
    external_account_id?: string;
    credential_ref?: string;
    enabled?: boolean;
    test_mode?: boolean;
    config?: Record<string, unknown>;
    api_key?: string;
  },
) {
  return apiFetch<AgentChannel>(`/agents/${agentId}/channels/registry`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function listAgentKnowledge(agentId: number) {
  return apiFetch<AgentKnowledgeItem[]>(`/agents/${agentId}/knowledge`);
}

export function createAgentKnowledge(
  agentId: number,
  payload: { title: string; kind?: string; content: string; tags?: string; enabled?: boolean },
) {
  return apiFetch<AgentKnowledgeItem>(`/agents/${agentId}/knowledge`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function listAgentActions(agentId: number) {
  return apiFetch<AgentAction[]>(`/agents/${agentId}/actions`);
}

export function createAgentAction(
  agentId: number,
  payload: {
    name: string;
    action_type: string;
    trigger_keywords?: string;
    config?: Record<string, unknown>;
    enabled?: boolean;
  },
) {
  return apiFetch<AgentAction>(`/agents/${agentId}/actions`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function testAgent(agentId: number, payload: { text: string; channel_type?: string }) {
  return apiFetch<AgentTestResult>(`/agents/${agentId}/test`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getAgentLogs(agentId: number) {
  return apiFetch<AgentLog[]>(`/agents/${agentId}/logs`);
}

export function getAgentAnalytics(agentId: number) {
  return apiFetch<AgentAnalytics>(`/agents/${agentId}/analytics`);
}

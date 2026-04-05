import { apiFetch } from './api';
import type {
  AgentActionItem,
  AgentChannel,
  AgentCreateFlowResponse,
  AgentKnowledgeSource,
  AgentOverview,
  AgentReadinessStatus,
  AgentSettings,
  AgentSetupStatus,
  AgentSummary,
  AgentTestResult,
} from '../types/agentsV2';

export function listAgentsV2() {
  return apiFetch<AgentSummary[]>('/agents');
}

export function createAgentV2(payload: Record<string, unknown>) {
  return apiFetch<AgentSummary>('/agents', {
    method: 'POST',
    body: JSON.stringify(payload),
  }).then(async (agent) => {
    const setup = await getAgentSetupStatusV2(agent.id);
    const response: AgentCreateFlowResponse = {
      agent,
      setup,
    };
    return response;
  });
}

export function duplicateAgentV2(agentId: number) {
  return apiFetch<AgentSummary>(`/agents/${agentId}/duplicate`, { method: 'POST' });
}

export function activateAgentV2(agentId: number) {
  return apiFetch<AgentSummary>(`/agents/${agentId}/activate`, { method: 'POST' });
}

export function pauseAgentV2(agentId: number) {
  return apiFetch<AgentSummary>(`/agents/${agentId}/pause`, { method: 'POST' });
}

export function getAgentOverviewV2(agentId: number) {
  return apiFetch<AgentOverview>(`/agents/${agentId}/overview`);
}

export function getAgentSetupStatusV2(agentId: number) {
  return apiFetch<AgentSetupStatus>(`/agents/${agentId}/setup-status`);
}

export function getAgentReadinessV2(agentId: number) {
  return apiFetch<AgentReadinessStatus>(`/agents/${agentId}/readiness`);
}

export function listAgentChannelsV2(agentId: number) {
  return apiFetch<AgentChannel[]>(`/agents/${agentId}/channels`);
}

export function connectAgentChannelV2(agentId: number, payload: Record<string, unknown>) {
  return apiFetch<AgentChannel>(`/agents/${agentId}/connect-channel`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function listAgentKnowledgeV2(agentId: number) {
  return apiFetch<AgentKnowledgeSource[]>(`/agents/${agentId}/knowledge`);
}

export function uploadAgentKnowledgeV2(agentId: number, payload: Record<string, unknown>) {
  return apiFetch<AgentKnowledgeSource>(`/agents/${agentId}/upload-knowledge`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function listAgentActionsV2(agentId: number) {
  return apiFetch<AgentActionItem[]>(`/agents/${agentId}/actions`);
}

export function saveAgentActionV2(agentId: number, payload: Record<string, unknown>) {
  return apiFetch<AgentActionItem>(`/agents/${agentId}/actions`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function runAgentTestV2(agentId: number, payload: Record<string, unknown>) {
  return apiFetch<AgentTestResult>(`/agents/${agentId}/run-test`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function listAgentLogsV2(agentId: number, filter?: string) {
  const query = filter ? `?kind=${encodeURIComponent(filter)}` : '';
  return apiFetch<Array<Record<string, unknown>>>(`/agents/${agentId}/logs${query}`);
}

export function getAgentAnalyticsV2(agentId: number) {
  return apiFetch<Record<string, unknown>>(`/agents/${agentId}/analytics`);
}

export function getAgentSettingsV2(agentId: number) {
  return apiFetch<AgentSettings>(`/agents/${agentId}/settings`);
}

export function updateAgentSettingsV2(agentId: number, payload: Record<string, unknown>) {
  return apiFetch<{ saved: boolean }>(`/agents/${agentId}/settings`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export function getAgentMetricsV2(agentId: number) {
  return apiFetch<{ metrics: Record<string, unknown> }>(`/agents/${agentId}/metrics`);
}

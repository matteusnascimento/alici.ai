import { apiFetch } from './api';
import type {
  AgentActionItem,
  AgentChannelBindingActionResult,
  AgentConnectedChannel,
  AgentCreateFlowResponse,
  ChannelIntegrationAccount,
  AgentKnowledgeSource,
  AgentOverview,
  AgentReadinessStatus,
  AgentSettings,
  AgentSetupStatus,
  AgentSummary,
  AgentTestResult,
  ChannelProviderCatalogItem,
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

export function archiveAgentV2(agentId: number) {
  return apiFetch<AgentSummary>(`/agents/${agentId}/archive`, { method: 'POST' });
}

export function deleteAgentV2(agentId: number) {
  return apiFetch<unknown>(`/agents/${agentId}`, { method: 'DELETE' });
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

export function listAgentKnowledgeV2(agentId: number) {
  return apiFetch<AgentKnowledgeSource[]>(`/agents/${agentId}/knowledge`);
}

export function uploadAgentKnowledgeV2(agentId: number, payload: Record<string, unknown>) {
  return apiFetch<AgentKnowledgeSource>(`/agents/${agentId}/upload-knowledge`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function uploadAgentKnowledgeFileV2(
  agentId: number,
  payload: { file: File; title?: string; tags?: string; enabled?: boolean },
) {
  const formData = new FormData();
  formData.append('file', payload.file);
  if (payload.title) formData.append('title', payload.title);
  if (payload.tags) formData.append('tags', payload.tags);
  if (payload.enabled !== undefined) formData.append('enabled', String(payload.enabled));

  return apiFetch<AgentKnowledgeSource>(`/agents/${agentId}/knowledge/upload-file`, {
    method: 'POST',
    body: formData,
  });
}

export function createAgentManualKnowledgeV2(
  agentId: number,
  payload: { title: string; content: string; tags?: string; enabled?: boolean },
) {
  return apiFetch<AgentKnowledgeSource>(`/agents/${agentId}/knowledge/manual`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function createAgentFaqKnowledgeV2(
  agentId: number,
  payload: { question: string; answer: string; tags?: string; enabled?: boolean },
) {
  return apiFetch<AgentKnowledgeSource>(`/agents/${agentId}/knowledge/faq`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function deleteAgentKnowledgeV2(agentId: number, sourceId: number) {
  return apiFetch<{ deleted: boolean }>(`/agents/${agentId}/knowledge/${sourceId}`, {
    method: 'DELETE',
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

export function listChannelProviderCatalog() {
  return apiFetch<ChannelProviderCatalogItem[]>('/integrations');
}

export function getChannelProviderStatus(provider: string) {
  return apiFetch<ChannelProviderCatalogItem>(`/integrations/${provider}/status`);
}

export function listChannelIntegrationAccounts() {
  return apiFetch<ChannelIntegrationAccount[]>('/integrations/accounts');
}

export function disconnectChannelProvider(provider: string) {
  return apiFetch<ChannelProviderCatalogItem>(`/integrations/${provider}/disconnect`, {
    method: 'POST',
  });
}

export function listAgentBoundChannels(agentId: number) {
  return apiFetch<AgentConnectedChannel[]>(`/agents/${agentId}/channels`);
}

export function connectAgentBoundChannel(
  agentId: number,
  payload: {
    provider: string;
    integration: Record<string, unknown>;
    endpoint: Record<string, unknown>;
    fallback_enabled?: boolean;
  },
) {
  return apiFetch<AgentConnectedChannel>(`/agents/${agentId}/channels/connect`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function disconnectAgentBoundChannel(agentId: number, bindingId: number) {
  return apiFetch<AgentConnectedChannel>(`/agents/${agentId}/channels/disconnect`, {
    method: 'POST',
    body: JSON.stringify({ binding_id: bindingId }),
  });
}

export function testAgentBoundChannel(agentId: number, bindingId: number, message?: string) {
  return apiFetch<AgentChannelBindingActionResult>(`/agents/${agentId}/channels/test`, {
    method: 'POST',
    body: JSON.stringify({ binding_id: bindingId, message }),
  });
}

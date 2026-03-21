import { apiFetch } from './api';
import type { Agent, AgentInput } from '../types/agent';

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

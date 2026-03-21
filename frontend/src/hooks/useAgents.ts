import { useEffect, useState } from 'react';

import { createAgent, listAgents, toggleAgent } from '../services/agents.service';
import type { Agent, AgentInput } from '../types/agent';

export function useAgents() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadAgents() {
    setLoading(true);
    try {
      const list = await listAgents();
      setAgents(list);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao carregar agentes');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadAgents();
  }, []);

  async function addAgent(payload: AgentInput) {
    setSaving(true);
    try {
      const created = await createAgent(payload);
      setAgents((current) => [created, ...current]);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao criar agente');
      throw err;
    } finally {
      setSaving(false);
    }
  }

  async function handleToggle(agentId: number) {
    try {
      const result = await toggleAgent(agentId);
      setAgents((current) => current.map((item) => (item.id === agentId ? { ...item, ativo: result.ativo } : item)));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao atualizar agente');
    }
  }

  return { agents, loading, saving, error, addAgent, handleToggle, reload: loadAgents };
}

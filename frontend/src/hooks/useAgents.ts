import { useEffect, useState } from 'react';

import {
  createAgent,
  createAgentAction,
  createAgentChannel,
  createAgentKnowledge,
  getAgentAnalytics,
  getAgentLogs,
  listAgentActions,
  listAgentChannels,
  listAgentKnowledge,
  listAgents,
  testAgent,
  toggleAgent,
} from '../services/agents.service';
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

export function useAgents() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedAgentId, setSelectedAgentId] = useState<number | null>(null);
  const [channels, setChannels] = useState<AgentChannel[]>([]);
  const [knowledge, setKnowledge] = useState<AgentKnowledgeItem[]>([]);
  const [actions, setActions] = useState<AgentAction[]>([]);
  const [logs, setLogs] = useState<AgentLog[]>([]);
  const [analytics, setAnalytics] = useState<AgentAnalytics | null>(null);
  const [lastTest, setLastTest] = useState<AgentTestResult | null>(null);

  async function loadAgents() {
    setLoading(true);
    try {
      const list = await listAgents();
      setAgents(list);
      if (list.length > 0 && !selectedAgentId) {
        setSelectedAgentId(list[0].id);
      }
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

  useEffect(() => {
    if (!selectedAgentId) {
      return;
    }
    void loadAgentOperations(selectedAgentId);
  }, [selectedAgentId]);

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

  async function loadAgentOperations(agentId: number) {
    setWorking(true);
    try {
      const [loadedChannels, loadedKnowledge, loadedActions, loadedLogs, loadedAnalytics] = await Promise.all([
        listAgentChannels(agentId),
        listAgentKnowledge(agentId),
        listAgentActions(agentId),
        getAgentLogs(agentId),
        getAgentAnalytics(agentId),
      ]);
      setChannels(loadedChannels);
      setKnowledge(loadedKnowledge);
      setActions(loadedActions);
      setLogs(loadedLogs);
      setAnalytics(loadedAnalytics);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao carregar operacoes do agente');
    } finally {
      setWorking(false);
    }
  }

  async function selectAgent(agentId: number) {
    setSelectedAgentId(agentId);
    await loadAgentOperations(agentId);
  }

  async function addChannel(payload: {
    channel_type: string;
    provider_name: string;
    channel_id: string;
    external_account_id?: string;
    credential_ref?: string;
    enabled?: boolean;
    test_mode?: boolean;
    config?: Record<string, unknown>;
    api_key?: string;
  }) {
    if (!selectedAgentId) return;
    setWorking(true);
    try {
      const created = await createAgentChannel(selectedAgentId, payload);
      setChannels((current) => [created, ...current]);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao criar canal');
      throw err;
    } finally {
      setWorking(false);
    }
  }

  async function addKnowledge(payload: { title: string; kind?: string; content: string; tags?: string; enabled?: boolean }) {
    if (!selectedAgentId) return;
    setWorking(true);
    try {
      const created = await createAgentKnowledge(selectedAgentId, payload);
      setKnowledge((current) => [created, ...current]);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao criar base de conhecimento');
      throw err;
    } finally {
      setWorking(false);
    }
  }

  async function addAction(payload: { name: string; action_type: string; trigger_keywords?: string; config?: Record<string, unknown>; enabled?: boolean }) {
    if (!selectedAgentId) return;
    setWorking(true);
    try {
      const created = await createAgentAction(selectedAgentId, payload);
      setActions((current) => [created, ...current]);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao criar acao');
      throw err;
    } finally {
      setWorking(false);
    }
  }

  async function runAgentTest(text: string, channel_type = 'api') {
    if (!selectedAgentId) return;
    setWorking(true);
    try {
      const result = await testAgent(selectedAgentId, { text, channel_type });
      setLastTest(result);
      await loadAgentOperations(selectedAgentId);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao testar agente');
      throw err;
    } finally {
      setWorking(false);
    }
  }

  return {
    agents,
    loading,
    saving,
    working,
    error,
    selectedAgentId,
    channels,
    knowledge,
    actions,
    logs,
    analytics,
    lastTest,
    addAgent,
    handleToggle,
    selectAgent,
    addChannel,
    addKnowledge,
    addAction,
    runAgentTest,
    reload: loadAgents,
  };
}

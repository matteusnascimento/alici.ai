import { useCallback, useEffect, useState } from 'react';

import {
  connectAgentProvider,
  disconnectAgentProvider,
  listAgentConnections,
  syncAgentProvider,
  testAgentProvider,
  updateAgentProviderConfig,
} from '../../services/agentsV2.service';
import type { AgentChannel, AgentConnectionActionResult } from '../../types/agentsV2';

export function useAgentChannels(agentId: number) {
  const [data, setData] = useState<AgentChannel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // Loading por provider para UX de botão individual
  const [actionLoading, setActionLoading] = useState<Record<string, boolean>>({});

  const setProviderLoading = (provider: string, value: boolean) =>
    setActionLoading((prev) => ({ ...prev, [provider]: value }));

  const reload = useCallback(async () => {
    if (!agentId) return;
    setLoading(true);
    try {
      const result = await listAgentConnections(agentId);
      setData(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao carregar conexões');
    } finally {
      setLoading(false);
    }
  }, [agentId]);

  useEffect(() => {
    void reload();
  }, [reload]);

  function updateLocalChannel(updated: AgentChannel) {
    setData((prev) =>
      prev.map((ch) => (ch.channel_type === updated.channel_type ? updated : ch)),
    );
  }

  async function connect(provider: string, config: Record<string, unknown> = {}) {
    setProviderLoading(provider, true);
    try {
      const updated = await connectAgentProvider(agentId, provider, config);
      updateLocalChannel(updated);
      return updated;
    } finally {
      setProviderLoading(provider, false);
    }
  }

  async function disconnect(provider: string) {
    setProviderLoading(provider, true);
    try {
      const updated = await disconnectAgentProvider(agentId, provider);
      updateLocalChannel(updated);
      return updated;
    } finally {
      setProviderLoading(provider, false);
    }
  }

  async function sync(provider: string) {
    setProviderLoading(provider, true);
    try {
      const updated = await syncAgentProvider(agentId, provider);
      updateLocalChannel(updated);
      return updated;
    } finally {
      setProviderLoading(provider, false);
    }
  }

  async function test(provider: string): Promise<AgentConnectionActionResult> {
    setProviderLoading(provider, true);
    try {
      return await testAgentProvider(agentId, provider);
    } finally {
      setProviderLoading(provider, false);
    }
  }

  async function updateConfig(provider: string, payload: Record<string, unknown>) {
    setProviderLoading(provider, true);
    try {
      const updated = await updateAgentProviderConfig(agentId, provider, payload);
      updateLocalChannel(updated);
      return updated;
    } finally {
      setProviderLoading(provider, false);
    }
  }

  return {
    data,
    loading,
    error,
    actionLoading,
    reload,
    connect,
    disconnect,
    sync,
    test,
    updateConfig,
  };
}

import { useCallback, useEffect, useState } from 'react';

import {
  connectAgentBoundChannel,
  disconnectAgentBoundChannel,
  listAgentBoundChannels,
  listChannelIntegrationAccounts,
  listChannelProviderCatalog,
  testAgentBoundChannel,
} from '../../services/agentsV2.service';
import type {
  AgentChannelBindingActionResult,
  AgentConnectedChannel,
  ChannelIntegrationAccount,
  ChannelProviderCatalogItem,
} from '../../types/agentsV2';

export function useAgentChannels(agentId: number) {
  const [providers, setProviders] = useState<ChannelProviderCatalogItem[]>([]);
  const [accounts, setAccounts] = useState<ChannelIntegrationAccount[]>([]);
  const [channels, setChannels] = useState<AgentConnectedChannel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<Record<string, boolean>>({});

  const setItemLoading = (key: string, value: boolean) =>
    setActionLoading((prev) => ({ ...prev, [key]: value }));

  const reload = useCallback(async () => {
    if (!agentId) return;
    setLoading(true);
    try {
      const [catalog, bindings, accountRows] = await Promise.all([
        listChannelProviderCatalog(),
        listAgentBoundChannels(agentId),
        listChannelIntegrationAccounts(),
      ]);
      setProviders(Array.isArray(catalog) ? catalog : []);
      setChannels(Array.isArray(bindings) ? bindings : []);
      setAccounts(Array.isArray(accountRows) ? accountRows : []);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao carregar conexões');
      setProviders([]);
      setChannels([]);
      setAccounts([]);
    } finally {
      setLoading(false);
    }
  }, [agentId]);

  useEffect(() => {
    void reload();
  }, [reload]);

  function upsertLocalChannel(updated: AgentConnectedChannel) {
    setChannels((prev) => {
      const exists = prev.some((item) => item.binding_id === updated.binding_id);
      if (!exists) {
        return [updated, ...prev];
      }
      return prev.map((item) => (item.binding_id === updated.binding_id ? updated : item));
    });
  }

  async function connect(payload: {
    provider: string;
    integration: Record<string, unknown>;
    endpoint: Record<string, unknown>;
    fallback_enabled?: boolean;
  }) {
    setItemLoading(`provider:${payload.provider}`, true);
    try {
      const updated = await connectAgentBoundChannel(agentId, payload);
      upsertLocalChannel(updated);
      const [catalog, accountRows] = await Promise.all([listChannelProviderCatalog(), listChannelIntegrationAccounts()]);
      setProviders(Array.isArray(catalog) ? catalog : []);
      setAccounts(Array.isArray(accountRows) ? accountRows : []);
      return updated;
    } finally {
      setItemLoading(`provider:${payload.provider}`, false);
    }
  }

  async function disconnect(bindingId: number, provider: string) {
    setItemLoading(`binding:${bindingId}`, true);
    try {
      const updated = await disconnectAgentBoundChannel(agentId, bindingId);
      upsertLocalChannel(updated);
      const [catalog, accountRows] = await Promise.all([listChannelProviderCatalog(), listChannelIntegrationAccounts()]);
      setProviders(Array.isArray(catalog) ? catalog : []);
      setAccounts(Array.isArray(accountRows) ? accountRows : []);
      return updated;
    } finally {
      setItemLoading(`binding:${bindingId}`, false);
    }
  }

  async function test(bindingId: number, provider: string, message?: string): Promise<AgentChannelBindingActionResult> {
    setItemLoading(`binding:${bindingId}`, true);
    try {
      const result = await testAgentBoundChannel(agentId, bindingId, message);
      const bindings = await listAgentBoundChannels(agentId);
      setChannels(Array.isArray(bindings) ? bindings : []);
      return result;
    } finally {
      setItemLoading(`binding:${bindingId}`, false);
    }
  }

  return {
    providers,
    accounts,
    channels,
    loading,
    error,
    actionLoading,
    reload,
    connect,
    disconnect,
    test,
  };
}

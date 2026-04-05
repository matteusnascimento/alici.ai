import { useEffect, useState } from 'react';

import { connectAgentChannelV2, listAgentChannelsV2 } from '../../services/agentsV2.service';
import type { AgentChannel } from '../../types/agentsV2';

export function useAgentChannels(agentId: number) {
  const [data, setData] = useState<AgentChannel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function reload() {
    setLoading(true);
    try {
      const result = await listAgentChannelsV2(agentId);
      setData(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao carregar canais');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!agentId) return;
    void reload();
  }, [agentId]);

  async function connect(payload: Record<string, unknown>) {
    const created = await connectAgentChannelV2(agentId, payload);
    setData((current) => [created, ...current.filter((item) => item.id !== created.id)]);
  }

  return { data, loading, error, reload, connect };
}

import { useEffect, useState } from 'react';

import { listAgentActionsV2, saveAgentActionV2 } from '../../services/agentsV2.service';
import type { AgentActionItem } from '../../types/agentsV2';

export function useAgentActions(agentId: number) {
  const [data, setData] = useState<AgentActionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function reload() {
    setLoading(true);
    try {
      const result = await listAgentActionsV2(agentId);
      setData(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao carregar acoes');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!agentId) return;
    void reload();
  }, [agentId]);

  async function save(payload: Record<string, unknown>) {
    const item = await saveAgentActionV2(agentId, payload);
    setData((current) => [item, ...current.filter((it) => it.id !== item.id)]);
  }

  return { data, loading, error, reload, save };
}

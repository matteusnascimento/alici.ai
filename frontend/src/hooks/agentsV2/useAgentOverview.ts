import { useEffect, useState } from 'react';

import { getAgentOverviewV2 } from '../../services/agentsV2.service';
import type { AgentOverview } from '../../types/agentsV2';

export function useAgentOverview(agentId: number) {
  const [data, setData] = useState<AgentOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function reload() {
    setLoading(true);
    try {
      const result = await getAgentOverviewV2(agentId);
      setData(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao carregar overview');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!agentId) return;
    void reload();
  }, [agentId]);

  return { data, loading, error, reload };
}

import { useEffect, useState } from 'react';

import { listAgentsV2 } from '../../services/agentsV2.service';
import type { AgentSummary } from '../../types/agentsV2';

export function useAgentsList() {
  const [data, setData] = useState<AgentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function reload() {
    setLoading(true);
    try {
      const result = await listAgentsV2();
      setData(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao carregar agentes');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void reload();
  }, []);

  return { data, loading, error, reload, setData };
}

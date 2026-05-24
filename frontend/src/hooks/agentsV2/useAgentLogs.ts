import { useEffect, useState } from 'react';

import { listAgentLogsV2 } from '../../services/agentsV2.service';

export function useAgentLogs(agentId: number, filter: string) {
  const [data, setData] = useState<Array<Record<string, unknown>>>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function reload() {
    setLoading(true);
    try {
      const result = await listAgentLogsV2(agentId, filter === 'all' ? undefined : filter);
      setData(Array.isArray(result) ? result : []);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao carregar logs');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!agentId) return;
    void reload();
  }, [agentId, filter]);

  return { data, loading, error, reload };
}

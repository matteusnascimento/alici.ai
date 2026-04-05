import { useEffect, useState } from 'react';

import { listAgentKnowledgeV2, uploadAgentKnowledgeV2 } from '../../services/agentsV2.service';
import type { AgentKnowledgeSource } from '../../types/agentsV2';

export function useAgentKnowledge(agentId: number) {
  const [data, setData] = useState<AgentKnowledgeSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function reload() {
    setLoading(true);
    try {
      const result = await listAgentKnowledgeV2(agentId);
      setData(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao carregar materiais');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!agentId) return;
    void reload();
  }, [agentId]);

  async function add(payload: Record<string, unknown>) {
    const item = await uploadAgentKnowledgeV2(agentId, payload);
    setData((current) => [item, ...current]);
  }

  return { data, loading, error, reload, add };
}

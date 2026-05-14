import { useState } from 'react';

import { runAgentTestV2 } from '../../services/agentsV2.service';
import type { AgentTestResult } from '../../types/agentsV2';

export function useRunAgentTest(agentId: number) {
  const [result, setResult] = useState<AgentTestResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run(payload: Record<string, unknown>) {
    setLoading(true);
    try {
      const response = await runAgentTestV2(agentId, payload);
      setResult(response);
      setError(null);
      return response;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao rodar teste');
      throw err;
    } finally {
      setLoading(false);
    }
  }

  return { result, loading, error, run };
}

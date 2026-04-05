import { useEffect, useState } from 'react';

import { getAgentSettingsV2, updateAgentSettingsV2 } from '../../services/agentsV2.service';
import type { AgentSettings } from '../../types/agentsV2';

export function useAgentSettings(agentId: number) {
  const [data, setData] = useState<AgentSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function reload() {
    setLoading(true);
    try {
      const result = await getAgentSettingsV2(agentId);
      setData(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao carregar configuracoes');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!agentId) return;
    void reload();
  }, [agentId]);

  async function save(next: AgentSettings) {
    setSaving(true);
    try {
      await updateAgentSettingsV2(agentId, next as unknown as Record<string, unknown>);
      setData(next);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao salvar configuracoes');
    } finally {
      setSaving(false);
    }
  }

  return { data, loading, saving, error, reload, save, setData };
}

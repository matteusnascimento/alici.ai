import { useParams } from 'react-router-dom';

import { useAgentSettings } from '../../../hooks/agentsV2/useAgentSettings';
import { AgentSettingsPanel } from './AgentSettingsPanel';

export function AgentSettingsPage() {
  const params = useParams();
  const agentId = Number(params.id || 0);
  const { data, loading, saving, error, save, setData } = useAgentSettings(agentId);

  if (loading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-40 animate-pulse rounded-3xl bg-white/5" />
        ))}
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-2xl border border-rose-400/25 bg-rose-500/10 p-5 text-sm text-rose-200">
        {error || 'Falha ao carregar configurações do agente.'}
      </div>
    );
  }

  return (
    <AgentSettingsPanel
      settings={data}
      onChange={setData}
      onSave={() => void save(data)}
      saving={saving}
    />
  );
}

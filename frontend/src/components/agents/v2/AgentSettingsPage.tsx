import { useParams } from 'react-router-dom';

import { useAgentSettings } from '../../../hooks/agentsV2/useAgentSettings';
import { AgentSettingsPanel } from './AgentSettingsPanel';

export function AgentSettingsPage() {
  const params = useParams();
  const agentId = Number(params.id || 0);
  const { data, loading, saving, error, save, setData } = useAgentSettings(agentId);

  if (loading) return <p className="text-slate-300">Carregando configuracoes...</p>;
  if (error || !data) return <p className="text-red-300">{error || 'Falha ao carregar configuracoes'}</p>;

  return (
    <div className="space-y-4">
      <header className="rounded-3xl border border-white/10 bg-white/5 p-4">
        <h1 className="font-display text-2xl text-white">Configuracoes do agente</h1>
      </header>
      <AgentSettingsPanel settings={data} onChange={setData} onSave={() => void save(data)} saving={saving} />
    </div>
  );
}

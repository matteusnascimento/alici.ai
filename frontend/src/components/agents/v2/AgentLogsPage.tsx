import { useState } from 'react';
import { useParams } from 'react-router-dom';

import { useAgentLogs } from '../../../hooks/agentsV2/useAgentLogs';
import { AgentLogList } from './AgentLogList';

const filters = [
  { key: 'all', label: 'Todos' },
  { key: 'conversations', label: 'Conversas' },
  { key: 'actions', label: 'Acoes' },
  { key: 'errors', label: 'Erros' },
  { key: 'escalations', label: 'Escalonamentos' },
];

export function AgentLogsPage() {
  const params = useParams();
  const agentId = Number(params.id || 0);
  const [filter, setFilter] = useState('all');
  const { data, loading, error } = useAgentLogs(agentId, filter);

  return (
    <div className="space-y-4">
      <header className="rounded-3xl border border-white/10 bg-white/5 p-4">
        <h1 className="font-display text-2xl text-white">Historico de atividade</h1>
      </header>
      <div className="flex flex-wrap gap-2">
        {filters.map((item) => (
          <button key={item.key} type="button" onClick={() => setFilter(item.key)} className={`rounded-xl border px-3 py-2 text-xs ${filter === item.key ? 'border-cyan-300/40 bg-cyan-500/15 text-cyan-100' : 'border-white/20 text-slate-100'}`}>
            {item.label}
          </button>
        ))}
      </div>
      {loading ? <p className="text-slate-300">Carregando logs...</p> : null}
      {error ? <p className="text-red-300">{error}</p> : null}
      <AgentLogList items={data} />
    </div>
  );
}

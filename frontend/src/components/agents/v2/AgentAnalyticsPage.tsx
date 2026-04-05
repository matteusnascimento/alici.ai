import { useParams } from 'react-router-dom';

import { useAgentAnalytics } from '../../../hooks/agentsV2/useAgentAnalytics';
import { AgentAnalyticsCards } from './AgentAnalyticsCards';
import { AgentAnalyticsCharts } from './AgentAnalyticsCharts';

export function AgentAnalyticsPage() {
  const params = useParams();
  const agentId = Number(params.id || 0);
  const { data, loading, error } = useAgentAnalytics(agentId);

  if (loading) return <p className="text-slate-300">Carregando analytics...</p>;
  if (error || !data) return <p className="text-red-300">{error || 'Falha ao carregar analytics'}</p>;

  return (
    <div className="space-y-4">
      <header className="rounded-3xl border border-white/10 bg-white/5 p-4">
        <h1 className="font-display text-2xl text-white">Resultados</h1>
      </header>
      <AgentAnalyticsCards data={data} />
      <AgentAnalyticsCharts data={data} />
    </div>
  );
}

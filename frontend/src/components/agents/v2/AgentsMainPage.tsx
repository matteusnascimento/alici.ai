import { useEffect, useState } from 'react';

import type { AgentSummary } from '../../../types/agentsV2';
import { activateAgentV2, duplicateAgentV2, listAgentsV2, pauseAgentV2 } from '../../../services/agentsV2.service';
import { AgentCard } from './AgentCard';
import { AgentEmptyState } from './AgentEmptyState';
import { AgentsHeader } from './AgentsHeader';
import { AgentsFiltersBar } from './AgentsFiltersBar';

export function AgentsMainPage() {
  const [agents, setAgents] = useState<AgentSummary[]>([]);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const data = await listAgentsV2();
      setAgents(data);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function handleToggle(agent: AgentSummary) {
    const next = agent.ativo ? await pauseAgentV2(agent.id) : await activateAgentV2(agent.id);
    setAgents((current) => current.map((item) => (item.id === agent.id ? next : item)));
  }

  async function handleDuplicate(agent: AgentSummary) {
    const copy = await duplicateAgentV2(agent.id);
    setAgents((current) => [copy, ...current]);
  }

  async function handleDuplicateTop() {
    if (!agents[0]) return;
    await handleDuplicate(agents[0]);
  }

  return (
    <div className="space-y-4">
      <AgentsHeader onDuplicateTop={handleDuplicateTop} />
      <AgentsFiltersBar search={search} status={statusFilter} onSearch={setSearch} onStatus={setStatusFilter} />
      {loading ? <p className="text-slate-300">Carregando agentes...</p> : null}
      {!loading && agents.length === 0 ? <AgentEmptyState /> : null}
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {agents
          .filter((agent) => {
            const byStatus = statusFilter === 'all' || (statusFilter === 'active' ? agent.ativo : !agent.ativo);
            const bySearch = search.trim().length === 0 || `${agent.nome} ${agent.funcao}`.toLowerCase().includes(search.toLowerCase());
            return byStatus && bySearch;
          })
          .map((agent) => (
          <AgentCard key={agent.id} agent={agent} onToggle={handleToggle} onDuplicate={handleDuplicate} />
          ))}
      </section>
    </div>
  );
}

import { useEffect, useState } from 'react';

import type { AgentSummary } from '../../../types/agentsV2';
import {
  activateAgentV2,
  archiveAgentV2,
  deleteAgentV2,
  duplicateAgentV2,
  listAgentsV2,
  pauseAgentV2,
} from '../../../services/agentsV2.service';
import { ApiError } from '../../../services/api';
import { AgentCard } from './AgentCard';
import { AgentDeleteModal } from './AgentDeleteModal';
import { AgentEmptyState } from './AgentEmptyState';
import { AgentsHeader } from './AgentsHeader';
import { AgentsFiltersBar } from './AgentsFiltersBar';

export function AgentsMainPage() {
  const [agents, setAgents] = useState<AgentSummary[]>([]);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<AgentSummary | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState('');
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    try {
      const data = await listAgentsV2();
      setAgents(Array.isArray(data) ? data : []);
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
    setFeedback(`Agente ${agent.nome} duplicado com sucesso.`);
  }

  async function handleArchive(agent: AgentSummary) {
    const updated = await archiveAgentV2(agent.id);
    setAgents((current) => current.filter((item) => item.id !== updated.id));
    setFeedback(`Agente ${agent.nome} arquivado.`);
  }

  function openDelete(agent: AgentSummary) {
    setDeleteTarget(agent);
    setDeleteConfirm('');
    setDeleteError(null);
  }

  function closeDelete() {
    if (deleteLoading) return;
    setDeleteTarget(null);
    setDeleteConfirm('');
    setDeleteError(null);
  }

  async function handleDeleteConfirm() {
    if (!deleteTarget) return;
    if (deleteConfirm.trim() !== deleteTarget.nome.trim()) {
      setDeleteError('Digite o nome do agente exatamente como exibido para confirmar a exclusao.');
      return;
    }

    setDeleteLoading(true);
    setDeleteError(null);
    try {
      await deleteAgentV2(deleteTarget.id);
      setAgents((current) => current.filter((item) => item.id !== deleteTarget.id));
      setFeedback(`Agente ${deleteTarget.nome} excluido com sucesso.`);
      closeDelete();
    } catch (err) {
      setDeleteError(err instanceof ApiError ? err.message : 'Nao foi possivel excluir o agente.');
    } finally {
      setDeleteLoading(false);
    }
  }

  async function handleDuplicateTop() {
    if (!agents[0]) return;
    await handleDuplicate(agents[0]);
  }

  return (
    <div className="space-y-4">
      <AgentsHeader onDuplicateTop={handleDuplicateTop} />
      <AgentsFiltersBar search={search} status={statusFilter} onSearch={setSearch} onStatus={setStatusFilter} />
      {feedback ? <p className="rounded-xl border border-cyan-300/30 bg-cyan-500/10 px-3 py-2 text-sm text-cyan-100">{feedback}</p> : null}
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
          <AgentCard
            key={agent.id}
            agent={agent}
            onToggle={handleToggle}
            onDuplicate={handleDuplicate}
            onArchive={handleArchive}
            onDelete={openDelete}
          />
          ))}
      </section>
      <AgentDeleteModal
        open={Boolean(deleteTarget)}
        agentName={deleteTarget?.nome ?? ''}
        confirmText={deleteConfirm}
        deleting={deleteLoading}
        error={deleteError}
        onConfirmTextChange={setDeleteConfirm}
        onClose={closeDelete}
        onConfirm={() => void handleDeleteConfirm()}
      />
    </div>
  );
}

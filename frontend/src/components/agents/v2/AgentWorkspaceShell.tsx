import { useEffect, useState } from 'react';
import { Link, NavLink, Outlet, useNavigate, useParams } from 'react-router-dom';

import { ApiError } from '../../../services/api';
import { archiveAgentV2, deleteAgentV2, duplicateAgentV2, getAgentOverviewV2 } from '../../../services/agentsV2.service';
import { AgentDeleteModal } from './AgentDeleteModal';

const tabs = [
  { key: 'overview', label: 'Visão geral' },
  { key: 'knowledge', label: 'Conhecimento' },
  { key: 'channels', label: 'Canais' },
  { key: 'test', label: 'Testes' },
  { key: 'analytics', label: 'Resultados' },
  { key: 'settings', label: 'Configurações' },
];

export function AgentWorkspaceShell() {
  const navigate = useNavigate();
  const params = useParams();
  const id = params.id;
  const [agentName, setAgentName] = useState<string>('');
  const [menuOpen, setMenuOpen] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState('');
  const [deleteLoading, setDeleteLoading] = useState(false);
  const numericId = Number(id || 0);

  useEffect(() => {
    if (!id) {
      return;
    }
    let mounted = true;
    async function loadAgentName() {
      try {
        const data = await getAgentOverviewV2(Number(id));
        if (mounted) {
          setAgentName(data.agent?.nome?.trim() || 'Agente sem nome');
        }
      } catch {
        if (mounted) {
          setAgentName(`Agente ${id}`);
        }
      }
    }
    void loadAgentName();
    return () => {
      mounted = false;
    };
  }, [id]);

  async function handleDuplicate() {
    if (!numericId) return;
    setError(null);
    try {
      const copy = await duplicateAgentV2(numericId);
      setFeedback('Agente duplicado com sucesso.');
      setMenuOpen(false);
      navigate(`/app/agents/${copy.id}/overview`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Nao foi possivel duplicar o agente.');
    }
  }

  async function handleArchive() {
    if (!numericId) return;
    setError(null);
    try {
      await archiveAgentV2(numericId);
      setMenuOpen(false);
      navigate('/app/agents');
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Nao foi possivel arquivar o agente.');
    }
  }

  async function handleDelete() {
    if (!numericId) return;
    if (deleteConfirm.trim() !== agentName.trim()) {
      setError('Digite o nome do agente exatamente como exibido para confirmar a exclusao.');
      return;
    }

    setDeleteLoading(true);
    setError(null);
    try {
      await deleteAgentV2(numericId);
      setDeleteOpen(false);
      navigate('/app/agents');
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Nao foi possivel excluir o agente.');
    } finally {
      setDeleteLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <header className="rounded-3xl border border-white/10 bg-gradient-to-r from-white/[0.08] to-white/[0.03] px-5 pt-5 pb-0">
        <div className="flex flex-wrap items-start justify-between gap-3 pb-4">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.25em] text-cyan-400/80">Workspace do agente</p>
            <h1 className="mt-1 font-display text-2xl font-bold text-white">{agentName || `Agente ${id}`}</h1>
          </div>
          <div className="flex items-center gap-2">
            <div className="relative">
              <button
                type="button"
                onClick={() => setMenuOpen((value) => !value)}
                className="rounded-xl border border-white/15 bg-white/[0.04] px-3 py-2 text-sm text-slate-300 transition hover:border-white/30 hover:text-white"
              >
                Ações
              </button>
              {menuOpen ? (
                <div className="absolute right-0 top-11 z-20 w-48 rounded-2xl border border-white/15 bg-[#0b1328] p-1.5 shadow-2xl">
                  <Link
                    to={`/app/agents/${id}/settings`}
                    className="flex items-center gap-2 rounded-xl px-3 py-2 text-sm text-slate-200 hover:bg-white/8 hover:text-white"
                    onClick={() => setMenuOpen(false)}
                  >
                    Editar configurações
                  </Link>
                  <button
                    type="button"
                    className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-sm text-slate-200 hover:bg-white/8 hover:text-white"
                    onClick={() => void handleDuplicate()}
                  >
                    Duplicar agente
                  </button>
                  <button
                    type="button"
                    className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-sm text-slate-200 hover:bg-white/8 hover:text-white"
                    onClick={() => void handleArchive()}
                  >
                    Arquivar
                  </button>
                  <div className="my-1 border-t border-white/8" />
                  <button
                    type="button"
                    className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-sm text-rose-300 hover:bg-rose-500/12"
                    onClick={() => {
                      setMenuOpen(false);
                      setDeleteOpen(true);
                      setDeleteConfirm('');
                    }}
                  >
                    Excluir agente
                  </button>
                </div>
              ) : null}
            </div>
            <Link to="/app/agents" className="rounded-xl border border-white/15 bg-white/[0.04] px-3 py-2 text-sm text-slate-300 transition hover:border-white/30 hover:text-white">← Agentes</Link>
          </div>
        </div>
        {feedback ? <div className="mx-0 mb-3 rounded-2xl border border-emerald-400/25 bg-emerald-500/10 px-4 py-2.5 text-sm text-emerald-200">{feedback}</div> : null}
        {error ? <div className="mx-0 mb-3 rounded-2xl border border-rose-400/25 bg-rose-500/10 px-4 py-2.5 text-sm text-rose-200">{error}</div> : null}
        <nav className="-mx-0.5 mt-1 flex flex-wrap gap-1 border-t border-white/8 pt-1">
          {tabs.map((tab) => (
            <NavLink
              key={tab.key}
              to={`/app/agents/${id}/${tab.key}`}
              className={({ isActive }) =>
                `rounded-none border-b-2 px-4 py-2.5 text-sm font-medium transition ${
                  isActive
                    ? 'border-cyan text-white'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`
              }
            >
              {tab.label}
            </NavLink>
          ))}
        </nav>
      </header>
      <Outlet />
      <AgentDeleteModal
        open={deleteOpen}
        agentName={agentName || `Agente ${id}`}
        confirmText={deleteConfirm}
        deleting={deleteLoading}
        error={error}
        onConfirmTextChange={setDeleteConfirm}
        onClose={() => {
          if (deleteLoading) return;
          setDeleteOpen(false);
        }}
        onConfirm={() => void handleDelete()}
      />
    </div>
  );
}

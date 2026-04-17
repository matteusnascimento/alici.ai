import { useEffect, useState } from 'react';
import { Link, NavLink, Outlet, useNavigate, useParams } from 'react-router-dom';

import { ApiError } from '../../../services/api';
import { archiveAgentV2, deleteAgentV2, duplicateAgentV2, getAgentOverviewV2 } from '../../../services/agentsV2.service';
import { AgentDeleteModal } from './AgentDeleteModal';

const tabs = [
  { key: 'overview', label: 'Overview' },
  { key: 'channels', label: 'Canais' },
  { key: 'knowledge', label: 'Materiais e informacoes' },
  { key: 'actions', label: 'Acoes permitidas' },
  { key: 'test', label: 'Sandbox' },
  { key: 'logs', label: 'Historico de atividade' },
  { key: 'analytics', label: 'Metricas' },
  { key: 'settings', label: 'Configuracoes' },
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
      <header className="rounded-3xl border border-white/10 bg-gradient-to-r from-white/[0.08] to-white/[0.03] p-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-cyan-300">Workspace do agente</p>
            <h1 className="font-display text-2xl text-white">{agentName || `Agente ${id}`}</h1>
          </div>
          <div className="flex items-center gap-2">
            <div className="relative">
              <button
                type="button"
                onClick={() => setMenuOpen((value) => !value)}
                className="rounded-xl border border-white/20 bg-white/[0.04] px-3 py-2 text-sm text-slate-100"
              >
                Acoes
              </button>
              {menuOpen ? (
                <div className="absolute right-0 top-11 z-20 w-48 rounded-xl border border-white/15 bg-[#0b1328] p-2 shadow-xl">
                  <Link
                    to={`/app/agents/${id}/settings`}
                    className="block rounded-lg px-2 py-2 text-xs text-slate-100 hover:bg-white/10"
                    onClick={() => setMenuOpen(false)}
                  >
                    Editar
                  </Link>
                  <button
                    type="button"
                    className="block w-full rounded-lg px-2 py-2 text-left text-xs text-slate-100 hover:bg-white/10"
                    onClick={() => void handleDuplicate()}
                  >
                    Duplicar
                  </button>
                  <button
                    type="button"
                    className="block w-full rounded-lg px-2 py-2 text-left text-xs text-slate-100 hover:bg-white/10"
                    onClick={() => void handleArchive()}
                  >
                    Arquivar
                  </button>
                  <button
                    type="button"
                    className="block w-full rounded-lg px-2 py-2 text-left text-xs text-rose-200 hover:bg-rose-500/15"
                    onClick={() => {
                      setMenuOpen(false);
                      setDeleteOpen(true);
                      setDeleteConfirm('');
                    }}
                  >
                    Excluir
                  </button>
                </div>
              ) : null}
            </div>
            <Link to="/app/agents" className="rounded-xl border border-white/20 bg-white/[0.04] px-3 py-2 text-sm text-slate-100 transition hover:border-cyan/50 hover:text-white">Voltar para agentes</Link>
          </div>
        </div>
        {feedback ? <p className="mt-3 rounded-xl border border-cyan-300/30 bg-cyan-500/10 px-3 py-2 text-sm text-cyan-100">{feedback}</p> : null}
        {error ? <p className="mt-3 rounded-xl border border-rose-300/40 bg-rose-500/10 px-3 py-2 text-sm text-rose-100">{error}</p> : null}
        <nav className="mt-4 flex flex-wrap gap-2">
          {tabs.map((tab) => (
            <NavLink
              key={tab.key}
              to={`/app/agents/${id}/${tab.key}`}
              className={({ isActive }) => `rounded-xl px-3 py-2 text-xs transition ${isActive ? 'bg-cyan text-ink font-semibold' : 'border border-white/20 bg-white/[0.03] text-slate-200 hover:border-cyan/40 hover:text-white'}`}
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

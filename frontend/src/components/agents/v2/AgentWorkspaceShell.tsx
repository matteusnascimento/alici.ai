import { useEffect, useState } from 'react';
import { Link, NavLink, Outlet, useParams } from 'react-router-dom';

import { getAgentOverviewV2 } from '../../../services/agentsV2.service';

const tabs = [
  { key: 'overview', label: 'Overview' },
  { key: 'knowledge', label: 'Materiais e informacoes' },
  { key: 'actions', label: 'Acoes permitidas' },
  { key: 'test', label: 'Teste sandbox' },
  { key: 'logs', label: 'Historico de atividade' },
  { key: 'analytics', label: 'Resultados' },
  { key: 'settings', label: 'Configuracoes' },
];

export function AgentWorkspaceShell() {
  const params = useParams();
  const id = params.id;
  const [agentName, setAgentName] = useState<string>('');

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

  return (
    <div className="space-y-4">
      <header className="rounded-3xl border border-white/10 bg-gradient-to-r from-white/[0.08] to-white/[0.03] p-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-cyan-300">Workspace do agente</p>
            <h1 className="font-display text-2xl text-white">{agentName || `Agente ${id}`}</h1>
          </div>
          <Link to="/app/agents" className="rounded-xl border border-white/20 bg-white/[0.04] px-3 py-2 text-sm text-slate-100 transition hover:border-cyan/50 hover:text-white">Voltar para agentes</Link>
        </div>
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
    </div>
  );
}

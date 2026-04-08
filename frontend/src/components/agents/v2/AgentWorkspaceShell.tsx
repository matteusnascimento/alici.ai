import { Link, NavLink, Outlet, useParams } from 'react-router-dom';

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

  return (
    <div className="space-y-4">
      <header className="rounded-3xl border border-white/10 bg-white/5 p-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-cyan-300">Workspace do agente</p>
            <h1 className="font-display text-2xl text-white">Agente #{id}</h1>
          </div>
          <Link to="/app/agents" className="rounded-xl border border-white/20 px-3 py-2 text-sm text-slate-100">Voltar para agentes</Link>
        </div>
        <nav className="mt-4 flex flex-wrap gap-2">
          {tabs.map((tab) => (
            <NavLink
              key={tab.key}
              to={`/app/agents/${id}/${tab.key}`}
              className={({ isActive }) => `rounded-xl px-3 py-2 text-xs ${isActive ? 'bg-cyan text-ink font-semibold' : 'border border-white/20 text-slate-200'}`}
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

import { LogOut } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';

import { useAuth } from '../../hooks/useAuth';

const titleMap: Record<string, string> = {
  '/app/dashboard': 'Dashboard',
  '/app/chat': 'Alici Chat',
  '/app/agents': 'Agents',
  '/app/studio': 'AXI Studio',
  '/app/account': 'Conta AXI',
};

export function Topbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const title = location.pathname.startsWith('/app/studio') || location.pathname.startsWith('/app/marketing')
    ? 'AXI Studio'
    : location.pathname.startsWith('/app/account')
      ? 'Conta AXI'
      : titleMap[location.pathname] || 'AXI';

  function handleLogout() {
    logout();
    navigate('/login');
  }

  return (
    <div className="flex flex-col gap-4 rounded-[2rem] border border-white/10 bg-white/5 p-6 backdrop-blur lg:flex-row lg:items-center lg:justify-between">
      <div>
        <p className="text-sm uppercase tracking-[0.3em] text-cyan">Plataforma AXI</p>
        <h2 className="mt-2 font-display text-3xl text-white">{title}</h2>
      </div>
      <div className="flex items-center gap-4 rounded-2xl border border-white/10 bg-ink/40 px-4 py-3 text-white">
        <div>
          <p className="font-semibold">{user?.name}</p>
          <p className="text-sm text-slate-300">Plano {user?.plan}</p>
        </div>
        <button className="inline-flex items-center gap-2 rounded-full border border-white/10 px-4 py-2 text-sm transition hover:border-cyan hover:text-cyan" onClick={handleLogout} type="button">
          <LogOut size={16} /> Sair
        </button>
      </div>
    </div>
  );
}

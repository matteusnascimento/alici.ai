import { Bell, CircleHelp, Search, Settings } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

import { useAuth } from '../../hooks/useAuth';

const titleRules: Array<[string, string, string]> = [
  ['/app/revenue', 'Revenue', 'Visao geral do seu negocio'],
  ['/app/chats', 'Chats', 'Central de atendimento omnichannel'],
  ['/app/assistant', 'AXI Assistant', 'Assistente interno para analise e planejamento'],
  ['/app/marketing', 'Marketing', 'Planejamento, campanhas e crescimento'],
  ['/app/studio', 'Studio', 'Criacao visual, templates e editor'],
  ['/app/integrations', 'Integrations', 'Canais, dados e conectores'],
  ['/app/account', 'Minha conta', 'Perfil, seguranca e preferencias'],
  ['/app/admin', 'Administracao', 'Usuarios, permissoes, billing e auditoria'],
];

function resolveTitle(pathname: string) {
  return titleRules.find(([prefix]) => pathname.startsWith(prefix)) ?? ['/', 'AXI', 'Business Pulse'];
}

export function Topbar() {
  const location = useLocation();
  const { user } = useAuth();
  const [, title, subtitle] = resolveTitle(location.pathname);
  const initials = (user?.name || 'AXI')
    .split(' ')
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

  return (
    <header className="flex flex-col gap-4 rounded-[1.5rem] border border-white/10 bg-[linear-gradient(145deg,rgba(15,23,42,0.88),rgba(2,6,23,0.72))] px-5 py-4 shadow-[0_18px_60px_rgba(0,0,0,0.26)] backdrop-blur-xl xl:flex-row xl:items-center xl:justify-between">
      <div className="min-w-0">
        <h1 className="font-display text-3xl text-white">{title}</h1>
        <p className="mt-1 text-sm text-slate-400">{subtitle}</p>
      </div>
      <div className="flex flex-wrap items-center gap-3">
        <label className="flex h-11 min-w-[280px] items-center gap-3 rounded-xl border border-white/10 bg-slate-950/70 px-4 text-sm text-slate-400">
          <Search size={17} />
          <span className="min-w-0 flex-1 truncate">Buscar reservas, clientes, metricas...</span>
          <span className="text-xs text-slate-500">⌘K</span>
        </label>
        <Link to="/app/account/notifications" className="relative grid h-11 w-11 place-items-center rounded-xl border border-white/10 text-slate-300 hover:bg-white/[0.05]" aria-label="Notificacoes">
          <Bell size={18} />
        </Link>
        <Link to="/app/account/help" className="grid h-11 w-11 place-items-center rounded-xl border border-white/10 text-slate-300 hover:bg-white/[0.05]" aria-label="Ajuda">
          <CircleHelp size={18} />
        </Link>
        <Link to="/app/account/personalization" className="grid h-11 w-11 place-items-center rounded-xl border border-white/10 text-slate-300 hover:bg-white/[0.05]" aria-label="Configuracoes">
          <Settings size={18} />
        </Link>
        <Link to="/app/account/overview" className="grid h-11 w-11 place-items-center rounded-full bg-blue-700 text-sm font-semibold text-white" aria-label="Perfil">
          {initials}
        </Link>
      </div>
    </header>
  );
}

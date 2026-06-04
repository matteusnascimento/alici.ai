import { CircleHelp, Search } from 'lucide-react';
import { Link } from 'react-router-dom';

import { NotificationDropdown } from './NotificationDropdown';

export function Topbar() {
  return (
    <header className="flex justify-end rounded-[1.5rem] border border-white/10 bg-[linear-gradient(145deg,rgba(15,23,42,0.88),rgba(2,6,23,0.72))] px-5 py-4 shadow-[0_18px_60px_rgba(0,0,0,0.26)] backdrop-blur-xl">
      <div className="flex w-full flex-wrap items-center justify-end gap-3">
        <label className="flex h-11 min-w-0 flex-1 items-center gap-3 rounded-xl border border-white/10 bg-slate-950/70 px-4 text-sm text-slate-400 md:max-w-[460px]">
          <Search size={17} />
          <span className="min-w-0 flex-1 truncate"><span className="font-semibold text-slate-200">Busca Global</span> reservas, clientes, metricas...</span>
          <span className="text-xs text-slate-500">Ctrl K</span>
        </label>
        <NotificationDropdown />
        <Link to="/app/account/help" className="grid h-11 w-11 place-items-center rounded-xl border border-white/10 text-slate-300 hover:bg-white/[0.05]" aria-label="Ajuda">
          <CircleHelp size={18} />
        </Link>
      </div>
    </header>
  );
}

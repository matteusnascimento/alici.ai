import { Megaphone, FolderOpen, Sparkles, FileText } from 'lucide-react';
import { NavLink, Outlet } from 'react-router-dom';

const NAV = [
  { to: '/app/marketing', label: 'Projetos', icon: FolderOpen, end: true },
  { to: '/app/marketing/campaign', label: 'Campanha', icon: Megaphone, end: false },
  { to: '/app/marketing/copy', label: 'Copy IA', icon: Sparkles, end: false },
  { to: '/app/marketing/brief', label: 'Briefing', icon: FileText, end: false },
];

export function MarketingShell() {
  return (
    <div className="flex h-full flex-col overflow-hidden">
      {/* Sub-nav */}
      <header className="flex shrink-0 items-center gap-1 border-b border-white/10 bg-storm/60 px-6 py-2 backdrop-blur">
        <span className="mr-4 text-xs uppercase tracking-[0.3em] text-cyan">Marketing</span>
        {NAV.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              [
                'flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm transition-colors',
                isActive
                  ? 'bg-cyan/15 text-cyan'
                  : 'text-slate-400 hover:bg-white/5 hover:text-white',
              ].join(' ')
            }
          >
            <Icon size={14} />
            {label}
          </NavLink>
        ))}
      </header>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        <Outlet />
      </div>
    </div>
  );
}

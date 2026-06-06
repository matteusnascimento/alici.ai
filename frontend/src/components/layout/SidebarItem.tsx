import type { LucideIcon } from 'lucide-react';
import { NavLink } from 'react-router-dom';

import { cn } from '../../utils/cn';

interface SidebarItemProps {
  label: string;
  to: string;
  icon: LucideIcon;
  expanded: boolean;
  onNavigate?: () => void;
}

export function SidebarItem({ label, to, icon: Icon, expanded, onNavigate }: SidebarItemProps) {
  return (
    <NavLink
      to={to}
      onClick={onNavigate}
      title={!expanded ? label : undefined}
      className={({ isActive }) =>
        cn(
          'group relative flex items-center text-sm transition-all',
          expanded ? 'h-14 min-h-14 justify-start gap-3 rounded-2xl border px-3' : 'mx-auto h-14 w-14 items-center justify-center rounded-2xl border p-0',
          isActive
            ? 'border-violet-300/55 bg-[linear-gradient(135deg,rgba(124,58,237,0.95),rgba(192,38,211,0.82))] text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.18),0_18px_44px_rgba(124,58,237,0.32)] before:absolute before:bottom-3 before:left-0 before:top-3 before:w-1 before:rounded-r-full before:bg-cyan-200'
            : 'border-transparent bg-white/[0.03] text-slate-300 hover:border-white/10 hover:bg-white/[0.07] hover:text-[var(--text-primary)]',
        )
      }
    >
      <span className="grid h-11 w-11 shrink-0 place-items-center rounded-full border border-white/15 bg-ink/70 text-cyan shadow-[inset_0_1px_0_rgba(255,255,255,0.1)]">
        <Icon size={20} strokeWidth={2.2} className="h-5 w-5 shrink-0" />
      </span>
      {expanded ? <span className="min-w-0 truncate text-sm font-medium leading-5 transition-all duration-300">{label}</span> : null}
    </NavLink>
  );
}

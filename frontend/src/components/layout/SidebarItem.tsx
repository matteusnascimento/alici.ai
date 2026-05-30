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
          expanded ? 'h-14 rounded-2xl border px-3 gap-3 justify-start' : 'mx-auto h-14 w-14 items-center justify-center rounded-2xl border p-0',
          isActive
            ? 'border-fuchsia-400/45 bg-white/[0.075] text-[var(--text-primary)] shadow-[inset_0_0_24px_rgba(192,38,211,0.16),0_0_28px_rgba(34,211,238,0.08)] before:absolute before:bottom-3 before:left-0 before:top-3 before:w-1 before:rounded-r-full before:bg-[var(--studio-gradient)]'
            : 'border-transparent bg-white/[0.03] text-slate-300 hover:border-white/10 hover:bg-white/[0.07] hover:text-[var(--text-primary)]',
        )
      }
    >
      <span className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-white/10 bg-ink/60 text-cyan shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]">
        <Icon size={18} className="shrink-0" />
      </span>
      {expanded ? <span className="whitespace-nowrap text-sm font-medium transition-all duration-300">{label}</span> : null}
    </NavLink>
  );
}

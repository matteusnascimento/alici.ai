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
          'group relative flex items-center rounded-2xl border px-3 py-3 text-sm transition',
          expanded ? 'gap-3' : 'justify-center',
          isActive
            ? 'border-cyan/45 bg-cyan/10 text-white shadow-[inset_0_0_20px_rgba(110,231,249,0.1)]'
            : 'border-transparent bg-white/[0.03] text-slate-300 hover:border-white/10 hover:bg-white/[0.06] hover:text-white',
        )
      }
    >
      <span className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-ink/60 text-cyan">
        <Icon size={17} />
      </span>
      <span
        className={cn(
          'whitespace-nowrap text-sm font-medium transition-all duration-300',
          expanded ? 'translate-x-0 opacity-100' : 'pointer-events-none -translate-x-2 opacity-0',
        )}
      >
        {label}
      </span>
    </NavLink>
  );
}

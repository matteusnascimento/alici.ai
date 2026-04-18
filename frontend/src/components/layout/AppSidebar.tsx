import { BadgeDollarSign, Bot, ChartColumnBig, LayoutDashboard, Link2, Megaphone, Menu, Settings2, Sparkles, X } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

import { SidebarItem } from './SidebarItem';
import { SidebarLogo } from './SidebarLogo';

interface AppSidebarProps {
  mobileOpen: boolean;
  onMobileOpen: () => void;
  onMobileClose: () => void;
  onDesktopExpandedChange?: (expanded: boolean) => void;
}

const items = [
  { label: 'Dashboard', to: '/app/dashboard', icon: LayoutDashboard },
  { label: 'Revenue', to: '/app/revenue', icon: BadgeDollarSign },
  { label: 'Alici Chat', to: '/app/chat', icon: Bot },
  { label: 'Agents', to: '/app/agents', icon: ChartColumnBig },
  { label: 'AXI Studio', to: '/app/studio', icon: Megaphone },
  { label: 'Marketing', to: '/app/marketing', icon: Sparkles },
  { label: 'Integrações', to: '/app/integrations', icon: Link2 },
  { label: 'Conta AXI', to: '/app/account', icon: Settings2 },
];

export function AppSidebar({
  mobileOpen,
  onMobileOpen,
  onMobileClose,
  onDesktopExpandedChange,
}: AppSidebarProps) {
  const [hoverCapable, setHoverCapable] = useState(false);
  const [expandedDesktop, setExpandedDesktop] = useState(false);

  useEffect(() => {
    if (typeof window.matchMedia !== 'function') {
      setHoverCapable(false);
      return;
    }
    const query = window.matchMedia('(hover: hover) and (pointer: fine)');
    const sync = () => setHoverCapable(query.matches);
    sync();
    query.addEventListener('change', sync);
    return () => query.removeEventListener('change', sync);
  }, []);

  const expanded = useMemo(() => (hoverCapable ? expandedDesktop : true), [expandedDesktop, hoverCapable]);

  useEffect(() => {
    onDesktopExpandedChange?.(expanded);
  }, [expanded, onDesktopExpandedChange]);

  return (
    <>
      <button
        type="button"
        onClick={onMobileOpen}
        className="fixed left-4 top-4 z-40 inline-flex h-11 w-11 items-center justify-center rounded-xl border border-white/15 bg-storm/90 text-[var(--text-primary)] shadow-soft backdrop-blur lg:hidden"
        aria-label="Abrir menu"
      >
        <Menu size={18} />
      </button>

      <aside
        onMouseEnter={() => hoverCapable && setExpandedDesktop(true)}
        onMouseLeave={() => hoverCapable && setExpandedDesktop(false)}
        className={[
          'fixed left-0 top-0 z-30 hidden h-screen shrink-0 overflow-hidden rounded-r-[2rem] border-r border-white/10',
          'bg-gradient-to-b from-storm/95 via-storm/85 to-ink/95 py-4 shadow-soft backdrop-blur lg:flex lg:flex-col',
          'transition-[width] duration-300 ease-out',
          expanded ? 'px-3 lg:w-[284px]' : 'px-0 lg:w-[92px]',
        ].join(' ')}
      >
        <SidebarLogo expanded={expanded} />
        <nav className={['mt-6 flex flex-1 flex-col overflow-y-auto pb-3', expanded ? 'gap-2.5 pr-1' : 'items-center gap-4 pr-0'].join(' ')}>
          {items.map((item) => (
            <SidebarItem key={item.to} expanded={expanded} {...item} />
          ))}
        </nav>
      </aside>

      {mobileOpen ? (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm lg:hidden" onClick={onMobileClose} aria-hidden="true" />
      ) : null}

      <aside
        className={[
          'fixed bottom-0 left-0 top-0 z-50 w-[304px] rounded-r-3xl border-r border-white/10',
          'bg-gradient-to-b from-storm via-storm/90 to-ink px-4 py-5 shadow-soft transition-transform duration-300 lg:hidden',
          mobileOpen ? 'translate-x-0' : '-translate-x-full',
        ].join(' ')}
      >
        <div className="mb-4 flex items-center justify-between">
          <p className="text-xs uppercase tracking-[0.35em] text-cyan">AXI</p>
          <button
            type="button"
            onClick={onMobileClose}
            className="inline-flex h-9 w-9 items-center justify-center rounded-xl border border-white/15 text-slate-200"
            aria-label="Fechar menu"
          >
            <X size={16} />
          </button>
        </div>
        <SidebarLogo expanded />
        <nav className="mt-5 flex flex-col gap-2.5 overflow-y-auto pb-2 pr-1">
          {items.map((item) => (
            <SidebarItem key={item.to} expanded onNavigate={onMobileClose} {...item} />
          ))}
        </nav>
      </aside>
    </>
  );
}

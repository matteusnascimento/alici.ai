import { BadgeDollarSign, Bot, Building2, ChartColumnBig, ChevronLeft, Gauge, Link2, LogOut, Megaphone, Menu, MessageSquare, ShieldCheck, Sparkles, UserCircle2, X } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';

import { useAuth } from '../../hooks/useAuth';
import { SidebarItem } from './SidebarItem';
import { SidebarLogo } from './SidebarLogo';

interface AppSidebarProps {
  mobileOpen: boolean;
  onMobileOpen: () => void;
  onMobileClose: () => void;
  onDesktopExpandedChange?: (expanded: boolean) => void;
}

const items = [
  { label: 'Control Room', to: '/app/control-room', icon: Gauge },
  { label: 'Revenue', to: '/app/revenue?view=business-pulse', icon: BadgeDollarSign },
  { label: 'Chats', to: '/app/chats', icon: MessageSquare },
  { label: 'AXI Assistant', to: '/app/assistant', icon: Bot },
  { label: 'Marketing', to: '/app/marketing', icon: Megaphone },
  { label: 'Studio', to: '/app/studio', icon: Sparkles },
  { label: 'Agents', to: '/app/agents', icon: ChartColumnBig },
  { label: 'Integrations', to: '/app/integrations', icon: Link2 },
];

function SidebarFooter({ expanded, onCollapse }: { expanded: boolean; onCollapse: () => void }) {
  const { user, logout } = useAuth();
  const displayName = user?.name || 'Usuario AXI';
  const role = user?.role === 'owner' ? 'Proprietario' : user?.role || 'Membro';
  const companyLabel = user?.plan ? `Plano ${user.plan}` : 'Empresa ativa';

  return (
    <div className={['mt-auto border-t border-white/10 pt-3', expanded ? 'space-y-3 px-0' : 'flex flex-col items-center gap-3 px-0'].join(' ')}>
      <div
        className={[
          'border border-white/10 bg-white/[0.045] shadow-[inset_0_1px_0_rgba(255,255,255,0.07)]',
          expanded ? 'rounded-2xl p-3' : 'grid h-12 w-12 place-items-center rounded-full p-0',
        ].join(' ')}
      >
        <div className="flex items-center gap-3">
          <span className="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-cyan-400/15 text-cyan-200">
            <Building2 size={20} />
          </span>
          {expanded ? (
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-white">Empresa</p>
              <p className="truncate text-xs text-slate-400">{companyLabel}</p>
            </div>
          ) : null}
        </div>
        {expanded ? (
          <Link to="/app/account/overview" className="mt-3 flex h-9 items-center justify-center rounded-xl border border-white/10 bg-white/[0.04] text-xs font-medium text-slate-200 hover:bg-white/[0.08]">
            Ver meu plano
          </Link>
        ) : null}
      </div>
      <div
        className={[
          'border border-violet-300/20 bg-[linear-gradient(135deg,rgba(124,58,237,0.22),rgba(255,255,255,0.045))]',
          expanded ? 'rounded-2xl p-3' : 'grid h-12 w-12 place-items-center rounded-full p-0',
        ].join(' ')}
      >
        <div className="flex items-center gap-3">
          <span className="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-[linear-gradient(135deg,#7c3aed,#22d3ee)] text-white">
            <UserCircle2 size={21} />
          </span>
          {expanded ? (
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-white">{displayName}</p>
              <p className="truncate text-xs capitalize text-slate-400">{role}</p>
            </div>
          ) : null}
        </div>
        {expanded ? (
          <Link to="/app/account/overview" className="mt-3 flex h-9 items-center justify-center rounded-xl border border-white/10 bg-white/[0.04] text-xs font-medium text-slate-200 hover:bg-white/[0.08]">
            Minha conta
          </Link>
        ) : null}
      </div>
      {user?.role === 'owner' ? (
        <SidebarItem expanded={expanded} label="Administracao" to="/app/admin" icon={ShieldCheck} />
      ) : null}
      {expanded ? (
        <button
          type="button"
          onClick={logout}
          className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm text-slate-400 hover:bg-white/[0.05] hover:text-white"
        >
          <LogOut size={17} />
          Sair
        </button>
      ) : null}
      {expanded ? (
        <button
          type="button"
          onClick={onCollapse}
          className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm text-slate-400 hover:bg-white/[0.05] hover:text-white"
        >
          <ChevronLeft size={17} />
          Recolher menu
        </button>
      ) : null}
    </div>
  );
}

export function AppSidebar({
  mobileOpen,
  onMobileOpen,
  onMobileClose,
  onDesktopExpandedChange,
}: AppSidebarProps) {
  const [hoverCapable, setHoverCapable] = useState(false);
  const [expandedDesktop, setExpandedDesktop] = useState(true);

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
        onMouseLeave={() => undefined}
        className={[
          'fixed left-0 top-0 z-30 hidden h-screen shrink-0 overflow-hidden rounded-r-[2rem] border-r border-white/10',
          'bg-[radial-gradient(circle_at_20%_0%,rgba(192,38,211,0.22),transparent_32%),linear-gradient(180deg,rgba(8,8,12,0.97),rgba(5,5,7,0.96))] py-4 shadow-[0_24px_80px_rgba(0,0,0,0.38)] backdrop-blur-xl lg:flex lg:flex-col',
          'transition-[width] duration-300 ease-out',
          expanded ? 'px-3 lg:w-[260px]' : 'px-0 lg:w-[92px]',
        ].join(' ')}
      >
        <SidebarLogo expanded={expanded} />
        <nav className={['mt-6 flex flex-1 flex-col overflow-y-auto pb-3', expanded ? 'gap-2.5 pr-1' : 'items-center gap-4 pr-0'].join(' ')}>
          {items.map((item) => (
            <SidebarItem key={item.to} expanded={expanded} {...item} />
          ))}
        </nav>
        <SidebarFooter expanded={expanded} onCollapse={() => setExpandedDesktop(false)} />
      </aside>

      {mobileOpen ? (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm lg:hidden" onClick={onMobileClose} aria-hidden="true" />
      ) : null}

      <aside
        className={[
          'fixed bottom-0 left-0 top-0 z-50 w-[304px] rounded-r-3xl border-r border-white/10',
          'bg-[radial-gradient(circle_at_20%_0%,rgba(192,38,211,0.22),transparent_32%),linear-gradient(180deg,rgba(8,8,12,0.97),rgba(5,5,7,0.96))] px-4 py-5 shadow-soft transition-transform duration-300 lg:hidden',
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
        <nav className="mt-5 flex max-h-[calc(100vh-310px)] flex-col gap-2.5 overflow-y-auto pb-2 pr-1">
          {items.map((item) => (
            <SidebarItem key={item.to} expanded onNavigate={onMobileClose} {...item} />
          ))}
        </nav>
        <SidebarFooter expanded onCollapse={onMobileClose} />
      </aside>
    </>
  );
}

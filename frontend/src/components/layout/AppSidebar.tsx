import { BadgeDollarSign, Bot, Building2, ChevronsLeft, ChevronsRight, Home, Link2, LogOut, Megaphone, Menu, MessageSquare, ShieldCheck, Sparkles, UserCircle2, X } from 'lucide-react';
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
  { label: 'Home', to: '/app', icon: Home, roles: ['owner', 'admin', 'gerente', 'marketing', 'atendimento', 'member'] },
  { label: 'Revenue', to: '/app/revenue?view=business-pulse', icon: BadgeDollarSign },
  { label: 'Chats', to: '/app/chats', icon: MessageSquare, roles: ['owner', 'admin', 'gerente', 'atendimento', 'member'] },
  { label: 'AXI Assistant', to: '/app/assistant', icon: Bot, roles: ['owner', 'admin', 'gerente', 'marketing', 'atendimento', 'member'] },
  { label: 'Marketing', to: '/app/marketing', icon: Megaphone, roles: ['owner', 'admin', 'gerente', 'marketing', 'member'] },
  { label: 'Studio', to: '/app/studio', icon: Sparkles, roles: ['owner', 'admin', 'gerente', 'marketing', 'member'] },
  { label: 'Integrations', to: '/app/integrations', icon: Link2, roles: ['owner', 'admin', 'member'] },
];

function SidebarFooter({ expanded }: { expanded: boolean }) {
  const { user, logout } = useAuth();
  const displayName = user?.name || 'Usuario AXI';
  const companyLabel = (user as { company?: string } | null)?.company || 'Empresa nao configurada';
  const canAdmin = user?.role === 'owner' || user?.role === 'admin';

  return (
    <div className={['mt-auto border-t border-white/10 pt-3', expanded ? 'space-y-2 px-0' : 'flex flex-col items-center gap-3 px-0'].join(' ')}>
      <div className={['border border-white/10 bg-white/[0.035]', expanded ? 'rounded-2xl p-3' : 'grid h-12 w-12 place-items-center rounded-full p-0'].join(' ')}>
        <div className="flex items-center gap-3">
          <span className="grid h-11 w-11 shrink-0 place-items-center rounded-full border border-white/10 bg-cyan-400/15 text-cyan-200">
            <Building2 strokeWidth={2.2} className="h-5 w-5 shrink-0" />
          </span>
          {expanded ? (
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-white">{companyLabel}</p>
              <p className="truncate text-xs text-slate-400">Empresa atual</p>
            </div>
          ) : null}
        </div>
      </div>
      <Link
        to="/app/account/overview"
        className={[
          'block border border-violet-300/20 bg-[linear-gradient(135deg,rgba(124,58,237,0.20),rgba(255,255,255,0.04))] transition hover:border-violet-200/35',
          expanded ? 'rounded-2xl p-3' : 'grid h-12 w-12 place-items-center rounded-full p-0',
        ].join(' ')}
      >
        <div className="flex items-center gap-3">
          <span className="grid h-11 w-11 shrink-0 place-items-center rounded-full border border-white/10 bg-[linear-gradient(135deg,#7c3aed,#22d3ee)] text-white">
            <UserCircle2 strokeWidth={2.2} className="h-5 w-5 shrink-0" />
          </span>
          {expanded ? (
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-white">{displayName}</p>
              <p className="truncate text-xs text-slate-400">Minha Conta</p>
            </div>
          ) : null}
        </div>
      </Link>
      {canAdmin ? (
        <SidebarItem expanded={expanded} label="Administracao" to="/app/admin" icon={ShieldCheck} />
      ) : null}
      {expanded ? (
        <button
          type="button"
          onClick={logout}
          className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm text-slate-400 hover:bg-white/[0.05] hover:text-white"
        >
          <LogOut strokeWidth={2.2} className="h-[18px] w-[18px] shrink-0" />
          Sair
        </button>
      ) : (
        <button
          type="button"
          onClick={logout}
          className="grid h-12 w-12 place-items-center rounded-full text-slate-400 hover:bg-white/[0.05] hover:text-white"
          aria-label="Sair"
        >
          <LogOut strokeWidth={2.2} className="h-[18px] w-[18px] shrink-0" />
        </button>
      )}
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
  const { user } = useAuth();
  const roleKey = user?.role ?? 'member';
  const navigationItems = useMemo(
    () => items.filter((item) => !item.roles || item.roles.includes(roleKey) || roleKey === 'owner' || roleKey === 'admin'),
    [roleKey],
  );

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
  const CollapseIcon = expanded ? ChevronsLeft : ChevronsRight;

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
          {navigationItems.map((item) => (
            <SidebarItem key={item.to} expanded={expanded} {...item} />
          ))}
          <button
            type="button"
            onClick={() => setExpandedDesktop((current) => !current)}
            className={[
              'mt-auto flex items-center border border-transparent bg-white/[0.03] text-sm text-slate-300 transition hover:border-white/10 hover:bg-white/[0.07] hover:text-white',
              expanded ? 'h-12 justify-start gap-3 rounded-2xl px-3' : 'mx-auto h-12 w-12 justify-center rounded-2xl p-0',
            ].join(' ')}
            aria-label={expanded ? 'Recolher sidebar' : 'Expandir sidebar'}
            title={!expanded ? 'Expandir sidebar' : undefined}
          >
            <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full border border-white/15 bg-ink/70 text-cyan shadow-[inset_0_1px_0_rgba(255,255,255,0.1)]">
              <CollapseIcon size={18} strokeWidth={2.2} className="h-[18px] w-[18px] shrink-0" />
            </span>
            {expanded ? <span className="min-w-0 truncate text-sm font-medium leading-5">Recolher menu</span> : null}
          </button>
        </nav>
        <SidebarFooter expanded={expanded} />
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
          {navigationItems.map((item) => (
            <SidebarItem key={item.to} expanded onNavigate={onMobileClose} {...item} />
          ))}
        </nav>
        <SidebarFooter expanded />
      </aside>
    </>
  );
}

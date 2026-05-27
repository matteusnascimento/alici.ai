import {
  BadgeDollarSign,
  BarChart3,
  Bot,
  BriefcaseBusiness,
  CalendarDays,
  ChevronDown,
  ChevronRight,
  ChartColumnBig,
  ClipboardList,
  Contact,
  FileText,
  GitBranch,
  Headphones,
  LayoutDashboard,
  Link2,
  Megaphone,
  Menu,
  MessageSquareText,
  Package,
  Phone,
  Settings2,
  Sparkles,
  Truck,
  Users,
  X,
} from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';

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
  {
    label: 'CRM',
    to: '/app/crm',
    icon: BriefcaseBusiness,
    children: [
      { label: 'Negócios', to: '/app/crm/negocios', icon: ChartColumnBig },
      { label: 'Pipelines', to: '/app/crm/pipelines', icon: GitBranch },
      { label: 'Contatos', to: '/app/crm/contatos', icon: Contact },
      { label: 'Grupos', to: '/app/crm/grupos', icon: Users },
      { label: 'Reuniões', to: '/app/crm/reunioes', icon: CalendarDays },
      { label: 'Produtos', to: '/app/crm/produtos', icon: Package },
      { label: 'Contratos', to: '/app/crm/contratos', icon: FileText },
      { label: 'Agenda', to: '/app/crm/agenda', icon: CalendarDays },
      { label: 'Ligações', to: '/app/crm/ligacoes', icon: Phone },
      { label: 'Mensagens Rápidas', to: '/app/crm/mensagens-rapidas', icon: MessageSquareText },
    ],
  },
  {
    label: 'CS',
    to: '/app/cs',
    icon: Headphones,
    children: [
      { label: 'Jornada', to: '/app/cs/jornada', icon: ClipboardList },
      { label: 'Logística', to: '/app/cs/logistica', icon: Truck },
    ],
  },
  {
    label: 'Análises',
    to: '/app/analytics',
    icon: BarChart3,
    children: [
      { label: 'Análises', to: '/app/analytics/analises', icon: BarChart3 },
      { label: 'Receita', to: '/app/analytics/receita', icon: BadgeDollarSign },
      { label: 'Forecast', to: '/app/analytics/forecast', icon: ChartColumnBig },
    ],
  },
  { label: 'Agents', to: '/app/agents', icon: ChartColumnBig },
  { label: 'AXI Studio', to: '/app/studio', icon: Megaphone },
  { label: 'Marketing', to: '/app/marketing', icon: Sparkles },
  { label: 'Integrações', to: '/app/integrations', icon: Link2 },
  { label: 'Conta AXI', to: '/app/account', icon: Settings2 },
];

type SidebarChild = NonNullable<(typeof items)[number]['children']>[number];
type SidebarEntry = (typeof items)[number];

function initialGroupState() {
  return Object.fromEntries(
    items.filter((item) => item.children?.length).map((item) => [item.to, true]),
  ) as Record<string, boolean>;
}

function SidebarChildren({
  children,
  expanded,
  onNavigate,
  id,
}: {
  children?: SidebarChild[];
  expanded: boolean;
  onNavigate?: () => void;
  id?: string;
}) {
  if (!children?.length || !expanded) return null;

  return (
    <div id={id} className="ml-5 border-l border-white/10 pl-2">
      {children.map((child) => {
        const Icon = child.icon;
        return (
          <NavLink
            key={child.to}
            to={child.to}
            onClick={onNavigate}
            className={({ isActive }) =>
              [
                'mt-1 flex h-11 items-center gap-3 rounded-xl px-3 text-sm transition',
                isActive
                  ? 'border border-cyan/45 bg-cyan/10 text-cyan shadow-[inset_0_0_20px_rgb(var(--accent-rgb)/0.10)]'
                  : 'text-slate-400 hover:bg-white/[0.05] hover:text-[var(--text-primary)]',
              ].join(' ')
            }
          >
            <Icon size={15} />
            <span className="truncate">{child.label}</span>
          </NavLink>
        );
      })}
    </div>
  );
}

function SidebarGroup({
  item,
  expanded,
  groupOpen,
  onToggle,
  onNavigate,
}: {
  item: SidebarEntry;
  expanded: boolean;
  groupOpen: boolean;
  onToggle: () => void;
  onNavigate?: () => void;
}) {
  const hasChildren = Boolean(item.children?.length);
  const contentId = `sidebar-group-${item.to.replace(/[^a-z0-9]+/gi, '-')}`;

  if (!expanded || !hasChildren) {
    return (
      <div className={expanded ? 'space-y-1' : ''}>
        <SidebarItem expanded={expanded} icon={item.icon} label={item.label} onNavigate={onNavigate} to={item.to} />
      </div>
    );
  }

  return (
    <div className="space-y-1">
      <div className="flex items-center gap-2">
        <div className="min-w-0 flex-1">
          <SidebarItem className="w-full" expanded icon={item.icon} label={item.label} onNavigate={onNavigate} to={item.to} />
        </div>
        <button
          type="button"
          onClick={onToggle}
          aria-expanded={groupOpen}
          aria-controls={contentId}
          aria-label={`${groupOpen ? 'Recolher' : 'Expandir'} ${item.label}`}
          title={`${groupOpen ? 'Recolher' : 'Expandir'} ${item.label}`}
          className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-white/10 bg-white/[0.03] text-slate-300 transition hover:border-cyan/35 hover:bg-cyan/10 hover:text-cyan"
        >
          {groupOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        </button>
      </div>
      <SidebarChildren id={contentId} children={item.children} expanded={groupOpen} onNavigate={onNavigate} />
    </div>
  );
}

export function AppSidebar({
  mobileOpen,
  onMobileOpen,
  onMobileClose,
  onDesktopExpandedChange,
}: AppSidebarProps) {
  const location = useLocation();
  const [hoverCapable, setHoverCapable] = useState(false);
  const [expandedDesktop, setExpandedDesktop] = useState(false);
  const [openGroups, setOpenGroups] = useState<Record<string, boolean>>(() => initialGroupState());
  const desktopNavRef = useRef<HTMLElement | null>(null);

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

  useEffect(() => {
    const activeGroup = items.find((item) => item.children?.some((child) => location.pathname.startsWith(child.to)));
    if (!activeGroup) return;
    setOpenGroups((current) => (current[activeGroup.to] ? current : { ...current, [activeGroup.to]: true }));
  }, [location.pathname]);

  function toggleGroup(groupTo: string) {
    setOpenGroups((current) => ({ ...current, [groupTo]: !(current[groupTo] ?? true) }));
  }

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
        onWheel={(event) => {
          if (!desktopNavRef.current) return;
          desktopNavRef.current.scrollTop += event.deltaY;
        }}
        onMouseEnter={() => hoverCapable && setExpandedDesktop(true)}
        onMouseLeave={() => hoverCapable && setExpandedDesktop(false)}
        className={[
          'fixed left-0 top-0 z-30 hidden h-screen min-h-0 shrink-0 overflow-hidden rounded-r-[2rem] border-r border-white/10',
          'bg-gradient-to-b from-storm/95 via-storm/85 to-ink/95 py-4 shadow-soft backdrop-blur lg:flex lg:flex-col',
          'transition-[width] duration-300 ease-out',
          expanded ? 'px-3 lg:w-[284px]' : 'px-0 lg:w-[92px]',
        ].join(' ')}
      >
        <SidebarLogo expanded={expanded} />
        <nav
          ref={desktopNavRef}
          className={[
            'mt-6 flex min-h-0 flex-1 flex-col overflow-y-auto overscroll-contain pb-3 [scrollbar-gutter:stable]',
            expanded ? 'gap-2.5 pr-1' : 'items-center gap-4 pr-0',
          ].join(' ')}
        >
          {items.map((item) => (
            <SidebarGroup
              key={item.to}
              item={item}
              expanded={expanded}
              groupOpen={openGroups[item.to] ?? true}
              onToggle={() => toggleGroup(item.to)}
            />
          ))}
        </nav>
      </aside>

      {mobileOpen ? (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm lg:hidden" onClick={onMobileClose} aria-hidden="true" />
      ) : null}

      <aside
        className={[
          'fixed bottom-0 left-0 top-0 z-50 flex w-[304px] min-h-0 flex-col rounded-r-3xl border-r border-white/10',
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
        <nav className="mt-5 flex min-h-0 flex-1 flex-col gap-2.5 overflow-y-auto overscroll-contain pb-2 pr-1 [scrollbar-gutter:stable]">
          {items.map((item) => (
            <SidebarGroup
              key={item.to}
              item={item}
              expanded
              groupOpen={openGroups[item.to] ?? true}
              onNavigate={onMobileClose}
              onToggle={() => toggleGroup(item.to)}
            />
          ))}
        </nav>
      </aside>
    </>
  );
}

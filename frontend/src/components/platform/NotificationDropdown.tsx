import {
  AlertTriangle,
  Bell,
  CalendarCheck,
  CreditCard,
  FileClock,
  Megaphone,
  MessageCircle,
  ShieldAlert,
  UserCheck,
  type LucideIcon,
} from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

import {
  listNotifications,
  markAllNotificationsRead,
  markNotificationRead,
} from '../../services/notifications.service';
import type { SystemNotification } from '../../types/notifications';

const iconByType: Record<string, LucideIcon> = {
  whatsapp: MessageCircle,
  mensagem: MessageCircle,
  cotacao: FileClock,
  reserva: CalendarCheck,
  campanha: Megaphone,
  integracao: AlertTriangle,
  pagamento: CreditCard,
  convite: UserCheck,
  seguranca: ShieldAlert,
};

function iconFor(tipo: string) {
  return iconByType[tipo.toLowerCase()] ?? Bell;
}

function relativeTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Agora';
  const diffMs = Date.now() - date.getTime();
  const minutes = Math.max(0, Math.floor(diffMs / 60000));
  if (minutes < 1) return 'Agora';
  if (minutes < 60) return `Ha ${minutes} min`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `Ha ${hours} h`;
  const days = Math.floor(hours / 24);
  return `Ha ${days} d`;
}

export function NotificationDropdown() {
  const [open, setOpen] = useState(false);
  const [showAll, setShowAll] = useState(false);
  const [items, setItems] = useState<SystemNotification[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const panelRef = useRef<HTMLDivElement | null>(null);
  const location = useLocation();

  const unreadCount = useMemo(() => items.filter((item) => !item.lida).length, [items]);
  const visibleItems = showAll ? items : items.slice(0, 6);

  async function load() {
    setLoading(true);
    try {
      const data = await listNotifications();
      setItems(Array.isArray(data) ? data : []);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao carregar notificacoes.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  useEffect(() => {
    setOpen(false);
  }, [location.pathname, location.search]);

  useEffect(() => {
    if (!open) return undefined;

    function handlePointer(event: MouseEvent) {
      const target = event.target;
      if (target instanceof Node && panelRef.current && !panelRef.current.contains(target)) {
        setOpen(false);
      }
    }

    function handleKey(event: KeyboardEvent) {
      if (event.key === 'Escape') setOpen(false);
    }

    document.addEventListener('mousedown', handlePointer);
    document.addEventListener('keydown', handleKey);
    return () => {
      document.removeEventListener('mousedown', handlePointer);
      document.removeEventListener('keydown', handleKey);
    };
  }, [open]);

  async function readAll() {
    if (unreadCount === 0) return;
    try {
      const data = await markAllNotificationsRead();
      setItems(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Nao foi possivel marcar como lidas.');
    }
  }

  function openNotification(notification: SystemNotification) {
    if (notification.lida) return;
    setItems((current) => current.map((item) => (item.id === notification.id ? { ...item, lida: true } : item)));
    void markNotificationRead(notification.id).catch(() => {
      setItems((current) => current.map((item) => (item.id === notification.id ? { ...item, lida: false } : item)));
    });
  }

  return (
    <div ref={panelRef} className="relative">
      <button
        type="button"
        onClick={() => {
          setOpen((current) => !current);
          if (!open) void load();
        }}
        className="relative grid h-11 w-11 place-items-center rounded-xl border border-white/10 text-slate-300 hover:bg-white/[0.05]"
        aria-label="Notificacoes"
        aria-expanded={open}
      >
        <Bell size={18} />
        {unreadCount > 0 ? (
          <span className="absolute right-2 top-2 grid min-h-[16px] min-w-[16px] place-items-center rounded-full bg-rose-500 px-1 text-[10px] font-bold leading-none text-white">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        ) : null}
      </button>

      {open ? (
        <section className="absolute right-0 top-[calc(100%+0.75rem)] z-50 w-[min(92vw,420px)] overflow-hidden rounded-2xl border border-white/10 bg-slate-950 shadow-[0_28px_90px_rgba(0,0,0,0.45)]">
          <header className="flex items-start justify-between gap-4 border-b border-white/10 px-4 py-4">
            <div>
              <h2 className="font-display text-xl text-white">Notificacoes</h2>
              <p className="mt-1 text-xs text-slate-500">{unreadCount} nao lidas</p>
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => void readAll()}
                disabled={unreadCount === 0}
                className="rounded-lg border border-white/10 px-3 py-2 text-xs font-semibold text-slate-200 hover:border-cyan-300/40 disabled:cursor-not-allowed disabled:opacity-45"
              >
                Marcar todas como lidas
              </button>
              <button
                type="button"
                onClick={() => setShowAll((current) => !current)}
                className="rounded-lg bg-violet-600 px-3 py-2 text-xs font-semibold text-white hover:bg-violet-500"
              >
                {showAll ? 'Ver menos' : 'Ver todas'}
              </button>
            </div>
          </header>

          <div className="max-h-[480px] overflow-y-auto p-2">
            {loading ? (
              <div className="px-4 py-8 text-center text-sm text-slate-400">Carregando notificacoes...</div>
            ) : error ? (
              <div className="rounded-xl border border-rose-400/25 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">{error}</div>
            ) : visibleItems.length === 0 ? (
              <div className="rounded-xl border border-dashed border-white/15 bg-white/[0.03] px-4 py-8 text-center text-sm text-slate-400">
                Nenhuma notificacao real do sistema no momento.
              </div>
            ) : (
              <div className="space-y-1">
                {visibleItems.map((notification) => {
                  const Icon = iconFor(notification.tipo);
                  return (
                    <Link
                      key={notification.id}
                      to={notification.destino}
                      onClick={() => openNotification(notification)}
                      className="grid grid-cols-[auto_minmax(0,1fr)_auto] gap-3 rounded-xl px-3 py-3 text-left transition hover:bg-white/[0.05]"
                    >
                      <span className={notification.lida ? 'grid h-10 w-10 place-items-center rounded-full bg-white/[0.04] text-slate-400' : 'grid h-10 w-10 place-items-center rounded-full bg-cyan-400/12 text-cyan-200'}>
                        <Icon size={18} />
                      </span>
                      <span className="min-w-0">
                        <span className="block truncate text-sm font-semibold text-white">{notification.titulo}</span>
                        <span className="mt-0.5 block text-xs leading-5 text-slate-400">{notification.descricao}</span>
                        <span className="mt-1 block text-xs font-medium text-violet-200">Abrir: {notification.destino}</span>
                      </span>
                      <span className="flex flex-col items-end gap-2 text-right">
                        <span className="text-[11px] text-slate-500">{relativeTime(notification.horario)}</span>
                        <span className={notification.lida ? 'h-2 w-2 rounded-full bg-slate-700' : 'h-2 w-2 rounded-full bg-rose-400'} />
                      </span>
                    </Link>
                  );
                })}
              </div>
            )}
          </div>
        </section>
      ) : null}
    </div>
  );
}

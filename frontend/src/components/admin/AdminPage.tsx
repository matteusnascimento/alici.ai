import {
  AlertTriangle,
  Bell,
  CreditCard,
  KeyRound,
  Loader2,
  Lock,
  MailPlus,
  Pencil,
  RotateCcw,
  ScrollText,
  ShieldCheck,
  Trash2,
  UserMinus,
  Users,
  type LucideIcon,
} from 'lucide-react';
import { type FormEvent, useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

import { ApiError } from '../../services/api';
import { getAdminOverview, type AdminMetric, type AdminOverview, type AdminUser } from '../../services/admin.service';

const adminPages = [
  { id: 'dashboard', label: 'Dashboard', path: '/app/admin', icon: ShieldCheck },
  { id: 'users', label: 'Usuarios', path: '/app/admin/users', icon: Users },
  { id: 'permissions', label: 'Permissoes', path: '/app/admin/permissions', icon: KeyRound },
  { id: 'billing', label: 'Billing', path: '/app/admin/billing', icon: CreditCard },
  { id: 'security', label: 'Seguranca', path: '/app/admin/security', icon: Lock },
  { id: 'audit', label: 'Auditoria', path: '/app/admin/audit', icon: ScrollText },
] as const;

type AdminPageId = (typeof adminPages)[number]['id'];
type PendingAction = 'invite' | 'edit' | 'disable' | 'reset' | 'delete' | 'permissions' | null;

const permissionModules = ['Revenue', 'Chats', 'AXI Assistant', 'Marketing', 'Studio', 'Integrations', 'Administracao'];
const permissionActions = ['Visualizar', 'Criar', 'Editar', 'Excluir'];

function pageFromPath(pathname: string): AdminPageId {
  if (pathname.startsWith('/app/admin/users')) return 'users';
  if (pathname.startsWith('/app/admin/permissions')) return 'permissions';
  if (pathname.startsWith('/app/admin/billing')) return 'billing';
  if (pathname.startsWith('/app/admin/security')) return 'security';
  if (pathname.startsWith('/app/admin/audit')) return 'audit';
  return 'dashboard';
}

function metricValue(items: AdminMetric[] | undefined, label: string) {
  return items?.find((item) => item.label === label)?.value ?? 0;
}

function EmptyState({ children }: { children: string }) {
  return (
    <div className="rounded-2xl border border-dashed border-white/15 bg-white/[0.03] p-6 text-center text-sm text-slate-400">
      {children}
    </div>
  );
}

function PageCard({ icon: Icon, title, value, detail, onClick }: { icon: LucideIcon; title: string; value: string | number; detail: string; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="rounded-2xl border border-white/10 bg-[linear-gradient(145deg,rgba(15,23,42,0.86),rgba(2,6,23,0.66))] p-5 text-left shadow-[0_20px_70px_rgba(0,0,0,0.28)] transition hover:border-violet-300/35"
    >
      <span className="grid h-12 w-12 place-items-center rounded-2xl bg-violet-500/16 text-violet-200">
        <Icon size={24} />
      </span>
      <p className="mt-4 text-sm text-slate-400">{title}</p>
      <p className="mt-1 font-display text-3xl text-white">{value}</p>
      <p className="mt-2 text-sm text-slate-500">{detail}</p>
    </button>
  );
}

function Section({ title, description, children }: { title: string; description: string; children: React.ReactNode }) {
  return (
    <section className="rounded-2xl border border-white/10 bg-slate-950/58 p-5 shadow-[0_22px_70px_rgba(0,0,0,0.25)]">
      <div className="mb-5">
        <h2 className="font-display text-2xl text-white">{title}</h2>
        <p className="mt-1 text-sm text-slate-400">{description}</p>
      </div>
      {children}
    </section>
  );
}

function UserActions({ user, onAction }: { user: AdminUser; onAction: (action: PendingAction, user: AdminUser) => void }) {
  return (
    <div className="flex flex-wrap gap-2">
      <button type="button" onClick={() => onAction('edit', user)} className="grid h-9 w-9 place-items-center rounded-lg border border-white/10 text-slate-300 hover:text-white" aria-label="Editar usuario">
        <Pencil size={15} />
      </button>
      <button type="button" onClick={() => onAction('disable', user)} className="grid h-9 w-9 place-items-center rounded-lg border border-white/10 text-slate-300 hover:text-white" aria-label="Desativar usuario">
        <UserMinus size={15} />
      </button>
      <button type="button" onClick={() => onAction('reset', user)} className="grid h-9 w-9 place-items-center rounded-lg border border-white/10 text-slate-300 hover:text-white" aria-label="Redefinir senha">
        <RotateCcw size={15} />
      </button>
      <button type="button" onClick={() => onAction('delete', user)} className="grid h-9 w-9 place-items-center rounded-lg border border-rose-400/20 text-rose-200 hover:bg-rose-500/10" aria-label="Excluir usuario">
        <Trash2 size={15} />
      </button>
    </div>
  );
}

export function AdminPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [overview, setOverview] = useState<AdminOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pendingAction, setPendingAction] = useState<PendingAction>(null);
  const [selectedUser, setSelectedUser] = useState<AdminUser | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const activePage = pageFromPath(location.pathname);

  useEffect(() => {
    setLoading(true);
    void getAdminOverview()
      .then((data) => {
        setOverview(data);
        setError(null);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : 'Falha ao carregar Administracao.'))
      .finally(() => setLoading(false));
  }, []);

  const users = overview?.usuarios ?? [];
  const billingEvents = metricValue(overview?.billing, 'Eventos Stripe');
  const auditRecords = (overview?.auditoria ?? []).reduce((total, item) => total + item.value, 0);
  const securityRecords = (overview?.seguranca ?? []).reduce((total, item) => total + item.value, 0);

  const selectedPermissionUser = useMemo(() => selectedUser ?? users[0] ?? null, [selectedUser, users]);

  function openAction(action: PendingAction, user: AdminUser | null = null) {
    setPendingAction(action);
    setSelectedUser(user);
    setActionError(null);
  }

  function submitUnavailable(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setActionError('Endpoint administrativo ainda nao disponivel no backend/app. Nenhuma alteracao foi salva.');
  }

  if (loading) {
    return <div className="grid min-h-[70vh] place-items-center"><Loader2 className="animate-spin text-violet-300" size={28} /></div>;
  }

  if (error) {
    return <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 p-5 text-rose-100">{error}</div>;
  }

  return (
    <div className="space-y-6 text-white">
      <header>
        <h1 className="font-display text-4xl">Administracao</h1>
        <p className="mt-2 text-sm text-slate-400">Gerencie usuarios, permissoes, billing e auditoria.</p>
      </header>

      <nav className="flex gap-2 overflow-x-auto rounded-2xl border border-white/10 bg-white/[0.03] p-2">
        {adminPages.map((page) => {
          const Icon = page.icon;
          const active = page.id === activePage;
          return (
            <button
              key={page.id}
              type="button"
              onClick={() => navigate(page.path)}
              className={[
                'inline-flex shrink-0 items-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold transition',
                active ? 'bg-violet-600 text-white shadow-[0_14px_30px_rgba(124,58,237,0.22)]' : 'text-slate-400 hover:bg-white/[0.05] hover:text-white',
              ].join(' ')}
            >
              <Icon size={16} />
              {page.label}
            </button>
          );
        })}
      </nav>

      {activePage === 'dashboard' ? (
        <>
          <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <PageCard icon={Users} title="Usuarios" value={users.length} detail="Usuarios reais retornados pelo backend" onClick={() => navigate('/app/admin/users')} />
            <PageCard icon={KeyRound} title="Permissoes" value={overview?.permissoes.length ?? 0} detail="Papeis existentes no backend atual" onClick={() => navigate('/app/admin/permissions')} />
            <PageCard icon={CreditCard} title="Billing" value={billingEvents} detail="Eventos Stripe registrados" onClick={() => navigate('/app/admin/billing')} />
            <PageCard icon={ScrollText} title="Auditoria" value={auditRecords} detail="Registros reais derivados" onClick={() => navigate('/app/admin/audit')} />
          </section>
          <Section title="Operacao administrativa" description="Resumo single-company sem telas paralelas de empresas ou papeis.">
            <div className="grid gap-3 md:grid-cols-3">
              <button type="button" onClick={() => navigate('/app/admin/users')} className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-left text-sm text-slate-200 hover:bg-white/[0.07]">Gerenciar usuarios</button>
              <button type="button" onClick={() => navigate('/app/admin/permissions')} className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-left text-sm text-slate-200 hover:bg-white/[0.07]">Definir permissoes</button>
              <button type="button" onClick={() => navigate('/app/admin/billing')} className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-left text-sm text-slate-200 hover:bg-white/[0.07]">Ver plano e cobranca</button>
            </div>
          </Section>
        </>
      ) : null}

      {activePage === 'users' ? (
        <Section title="Usuarios" description="Lista de usuarios da empresa atual. As acoes mutaveis exigem endpoint backend real.">
          <div className="mb-4 flex justify-end">
            <button type="button" onClick={() => openAction('invite')} className="inline-flex items-center gap-2 rounded-xl bg-violet-600 px-4 py-3 text-sm font-semibold text-white hover:bg-violet-500">
              <MailPlus size={16} /> Novo usuario
            </button>
          </div>
          <div className="overflow-x-auto rounded-xl border border-white/10">
            <table className="min-w-full text-sm">
              <thead className="bg-white/[0.03] text-left text-slate-400">
                <tr>
                  <th className="px-4 py-3">Nome</th>
                  <th className="px-4 py-3">Email</th>
                  <th className="px-4 py-3">Cargo</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Ultimo acesso</th>
                  <th className="px-4 py-3">Acoes</th>
                </tr>
              </thead>
              <tbody>
                {users.length === 0 ? (
                  <tr><td className="px-4 py-6 text-slate-400" colSpan={6}>Sem usuarios reais para listar.</td></tr>
                ) : users.map((user) => (
                  <tr key={user.id} className="border-t border-white/10">
                    <td className="px-4 py-4 font-semibold text-white">{user.name}</td>
                    <td className="px-4 py-4 text-slate-300">{user.email}</td>
                    <td className="px-4 py-4 capitalize text-slate-300">{user.role}</td>
                    <td className="px-4 py-4"><span className="rounded-full bg-emerald-500/15 px-2 py-1 text-xs text-emerald-300">Ativo</span></td>
                    <td className="px-4 py-4 text-slate-400">Nao informado pelo backend</td>
                    <td className="px-4 py-4"><UserActions user={user} onAction={openAction} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Section>
      ) : null}

      {activePage === 'permissions' ? (
        <Section title="Permissoes" description="Matriz por usuario e modulo, preparada para persistencia real quando o endpoint estiver disponivel.">
          <div className="grid gap-5 xl:grid-cols-[280px_minmax(0,1fr)]">
            <aside className="space-y-2">
              {users.length === 0 ? <EmptyState>Sem usuarios reais.</EmptyState> : users.map((user) => (
                <button
                  key={user.id}
                  type="button"
                  onClick={() => setSelectedUser(user)}
                  className={[
                    'w-full rounded-xl border px-4 py-3 text-left text-sm transition',
                    selectedPermissionUser?.id === user.id ? 'border-violet-300/35 bg-violet-600 text-white' : 'border-white/10 bg-white/[0.03] text-slate-300 hover:bg-white/[0.06]',
                  ].join(' ')}
                >
                  <span className="block font-semibold">{user.name}</span>
                  <span className="text-xs opacity-80">{user.email}</span>
                </button>
              ))}
            </aside>
            <div className="overflow-x-auto rounded-xl border border-white/10">
              <table className="min-w-[760px] w-full text-sm">
                <thead className="bg-white/[0.03] text-left text-slate-400">
                  <tr>
                    <th className="px-4 py-3">Modulo</th>
                    {permissionActions.map((action) => <th key={action} className="px-4 py-3">{action}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {permissionModules.map((module) => (
                    <tr key={module} className="border-t border-white/10">
                      <td className="px-4 py-3 font-semibold text-white">{module}</td>
                      {permissionActions.map((action) => (
                        <td key={`${module}-${action}`} className="px-4 py-3">
                          <input type="checkbox" defaultChecked={selectedPermissionUser?.role === 'owner' || action === 'Visualizar'} className="h-4 w-4 accent-violet-500" />
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          <form onSubmit={submitUnavailable} className="mt-5 flex flex-col items-start gap-3">
            {actionError ? <p className="rounded-xl border border-rose-400/25 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">{actionError}</p> : null}
            <button type="submit" className="rounded-xl bg-violet-600 px-5 py-3 text-sm font-semibold text-white hover:bg-violet-500">Salvar permissoes</button>
          </form>
        </Section>
      ) : null}

      {activePage === 'billing' ? (
        <Section title="Billing" description="Plano, consumo, faturas e eventos Stripe reais ficam na Administracao.">
          {(overview?.billing ?? []).length === 0 ? <EmptyState>Sem eventos reais de billing retornados.</EmptyState> : (
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {overview!.billing.map((item) => (
                <div key={item.label} className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                  <p className="text-sm text-slate-400">{item.label}</p>
                  <p className="mt-2 font-display text-3xl text-white">{item.value}</p>
                </div>
              ))}
            </div>
          )}
        </Section>
      ) : null}

      {activePage === 'security' ? (
        <Section title="Seguranca" description="Politicas, sessoes e alertas administrativos retornados pelo backend atual.">
          <div className="grid gap-3 md:grid-cols-2">
            {(overview?.seguranca ?? []).map((item) => (
              <div key={item.label} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.035] px-4 py-3">
                <span className="text-slate-300">{item.label}</span>
                <span className="font-semibold text-white">{item.value}</span>
              </div>
            ))}
            {securityRecords === 0 ? <EmptyState>Sem registros reais de seguranca.</EmptyState> : null}
          </div>
        </Section>
      ) : null}

      {activePage === 'audit' ? (
        <Section title="Auditoria" description="Eventos administrativos reais derivados do backend.">
          {(overview?.auditoria ?? []).length === 0 ? <EmptyState>Sem registros reais de auditoria.</EmptyState> : (
            <div className="space-y-3">
              {overview!.auditoria.map((item) => (
                <div key={item.label} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.035] px-4 py-3">
                  <span className="text-slate-300">{item.label}</span>
                  <span className="font-semibold text-white">{item.value} registros</span>
                </div>
              ))}
            </div>
          )}
        </Section>
      ) : null}

      {pendingAction ? (
        <div className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4 backdrop-blur">
          <form onSubmit={submitUnavailable} className="w-full max-w-2xl rounded-3xl border border-white/10 bg-slate-950 p-5 shadow-[0_30px_100px_rgba(0,0,0,0.55)]">
            <div className="flex items-start gap-3">
              <span className="grid h-11 w-11 shrink-0 place-items-center rounded-2xl bg-amber-500/15 text-amber-200">
                <AlertTriangle size={22} />
              </span>
              <div>
                <h2 className="font-display text-2xl text-white">{pendingAction === 'invite' ? 'Novo usuario' : `Acao: ${pendingAction}`}</h2>
                <p className="mt-1 text-sm text-slate-400">
                  {selectedUser ? `Usuario selecionado: ${selectedUser.name}. ` : ''}
                  O backend atual ainda nao expoe persistencia para esta acao administrativa.
                </p>
              </div>
            </div>
            {pendingAction === 'invite' ? (
              <div className="mt-5 grid gap-3 md:grid-cols-2">
                {['Nome', 'Email', 'Telefone', 'Cargo'].map((label) => (
                  <label key={label} className="text-sm text-slate-300">
                    {label}
                    <input className="mt-1 w-full rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-white outline-none focus:border-violet-300" />
                  </label>
                ))}
                <div className="md:col-span-2">
                  <p className="mb-2 text-sm text-slate-300">Permissoes iniciais</p>
                  <div className="grid gap-2 md:grid-cols-3">
                    {permissionModules.map((module) => (
                      <label key={module} className="flex items-center gap-2 rounded-xl border border-white/10 px-3 py-2 text-sm text-slate-300">
                        <input type="checkbox" className="accent-violet-500" /> {module}
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            ) : null}
            {actionError ? <p className="mt-4 rounded-xl border border-rose-400/25 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">{actionError}</p> : null}
            <div className="mt-5 flex justify-end gap-3">
              <button type="button" onClick={() => openAction(null)} className="rounded-xl border border-white/10 px-4 py-3 text-sm font-semibold text-slate-200">Cancelar</button>
              <button type="submit" className="rounded-xl bg-violet-600 px-4 py-3 text-sm font-semibold text-white">{pendingAction === 'invite' ? 'Enviar convite' : 'Confirmar acao'}</button>
            </div>
          </form>
        </div>
      ) : null}
    </div>
  );
}

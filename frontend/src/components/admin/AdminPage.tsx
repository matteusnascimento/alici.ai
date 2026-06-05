import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  CreditCard,
  KeyRound,
  Loader2,
  Lock,
  MailPlus,
  Pencil,
  RotateCcw,
  ScrollText,
  ShieldCheck,
  UserCheck,
  UserMinus,
  Users,
  type LucideIcon,
} from 'lucide-react';
import { type FormEvent, type ReactNode, useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

import { ApiError } from '../../services/api';
import {
  ADMIN_PERMISSION_MODULES,
  createEmptyPermissions,
  disableAdminUser,
  enableAdminUser,
  getAdminAudit,
  getAdminOverview,
  getAdminSecurity,
  getAdminUserPermissions,
  inviteAdminUser,
  listAdminUsers,
  resetAdminUserPassword,
  saveAdminUserPermissions,
  updateAdminUser,
  type AdminAuditResponse,
  type AdminMetric,
  type AdminOverview,
  type AdminPermissionLevel,
  type AdminPermissionMap,
  type AdminSecurityResponse,
  type AdminUser,
} from '../../services/admin.service';
import { AdminBillingPage } from './AdminBillingPage';

const adminPages = [
  { id: 'dashboard', label: 'Dashboard', path: '/app/admin', icon: ShieldCheck },
  { id: 'users', label: 'Usuarios', path: '/app/admin/users', icon: Users },
  { id: 'permissions', label: 'Permissoes', path: '/app/admin/permissions', icon: KeyRound },
  { id: 'billing', label: 'Billing', path: '/app/admin/billing', icon: CreditCard },
  { id: 'security', label: 'Seguranca', path: '/app/admin/security', icon: Lock },
  { id: 'audit', label: 'Auditoria', path: '/app/admin/audit', icon: ScrollText },
] as const;

type AdminPageId = (typeof adminPages)[number]['id'];
type PendingAction = 'edit' | null;

const permissionLevels: Array<{ value: AdminPermissionLevel; label: string }> = [
  { value: 'none', label: 'Nenhum' },
  { value: 'read', label: 'Leitura' },
  { value: 'write', label: 'Escrita' },
  { value: 'admin', label: 'Admin' },
];

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

function formatDate(value: string | null | undefined) {
  if (!value) return 'Nao informado';
  return new Date(value).toLocaleString('pt-BR');
}

function statusLabel(status: AdminUser['status']) {
  if (status === 'inactive') return 'Inativo';
  if (status === 'pending') return 'Pendente';
  return 'Ativo';
}

function statusClass(status: AdminUser['status']) {
  if (status === 'inactive') return 'bg-rose-500/15 text-rose-200';
  if (status === 'pending') return 'bg-amber-500/15 text-amber-200';
  return 'bg-emerald-500/15 text-emerald-300';
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

function Section({ title, description, children }: { title: string; description: string; children: ReactNode }) {
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

function Notice({ kind = 'info', children }: { kind?: 'info' | 'error' | 'success'; children: string }) {
  const classes = {
    info: 'border-cyan-400/25 bg-cyan-500/10 text-cyan-100',
    error: 'border-rose-400/25 bg-rose-500/10 text-rose-100',
    success: 'border-emerald-400/25 bg-emerald-500/10 text-emerald-100',
  }[kind];
  return <p className={`rounded-xl border px-4 py-3 text-sm ${classes}`}>{children}</p>;
}

function InviteUserForm({
  onCancel,
  onCreated,
}: {
  onCancel: () => void;
  onCreated: (response: { user: AdminUser; message: string; invite_token: string | null }) => void;
}) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [phone, setPhone] = useState('');
  const [permissions, setPermissions] = useState<AdminPermissionMap>(() => ({
    ...createEmptyPermissions(),
    revenue: 'read',
    chats: 'read',
    assistant: 'read',
  }));
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const response = await inviteAdminUser({
        name,
        email,
        job_title: jobTitle || undefined,
        phone: phone || undefined,
        permissions,
      });
      onCreated(response);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Falha ao criar convite.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={submit} className="space-y-5">
      <div className="grid gap-4 md:grid-cols-2">
        <label className="text-sm text-slate-300">
          Nome
          <input required value={name} onChange={(event) => setName(event.target.value)} className="mt-1 w-full rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-white outline-none focus:border-violet-300" />
        </label>
        <label className="text-sm text-slate-300">
          Email
          <input required type="email" value={email} onChange={(event) => setEmail(event.target.value)} className="mt-1 w-full rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-white outline-none focus:border-violet-300" />
        </label>
        <label className="text-sm text-slate-300">
          Cargo
          <input value={jobTitle} onChange={(event) => setJobTitle(event.target.value)} className="mt-1 w-full rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-white outline-none focus:border-violet-300" />
        </label>
        <label className="text-sm text-slate-300">
          Telefone
          <input value={phone} onChange={(event) => setPhone(event.target.value)} className="mt-1 w-full rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-white outline-none focus:border-violet-300" />
        </label>
      </div>

      <div className="overflow-x-auto rounded-xl border border-white/10">
        <table className="min-w-[720px] w-full text-sm">
          <thead className="bg-white/[0.03] text-left text-slate-400">
            <tr>
              <th className="px-4 py-3">Modulo</th>
              <th className="px-4 py-3">Nivel inicial</th>
            </tr>
          </thead>
          <tbody>
            {ADMIN_PERMISSION_MODULES.map((module) => (
              <tr key={module.key} className="border-t border-white/10">
                <td className="px-4 py-3 font-semibold text-white">{module.label}</td>
                <td className="px-4 py-3">
                  <select
                    value={permissions[module.key]}
                    onChange={(event) => setPermissions((current) => ({ ...current, [module.key]: event.target.value as AdminPermissionLevel }))}
                    className="w-full rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-white outline-none focus:border-violet-300"
                  >
                    {permissionLevels.map((level) => <option key={level.value} value={level.value}>{level.label}</option>)}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {error ? <Notice kind="error">{error}</Notice> : null}
      <div className="flex flex-wrap justify-end gap-3">
        <button type="button" onClick={onCancel} className="rounded-xl border border-white/10 px-4 py-3 text-sm font-semibold text-slate-200">Cancelar</button>
        <button type="submit" disabled={saving} className="inline-flex items-center gap-2 rounded-xl bg-violet-600 px-4 py-3 text-sm font-semibold text-white disabled:opacity-60">
          {saving ? <Loader2 className="animate-spin" size={16} /> : <MailPlus size={16} />}
          Enviar convite
        </button>
      </div>
    </form>
  );
}

function EditUserDialog({
  user,
  onCancel,
  onSaved,
}: {
  user: AdminUser;
  onCancel: () => void;
  onSaved: (user: AdminUser) => void;
}) {
  const [name, setName] = useState(user.name);
  const [email, setEmail] = useState(user.email);
  const [jobTitle, setJobTitle] = useState(user.job_title ?? '');
  const [phone, setPhone] = useState(user.phone ?? '');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const updated = await updateAdminUser(user.id, {
        name,
        email,
        job_title: jobTitle,
        phone,
      });
      onSaved(updated);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Falha ao atualizar usuario.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4 backdrop-blur">
      <form onSubmit={submit} className="w-full max-w-xl rounded-3xl border border-white/10 bg-slate-950 p-5 shadow-[0_30px_100px_rgba(0,0,0,0.55)]">
        <h2 className="font-display text-2xl text-white">Editar usuario</h2>
        <p className="mt-1 text-sm text-slate-400">Atualize dados administrativos do colaborador.</p>
        <div className="mt-5 grid gap-3 md:grid-cols-2">
          <label className="text-sm text-slate-300">
            Nome
            <input required value={name} onChange={(event) => setName(event.target.value)} className="mt-1 w-full rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-white outline-none focus:border-violet-300" />
          </label>
          <label className="text-sm text-slate-300">
            Email
            <input required type="email" value={email} onChange={(event) => setEmail(event.target.value)} className="mt-1 w-full rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-white outline-none focus:border-violet-300" />
          </label>
          <label className="text-sm text-slate-300">
            Cargo
            <input value={jobTitle} onChange={(event) => setJobTitle(event.target.value)} className="mt-1 w-full rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-white outline-none focus:border-violet-300" />
          </label>
          <label className="text-sm text-slate-300">
            Telefone
            <input value={phone} onChange={(event) => setPhone(event.target.value)} className="mt-1 w-full rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-white outline-none focus:border-violet-300" />
          </label>
        </div>
        {error ? <div className="mt-4"><Notice kind="error">{error}</Notice></div> : null}
        <div className="mt-5 flex justify-end gap-3">
          <button type="button" onClick={onCancel} className="rounded-xl border border-white/10 px-4 py-3 text-sm font-semibold text-slate-200">Cancelar</button>
          <button type="submit" disabled={saving} className="rounded-xl bg-violet-600 px-4 py-3 text-sm font-semibold text-white disabled:opacity-60">
            {saving ? 'Salvando...' : 'Salvar'}
          </button>
        </div>
      </form>
    </div>
  );
}

export function AdminPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [overview, setOverview] = useState<AdminOverview | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [security, setSecurity] = useState<AdminSecurityResponse | null>(null);
  const [audit, setAudit] = useState<AdminAuditResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [pendingAction, setPendingAction] = useState<PendingAction>(null);
  const [selectedUser, setSelectedUser] = useState<AdminUser | null>(null);
  const [permissionDraft, setPermissionDraft] = useState<AdminPermissionMap>(() => createEmptyPermissions());
  const [savingPermissions, setSavingPermissions] = useState(false);
  const activePage = pageFromPath(location.pathname);
  const isInviteRoute = location.pathname === '/app/admin/users/new';

  useEffect(() => {
    void loadAdminData();
  }, []);

  useEffect(() => {
    const user = selectedUser ?? users[0] ?? null;
    if (!user) return;
    setSelectedUser(user);
    setPermissionDraft({ ...createEmptyPermissions(), ...user.permissions });
    void getAdminUserPermissions(user.id)
      .then((data) => setPermissionDraft({ ...createEmptyPermissions(), ...data.permissions }))
      .catch(() => undefined);
  }, [selectedUser?.id, users]);

  async function loadAdminData() {
    setLoading(true);
    try {
      const [overviewData, usersData, securityData, auditData] = await Promise.all([
        getAdminOverview(),
        listAdminUsers(),
        getAdminSecurity(),
        getAdminAudit(),
      ]);
      setOverview(overviewData);
      setUsers(usersData);
      setSecurity(securityData);
      setAudit(auditData);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Falha ao carregar Administracao.');
    } finally {
      setLoading(false);
    }
  }

  function replaceUser(updated: AdminUser) {
    setUsers((current) => current.map((item) => (item.id === updated.id ? updated : item)));
    setOverview((current) => current ? { ...current, usuarios: current.usuarios.map((item) => (item.id === updated.id ? updated : item)) } : current);
    if (selectedUser?.id === updated.id) setSelectedUser(updated);
  }

  async function handleDisable(user: AdminUser) {
    setMessage(null);
    try {
      const response = user.status === 'inactive' ? await enableAdminUser(user.id) : await disableAdminUser(user.id);
      if (response.user) replaceUser(response.user);
      setMessage(response.message);
      void refreshSecurityAndAudit();
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : 'Acao nao concluida.');
    }
  }

  async function handleReset(user: AdminUser) {
    setMessage(null);
    try {
      const response = await resetAdminUserPassword(user.id);
      setMessage(response.reset_token ? `${response.message} Token dev: ${response.reset_token}` : response.message);
      void refreshSecurityAndAudit();
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : 'Redefinicao nao concluida.');
    }
  }

  async function refreshSecurityAndAudit() {
    const [securityData, auditData] = await Promise.all([getAdminSecurity(), getAdminAudit()]);
    setSecurity(securityData);
    setAudit(auditData);
  }

  async function savePermissions() {
    if (!selectedUser) return;
    setSavingPermissions(true);
    setMessage(null);
    try {
      const response = await saveAdminUserPermissions(selectedUser.id, permissionDraft);
      const updated = { ...selectedUser, permissions: response.permissions };
      replaceUser(updated);
      setMessage('Permissoes salvas corretamente.');
      void refreshSecurityAndAudit();
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : 'Falha ao salvar permissoes.');
    } finally {
      setSavingPermissions(false);
    }
  }

  const billingEvents = metricValue(overview?.billing, 'Eventos Stripe');
  const auditRecords = metricValue(overview?.auditoria, 'Eventos registrados');
  const securityRecords = metricValue(overview?.seguranca, 'Sessoes ativas');

  const selectedPermissionUser = useMemo(() => selectedUser ?? users[0] ?? null, [selectedUser, users]);

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
        <p className="mt-2 text-sm text-slate-400">Gerencie usuarios, convites, permissoes, seguranca, auditoria e billing administrativo.</p>
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

      {message ? <Notice kind={message.toLowerCase().includes('falha') || message.toLowerCase().includes('negado') ? 'error' : 'info'}>{message}</Notice> : null}

      {activePage === 'dashboard' ? (
        <>
          <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <PageCard icon={Users} title="Usuarios" value={users.length} detail="Usuarios reais da administracao" onClick={() => navigate('/app/admin/users')} />
            <PageCard icon={KeyRound} title="Permissoes" value={overview?.permissoes.length ?? ADMIN_PERMISSION_MODULES.length} detail="Modulos com controle por nivel" onClick={() => navigate('/app/admin/permissions')} />
            <PageCard icon={CreditCard} title="Billing" value={billingEvents} detail="Eventos Stripe registrados" onClick={() => navigate('/app/admin/billing')} />
            <PageCard icon={ScrollText} title="Auditoria" value={auditRecords} detail="Eventos administrativos persistidos" onClick={() => navigate('/app/admin/audit')} />
          </section>
          <Section title="Operacao administrativa" description="Acoes principais para operar uma pousada real com usuarios e permissoes.">
            <div className="grid gap-3 md:grid-cols-3">
              <button type="button" onClick={() => navigate('/app/admin/users/new')} className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-left text-sm text-slate-200 hover:bg-white/[0.07]">Convidar usuario</button>
              <button type="button" onClick={() => navigate('/app/admin/permissions')} className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-left text-sm text-slate-200 hover:bg-white/[0.07]">Definir permissoes</button>
              <button type="button" onClick={() => navigate('/app/admin/security')} className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-left text-sm text-slate-200 hover:bg-white/[0.07]">Revisar seguranca</button>
            </div>
          </Section>
        </>
      ) : null}

      {activePage === 'users' ? (
        <Section
          title={isInviteRoute ? 'Convidar usuario' : 'Usuarios'}
          description={isInviteRoute ? 'Crie o colaborador e defina permissoes iniciais.' : 'Lista profissional de usuarios, status, ultimo acesso e acoes operacionais.'}
        >
          {isInviteRoute ? (
            <InviteUserForm
              onCancel={() => navigate('/app/admin/users')}
              onCreated={(response) => {
                setUsers((current) => [response.user, ...current]);
                setMessage(response.invite_token ? `${response.message} Token dev: ${response.invite_token}` : response.message);
                navigate('/app/admin/users');
                void refreshSecurityAndAudit();
              }}
            />
          ) : (
            <>
              <div className="mb-4 flex justify-end">
                <button type="button" onClick={() => navigate('/app/admin/users/new')} className="inline-flex items-center gap-2 rounded-xl bg-violet-600 px-4 py-3 text-sm font-semibold text-white hover:bg-violet-500">
                  <MailPlus size={16} /> Novo usuario
                </button>
              </div>
              <div className="overflow-x-auto rounded-xl border border-white/10">
                <table className="min-w-[920px] w-full text-sm">
                  <thead className="bg-white/[0.03] text-left text-slate-400">
                    <tr>
                      <th className="px-4 py-3">Nome</th>
                      <th className="px-4 py-3">Email</th>
                      <th className="px-4 py-3">Cargo</th>
                      <th className="px-4 py-3">Status</th>
                      <th className="px-4 py-3">Ultimo acesso</th>
                      <th className="px-4 py-3">Permissoes</th>
                      <th className="px-4 py-3">Acoes</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.length === 0 ? (
                      <tr><td className="px-4 py-6 text-slate-400" colSpan={7}>Nenhum usuário encontrado.</td></tr>
                    ) : users.map((user) => (
                      <tr key={user.id} className="border-t border-white/10">
                        <td className="px-4 py-4 font-semibold text-white">{user.name}</td>
                        <td className="px-4 py-4 text-slate-300">{user.email}</td>
                        <td className="px-4 py-4 text-slate-300">{user.job_title || user.role}</td>
                        <td className="px-4 py-4"><span className={`rounded-full px-2 py-1 text-xs ${statusClass(user.status)}`}>{statusLabel(user.status)}</span></td>
                        <td className="px-4 py-4 text-slate-400">{formatDate(user.last_login_at)}</td>
                        <td className="px-4 py-4 text-slate-300">
                          {Object.values(user.permissions ?? {}).filter((level) => level !== 'none').length || 0} modulos
                        </td>
                        <td className="px-4 py-4">
                          <div className="flex flex-wrap gap-2">
                            <button type="button" onClick={() => { setSelectedUser(user); setPendingAction('edit'); }} className="grid h-9 w-9 place-items-center rounded-lg border border-white/10 text-slate-300 hover:text-white" aria-label="Editar usuario">
                              <Pencil size={15} />
                            </button>
                            <button type="button" onClick={() => void handleDisable(user)} className="grid h-9 w-9 place-items-center rounded-lg border border-white/10 text-slate-300 hover:text-white" aria-label={user.status === 'inactive' ? 'Reativar usuario' : 'Desativar usuario'}>
                              {user.status === 'inactive' ? <UserCheck size={15} /> : <UserMinus size={15} />}
                            </button>
                            <button type="button" onClick={() => void handleReset(user)} className="grid h-9 w-9 place-items-center rounded-lg border border-white/10 text-slate-300 hover:text-white" aria-label="Redefinir senha">
                              <RotateCcw size={15} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </Section>
      ) : null}

      {activePage === 'permissions' ? (
        <Section title="Permissoes" description="Controle por usuario e modulo: none, read, write ou admin.">
          <div className="grid gap-5 xl:grid-cols-[280px_minmax(0,1fr)]">
            <aside className="space-y-2">
              {users.length === 0 ? <EmptyState>Nenhum usuário encontrado.</EmptyState> : users.map((user) => (
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
            <div>
              {!selectedPermissionUser ? <EmptyState>Nenhum usuário encontrado.</EmptyState> : (
                <div className="overflow-x-auto rounded-xl border border-white/10">
                  <table className="min-w-[760px] w-full text-sm">
                    <thead className="bg-white/[0.03] text-left text-slate-400">
                      <tr>
                        <th className="px-4 py-3">Modulo</th>
                        <th className="px-4 py-3">Nivel</th>
                      </tr>
                    </thead>
                    <tbody>
                      {ADMIN_PERMISSION_MODULES.map((module) => (
                        <tr key={module.key} className="border-t border-white/10">
                          <td className="px-4 py-3 font-semibold text-white">{module.label}</td>
                          <td className="px-4 py-3">
                            <select
                              value={permissionDraft[module.key] ?? 'none'}
                              onChange={(event) => setPermissionDraft((current) => ({ ...current, [module.key]: event.target.value as AdminPermissionLevel }))}
                              className="w-full max-w-xs rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-white outline-none focus:border-violet-300"
                            >
                              {permissionLevels.map((level) => <option key={level.value} value={level.value}>{level.label}</option>)}
                            </select>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
              <div className="mt-5 flex justify-end">
                <button type="button" onClick={() => void savePermissions()} disabled={!selectedPermissionUser || savingPermissions} className="rounded-xl bg-violet-600 px-5 py-3 text-sm font-semibold text-white disabled:opacity-60">
                  {savingPermissions ? 'Salvando...' : 'Salvar permissoes'}
                </button>
              </div>
            </div>
          </div>
        </Section>
      ) : null}

      {activePage === 'billing' ? <AdminBillingPage /> : null}

      {activePage === 'security' ? (
        <Section title="Seguranca" description="Logins, sessoes abertas e tokens revogados sem dados simulados.">
          <div className="mb-4 grid gap-4 md:grid-cols-3">
            <PageCard icon={Activity} title="Sessoes ativas" value={securityRecords} detail="Refresh tokens ativos" onClick={() => undefined} />
            <PageCard icon={CheckCircle2} title="Ultimos logins" value={security?.last_logins.length ?? 0} detail="Usuarios com acesso recente" onClick={() => undefined} />
            <PageCard icon={AlertTriangle} title="Tokens revogados" value={security?.revoked_tokens.length ?? 0} detail="Sessoes encerradas ou bloqueadas" onClick={() => undefined} />
          </div>
          <div className="grid gap-4 xl:grid-cols-2">
            {[
              { title: 'Ultimos logins', items: security?.last_logins ?? [] },
              { title: 'Dispositivos ativos', items: security?.active_sessions ?? [] },
              { title: 'Sessoes abertas', items: security?.open_sessions ?? [] },
              { title: 'Tokens revogados', items: security?.revoked_tokens ?? [] },
              { title: 'Tentativas de login', items: security?.login_attempts ?? [] },
            ].map((block) => (
              <div key={block.title} className="rounded-2xl border border-white/10 bg-white/[0.025] p-4">
                <h3 className="font-display text-xl text-white">{block.title}</h3>
                {block.items.length === 0 ? <div className="mt-3"><EmptyState>Nenhum registro disponível.</EmptyState></div> : (
                  <div className="mt-3 space-y-2">
                    {block.items.map((item) => (
                      <div key={`${block.title}-${item.id}`} className="rounded-xl border border-white/10 bg-white/[0.035] px-4 py-3">
                        <div className="flex items-center justify-between gap-3">
                          <p className="font-semibold text-white">{item.user_name || item.user_email || item.event_type}</p>
                          <span className="rounded-full bg-white/[0.06] px-2 py-1 text-xs text-slate-300">{item.status}</span>
                        </div>
                        <p className="mt-1 text-xs text-slate-500">{formatDate(item.created_at)} {item.expires_at ? `-> expira ${formatDate(item.expires_at)}` : ''}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </Section>
      ) : null}

      {activePage === 'audit' ? (
        <Section title="Auditoria" description="Eventos administrativos persistidos no backend.">
          {(audit?.events ?? []).length === 0 ? <EmptyState>Nenhum evento registrado.</EmptyState> : (
            <div className="overflow-x-auto rounded-xl border border-white/10">
              <table className="min-w-[860px] w-full text-sm">
                <thead className="bg-white/[0.03] text-left text-slate-400">
                  <tr>
                    <th className="px-4 py-3">Data</th>
                    <th className="px-4 py-3">Usuario</th>
                    <th className="px-4 py-3">Acao</th>
                    <th className="px-4 py-3">Origem</th>
                    <th className="px-4 py-3">Detalhes</th>
                  </tr>
                </thead>
                <tbody>
                  {audit!.events.map((event) => (
                    <tr key={event.id} className="border-t border-white/10">
                      <td className="px-4 py-3 text-slate-400">{formatDate(event.data)}</td>
                      <td className="px-4 py-3 text-white">{event.usuario || 'Sistema'}</td>
                      <td className="px-4 py-3 font-semibold text-white">{event.acao}</td>
                      <td className="px-4 py-3 text-slate-300">{event.origem}</td>
                      <td className="px-4 py-3 text-slate-400">{event.detalhes ? JSON.stringify(event.detalhes) : 'Sem detalhes'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Section>
      ) : null}

      {pendingAction === 'edit' && selectedUser ? (
        <EditUserDialog
          user={selectedUser}
          onCancel={() => setPendingAction(null)}
          onSaved={(updated) => {
            replaceUser(updated);
            setPendingAction(null);
            setMessage('Usuario atualizado.');
            void refreshSecurityAndAudit();
          }}
        />
      ) : null}
    </div>
  );
}

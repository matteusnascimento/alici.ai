import {
  Bell,
  Building2,
  ChevronLeft,
  ChevronRight,
  CreditCard,
  Eye,
  HelpCircle,
  KeyRound,
  Loader2,
  MoreHorizontal,
  Pencil,
  Plus,
  ScrollText,
  Search,
  Settings,
  ShieldCheck,
  Users,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { type FormEvent, useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom';

import { ApiError } from '../../services/api';
import { createAdminCompany, getAdminOverview, type AdminMetric, type AdminOverview } from '../../services/admin.service';

const adminTabs = ['Dashboard', 'Empresas', 'Usuarios', 'Papeis', 'Permissoes', 'Billing', 'Seguranca', 'Auditoria'] as const;
type AdminTab = (typeof adminTabs)[number];
const companyModules = ['Revenue', 'Chats', 'AXI Assistant', 'Marketing', 'Studio', 'Integrations'];

const tabToPath: Record<AdminTab, string> = {
  Dashboard: '/app/admin',
  Empresas: '/app/admin/companies',
  Usuarios: '/app/admin/users',
  Papeis: '/app/admin/roles',
  Permissoes: '/app/admin/permissions',
  Billing: '/app/admin/billing',
  Seguranca: '/app/admin/security',
  Auditoria: '/app/admin/audit',
};

function tabFromPath(pathname: string): AdminTab {
  if (pathname.startsWith('/app/admin/companies')) return 'Empresas';
  if (pathname.startsWith('/app/admin/users')) return 'Usuarios';
  if (pathname.startsWith('/app/admin/roles')) return 'Papeis';
  if (pathname.startsWith('/app/admin/permissions')) return 'Permissoes';
  if (pathname.startsWith('/app/admin/billing')) return 'Billing';
  if (pathname.startsWith('/app/admin/security')) return 'Seguranca';
  if (pathname.startsWith('/app/admin/audit')) return 'Auditoria';
  return 'Dashboard';
}

function metricValue(items: AdminMetric[] | undefined, label: string) {
  return items?.find((item) => item.label === label)?.value ?? 0;
}

function formatPlan(plan: string | null | undefined) {
  if (!plan) return 'Sem plano';
  return plan.charAt(0).toUpperCase() + plan.slice(1);
}

function KpiCard({
  icon: Icon,
  title,
  value,
  detail,
  action,
  tone,
  onAction,
}: {
  icon: LucideIcon;
  title: string;
  value: string | number;
  detail: string;
  action: string;
  tone: string;
  onAction: () => void;
}) {
  return (
    <article className="min-h-[154px] rounded-2xl border border-white/10 bg-[linear-gradient(145deg,rgba(15,23,42,0.92),rgba(2,6,23,0.74))] p-5 shadow-[0_22px_70px_rgba(0,0,0,0.30)]">
      <div className="flex items-start gap-4">
        <span className={`grid h-14 w-14 shrink-0 place-items-center rounded-2xl ${tone}`}>
          <Icon size={27} />
        </span>
        <div className="min-w-0">
          <p className="text-sm text-slate-300">{title}</p>
          <p className="mt-2 font-display text-3xl text-white">{value}</p>
          <p className="mt-1 text-sm text-emerald-300">{detail}</p>
        </div>
      </div>
      <button type="button" onClick={onAction} className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-violet-300">
        {action} <ChevronRight size={15} />
      </button>
    </article>
  );
}

function EmptyState({ children, className = '' }: { children: string; className?: string }) {
  return (
    <div className={`grid min-h-28 place-items-center rounded-2xl border border-dashed border-white/15 bg-white/[0.03] p-5 text-center text-sm text-slate-400 ${className}`}>
      {children}
    </div>
  );
}

function ModuleCard({ icon: Icon, title, description, tone, onAction }: { icon: LucideIcon; title: string; description: string; tone: string; onAction: () => void }) {
  return (
    <article className="rounded-2xl border border-white/10 bg-[linear-gradient(145deg,rgba(15,23,42,0.82),rgba(2,6,23,0.64))] p-5">
      <div className="flex items-center gap-4">
        <span className={`grid h-14 w-14 place-items-center rounded-full ${tone}`}>
          <Icon size={24} />
        </span>
        <div>
          <p className="font-semibold text-white">{title}</p>
          <p className="mt-1 text-sm text-slate-400">{description}</p>
          <button type="button" onClick={onAction} className="mt-3 text-sm font-semibold text-violet-300">Gerenciar {'->'}</button>
        </div>
      </div>
    </article>
  );
}

export function AdminPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const [overview, setOverview] = useState<AdminOverview | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [savingCompany, setSavingCompany] = useState(false);
  const [newCompany, setNewCompany] = useState({
    nome: '',
    razao_social: '',
    cnpj: '',
    email: '',
    telefone: '',
    plano: 'pro' as 'basic' | 'pro' | 'enterprise',
    modules: ['Revenue', 'Chats', 'AXI Assistant', 'Marketing', 'Studio', 'Integrations'],
  });
  const [activeTab, setActiveTab] = useState<AdminTab>(() => tabFromPath(location.pathname));

  useEffect(() => {
    setActiveTab(tabFromPath(location.pathname));
  }, [location.pathname]);

  function goToAdmin(tab: AdminTab, action?: string, extra?: Record<string, string>) {
    const params = new URLSearchParams();
    if (action) params.set('action', action);
    Object.entries(extra ?? {}).forEach(([key, value]) => params.set(key, value));
    navigate(`${tabToPath[tab]}${params.toString() ? `?${params}` : ''}`);
    setActiveTab(tab);
  }

  function openCompany(companyName: string) {
    navigate(`/app/admin/companies/${encodeURIComponent(companyName)}`);
  }

  function loadOverview() {
    setLoading(true);
    return getAdminOverview()
      .then((data) => {
        setOverview(data);
        setError(null);
      })
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : 'Falha ao carregar Administracao');
      })
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    void loadOverview();
  }, []);

  async function handleCreateCompany(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSavingCompany(true);
    setActionError(null);
    try {
      await createAdminCompany(newCompany);
      await loadOverview();
      navigate('/app/admin/companies');
    } catch (err) {
      setActionError(err instanceof ApiError ? err.message : 'Empresa nao foi criada.');
    } finally {
      setSavingCompany(false);
    }
  }

  function toggleCompanyModule(module: string) {
    setNewCompany((current) => ({
      ...current,
      modules: current.modules.includes(module)
        ? current.modules.filter((item) => item !== module)
        : [...current.modules, module],
    }));
  }

  const cards = useMemo(() => {
    const empresas = overview?.empresas.length ?? 0;
    const usuarios = overview?.usuarios.length ?? 0;
    const permissoes = overview?.permissoes.length ?? 0;
    const billingEvents = metricValue(overview?.billing, 'Eventos Stripe');
    const auditUsers = metricValue(overview?.auditoria, 'Usuarios cadastrados');
    return [
      { title: 'Empresas ativas', value: empresas, detail: empresas ? `${empresas} reais` : 'Sem empresas reais', action: 'Ver todas', icon: Building2, tone: 'bg-violet-500/20 text-violet-200', tab: 'Empresas' as const },
      { title: 'Usuarios ativos', value: usuarios, detail: usuarios ? `${usuarios} reais` : 'Sem usuarios reais', action: 'Ver todos', icon: Users, tone: 'bg-blue-500/20 text-blue-200', tab: 'Usuarios' as const },
      { title: 'Papeis criados', value: permissoes, detail: 'Configurados no backend', action: 'Ver todos', icon: ShieldCheck, tone: 'bg-emerald-500/20 text-emerald-200', tab: 'Papeis' as const },
      { title: 'Receita mensal', value: billingEvents, detail: 'Eventos Stripe reais', action: 'Ver detalhes', icon: CreditCard, tone: 'bg-amber-500/20 text-amber-200', tab: 'Billing' as const },
      { title: 'Logs de auditoria', value: auditUsers, detail: 'Registros derivados', action: 'Ver auditoria', icon: ScrollText, tone: 'bg-purple-500/20 text-purple-200', tab: 'Auditoria' as const },
    ];
  }, [overview]);

  const recentUsers = overview?.usuarios.slice(0, 4) ?? [];
  const roleRows = (overview?.permissoes ?? []).map((role) => ({
    role,
    percent: role === 'owner' ? 100 : 0,
    users: overview?.usuarios.filter((user) => user.role === role).length ?? 0,
  }));
  const selectedAction = searchParams.get('action');
  const selectedCompany = location.pathname.startsWith('/app/admin/companies/')
    ? decodeURIComponent(location.pathname.split('/').pop() ?? '')
    : searchParams.get('empresa');

  if (loading) {
    return <div className="grid min-h-[70vh] place-items-center"><Loader2 className="animate-spin text-violet-300" size={28} /></div>;
  }

  if (error) {
    return <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 p-5 text-rose-100">{error}</div>;
  }

  return (
    <div className="min-h-[calc(100vh-2rem)] rounded-[1.75rem] border border-white/10 bg-[radial-gradient(circle_at_10%_0%,rgba(124,58,237,0.16),transparent_30%),#050914] p-5 text-white shadow-[0_28px_100px_rgba(0,0,0,0.48)] md:p-7">
      <header className="flex flex-col gap-5 xl:flex-row xl:items-center xl:justify-between">
        <div className="flex items-center gap-4">
          <span className="grid h-16 w-16 place-items-center rounded-2xl bg-violet-700 text-white shadow-[0_18px_45px_rgba(124,58,237,0.35)]">
            <Settings size={31} />
          </span>
          <div>
            <h1 className="font-display text-4xl">Administracao</h1>
            <p className="mt-1 max-w-2xl text-sm text-slate-300">
              Gerencie empresas, usuarios, permissoes, planos e seguranca da plataforma.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button type="button" onClick={() => navigate('/app/account/notifications')} className="relative grid h-11 w-11 place-items-center rounded-full border border-white/10 text-slate-200" aria-label="Notificacoes">
            <Bell size={19} />
          </button>
          <button type="button" onClick={() => navigate('/app/account/help')} className="inline-flex items-center gap-2 rounded-full border border-white/10 px-4 py-2 text-sm text-slate-200">
            <HelpCircle size={17} /> Ajuda
          </button>
        </div>
      </header>

      <nav className="mt-6 flex gap-2 overflow-x-auto">
        {adminTabs.map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => goToAdmin(tab)}
            className={[
              'shrink-0 rounded-xl px-4 py-2 text-sm font-semibold transition',
              activeTab === tab ? 'bg-violet-600 text-white shadow-[0_12px_28px_rgba(124,58,237,0.25)]' : 'text-slate-400 hover:bg-white/[0.04] hover:text-white',
            ].join(' ')}
          >
            {tab}
          </button>
        ))}
      </nav>

      {selectedAction === 'new' && activeTab === 'Empresas' ? (
        <form onSubmit={handleCreateCompany} className="mt-5 grid gap-4 rounded-2xl border border-violet-300/25 bg-violet-500/10 p-5">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-violet-200">Nova empresa</p>
            <h2 className="mt-1 font-display text-2xl text-white">Criar empresa no AXI</h2>
            <p className="mt-1 text-sm text-violet-100/80">O cadastro cria um registro real vinculado a um usuario proprietario inicial.</p>
          </div>

          <div className="grid gap-4 xl:grid-cols-4">
            <section className="rounded-2xl border border-white/10 bg-slate-950/55 p-4">
              <p className="font-semibold text-white">1. Dados da empresa</p>
              <div className="mt-3 grid gap-3">
                <label className="text-sm text-slate-300">
                  Nome
                  <input required value={newCompany.nome} onChange={(event) => setNewCompany((current) => ({ ...current, nome: event.target.value }))} className="mt-1 w-full rounded-xl border border-white/10 bg-slate-950 px-3 py-2 text-white outline-none focus:border-violet-300" />
                </label>
                <label className="text-sm text-slate-300">
                  Razao social
                  <input value={newCompany.razao_social} onChange={(event) => setNewCompany((current) => ({ ...current, razao_social: event.target.value }))} className="mt-1 w-full rounded-xl border border-white/10 bg-slate-950 px-3 py-2 text-white outline-none focus:border-violet-300" />
                </label>
                <label className="text-sm text-slate-300">
                  CNPJ
                  <input value={newCompany.cnpj} onChange={(event) => setNewCompany((current) => ({ ...current, cnpj: event.target.value }))} className="mt-1 w-full rounded-xl border border-white/10 bg-slate-950 px-3 py-2 text-white outline-none focus:border-violet-300" />
                </label>
                <label className="text-sm text-slate-300">
                  Email institucional
                  <input required type="email" value={newCompany.email} onChange={(event) => setNewCompany((current) => ({ ...current, email: event.target.value }))} className="mt-1 w-full rounded-xl border border-white/10 bg-slate-950 px-3 py-2 text-white outline-none focus:border-violet-300" />
                </label>
                <label className="text-sm text-slate-300">
                  Telefone
                  <input value={newCompany.telefone} onChange={(event) => setNewCompany((current) => ({ ...current, telefone: event.target.value }))} className="mt-1 w-full rounded-xl border border-white/10 bg-slate-950 px-3 py-2 text-white outline-none focus:border-violet-300" />
                </label>
              </div>
            </section>

            <section className="rounded-2xl border border-white/10 bg-slate-950/55 p-4">
              <p className="font-semibold text-white">2. Plano</p>
              <div className="mt-3 grid gap-2">
                {(['basic', 'pro', 'enterprise'] as const).map((plan) => (
                  <label key={plan} className="flex items-center gap-3 rounded-xl border border-white/10 px-3 py-3 text-sm capitalize text-slate-200">
                    <input type="radio" name="plano" checked={newCompany.plano === plan} onChange={() => setNewCompany((current) => ({ ...current, plano: plan }))} />
                    {plan}
                  </label>
                ))}
              </div>
            </section>

            <section className="rounded-2xl border border-white/10 bg-slate-950/55 p-4">
              <p className="font-semibold text-white">3. Modulos habilitados</p>
              <div className="mt-3 grid gap-2">
                {companyModules.map((module) => (
                  <label key={module} className="flex items-center gap-3 rounded-xl border border-white/10 px-3 py-2 text-sm text-slate-200">
                    <input type="checkbox" checked={newCompany.modules.includes(module)} onChange={() => toggleCompanyModule(module)} />
                    {module}
                  </label>
                ))}
              </div>
            </section>

            <section className="rounded-2xl border border-white/10 bg-slate-950/55 p-4">
              <p className="font-semibold text-white">4. Confirmacao</p>
              <div className="mt-3 space-y-2 text-sm text-slate-300">
                <p>Empresa: <span className="text-white">{newCompany.nome || '-'}</span></p>
                <p>Plano: <span className="capitalize text-white">{newCompany.plano}</span></p>
                <p>Modulos: <span className="text-white">{newCompany.modules.length}</span></p>
              </div>
              {actionError ? <p className="mt-3 rounded-xl border border-rose-400/30 bg-rose-500/10 p-3 text-sm text-rose-100">{actionError}</p> : null}
              <div className="mt-5 flex gap-2">
                <button type="button" onClick={() => navigate('/app/admin/companies')} className="flex-1 rounded-xl border border-white/10 px-4 py-3 text-sm font-semibold text-slate-200">Cancelar</button>
                <button type="submit" disabled={savingCompany} className="flex-1 rounded-xl bg-violet-600 px-4 py-3 text-sm font-semibold text-white disabled:opacity-60">
                  {savingCompany ? 'Salvando...' : 'Salvar empresa'}
                </button>
              </div>
            </section>
          </div>
        </form>
      ) : selectedAction ? (
        <section className="mt-5 rounded-2xl border border-violet-300/25 bg-violet-500/10 p-4 text-sm text-violet-100">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="font-semibold">Fluxo selecionado: {activeTab}</p>
              <p className="mt-1 text-violet-100/80">
                Acao: {selectedAction}{selectedCompany ? ` - ${selectedCompany}` : ''}. O proximo passo usa a area real deste modulo, sem criar sucesso automatico.
              </p>
            </div>
            <button type="button" onClick={() => goToAdmin(activeTab)} className="rounded-xl border border-white/15 px-4 py-2 font-semibold text-white">
              Limpar acao
            </button>
          </div>
        </section>
      ) : null}

      <section className="mt-6 grid gap-5 md:grid-cols-2 2xl:grid-cols-5">
        {cards.map((card) => <KpiCard key={card.title} {...card} onAction={() => goToAdmin(card.tab)} />)}
      </section>

      <section className="mt-5 grid gap-5 2xl:grid-cols-[minmax(0,1fr)_420px]">
        <main className="space-y-5">
          <section className="rounded-2xl border border-white/10 bg-slate-950/60 p-5 shadow-[0_22px_70px_rgba(0,0,0,0.28)]">
            <div className="mb-5 flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
              <div>
                <h2 className="font-display text-2xl">Empresas</h2>
                <p className="mt-1 text-sm text-slate-400">Todas as empresas cadastradas na plataforma.</p>
              </div>
              <div className="flex flex-col gap-3 md:flex-row">
                <label className="flex min-w-[280px] items-center gap-2 rounded-xl border border-white/10 bg-slate-950 px-4 py-3 text-sm text-slate-400">
                  <Search size={16} />
                  Buscar empresas...
                </label>
                <button type="button" onClick={() => goToAdmin('Empresas', 'new')} className="inline-flex items-center justify-center gap-2 rounded-xl bg-violet-600 px-4 py-3 text-sm font-semibold">
                  <Plus size={16} /> Nova empresa
                </button>
              </div>
            </div>
            <div className="overflow-x-auto rounded-xl border border-white/10">
              <table className="min-w-full text-sm">
                <thead className="bg-white/[0.03] text-left text-slate-400">
                  <tr>
                    <th className="px-4 py-3">Empresa</th>
                    <th className="px-4 py-3">Plano</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3">Usuarios</th>
                    <th className="px-4 py-3">Criado em</th>
                    <th className="px-4 py-3">Acoes</th>
                  </tr>
                </thead>
                <tbody>
                  {(overview?.empresas ?? []).length === 0 ? (
                    <tr><td className="px-4 py-6 text-slate-400" colSpan={6}>Sem empresas reais cadastradas nos perfis atuais.</td></tr>
                  ) : overview!.empresas.map((empresa) => (
                    <tr key={empresa.name} className="border-t border-white/10">
                      <td className="px-4 py-4">
                        <div>
                          <button type="button" onClick={() => openCompany(empresa.name)} className="font-semibold text-white hover:text-violet-200">
                            {empresa.name}
                          </button>
                          <p className="text-xs text-slate-400">{empresa.email ?? 'Sem email principal'}</p>
                        </div>
                      </td>
                      <td className="px-4 py-4"><span className="rounded-full bg-violet-500/20 px-2 py-1 text-xs text-violet-200">{formatPlan(empresa.plan)}</span></td>
                      <td className="px-4 py-4"><span className="rounded-full bg-emerald-500/15 px-2 py-1 text-xs text-emerald-300">{empresa.status}</span></td>
                      <td className="px-4 py-4 text-slate-300">{empresa.users_count}</td>
                      <td className="px-4 py-4 text-slate-300">{empresa.created_at ?? '-'}</td>
                      <td className="px-4 py-4">
                        <div className="flex gap-2 text-slate-300">
                          <button className="grid h-9 w-9 place-items-center rounded-lg border border-white/10" onClick={() => openCompany(empresa.name)} type="button" aria-label="Visualizar"><Eye size={16} /></button>
                          <button className="grid h-9 w-9 place-items-center rounded-lg border border-white/10" onClick={() => goToAdmin('Empresas', 'edit', { empresa: empresa.name })} type="button" aria-label="Editar"><Pencil size={16} /></button>
                          <button className="grid h-9 w-9 place-items-center rounded-lg border border-white/10" onClick={() => goToAdmin('Empresas', 'more', { empresa: empresa.name })} type="button" aria-label="Mais opcoes"><MoreHorizontal size={16} /></button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="mt-4 flex items-center justify-between text-sm text-slate-400">
              <span>Mostrando {(overview?.empresas ?? []).length} empresas reais</span>
              <div className="flex gap-2">
                <button type="button" disabled className="grid h-9 w-9 place-items-center rounded-lg border border-white/10 opacity-50"><ChevronLeft size={15} /></button>
                <button type="button" className="grid h-9 w-9 place-items-center rounded-lg border border-violet-400/40 bg-violet-600 text-white">1</button>
                <button type="button" disabled className="grid h-9 w-9 place-items-center rounded-lg border border-white/10 opacity-50"><ChevronRight size={15} /></button>
              </div>
            </div>
          </section>

          <section className="grid gap-5 xl:grid-cols-4">
            <ModuleCard icon={Users} title="Usuarios" description="Gerencie usuarios e acessos." tone="bg-blue-500/20 text-blue-200" onAction={() => goToAdmin('Usuarios')} />
            <ModuleCard icon={KeyRound} title="Papeis e permissoes" description="Defina papeis por modulo." tone="bg-emerald-500/20 text-emerald-200" onAction={() => goToAdmin('Permissoes')} />
            <ModuleCard icon={CreditCard} title="Billing" description="Planos, faturas e metodos." tone="bg-amber-500/20 text-amber-200" onAction={() => goToAdmin('Billing')} />
            <ModuleCard icon={ShieldCheck} title="Seguranca" description="Login, sessoes e politicas." tone="bg-rose-500/20 text-rose-200" onAction={() => goToAdmin('Seguranca')} />
          </section>

          <section className="grid gap-5 xl:grid-cols-[0.9fr_1fr_1.2fr]">
            <article className="rounded-2xl border border-white/10 bg-slate-950/60 p-5">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="font-display text-xl">Usuarios recentes</h2>
                <button type="button" onClick={() => goToAdmin('Usuarios')} className="text-sm text-violet-300">Ver todos</button>
              </div>
              {recentUsers.length === 0 ? <EmptyState>Sem usuarios reais para listar.</EmptyState> : (
                <div className="space-y-3">
                  {recentUsers.map((user) => (
                    <div key={user.id} className="flex items-center justify-between gap-3">
                      <div>
                        <p className="font-semibold text-white">{user.name}</p>
                        <p className="text-xs text-slate-400">{user.email}</p>
                      </div>
                      <span className="rounded-full bg-violet-500/20 px-2 py-1 text-xs text-violet-200">{user.role}</span>
                    </div>
                  ))}
                </div>
              )}
            </article>

            <article className="rounded-2xl border border-white/10 bg-slate-950/60 p-5">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="font-display text-xl">Permissoes por papel</h2>
                <button type="button" onClick={() => goToAdmin('Papeis')} className="text-sm text-violet-300">Ver todos</button>
              </div>
              {roleRows.length === 0 ? <EmptyState>Sem papeis reais configurados.</EmptyState> : (
                <div className="space-y-4">
                  {roleRows.map((row) => (
                    <div key={row.role}>
                      <div className="mb-1 flex justify-between text-sm">
                        <span className="capitalize text-slate-200">{row.role}</span>
                        <span className="text-slate-400">{row.percent ? `${row.percent}%` : 'Sem matriz real'}</span>
                      </div>
                      <p className="mb-2 text-xs text-slate-500">{row.users} usuarios</p>
                      <div className="h-2 rounded-full bg-white/10">
                        <div className="h-2 rounded-full bg-violet-500" style={{ width: `${row.percent}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </article>

            <article className="rounded-2xl border border-white/10 bg-slate-950/60 p-5">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="font-display text-xl">Logs de auditoria</h2>
                <button type="button" onClick={() => goToAdmin('Auditoria')} className="text-sm text-violet-300">Ver todos</button>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead className="text-left text-slate-400">
                    <tr>
                      <th className="py-2">Data</th>
                      <th className="py-2">Usuario</th>
                      <th className="py-2">Acao</th>
                      <th className="py-2">Modulo</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(overview?.auditoria ?? []).map((item) => (
                      <tr key={item.label} className="border-t border-white/10">
                        <td className="py-3 text-slate-400">-</td>
                        <td className="py-3 text-slate-300">Sistema</td>
                        <td className="py-3 text-white">{item.label}</td>
                        <td className="py-3 text-slate-400">{item.value} registros</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </article>
          </section>
        </main>

        <aside className="space-y-5">
          <section className="rounded-2xl border border-white/10 bg-slate-950/60 p-5 shadow-[0_22px_70px_rgba(0,0,0,0.28)]">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="font-display text-xl">Atividades recentes</h2>
              <button type="button" onClick={() => goToAdmin('Auditoria')} className="text-sm text-violet-300">Ver auditoria</button>
            </div>
            {(overview?.auditoria ?? []).length === 0 ? <EmptyState>Sem atividades reais registradas.</EmptyState> : (
              <div className="space-y-4">
                {(overview?.auditoria ?? []).map((item) => (
                  <div key={item.label} className="flex items-start gap-3">
                    <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-violet-500/15 text-violet-200">
                      <ScrollText size={20} />
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="font-semibold text-white">{item.label}</p>
                      <p className="text-sm text-slate-400">{item.value} registros reais derivados do backend.</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
            <button type="button" onClick={() => goToAdmin('Auditoria')} className="mt-5 w-full rounded-xl border border-white/10 px-4 py-3 text-sm font-semibold text-slate-200">
              Ver todas as atividades
            </button>
          </section>

          <section className="rounded-2xl border border-white/10 bg-slate-950/60 p-5">
            <h2 className="font-display text-xl">Matriz de permissoes</h2>
            <p className="mt-1 text-sm text-slate-400">Modulos preparados para papeis owner e member.</p>
            <div className="mt-4 grid gap-2">
              {['Revenue', 'Chats', 'AXI Assistant', 'Marketing', 'Studio', 'Integrations', 'Account', 'Administracao'].map((module) => (
                <div key={module} className="grid grid-cols-[1fr_auto] rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2 text-sm">
                  <span className="text-slate-300">{module}</span>
                  <span className="text-violet-200">Owner</span>
                </div>
              ))}
            </div>
          </section>
        </aside>
      </section>
    </div>
  );
}

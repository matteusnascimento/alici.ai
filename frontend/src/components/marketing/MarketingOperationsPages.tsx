import {
  BarChart3,
  Bot,
  CalendarDays,
  CheckCircle2,
  FileText,
  GitBranch,
  Image,
  Loader2,
  Megaphone,
  Plus,
  Search,
  Send,
  Target,
  Users,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { type FormEvent, useEffect, useMemo, useState } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';

import { ApiError } from '../../services/api';
import {
  createProject,
  listCampaigns,
  listMarketingResource,
} from '../../services/marketing.service';
import type { MarketingCampaignListItem, MarketingDataStatus, MarketingProjectCreate } from '../../types/marketing';

const marketingNav = [
  { label: 'Planejamento', to: '/app/marketing/planning', icon: Target },
  { label: 'Campanhas', to: '/app/marketing/campaigns', icon: Megaphone },
  { label: 'Audiencias', to: '/app/marketing/audiences', icon: Users },
  { label: 'Criativos', to: '/app/marketing/creatives', icon: Image },
  { label: 'Automacoes', to: '/app/marketing/automations', icon: GitBranch },
  { label: 'Calendario', to: '/app/marketing/calendar', icon: CalendarDays },
  { label: 'Relatorios', to: '/app/marketing/reports', icon: BarChart3 },
  { label: 'Insights IA', to: '/app/marketing/insights', icon: Bot },
];

const campaignStatuses = ['Rascunho', 'Agendada', 'Ativa', 'Pausada', 'Finalizada'];

function Shell({ title, subtitle, children }: { title: string; subtitle: string; children: React.ReactNode }) {
  return (
    <div className="min-h-[calc(100vh-2rem)] rounded-[1.75rem] border border-white/10 bg-[radial-gradient(circle_at_8%_0%,rgba(124,58,237,0.14),transparent_30%),#050914] p-5 text-white shadow-[0_28px_100px_rgba(0,0,0,0.48)] md:p-7">
      <div className="mb-6 flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-violet-300">Marketing</p>
          <h1 className="mt-1 font-display text-4xl">{title}</h1>
          <p className="mt-2 max-w-2xl text-sm text-slate-300">{subtitle}</p>
        </div>
        <Link to="/app/integrations" className="inline-flex items-center justify-center rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm font-semibold text-slate-200 hover:border-violet-300/40">
          Conectar canais
        </Link>
      </div>
      <nav className="mb-6 flex gap-2 overflow-x-auto">
        {marketingNav.map(({ label, to, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => [
              'inline-flex shrink-0 items-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold transition',
              isActive ? 'bg-violet-600 text-white' : 'border border-white/10 text-slate-400 hover:bg-white/[0.04] hover:text-white',
            ].join(' ')}
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </nav>
      {children}
    </div>
  );
}

function EmptyState({ message, actionTo, actionLabel }: { message: string; actionTo?: string; actionLabel?: string }) {
  return (
    <div className="grid min-h-40 place-items-center rounded-2xl border border-dashed border-white/15 bg-white/[0.035] p-5 text-center text-sm text-slate-400">
      <div>
        <p>{message}</p>
        {actionTo && actionLabel ? (
          <Link to={actionTo} className="mt-4 inline-flex rounded-xl bg-violet-600 px-4 py-2 text-sm font-semibold text-white">
            {actionLabel}
          </Link>
        ) : null}
      </div>
    </div>
  );
}

function DataCard({ title, icon: Icon, children }: { title: string; icon: LucideIcon; children: React.ReactNode }) {
  return (
    <section className="rounded-2xl border border-white/10 bg-slate-950/60 p-5 shadow-[0_20px_60px_rgba(0,0,0,0.24)]">
      <div className="mb-4 flex items-center gap-3">
        <span className="grid h-10 w-10 place-items-center rounded-xl bg-violet-500/15 text-violet-200">
          <Icon size={19} />
        </span>
        <h2 className="font-display text-xl">{title}</h2>
      </div>
      {children}
    </section>
  );
}

function ResourceList({ resource, emptyMessage }: { resource: 'action-plans' | 'calendar' | 'content' | 'audiences' | 'automations' | 'reports' | 'insights'; emptyMessage: string }) {
  const [items, setItems] = useState<MarketingDataStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    listMarketingResource(resource)
      .then((rows) => {
        setItems(rows);
        setError(null);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : 'Falha ao carregar dados de Marketing.'))
      .finally(() => setLoading(false));
  }, [resource]);

  if (loading) return <Loader2 className="animate-spin text-violet-300" />;
  if (error) return <div className="rounded-xl border border-rose-400/30 bg-rose-500/10 p-4 text-sm text-rose-100">{error}</div>;
  if (!items.length) return <EmptyState message={emptyMessage} actionTo="/app/integrations" actionLabel="Configurar integracoes" />;

  return (
    <div className="space-y-2">
      {items.map((item) => (
        <div key={item.message} className="rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-slate-300">
          {item.message}
        </div>
      ))}
    </div>
  );
}

export function MarketingPlanningPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState<MarketingProjectCreate>({
    name: '',
    objective: '',
    audience: '',
    offer: '',
    tone: 'premium',
    notes: '',
  });
  const [budget, setBudget] = useState('');
  const [period, setPeriod] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const project = await createProject({
        ...form,
        notes: [form.notes, budget ? `Orcamento: ${budget}` : '', period ? `Periodo: ${period}` : ''].filter(Boolean).join('\n'),
      });
      navigate(`/app/marketing/projects/${project.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Plano nao foi criado.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <Shell title="Planejamento" subtitle="Crie planos reais com objetivo, datas, orcamento e publico alvo.">
      <form onSubmit={submit} className="grid gap-5 xl:grid-cols-[1fr_360px]">
        <DataCard title="Criar plano" icon={Target}>
          <div className="grid gap-4 md:grid-cols-2">
            <label className="text-sm text-slate-300">Nome da campanha<input required value={form.name} onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))} className="mt-1 w-full rounded-xl border border-white/10 bg-slate-950 px-3 py-3 text-white outline-none focus:border-violet-300" /></label>
            <label className="text-sm text-slate-300">Objetivo<input required value={form.objective} onChange={(event) => setForm((current) => ({ ...current, objective: event.target.value }))} className="mt-1 w-full rounded-xl border border-white/10 bg-slate-950 px-3 py-3 text-white outline-none focus:border-violet-300" /></label>
            <label className="text-sm text-slate-300">Datas<input value={period} onChange={(event) => setPeriod(event.target.value)} placeholder="01/07/2026 a 31/07/2026" className="mt-1 w-full rounded-xl border border-white/10 bg-slate-950 px-3 py-3 text-white outline-none focus:border-violet-300" /></label>
            <label className="text-sm text-slate-300">Orcamento<input value={budget} onChange={(event) => setBudget(event.target.value)} placeholder="R$ 3.000" className="mt-1 w-full rounded-xl border border-white/10 bg-slate-950 px-3 py-3 text-white outline-none focus:border-violet-300" /></label>
            <label className="text-sm text-slate-300 md:col-span-2">Publico alvo<input required value={form.audience} onChange={(event) => setForm((current) => ({ ...current, audience: event.target.value }))} className="mt-1 w-full rounded-xl border border-white/10 bg-slate-950 px-3 py-3 text-white outline-none focus:border-violet-300" /></label>
            <label className="text-sm text-slate-300 md:col-span-2">Oferta<input required value={form.offer} onChange={(event) => setForm((current) => ({ ...current, offer: event.target.value }))} className="mt-1 w-full rounded-xl border border-white/10 bg-slate-950 px-3 py-3 text-white outline-none focus:border-violet-300" /></label>
          </div>
          {error ? <p className="mt-4 rounded-xl border border-rose-400/30 bg-rose-500/10 p-3 text-sm text-rose-100">{error}</p> : null}
        </DataCard>
        <DataCard title="Resumo" icon={CheckCircle2}>
          <div className="space-y-3 text-sm text-slate-300">
            <p>Objetivo: <span className="text-white">{form.objective || '-'}</span></p>
            <p>Periodo: <span className="text-white">{period || '-'}</span></p>
            <p>Orcamento: <span className="text-white">{budget || '-'}</span></p>
            <p>Publico: <span className="text-white">{form.audience || '-'}</span></p>
          </div>
          <button type="submit" disabled={saving} className="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-violet-600 px-4 py-3 text-sm font-semibold text-white disabled:opacity-60">
            <Plus size={16} /> {saving ? 'Criando...' : 'Criar plano'}
          </button>
        </DataCard>
      </form>
    </Shell>
  );
}

export function MarketingCampaignsPage() {
  const [campaigns, setCampaigns] = useState<MarketingCampaignListItem[]>([]);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listCampaigns()
      .then((data) => {
        setCampaigns(data.campaigns);
        setMessage(data.message);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <Shell title="Campanhas" subtitle="CRUD de campanhas baseado em projetos reais de Marketing.">
      <DataCard title="Campanhas" icon={Megaphone}>
        <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <label className="flex min-w-0 flex-1 items-center gap-2 rounded-xl border border-white/10 bg-slate-950 px-3 py-3 text-sm text-slate-400"><Search size={16} /> Buscar campanha</label>
          <Link to="/app/marketing/planning" className="inline-flex items-center justify-center gap-2 rounded-xl bg-violet-600 px-4 py-3 text-sm font-semibold text-white"><Plus size={16} /> Nova campanha</Link>
        </div>
        {loading ? <Loader2 className="animate-spin text-violet-300" /> : campaigns.length === 0 ? (
          <EmptyState message={message || 'Nenhuma campanha real cadastrada.'} actionTo="/app/marketing/planning" actionLabel="Criar campanha" />
        ) : (
          <div className="overflow-x-auto rounded-xl border border-white/10">
            <table className="min-w-full text-sm">
              <thead className="bg-white/[0.03] text-left text-slate-400"><tr><th className="px-4 py-3">Campanha</th><th className="px-4 py-3">Objetivo</th><th className="px-4 py-3">Publico</th><th className="px-4 py-3">Status</th><th className="px-4 py-3">Acoes</th></tr></thead>
              <tbody>{campaigns.map((campaign) => <tr key={campaign.id} className="border-t border-white/10"><td className="px-4 py-3 text-white">{campaign.name}</td><td className="px-4 py-3 text-slate-300">{campaign.objective}</td><td className="px-4 py-3 text-slate-300">{campaign.audience}</td><td className="px-4 py-3"><span className="rounded-full bg-violet-500/15 px-2 py-1 text-xs text-violet-200">{campaign.status}</span></td><td className="px-4 py-3"><Link className="text-violet-300" to={`/app/marketing/projects/${campaign.id}`}>Editar</Link></td></tr>)}</tbody>
            </table>
          </div>
        )}
        <div className="mt-4 flex flex-wrap gap-2">{campaignStatuses.map((status) => <span key={status} className="rounded-full border border-white/10 px-3 py-1 text-xs text-slate-300">{status}</span>)}</div>
      </DataCard>
    </Shell>
  );
}

export function MarketingAudiencesPage() {
  return <Shell title="Audiencias" subtitle="Crie publicos por cidade, estado, pais, ticket, origem, reservas e comportamento."><DataCard title="Publicos" icon={Users}><ResourceList resource="audiences" emptyMessage="Nenhuma audiencia real criada ou importada do Revenue ainda." /></DataCard></Shell>;
}

export function MarketingCreativesPage() {
  const creativeTypes = [
    { label: 'Story', to: '/app/studio/templates?category=Stories' },
    { label: 'Poster', to: '/app/studio/tools/ad' },
    { label: 'Video', to: '/app/studio/editor/video?mode=new' },
    { label: 'Banner', to: '/app/studio/templates?category=Ads' },
  ];
  return (
    <Shell title="Criativos" subtitle="Abra o Studio no editor correto conforme o tipo do criativo.">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {creativeTypes.map((item) => <Link key={item.label} to={item.to} className="rounded-2xl border border-white/10 bg-slate-950/60 p-5 text-white hover:border-violet-300/40"><Image className="mb-4 text-violet-300" /><span className="font-display text-xl">{item.label}</span><p className="mt-2 text-sm text-slate-400">Abrir no Studio</p></Link>)}
      </div>
    </Shell>
  );
}

export function MarketingAutomationsPage() {
  return <Shell title="Automacoes" subtitle="Fluxos e disparos por evento para futuras integracoes Meta, Google, Instagram e WhatsApp."><DataCard title="Fluxos" icon={GitBranch}><ResourceList resource="automations" emptyMessage="Nenhuma automacao real configurada." /></DataCard></Shell>;
}

export function MarketingCalendarPage() {
  const days = Array.from({ length: 35 }, (_, index) => index + 1);
  return (
    <Shell title="Calendario" subtitle="Visual mensal de campanhas agendadas e conteudo programado.">
      <DataCard title="Junho 2026" icon={CalendarDays}>
        <ResourceList resource="calendar" emptyMessage="Nenhuma campanha agendada ou conteudo programado." />
        <div className="mt-5 grid grid-cols-7 gap-2">{days.map((day) => <div key={day} className="min-h-24 rounded-xl border border-white/10 bg-white/[0.025] p-2 text-xs text-slate-400">{day}</div>)}</div>
      </DataCard>
    </Shell>
  );
}

export function MarketingReportsPage() {
  return <Shell title="Relatorios" subtitle="Canal por canal, ROI, leads e reservas com dados reais."><DataCard title="Relatorios" icon={FileText}><ResourceList resource="reports" emptyMessage="Sem relatorios reais. Conecte canais e Revenue para calcular ROI, leads e reservas." /></DataCard></Shell>;
}

export function MarketingInsightsPage() {
  return <Shell title="Insights IA" subtitle="Recomendacoes com dados do Revenue, sugestoes de campanhas, publico e orcamento."><DataCard title="Recomendacoes" icon={Bot}><ResourceList resource="insights" emptyMessage="Sem dados suficientes para gerar insights confiaveis sem simular resultado." /><Link to="/app/revenue?view=business-pulse" className="mt-4 inline-flex items-center gap-2 rounded-xl border border-violet-300/30 px-4 py-3 text-sm font-semibold text-violet-100"><Send size={16} /> Abrir Revenue</Link></DataCard></Shell>;
}

export function MarketingOverviewRedirect() {
  return <MarketingPlanningPage />;
}

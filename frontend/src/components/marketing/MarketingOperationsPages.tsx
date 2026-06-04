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
import { type Dispatch, type FormEvent, type SetStateAction, useEffect, useMemo, useState } from 'react';
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom';

import { MiniAssistantCard } from '../assistant/MiniAssistantCard';
import { ApiError } from '../../services/api';
import {
  createCampaign,
  createPlan,
  createAudience,
  createCalendarEvent,
  listAudiences,
  listCampaigns,
  listCalendarEvents,
  listProjects,
  listMarketingResource,
} from '../../services/marketing.service';
import type { MarketingAudience, MarketingCalendarEvent, MarketingCampaignListItem, MarketingDataStatus, MarketingProject, MarketingProjectCreate } from '../../types/marketing';

const marketingNav = [
  { label: 'Visao Geral', to: '/app/marketing', icon: BarChart3 },
  { label: 'Planejamento', to: '/app/marketing/planning', icon: Target },
  { label: 'Campanhas', to: '/app/marketing/campaigns', icon: Megaphone },
  { label: 'Audiencias', to: '/app/marketing/audiences', icon: Users },
  { label: 'Criativos', to: '/app/marketing/creatives', icon: Image },
  { label: 'Automacoes', to: '/app/marketing/automations', icon: GitBranch },
  { label: 'Calendario', to: '/app/marketing/calendar', icon: CalendarDays },
  { label: 'Relatorios', to: '/app/marketing/reports', icon: BarChart3 },
  { label: 'AXI Assistant', to: '/app/assistant', icon: Bot },
];

const campaignStatuses = ['Rascunho', 'Agendada', 'Ativa', 'Pausada', 'Finalizada'];
const originOptions = ['Salvador', 'Feira', 'Sao Paulo', 'Brasilia', 'Belo Horizonte'];
const ageOptions = ['18-25', '26-35', '36-45', '46+'];
const channelOptions = ['Instagram', 'Meta Ads', 'Google Ads', 'WhatsApp', 'Email', 'Website'];
const objectiveOptions = ['Gerar Leads', 'Gerar Reservas', 'Aumentar Ocupacao', 'Baixa Temporada', 'Remarketing', 'Clientes antigos'];

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

function StatTile({ label, value, description, icon: Icon }: { label: string; value: string; description: string; icon: LucideIcon }) {
  return (
    <section className="rounded-2xl border border-white/10 bg-[linear-gradient(145deg,rgba(15,23,42,0.88),rgba(2,6,23,0.72))] p-4 shadow-[0_18px_48px_rgba(0,0,0,0.24)]">
      <div className="flex items-center gap-3">
        <span className="grid h-10 w-10 place-items-center rounded-xl bg-violet-500/15 text-violet-200">
          <Icon size={18} />
        </span>
        <div>
          <p className="text-xs text-slate-400">{label}</p>
          <p className="text-xl font-semibold text-white">{value}</p>
        </div>
      </div>
      <p className="mt-3 text-xs leading-5 text-slate-500">{description}</p>
    </section>
  );
}

function FormInput({
  label,
  value,
  onChange,
  placeholder,
  required,
  className = '',
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  required?: boolean;
  className?: string;
}) {
  return (
    <label className={`text-sm text-slate-300 ${className}`}>
      {label}
      <input
        required={required}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        className="mt-1 h-12 w-full rounded-xl border border-white/10 bg-slate-950 px-3 text-white outline-none transition placeholder:text-slate-600 focus:border-violet-300"
      />
    </label>
  );
}

function OptionGroup({
  title,
  options,
  selected,
  onToggle,
}: {
  title: string;
  options: string[];
  selected: string[];
  onToggle: (value: string) => void;
}) {
  return (
    <div>
      <p className="mb-2 text-sm font-semibold text-slate-300">{title}</p>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => {
          const active = selected.includes(option);
          return (
            <button
              key={option}
              type="button"
              onClick={() => onToggle(option)}
              className={[
                'rounded-full border px-3 py-2 text-xs font-semibold transition',
                active ? 'border-violet-300 bg-violet-500/20 text-violet-100' : 'border-white/10 bg-white/[0.03] text-slate-400 hover:border-violet-300/35 hover:text-white',
              ].join(' ')}
            >
              {option}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function PlanningSummary({
  form,
  period,
  budget,
  complete,
  saving,
  submitLabel,
}: {
  form: MarketingProjectCreate;
  period: string;
  budget: string;
  complete: boolean;
  saving: boolean;
  submitLabel: string;
}) {
  const rows = [
    ['Objetivo', form.objective || '-'],
    ['Periodo', period || '-'],
    ['Orcamento', budget || '-'],
    ['Publico', form.audience || '-'],
    ['Oferta', form.offer || '-'],
  ];

  return (
    <DataCard title="Resumo" icon={CheckCircle2}>
      <div className="space-y-3 text-sm text-slate-300">
        {rows.map(([label, value]) => (
          <p key={label} className="flex items-start justify-between gap-4 rounded-xl border border-white/10 bg-white/[0.025] px-3 py-2">
            <span className="text-slate-500">{label}</span>
            <span className="max-w-[12rem] text-right text-white">{value}</span>
          </p>
        ))}
      </div>
      <button
        type="submit"
        disabled={saving || !complete}
        className="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-violet-600 px-4 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
      >
        <Plus size={16} /> {saving ? 'Criando...' : submitLabel}
      </button>
      <p className="mt-3 text-xs leading-5 text-slate-500">
        O plano sera salvo como projeto real de Marketing e depois podera alimentar campanhas, calendario e conteudo.
      </p>
    </DataCard>
  );
}

function RecentPlans({ projects, loading }: { projects: MarketingProject[]; loading: boolean }) {
  return (
    <DataCard title="Planos reais" icon={Megaphone}>
      {loading ? (
        <Loader2 className="animate-spin text-violet-300" />
      ) : projects.length ? (
        <div className="space-y-2">
          {projects.slice(0, 4).map((project) => (
            <Link key={project.id} to={`/app/marketing/projects/${project.id}`} className="block rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 transition hover:border-violet-300/40">
              <p className="truncate text-sm font-semibold text-white">{project.name}</p>
              <p className="mt-1 truncate text-xs text-slate-400">{project.objective}</p>
            </Link>
          ))}
        </div>
      ) : (
        <EmptyState message="Nenhum plano real criado ainda. Preencha o planejamento para iniciar." />
      )}
    </DataCard>
  );
}

function PlanningNextSteps() {
  const steps = [
    { label: 'Criar criativos', to: '/app/marketing/creatives', icon: Image },
    { label: 'Agendar conteudo', to: '/app/marketing/calendar', icon: CalendarDays },
    { label: 'Abrir campanhas', to: '/app/marketing/campaigns', icon: Megaphone },
    { label: 'Medir em Revenue', to: '/app/revenue?view=marketing', icon: BarChart3 },
  ];

  return (
    <DataCard title="Proximos passos" icon={GitBranch}>
      <div className="grid gap-2">
        {steps.map(({ label, to, icon: Icon }) => (
          <Link key={label} to={to} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.03] px-3 py-3 text-sm font-semibold text-slate-200 transition hover:border-violet-300/40 hover:text-white">
            <span className="flex items-center gap-2"><Icon size={16} className="text-violet-300" /> {label}</span>
            <Send size={14} className="text-slate-500" />
          </Link>
        ))}
      </div>
    </DataCard>
  );
}

function ResourceList({ resource, emptyMessage }: { resource: 'action-plans' | 'content' | 'automations' | 'reports' | 'insights'; emptyMessage: string }) {
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
  const location = useLocation();
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
  const [origins, setOrigins] = useState<string[]>([]);
  const [ages, setAges] = useState<string[]>([]);
  const [channels, setChannels] = useState<string[]>([]);
  const [projects, setProjects] = useState<MarketingProject[]>([]);
  const [projectsLoading, setProjectsLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setProjectsLoading(true);
    listProjects()
      .then((rows) => setProjects(Array.isArray(rows) ? rows : []))
      .catch(() => setProjects([]))
      .finally(() => setProjectsLoading(false));
  }, []);

  const complete = Boolean(form.name.trim() && form.objective.trim() && form.audience.trim() && form.offer.trim());

  const isCampaignForm = location.pathname.includes('/campaigns/new');
  const entityLabel = isCampaignForm ? 'campanha' : 'plano';

  function toggleList(setter: Dispatch<SetStateAction<string[]>>, value: string) {
    setter((current) => (current.includes(value) ? current.filter((item) => item !== value) : [...current, value]));
  }

  function applyObjective(value: string) {
    setForm((current) => ({ ...current, objective: value }));
  }

  function syncAudience(nextOrigins = origins, nextAges = ages) {
    const parts = [
      nextOrigins.length ? `Origem: ${nextOrigins.join(' + ')}` : '',
      nextAges.length ? `Idade: ${nextAges.join(' / ')}` : '',
    ].filter(Boolean);
    setForm((current) => ({ ...current, audience: parts.join(' | ') }));
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const payload = {
        ...form,
        notes: [
          form.notes,
          budget ? `Orcamento: ${budget}` : '',
          period ? `Periodo: ${period}` : '',
          channels.length ? `Canais: ${channels.join(', ')}` : '',
        ].filter(Boolean).join('\n'),
      };
      const project = isCampaignForm ? await createCampaign(payload) : await createPlan(payload);
      navigate(isCampaignForm ? '/app/marketing/campaigns' : '/app/marketing/planning', {
        replace: true,
        state: { createdProjectId: project.id },
      });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : isCampaignForm ? 'Campanha nao foi criada.' : 'Plano nao foi criado.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <Shell
      title={isCampaignForm ? 'Nova Campanha' : 'Criar Plano de Marketing'}
      subtitle="Crie planos reais em uma tela secundaria, mantendo o dashboard principal como HUB de Marketing."
    >
      <div className="mb-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatTile label="Planos criados" value={projectsLoading ? '...' : String(projects.length)} description="Projetos reais salvos no backend de Marketing." icon={Target} />
        <StatTile label="Campanhas" value="Real" description="A aba Campanhas lista somente projetos persistidos." icon={Megaphone} />
        <StatTile label="Criativos" value="Studio" description="Criacao visual abre o editor correto no AXI Studio." icon={Image} />
        <StatTile label="Analise" value="Revenue" description="ROI, funil e performance ficam centralizados em Revenue." icon={BarChart3} />
      </div>

      <form onSubmit={submit} className="grid gap-5 2xl:grid-cols-[minmax(0,1fr)_360px]">
        <main className="space-y-5">
          <div className="grid gap-3 rounded-2xl border border-white/10 bg-white/[0.035] p-4 md:grid-cols-4">
            {['Briefing', 'Publico', 'Canais', 'Revisao'].map((step, index) => (
              <div key={step} className="flex items-center gap-3 rounded-xl bg-slate-950/60 px-3 py-2 text-sm text-slate-300">
                <span className="grid h-7 w-7 place-items-center rounded-full bg-violet-500/20 text-xs font-semibold text-violet-100">{index + 1}</span>
                {step}
              </div>
            ))}
          </div>
          <DataCard title={isCampaignForm ? 'Criar campanha' : 'Criar plano'} icon={Target}>
            <div className="grid gap-4 md:grid-cols-2">
              <FormInput required label={`Nome da ${entityLabel}`} value={form.name} onChange={(value) => setForm((current) => ({ ...current, name: value }))} placeholder="Ferias Julho - Pousada Mar & Sol" />
              <FormInput label="Datas" value={period} onChange={setPeriod} placeholder="01/07/2026 a 31/07/2026" />
              <FormInput label="Orcamento" value={budget} onChange={setBudget} placeholder="R$ 3.000" />
              <div className="md:col-span-2">
                <OptionGroup title="Objetivo" options={objectiveOptions} selected={form.objective ? [form.objective] : []} onToggle={applyObjective} />
                <FormInput required className="mt-3 block" label="Objetivo detalhado" value={form.objective} onChange={(value) => setForm((current) => ({ ...current, objective: value }))} placeholder="Aumentar reservas diretas em julho" />
              </div>
              <div className="grid gap-4 rounded-2xl border border-white/10 bg-white/[0.025] p-4 md:col-span-2">
                <OptionGroup
                  title="Origem do publico"
                  options={originOptions}
                  selected={origins}
                  onToggle={(value) => {
                    const next = origins.includes(value) ? origins.filter((item) => item !== value) : [...origins, value];
                    setOrigins(next);
                    syncAudience(next, ages);
                  }}
                />
                <OptionGroup
                  title="Idade"
                  options={ageOptions}
                  selected={ages}
                  onToggle={(value) => {
                    const next = ages.includes(value) ? ages.filter((item) => item !== value) : [...ages, value];
                    setAges(next);
                    syncAudience(origins, next);
                  }}
                />
                <FormInput required label="Publico alvo" value={form.audience} onChange={(value) => setForm((current) => ({ ...current, audience: value }))} placeholder="Casais 25-45 de Salvador e Feira" />
              </div>
              <div className="md:col-span-2">
                <OptionGroup title="Canais" options={channelOptions} selected={channels} onToggle={(value) => toggleList(setChannels, value)} />
              </div>
              <FormInput required className="md:col-span-2" label="Oferta" value={form.offer} onChange={(value) => setForm((current) => ({ ...current, offer: value }))} placeholder="2 diarias com cafe da manha incluso e late checkout" />
              <label className="text-sm text-slate-300 md:col-span-2">
                Observacoes
                <textarea
                  value={form.notes}
                  onChange={(event) => setForm((current) => ({ ...current, notes: event.target.value }))}
                  placeholder="Canais, restricoes, diferenciais, tom da marca..."
                  className="mt-1 min-h-24 w-full resize-none rounded-xl border border-white/10 bg-slate-950 px-3 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-violet-300"
                />
              </label>
            </div>
            {error ? <p className="mt-4 rounded-xl border border-rose-400/30 bg-rose-500/10 p-3 text-sm text-rose-100">{error}</p> : null}
          </DataCard>

          <section className="grid gap-5 xl:grid-cols-3">
            <DataCard title="Fluxo do plano" icon={GitBranch}>
              <div className="space-y-3 text-sm">
                {['Planejamento salvo', 'Criativos no Studio', 'Calendario de publicacao', 'Campanha acompanhada no Revenue'].map((step, index) => (
                  <div key={step} className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/[0.03] px-3 py-3 text-slate-300">
                    <span className="grid h-7 w-7 place-items-center rounded-full bg-violet-500/15 text-xs font-semibold text-violet-100">{index + 1}</span>
                    {step}
                  </div>
                ))}
              </div>
            </DataCard>
            <RecentPlans projects={projects} loading={projectsLoading} />
            <PlanningNextSteps />
          </section>
        </main>

        <aside className="space-y-5">
          <PlanningSummary form={form} period={period} budget={budget} complete={complete} saving={saving} submitLabel={isCampaignForm ? 'Criar campanha' : 'Criar plano'} />
          <MiniAssistantCard context="marketing" />
          <DataCard title="Contrato de dados" icon={CheckCircle2}>
            <div className="space-y-2 text-sm text-slate-300">
              <p className="rounded-xl border border-emerald-400/20 bg-emerald-400/10 px-3 py-2 text-emerald-100">Salva plano real no backend.</p>
              <p className="rounded-xl border border-violet-400/20 bg-violet-400/10 px-3 py-2 text-violet-100">Criativos abrem no Studio.</p>
              <p className="rounded-xl border border-cyan-400/20 bg-cyan-400/10 px-3 py-2 text-cyan-100">Analise fica em Revenue.</p>
              <p className="rounded-xl border border-rose-400/20 bg-rose-400/10 px-3 py-2 text-rose-100">Sem simular resultado.</p>
            </div>
          </DataCard>
        </aside>
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
          <Link to="/app/marketing/campaigns/new" className="inline-flex items-center justify-center gap-2 rounded-xl bg-violet-600 px-4 py-3 text-sm font-semibold text-white"><Plus size={16} /> Nova campanha</Link>
        </div>
        {loading ? <Loader2 className="animate-spin text-violet-300" /> : campaigns.length === 0 ? (
          <EmptyState message={message || 'Nenhuma campanha real cadastrada.'} actionTo="/app/marketing/campaigns/new" actionLabel="Criar campanha" />
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
  const [audiences, setAudiences] = useState<MarketingAudience[]>([]);
  const [form, setForm] = useState({
    name: '',
    city: '',
    state: '',
    country: 'Brasil',
    ticket: '',
    source: '',
    reservations: '',
    behavior: '',
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listAudiences()
      .then((rows) => setAudiences(rows))
      .catch((err) => setError(err instanceof ApiError ? err.message : 'Falha ao carregar audiencias.'))
      .finally(() => setLoading(false));
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const created = await createAudience(form);
      setAudiences((current) => [created, ...current]);
      setForm({ name: '', city: '', state: '', country: 'Brasil', ticket: '', source: '', reservations: '', behavior: '' });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Audiencia nao foi criada.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <Shell title="Audiencias" subtitle="Crie publicos por cidade, estado, pais, ticket, origem, reservas e comportamento.">
      <div className="grid gap-5 xl:grid-cols-[420px_minmax(0,1fr)]">
        <DataCard title="Criar publico" icon={Users}>
          <form onSubmit={submit} className="grid gap-3">
            <FormInput required label="Nome" value={form.name} onChange={(value) => setForm((current) => ({ ...current, name: value }))} placeholder="Casais Salvador alto ticket" />
            <div className="grid gap-3 md:grid-cols-2">
              <FormInput label="Cidade" value={form.city} onChange={(value) => setForm((current) => ({ ...current, city: value }))} />
              <FormInput label="Estado" value={form.state} onChange={(value) => setForm((current) => ({ ...current, state: value }))} />
              <FormInput label="Pais" value={form.country} onChange={(value) => setForm((current) => ({ ...current, country: value }))} />
              <FormInput label="Ticket" value={form.ticket} onChange={(value) => setForm((current) => ({ ...current, ticket: value }))} placeholder="R$ 800+" />
              <FormInput label="Origem" value={form.source} onChange={(value) => setForm((current) => ({ ...current, source: value }))} placeholder="Instagram, WhatsApp..." />
              <FormInput label="Reservas" value={form.reservations} onChange={(value) => setForm((current) => ({ ...current, reservations: value }))} placeholder="2+ reservas" />
            </div>
            <label className="text-sm text-slate-300">
              Comportamento
              <textarea value={form.behavior} onChange={(event) => setForm((current) => ({ ...current, behavior: event.target.value }))} className="mt-1 min-h-24 w-full resize-none rounded-xl border border-white/10 bg-slate-950 px-3 py-3 text-white outline-none focus:border-violet-300" />
            </label>
            {error ? <p className="rounded-xl border border-rose-400/30 bg-rose-500/10 p-3 text-sm text-rose-100">{error}</p> : null}
            <button disabled={saving || !form.name.trim()} type="submit" className="rounded-xl bg-violet-600 px-4 py-3 text-sm font-semibold text-white disabled:opacity-50">{saving ? 'Salvando...' : 'Criar publico'}</button>
          </form>
        </DataCard>
        <DataCard title="Publicos" icon={Users}>
          {loading ? <Loader2 className="animate-spin text-violet-300" /> : audiences.length ? (
            <div className="grid gap-3">
              {audiences.map((audience) => (
                <article key={audience.id} className="rounded-xl border border-white/10 bg-white/[0.03] p-4 text-sm">
                  <p className="font-semibold text-white">{audience.name}</p>
                  <p className="mt-1 text-slate-400">{[audience.city, audience.state, audience.country].filter(Boolean).join(' / ') || 'Sem localidade'}</p>
                  <p className="mt-2 text-slate-500">Ticket: {audience.ticket || '-'} | Origem: {audience.source || '-'} | Reservas: {audience.reservations || '-'}</p>
                  {audience.behavior ? <p className="mt-2 text-slate-300">{audience.behavior}</p> : null}
                </article>
              ))}
            </div>
          ) : <EmptyState message="Nenhuma audiencia real criada ou importada do Revenue ainda." />}
        </DataCard>
      </div>
    </Shell>
  );
}

export function MarketingCreativesPage() {
  const creativeTypes = [
    { label: 'Story', editor: '/app/studio/editor/new?source=marketing&type=story', template: '/app/studio/templates?category=Stories' },
    { label: 'Poster', editor: '/app/studio/editor/new?source=marketing&type=poster', template: '/app/studio/tools/ad' },
    { label: 'Video', editor: '/app/studio/editor/video?source=marketing&type=video', template: '/app/studio/templates?category=Video' },
    { label: 'Banner', editor: '/app/studio/editor/new?source=marketing&type=banner', template: '/app/studio/templates?category=Ads' },
  ];
  return (
    <Shell title="Criativos" subtitle="Abra o Studio no editor correto conforme o tipo do criativo.">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {creativeTypes.map((item) => (
          <article key={item.label} className="rounded-2xl border border-white/10 bg-slate-950/60 p-5 text-white">
            <Image className="mb-4 text-violet-300" />
            <span className="font-display text-xl">{item.label}</span>
            <div className="mt-5 grid gap-2">
              <Link to={item.editor} className="rounded-xl bg-violet-600 px-3 py-2 text-center text-sm font-semibold text-white">Criar no Studio</Link>
              <Link to={item.template} className="rounded-xl border border-white/10 px-3 py-2 text-center text-sm font-semibold text-slate-200">Usar template</Link>
              <Link to="/app/marketing/campaigns" className="rounded-xl border border-white/10 px-3 py-2 text-center text-sm font-semibold text-slate-300">Vincular campanha</Link>
            </div>
          </article>
        ))}
      </div>
    </Shell>
  );
}

export function MarketingAutomationsPage() {
  return <Shell title="Automacoes" subtitle="Fluxos e disparos por evento para futuras integracoes Meta, Google, Instagram e WhatsApp."><DataCard title="Fluxos" icon={GitBranch}><ResourceList resource="automations" emptyMessage="Nenhuma automacao real configurada." /></DataCard></Shell>;
}

export function MarketingCalendarPage() {
  const [cursor, setCursor] = useState(() => new Date(2026, 5, 1));
  const [mode, setMode] = useState<'mes' | 'semana' | 'dia'>('mes');
  const [selectedDay, setSelectedDay] = useState<number | null>(null);
  const [events, setEvents] = useState<MarketingCalendarEvent[]>([]);
  const [eventTitle, setEventTitle] = useState('');
  const [eventChannel, setEventChannel] = useState('Instagram');
  const [loadingEvents, setLoadingEvents] = useState(true);
  const [eventError, setEventError] = useState<string | null>(null);
  const label = cursor.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' });
  const daysInMonth = new Date(cursor.getFullYear(), cursor.getMonth() + 1, 0).getDate();
  const firstWeekday = new Date(cursor.getFullYear(), cursor.getMonth(), 1).getDay();
  const days = useMemo(() => {
    const blanks = Array.from({ length: firstWeekday }, () => null);
    const monthDays = Array.from({ length: daysInMonth }, (_, index) => index + 1);
    return [...blanks, ...monthDays];
  }, [daysInMonth, firstWeekday]);

  function shiftMonth(delta: number) {
    setCursor((current) => new Date(current.getFullYear(), current.getMonth() + delta, 1));
    setSelectedDay(null);
  }

  useEffect(() => {
    listCalendarEvents()
      .then((rows) => setEvents(rows))
      .catch((err) => setEventError(err instanceof ApiError ? err.message : 'Falha ao carregar calendario.'))
      .finally(() => setLoadingEvents(false));
  }, []);

  function eventsForDay(day: number) {
    const dateKey = `${cursor.getFullYear()}-${String(cursor.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    return events.filter((event) => event.date === dateKey);
  }

  async function createSelectedEvent() {
    if (!selectedDay || !eventTitle.trim()) return;
    const dateKey = `${cursor.getFullYear()}-${String(cursor.getMonth() + 1).padStart(2, '0')}-${String(selectedDay).padStart(2, '0')}`;
    setEventError(null);
    try {
      const created = await createCalendarEvent({
        title: eventTitle,
        date: dateKey,
        channel: eventChannel,
        status: 'scheduled',
        notes: '',
      });
      setEvents((current) => [...current, created]);
      setEventTitle('');
    } catch (err) {
      setEventError(err instanceof ApiError ? err.message : 'Evento nao foi criado.');
    }
  }

  return (
    <Shell title="Calendario" subtitle="Visual mensal de campanhas agendadas e conteudo programado.">
      <DataCard title={label.charAt(0).toUpperCase() + label.slice(1)} icon={CalendarDays}>
        <div className="mb-5 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex flex-wrap gap-2">
            {(['mes', 'semana', 'dia'] as const).map((item) => (
              <button
                key={item}
                type="button"
                onClick={() => setMode(item)}
                className={[
                  'rounded-xl px-3 py-2 text-sm font-semibold',
                  mode === item ? 'bg-violet-600 text-white' : 'border border-white/10 text-slate-300',
                ].join(' ')}
              >
                {item === 'mes' ? 'Mes' : item === 'semana' ? 'Semana' : 'Dia'}
              </button>
            ))}
          </div>
          <div className="flex flex-wrap gap-2">
            <button type="button" onClick={() => shiftMonth(-1)} className="rounded-xl border border-white/10 px-3 py-2 text-sm text-slate-300">Anterior</button>
            <button type="button" onClick={() => setCursor(new Date())} className="rounded-xl border border-white/10 px-3 py-2 text-sm text-slate-300">Hoje</button>
            <button type="button" onClick={() => shiftMonth(1)} className="rounded-xl border border-white/10 px-3 py-2 text-sm text-slate-300">Proximo</button>
          </div>
        </div>
        {loadingEvents ? <Loader2 className="animate-spin text-violet-300" /> : eventError ? <p className="rounded-xl border border-rose-400/30 bg-rose-500/10 p-3 text-sm text-rose-100">{eventError}</p> : events.length === 0 ? <EmptyState message="Nenhuma campanha agendada ou conteudo programado." /> : null}
        <div className="mt-5 grid grid-cols-7 gap-2">
          {['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab'].map((day) => (
            <div key={day} className="px-2 text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">{day}</div>
          ))}
          {days.map((day, index) => (
            <button
              key={`${day ?? 'blank'}-${index}`}
              type="button"
              disabled={!day}
              onClick={() => setSelectedDay(day)}
              className={[
                'min-h-24 rounded-xl border p-2 text-left text-xs transition',
                day ? 'border-white/10 bg-white/[0.025] text-slate-300 hover:border-violet-300/40' : 'border-transparent bg-transparent',
              ].join(' ')}
            >
              {day ? (
                <>
                  <span className="font-semibold text-white">{day}</span>
                  {eventsForDay(day).length ? (
                    <div className="mt-3 space-y-1">
                      {eventsForDay(day).slice(0, 2).map((event) => (
                        <p key={event.id} className="truncate rounded-lg bg-violet-500/15 px-2 py-1 text-violet-100">{event.title}</p>
                      ))}
                    </div>
                  ) : <p className="mt-3 text-slate-500">Sem evento real</p>}
                </>
              ) : null}
            </button>
          ))}
        </div>
        {selectedDay ? (
          <div className="fixed inset-0 z-50 grid place-items-center bg-black/60 px-4">
            <div className="w-full max-w-md rounded-2xl border border-white/10 bg-slate-950 p-5 shadow-[0_30px_100px_rgba(0,0,0,0.5)]">
              <h3 className="font-display text-2xl text-white">Eventos de {String(selectedDay).padStart(2, '0')}/{String(cursor.getMonth() + 1).padStart(2, '0')}</h3>
              {eventsForDay(selectedDay).length ? (
                <div className="mt-4 space-y-2">
                  {eventsForDay(selectedDay).map((event) => (
                    <div key={event.id} className="rounded-xl border border-white/10 bg-white/[0.03] p-3 text-sm text-slate-300">
                      <p className="font-semibold text-white">{event.title}</p>
                      <p className="text-slate-500">{event.channel || 'Sem canal'} | {event.status}</p>
                    </div>
                  ))}
                </div>
              ) : <p className="mt-2 text-sm text-slate-400">Nao ha campanhas ou conteudos reais agendados para este dia.</p>}
              <div className="mt-5 grid gap-3">
                <FormInput label="Novo evento" value={eventTitle} onChange={setEventTitle} placeholder="Post Instagram - Pacote romantico" />
                <FormInput label="Canal" value={eventChannel} onChange={setEventChannel} placeholder="Instagram" />
              </div>
              <div className="mt-5 flex gap-2">
                <button type="button" onClick={createSelectedEvent} className="flex-1 rounded-xl bg-violet-600 px-4 py-3 text-center text-sm font-semibold text-white">Salvar evento</button>
                <Link to="/app/marketing/campaigns/new" className="rounded-xl border border-violet-300/30 px-4 py-3 text-center text-sm font-semibold text-violet-100">Criar campanha</Link>
                <button type="button" onClick={() => setSelectedDay(null)} className="rounded-xl border border-white/10 px-4 py-3 text-sm font-semibold text-slate-300">Fechar</button>
              </div>
            </div>
          </div>
        ) : null}
      </DataCard>
    </Shell>
  );
}

export function MarketingReportsPage() {
  return <Shell title="Relatorios" subtitle="Canal por canal, ROI, leads e reservas com dados reais."><DataCard title="Relatorios" icon={FileText}><ResourceList resource="reports" emptyMessage="Sem relatorios reais. Conecte canais e Revenue para calcular ROI, leads e reservas." /></DataCard></Shell>;
}

export function MarketingInsightsPage() {
  return <Shell title="AXI Assistant" subtitle="Assistente executivo para criar, analisar e executar com contexto de Marketing."><MiniAssistantCard context="marketing" /></Shell>;
}

export function MarketingOverviewRedirect() {
  return <MarketingPlanningPage />;
}

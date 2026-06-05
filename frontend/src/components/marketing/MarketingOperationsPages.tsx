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
  publishCampaign,
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

const campaignStatuses = ['Rascunho', 'Pronta', 'Publicada', 'Ativa', 'Pausada', 'Finalizada', 'Erro'];
const channelOptions = ['Instagram', 'Meta Ads', 'Google Ads', 'WhatsApp', 'Email', 'Website'];
const objectiveOptions = ['Reservas', 'Leads', 'Mensagens WhatsApp', 'Trafego', 'Conversoes', 'Receita', 'Remarketing', 'Reconhecimento', 'Fidelizacao', 'Baixa temporada', 'Alta temporada'];
const ageRangeOptions = ['18-24', '25-34', '35-44', '45-54', '55-64', '65+'];
const clientProfileOptions = ['Casais', 'Familias', 'Executivos', 'Mochileiros', 'Lua de mel', 'Grupos', 'Eventos', 'Turismo internacional', 'Turismo nacional'];
const dataSourceLabels = ['Google Ads', 'Google Analytics', 'Meta Ads', 'Revenue', 'Reservas', 'Website Tracker'];
type LocationKind = 'Cidade' | 'Estado' | 'Pais' | 'Regiao' | 'Continente';
type OriginSegment = { name: string; kind: LocationKind; parent?: string };
const originOptions: OriginSegment[] = [
  { name: 'Salvador', kind: 'Cidade', parent: 'Bahia, Brasil' },
  { name: 'Sao Paulo', kind: 'Cidade', parent: 'Sao Paulo, Brasil' },
  { name: 'Belo Horizonte', kind: 'Cidade', parent: 'Minas Gerais, Brasil' },
  { name: 'Brasilia', kind: 'Cidade', parent: 'Distrito Federal, Brasil' },
  { name: 'Curitiba', kind: 'Cidade', parent: 'Parana, Brasil' },
  { name: 'Rio de Janeiro', kind: 'Cidade', parent: 'Rio de Janeiro, Brasil' },
  { name: 'Recife', kind: 'Cidade', parent: 'Pernambuco, Brasil' },
  { name: 'Fortaleza', kind: 'Cidade', parent: 'Ceara, Brasil' },
  { name: 'Bahia', kind: 'Estado', parent: 'Brasil' },
  { name: 'Sao Paulo', kind: 'Estado', parent: 'Brasil' },
  { name: 'Minas Gerais', kind: 'Estado', parent: 'Brasil' },
  { name: 'Rio de Janeiro', kind: 'Estado', parent: 'Brasil' },
  { name: 'Pernambuco', kind: 'Estado', parent: 'Brasil' },
  { name: 'Parana', kind: 'Estado', parent: 'Brasil' },
  { name: 'Brasil', kind: 'Pais' },
  { name: 'Argentina', kind: 'Pais' },
  { name: 'Chile', kind: 'Pais' },
  { name: 'Uruguai', kind: 'Pais' },
  { name: 'Portugal', kind: 'Pais' },
  { name: 'Estados Unidos', kind: 'Pais' },
  { name: 'Canada', kind: 'Pais' },
  { name: 'Nordeste', kind: 'Regiao', parent: 'Brasil' },
  { name: 'Sudeste', kind: 'Regiao', parent: 'Brasil' },
  { name: 'Sul', kind: 'Regiao', parent: 'Brasil' },
  { name: 'Centro-Oeste', kind: 'Regiao', parent: 'Brasil' },
  { name: 'Norte', kind: 'Regiao', parent: 'Brasil' },
  { name: 'Europa', kind: 'Continente' },
  { name: 'America Latina', kind: 'Regiao' },
  { name: 'America do Norte', kind: 'Continente' },
];
const suggestedCampaigns = [
  { name: 'Ferias de Julho', objective: 'Reservas', offer: 'Pacote de inverno com cafe da manha e late checkout', channels: ['Instagram', 'Google Ads'], budget: 'R$ 3.000' },
  { name: 'Lua de Mel', objective: 'Receita', offer: 'Experiencia romantica com decoracao e jantar', channels: ['Instagram', 'WhatsApp'], budget: 'R$ 1.800' },
  { name: 'Baixa Temporada', objective: 'Baixa temporada', offer: 'Diarias flexiveis para meio de semana', channels: ['Google Ads', 'Website'], budget: 'R$ 1.500' },
  { name: 'Final de Semana', objective: 'Mensagens WhatsApp', offer: 'Escapada curta com reserva direta', channels: ['Instagram', 'WhatsApp'], budget: 'R$ 1.200' },
  { name: 'Reveillon', objective: 'Leads', offer: 'Lista de espera para pacote de fim de ano', channels: ['Meta Ads', 'Email'], budget: 'R$ 2.500' },
];
const monthOptions = ['Julho', 'Agosto', 'Setembro'];

function normalizeSearch(value: string) {
  return value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
}

function sameOriginSegment(a: OriginSegment, b: OriginSegment) {
  return normalizeSearch(a.name) === normalizeSearch(b.name) && a.kind === b.kind;
}

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
  origins,
  secondaryObjectives,
  clientProfiles,
  ageRanges,
  complete,
  saving,
  submitLabel,
}: {
  form: MarketingProjectCreate;
  period: string;
  budget: string;
  origins: OriginSegment[];
  secondaryObjectives: string[];
  clientProfiles: string[];
  ageRanges: string[];
  complete: boolean;
  saving: boolean;
  submitLabel: string;
}) {
  const compact = (items: string[]) => {
    if (!items.length) return '-';
    const visible = items.slice(0, 3).join(', ');
    return items.length > 3 ? `${visible} +${items.length - 3}` : visible;
  };

  const rows = [
    ['Objetivo principal', form.objective || '-'],
    ['Complementares', compact(secondaryObjectives)],
    ['Periodo', period || '-'],
    ['Orcamento', budget || '-'],
    ['Mercado', compact(origins.map((item) => item.name))],
    ['Perfil', compact(clientProfiles)],
    ['Faixa etaria', compact(ageRanges)],
    ['Oferta', form.offer || '-'],
  ];

  return (
    <DataCard title="Resumo" icon={CheckCircle2}>
      <div className="space-y-3 text-sm text-slate-300">
        <div className="rounded-2xl border border-violet-300/20 bg-violet-500/10 p-3">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-violet-200">Mercado de origem</p>
          {origins.length ? (
            <div className="mt-3 flex flex-wrap gap-2">
              {origins.slice(0, 6).map((item) => (
                <span key={`${item.kind}-${item.name}`} className="rounded-full bg-slate-950/70 px-3 py-1 text-xs font-semibold text-white">
                  {item.name}
                </span>
              ))}
            </div>
          ) : (
            <p className="mt-3 text-sm text-slate-400">Nenhum segmento selecionado.</p>
          )}
          <p className="mt-3 text-xs text-violet-100">{origins.length} segmentos selecionados</p>
        </div>
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
  const [originSegments, setOriginSegments] = useState<OriginSegment[]>([]);
  const [originInput, setOriginInput] = useState('');
  const [ageRanges, setAgeRanges] = useState<string[]>([]);
  const [clientProfiles, setClientProfiles] = useState<string[]>([]);
  const [secondaryObjectives, setSecondaryObjectives] = useState<string[]>([]);
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

  const selectedOriginNames = useMemo(() => originSegments.map((item) => item.name), [originSegments]);
  const audienceSummary = useMemo(() => {
    const parts = [
      selectedOriginNames.length ? `Mercado: ${selectedOriginNames.join(', ')}` : '',
      clientProfiles.length ? `Perfil: ${clientProfiles.join(', ')}` : '',
      ageRanges.length ? `Faixa etaria: ${ageRanges.join(', ')}` : '',
    ].filter(Boolean);
    return parts.join(' | ');
  }, [ageRanges, clientProfiles, selectedOriginNames]);

  useEffect(() => {
    setForm((current) => (current.audience === audienceSummary ? current : { ...current, audience: audienceSummary }));
  }, [audienceSummary]);

  const filteredOriginOptions = useMemo(() => {
    const query = normalizeSearch(originInput);
    const available = originOptions.filter((option) => !originSegments.some((item) => sameOriginSegment(item, option)));
    if (!query) return available.slice(0, 8);
    return available
      .filter((option) => normalizeSearch(`${option.name} ${option.kind} ${option.parent ?? ''}`).includes(query))
      .slice(0, 8);
  }, [originInput, originSegments]);

  const complete = Boolean(form.name.trim() && form.objective.trim() && originSegments.length && form.offer.trim());

  const isCampaignForm = location.pathname.includes('/campaigns/new');
  const entityLabel = isCampaignForm ? 'campanha' : 'plano';

  function toggleList(setter: Dispatch<SetStateAction<string[]>>, value: string) {
    setter((current) => (current.includes(value) ? current.filter((item) => item !== value) : [...current, value]));
  }

  function applyObjective(value: string) {
    setForm((current) => ({ ...current, objective: value }));
    setSecondaryObjectives((current) => current.filter((item) => item !== value));
  }

  function addOriginSegment(value: string | OriginSegment) {
    const segment = typeof value === 'string'
      ? { name: value.trim(), kind: 'Regiao' as LocationKind }
      : value;
    if (!segment.name) return;
    setOriginSegments((current) => (current.some((item) => sameOriginSegment(item, segment)) ? current : [...current, segment]));
    setOriginInput('');
  }

  function removeOriginSegment(value: OriginSegment) {
    setOriginSegments((current) => current.filter((item) => !sameOriginSegment(item, value)));
  }

  function applySuggestedCampaign(item: (typeof suggestedCampaigns)[number]) {
    setForm((current) => ({
      ...current,
      name: current.name || item.name,
      objective: item.objective,
      offer: current.offer || item.offer,
    }));
    setChannels(item.channels);
    setBudget(item.budget);
    setSecondaryObjectives((current) => current.filter((objective) => objective !== item.objective));
  }

  function parseBudget(value: string) {
    const normalized = value.replace(/[^\d,.-]/g, '').replace(/\./g, '').replace(',', '.');
    const parsed = Number(normalized);
    return Number.isFinite(parsed) && parsed > 0 ? parsed : undefined;
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const payload = {
        ...form,
        channels: channels.join(', '),
        budget: parseBudget(budget),
        notes: [
          form.notes,
          budget ? `Orcamento: ${budget}` : '',
          period ? `Periodo: ${period}` : '',
          originSegments.length ? `Mercado de origem: ${originSegments.map((item) => `${item.name} (${item.kind})`).join(', ')}` : '',
          secondaryObjectives.length ? `Objetivos complementares: ${secondaryObjectives.join(', ')}` : '',
          clientProfiles.length ? `Perfil do cliente: ${clientProfiles.join(', ')}` : '',
          ageRanges.length ? `Faixa etaria: ${ageRanges.join(', ')}` : '',
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
      <section className="mb-5 grid gap-5 2xl:grid-cols-[minmax(0,1fr)_360px]">
        <div className="rounded-3xl border border-white/10 bg-[linear-gradient(145deg,rgba(15,23,42,0.92),rgba(30,27,75,0.45))] p-5 shadow-[0_24px_80px_rgba(0,0,0,0.3)]">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-violet-300">Marketing Planner</p>
              <h2 className="mt-1 font-display text-3xl text-white">Segmentacao profissional para campanhas</h2>
              <p className="mt-2 max-w-2xl text-sm text-slate-400">Defina mercado de origem, objetivo, perfil e faixa etaria como em plataformas modernas de midia paga.</p>
            </div>
            <Link to="/app/studio" className="inline-flex items-center justify-center gap-2 rounded-xl border border-violet-300/25 bg-violet-500/10 px-4 py-3 text-sm font-semibold text-violet-100">
              <Image size={16} /> Criar criativo
            </Link>
          </div>
          <div className="mt-5 grid gap-3 lg:grid-cols-[minmax(0,1fr)_minmax(260px,0.7fr)]">
            <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
              <p className="text-sm font-semibold text-white">Mercados recomendados</p>
              <p className="mt-2 text-sm leading-6 text-slate-400">
                Sem dados reais suficientes para recomendacao automatica. Quando Google Ads, Analytics, Meta Ads, Revenue, Reservas ou Website Tracker enviarem dados, o AXI sugerira origens com maior potencial.
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
              <p className="text-sm font-semibold text-white">Origem dos dados</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {dataSourceLabels.map((source) => (
                  <span key={source} className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1 text-xs text-slate-300">
                    {source}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        <aside className="rounded-3xl border border-white/10 bg-slate-950/70 p-5 shadow-[0_24px_80px_rgba(0,0,0,0.28)]">
          <p className="flex items-center gap-2 text-sm font-semibold text-violet-100"><Bot size={17} /> AXI Marketing Assistant</p>
          <p className="mt-3 text-sm leading-6 text-slate-300">
            Sem dados suficientes do Revenue para uma recomendacao automatica. Use um playbook abaixo ou conecte campanhas e reservas para recomendacoes reais.
          </p>
          <div className="mt-4 space-y-2">
            {suggestedCampaigns.slice(0, 5).map((item) => (
              <button
                key={item.name}
                type="button"
                onClick={() => applySuggestedCampaign(item)}
                className="flex w-full items-center justify-between rounded-xl border border-white/10 bg-white/[0.035] px-3 py-3 text-left text-sm text-slate-200 transition hover:border-violet-300/35"
              >
                <span>{item.name}</span>
                <Send size={14} className="text-violet-300" />
              </button>
            ))}
          </div>
        </aside>
      </section>

      <form onSubmit={submit} className="grid gap-5 2xl:grid-cols-[minmax(0,1fr)_360px]">
        <main className="space-y-5">
          <div className="grid gap-3 rounded-2xl border border-white/10 bg-white/[0.035] p-4 md:grid-cols-5">
            {['Mercado', 'Objetivo', 'Publico', 'Canais', 'Resumo'].map((step, index) => (
              <div key={step} className="flex items-center gap-3 rounded-xl bg-slate-950/60 px-3 py-2 text-sm text-slate-300">
                <span className="grid h-7 w-7 place-items-center rounded-full bg-violet-500/20 text-xs font-semibold text-violet-100">{index + 1}</span>
                {step}
              </div>
            ))}
          </div>
          <DataCard title={isCampaignForm ? 'Wizard da campanha' : 'Wizard do plano'} icon={Target}>
            <div className="grid gap-4 md:grid-cols-2">
              <FormInput required label={`Nome da ${entityLabel}`} value={form.name} onChange={(value) => setForm((current) => ({ ...current, name: value }))} placeholder="Ferias Julho - Pousada Mar & Sol" />
              <FormInput label="Datas" value={period} onChange={setPeriod} placeholder="01/07/2026 a 31/07/2026" />
              <FormInput label="Orcamento" value={budget} onChange={setBudget} placeholder="R$ 3.000" />
              <div className="grid gap-2 rounded-2xl border border-white/10 bg-white/[0.025] p-3">
                <p className="text-sm font-semibold text-slate-300">Periodo rapido</p>
                <div className="flex flex-wrap gap-2">
                  {monthOptions.map((month) => (
                    <button
                      key={month}
                      type="button"
                      onClick={() => setPeriod(month)}
                      className={`rounded-full border px-3 py-2 text-xs font-semibold transition ${period === month ? 'border-violet-300 bg-violet-500/20 text-violet-100' : 'border-white/10 bg-white/[0.03] text-slate-400 hover:border-violet-300/35'}`}
                    >
                      {month}
                    </button>
                  ))}
                </div>
              </div>
              <div className="grid gap-4 rounded-2xl border border-white/10 bg-white/[0.025] p-4 md:col-span-2">
                <div>
                  <p className="mb-2 text-sm font-semibold text-slate-300">Mercado de Origem</p>
                  <div className="relative">
                    <div className="flex flex-col gap-2 md:flex-row">
                      <input
                        value={originInput}
                        onChange={(event) => setOriginInput(event.target.value)}
                        onKeyDown={(event) => {
                          if (event.key === 'Enter') {
                            event.preventDefault();
                            addOriginSegment(originInput.trim() ? filteredOriginOptions[0] ?? originInput : originInput);
                          }
                        }}
                        placeholder="Pesquisar cidade, estado, pais ou regiao..."
                        className="h-12 flex-1 rounded-xl border border-white/10 bg-slate-950 px-3 text-white outline-none transition placeholder:text-slate-600 focus:border-violet-300"
                      />
                      <button type="button" onClick={() => addOriginSegment(originInput.trim() ? filteredOriginOptions[0] ?? originInput : originInput)} className="rounded-xl bg-violet-600 px-4 py-3 text-sm font-semibold text-white">
                        Adicionar
                      </button>
                    </div>
                    <div className="mt-3 grid gap-2 md:grid-cols-2">
                      {filteredOriginOptions.map((option) => (
                        <button
                          key={`${option.kind}-${option.name}-${option.parent ?? ''}`}
                          type="button"
                          onClick={() => addOriginSegment(option)}
                          className="flex items-center justify-between rounded-xl border border-white/10 bg-slate-950/70 px-3 py-3 text-left transition hover:border-violet-300/35"
                        >
                          <span>
                            <span className="block text-sm font-semibold text-white">{option.name}</span>
                            <span className="text-xs text-slate-500">{option.parent ?? option.kind}</span>
                          </span>
                          <span className="rounded-full bg-violet-500/15 px-2 py-1 text-[11px] font-semibold text-violet-100">{option.kind}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                  {originSegments.length ? (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {originSegments.map((segment) => (
                        <button key={`${segment.kind}-${segment.name}`} type="button" onClick={() => removeOriginSegment(segment)} className="rounded-full bg-violet-500/20 px-3 py-2 text-xs font-semibold text-violet-100">
                          {segment.name} <span className="text-violet-200/70">({segment.kind})</span> x
                        </button>
                      ))}
                    </div>
                  ) : null}
                  <p className="mt-3 text-xs text-slate-500">{originSegments.length} segmentos selecionados</p>
                </div>
              </div>
              <div className="grid gap-4 rounded-2xl border border-white/10 bg-white/[0.025] p-4 md:col-span-2">
                <label className="text-sm font-semibold text-slate-300">
                  Objetivo principal
                  <select
                    required
                    value={form.objective}
                    onChange={(event) => applyObjective(event.target.value)}
                    className="mt-2 h-12 w-full rounded-xl border border-white/10 bg-slate-950 px-3 text-white outline-none transition focus:border-violet-300"
                  >
                    <option value="">Selecione um objetivo</option>
                    {objectiveOptions.map((objective) => (
                      <option key={objective} value={objective}>{objective}</option>
                    ))}
                  </select>
                </label>
                <OptionGroup
                  title="Objetivos complementares"
                  options={objectiveOptions.filter((objective) => objective !== form.objective)}
                  selected={secondaryObjectives}
                  onToggle={(value) => toggleList(setSecondaryObjectives, value)}
                />
              </div>
              <div className="grid gap-4 rounded-2xl border border-white/10 bg-white/[0.025] p-4 md:col-span-2">
                <OptionGroup
                  title="Perfil do cliente"
                  options={clientProfileOptions}
                  selected={clientProfiles}
                  onToggle={(value) => toggleList(setClientProfiles, value)}
                />
                <OptionGroup
                  title="Faixa etaria"
                  options={ageRangeOptions}
                  selected={ageRanges}
                  onToggle={(value) => toggleList(setAgeRanges, value)}
                />
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
          <PlanningSummary
            form={form}
            period={period}
            budget={budget}
            origins={originSegments}
            secondaryObjectives={secondaryObjectives}
            clientProfiles={clientProfiles}
            ageRanges={ageRanges}
            complete={complete}
            saving={saving}
            submitLabel={isCampaignForm ? 'Criar campanha' : 'Criar plano'}
          />
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
  const [publishingId, setPublishingId] = useState<number | null>(null);
  const [publishMessage, setPublishMessage] = useState<string | null>(null);

  useEffect(() => {
    listCampaigns()
      .then((data) => {
        setCampaigns(data.campaigns);
        setMessage(data.message);
      })
      .finally(() => setLoading(false));
  }, []);

  async function handlePublish(campaign: MarketingCampaignListItem) {
    const channels = (campaign.channels || '').split(',').map((item) => item.trim()).filter(Boolean);
    setPublishingId(campaign.id);
    setPublishMessage(null);
    try {
      await publishCampaign(campaign.id, channels);
      setPublishMessage('Campanha publicada.');
    } catch (err) {
      setPublishMessage(err instanceof ApiError ? err.message : 'Publicacao bloqueada.');
      void listCampaigns().then((data) => {
        setCampaigns(data.campaigns);
        setMessage(data.message);
      });
    } finally {
      setPublishingId(null);
    }
  }

  const statusSummary = [
    { label: 'Campanhas Ativas', value: campaigns.filter((item) => item.status === 'active').length },
    { label: 'Em Revisao', value: campaigns.filter((item) => item.status === 'ready' || item.status === 'published').length },
    { label: 'Rascunhos', value: campaigns.filter((item) => item.status === 'draft' || item.status === 'project').length },
    { label: 'Finalizadas', value: campaigns.filter((item) => item.status === 'finished').length },
  ];

  function formatBudget(value?: number | null) {
    return value ? new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value) : 'Orcamento pendente';
  }

  function campaignChannels(campaign: MarketingCampaignListItem) {
    return (campaign.channels || '').split(',').map((item) => item.trim()).filter(Boolean);
  }

  return (
    <Shell title="Campanhas" subtitle="Organize execucao, criativos, canais e publicacao sem transformar Marketing em cadastro.">
      <DataCard title="Campanhas" icon={Megaphone}>
        <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <label className="flex min-w-0 flex-1 items-center gap-2 rounded-xl border border-white/10 bg-slate-950 px-3 py-3 text-sm text-slate-400"><Search size={16} /> Buscar campanha</label>
          <Link to="/app/marketing/campaigns/new" className="inline-flex items-center justify-center gap-2 rounded-xl bg-violet-600 px-4 py-3 text-sm font-semibold text-white"><Plus size={16} /> Nova campanha</Link>
        </div>
        <div className="mb-5 grid gap-3 md:grid-cols-4">
          {statusSummary.map((item) => (
            <div key={item.label} className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
              <p className="text-xs text-slate-500">{item.label}</p>
              <p className="mt-1 font-display text-3xl text-white">{item.value}</p>
            </div>
          ))}
        </div>
        {loading ? <Loader2 className="animate-spin text-violet-300" /> : campaigns.length === 0 ? (
          <EmptyState message={message || 'Nenhuma campanha real cadastrada.'} actionTo="/app/marketing/campaigns/new" actionLabel="Criar campanha" />
        ) : (
          <div className="grid gap-4 xl:grid-cols-2">
            {campaigns.map((campaign) => {
              const channels = campaignChannels(campaign);
              return (
                <article key={campaign.id} className="rounded-3xl border border-white/10 bg-[linear-gradient(145deg,rgba(15,23,42,0.88),rgba(2,6,23,0.72))] p-5 shadow-[0_22px_70px_rgba(0,0,0,0.28)]">
                  <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                    <div>
                      <h3 className="font-display text-2xl text-white">{campaign.name}</h3>
                      <p className="mt-1 text-sm text-slate-400">{campaign.objective}</p>
                    </div>
                    <span className={`w-fit rounded-full px-3 py-1 text-xs font-semibold ${campaign.status === 'error' ? 'bg-rose-500/15 text-rose-200' : 'bg-violet-500/15 text-violet-100'}`}>
                      {campaign.status}
                    </span>
                  </div>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {channels.length ? channels.map((channel) => (
                      <span key={channel} className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs text-slate-300">{channel}</span>
                    )) : <span className="rounded-full border border-amber-300/20 bg-amber-400/10 px-3 py-1 text-xs text-amber-100">Sem canal definido</span>}
                  </div>
                  <div className="mt-5 grid gap-3 md:grid-cols-3">
                    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                      <p className="text-xs text-slate-500">Orcamento</p>
                      <p className="mt-1 font-semibold text-white">{formatBudget(campaign.budget)}</p>
                    </div>
                    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                      <p className="text-xs text-slate-500">Reservas</p>
                      <p className="mt-1 font-semibold text-slate-300">Sem dados reais</p>
                    </div>
                    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                      <p className="text-xs text-slate-500">Receita</p>
                      <p className="mt-1 font-semibold text-slate-300">Sem dados reais</p>
                    </div>
                  </div>
                  <div className="mt-5 rounded-2xl border border-white/10 bg-white/[0.025] p-4">
                    <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Criativo</p>
                    <Link to={`/app/studio/editor/new?source=marketing&campaign=${campaign.id}`} className="mt-3 inline-flex items-center gap-2 rounded-xl border border-violet-300/30 bg-violet-500/10 px-4 py-3 text-sm font-semibold text-violet-100">
                      <Image size={16} /> Criar criativo no Studio
                    </Link>
                  </div>
                  {campaign.last_publish_error ? <p className="mt-4 rounded-xl border border-rose-400/25 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">{campaign.last_publish_error}</p> : null}
                  <div className="mt-5 flex flex-wrap gap-2">
                    <Link className="rounded-xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200" to={`/app/marketing/projects/${campaign.id}`}>Ver</Link>
                    <Link className="rounded-xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200" to={`/app/marketing/projects/${campaign.id}`}>Editar</Link>
                    <button type="button" disabled={publishingId === campaign.id} onClick={() => void handlePublish(campaign)} className="rounded-xl bg-violet-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50">
                      {publishingId === campaign.id ? 'Publicando...' : 'Publicar'}
                    </button>
                  </div>
                </article>
              );
            })}
          </div>
        )}
        {publishMessage ? <p className="mt-3 rounded-xl border border-amber-300/20 bg-amber-400/10 px-4 py-3 text-sm text-amber-100">{publishMessage}</p> : null}
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
  const [cursor, setCursor] = useState(() => new Date());
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

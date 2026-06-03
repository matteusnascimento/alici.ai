import {
  ArrowUpRight,
  Bot,
  CalendarDays,
  ChevronRight,
  CheckCircle2,
  CircleDollarSign,
  ClipboardList,
  Clock3,
  Gauge,
  Loader2,
  MapPinned,
  MapPin,
  MessageCircle,
  Percent,
  Send,
  Sparkles,
  Target,
  Users,
  WalletCards,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';

import type {
  RevenueBreakdownItem,
  RevenueFunnelStep,
  RevenueIntelligenceSnapshot,
  RevenueSeriesPoint,
  RevenueSeriesResponse,
} from '../../services/revenue.service';
import { getRevenueIntelligence, getRevenueSeries } from '../../services/revenue.service';
import { normalizeRevenueSnapshot, normalizeRevenueSeries } from '../../utils/dataHelpers';

const periodOptions = [7, 30, 90] as const;

const revenueAreas = [
  { key: 'business-pulse', label: 'Business Pulse' },
  { key: 'inbox', label: 'Inbox' },
  { key: 'leads', label: 'Leads' },
  { key: 'pipeline', label: 'Funil' },
  { key: 'reservations', label: 'Reservas' },
  { key: 'forecast', label: 'Forecast' },
  { key: 'marketing', label: 'Canais' },
  { key: 'agents', label: 'Agentes' },
] as const;

type RevenueAreaKey = (typeof revenueAreas)[number]['key'];

const revenueAreaAliases: Record<string, RevenueAreaKey> = {
  overview: 'business-pulse',
  geral: 'business-pulse',
  'business_pulse': 'business-pulse',
  roi: 'business-pulse',
  conversoes: 'business-pulse',
  funil: 'pipeline',
  pipelines: 'pipeline',
  reservas: 'reservations',
  canais: 'marketing',
  crm: 'leads',
  customers: 'leads',
  reports: 'forecast',
  insights: 'forecast',
};

const assistantPrompts = [
  'Quantas reservas tivemos hoje?',
  'Qual canal gera mais receita?',
  'Qual campanha teve melhor ROI?',
  'Crie um plano para aumentar as reservas.',
];

const formatCurrency = (value: number) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }).format(value);

const formatNumber = (value: number) => value.toLocaleString('pt-BR');

function hasBusinessData(snapshot: RevenueIntelligenceSnapshot | null) {
  const summary = snapshot?.summary;
  return Boolean(summary && (summary.receita_total > 0 || summary.reservas_fechadas > 0 || summary.leads_recebidos > 0));
}

function EmptyState({ children }: { children: string }) {
  return (
    <div className="flex min-h-32 items-center justify-center rounded-2xl border border-dashed border-white/15 bg-white/[0.03] p-5 text-center text-sm text-slate-400">
      {children}
    </div>
  );
}

function IconFrame({
  icon: Icon,
  tone,
  size = 'md',
}: {
  icon: LucideIcon;
  tone: string;
  size?: 'sm' | 'md' | 'lg';
}) {
  const frameSize = size === 'lg' ? 'h-12 w-12' : size === 'sm' ? 'h-10 w-10' : 'h-11 w-11';
  const iconSize = size === 'lg' ? 'h-[21px] w-[21px]' : size === 'sm' ? 'h-[18px] w-[18px]' : 'h-5 w-5';

  return (
    <span className={`grid ${frameSize} shrink-0 place-items-center rounded-full border border-white/10 shadow-[inset_0_1px_0_rgba(255,255,255,0.14)] ${tone}`}>
      <Icon strokeWidth={2.2} className={`${iconSize} shrink-0`} />
    </span>
  );
}

function KpiCard({
  icon: Icon,
  title,
  value,
  detail,
  tone,
}: {
  icon: LucideIcon;
  title: string;
  value: string;
  detail: string;
  tone: string;
}) {
  return (
    <article className="min-h-[154px] rounded-2xl border border-white/10 bg-[linear-gradient(145deg,rgba(15,23,42,0.9),rgba(2,6,23,0.72))] p-4 shadow-[0_22px_65px_rgba(0,0,0,0.30)]">
      <div className="flex items-start gap-3">
        <IconFrame icon={Icon} tone={tone} size="lg" />
        <p className="min-w-0 pt-1 text-sm font-medium leading-5 text-slate-300">{title}</p>
      </div>
      <p className="mt-5 font-display text-3xl text-white">{value}</p>
      <p className="mt-2 flex items-center gap-1 text-xs font-medium text-emerald-300">
        <ArrowUpRight size={13} className="h-[13px] w-[13px] shrink-0" />
        {detail}
      </p>
    </article>
  );
}

function RevenueLineChart({ points }: { points: RevenueSeriesPoint[] }) {
  const positivePoints = points.filter((point) => point.receita > 0);
  if (positivePoints.length === 0) {
    return <EmptyState>Sem receita registrada no periodo selecionado.</EmptyState>;
  }

  const maxRevenue = Math.max(...points.map((point) => point.receita), 1);
  const width = 720;
  const height = 210;
  const plot = points.map((point, index) => {
    const x = points.length === 1 ? width / 2 : (index / (points.length - 1)) * width;
    const y = height - (point.receita / maxRevenue) * (height - 24) - 12;
    return { ...point, x, y };
  });
  const path = plot.map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x.toFixed(1)} ${point.y.toFixed(1)}`).join(' ');
  const areaPath = `${path} L ${plot[plot.length - 1].x.toFixed(1)} ${height} L ${plot[0].x.toFixed(1)} ${height} Z`;

  return (
    <div className="overflow-hidden rounded-lg border border-white/10 bg-slate-950/45 p-4">
      <svg viewBox={`0 0 ${width} ${height}`} className="h-64 w-full" role="img" aria-label="Grafico de receita">
        <defs>
          <linearGradient id="revenueArea" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="#8b5cf6" stopOpacity="0.45" />
            <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0" />
          </linearGradient>
        </defs>
        {[0, 1, 2, 3].map((line) => (
          <line key={line} x1="0" x2={width} y1={(height / 4) * line + 8} y2={(height / 4) * line + 8} stroke="rgba(148,163,184,0.16)" />
        ))}
        <path d={areaPath} fill="url(#revenueArea)" />
        <path d={path} fill="none" stroke="#8b5cf6" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
        {plot.map((point) => (
          <circle key={`${point.start_date}-${point.label}`} cx={point.x} cy={point.y} r="4" fill="#c4b5fd" stroke="#111827" strokeWidth="2" />
        ))}
      </svg>
      <div className="mt-3 flex justify-between gap-2 text-xs text-slate-400">
        <span>{points[0]?.label}</span>
        <span>{points[Math.floor(points.length / 2)]?.label}</span>
        <span>{points[points.length - 1]?.label}</span>
      </div>
    </div>
  );
}

function ReservationSources({ items }: { items: RevenueBreakdownItem[] }) {
  const total = items.reduce((sum, item) => sum + item.valor, 0);
  if (!total) {
    return <EmptyState>Sem origem de reservas registrada no periodo.</EmptyState>;
  }
  const colors = ['#3b82f6', '#8b5cf6', '#f43f5e', '#f59e0b', '#14b8a6', '#64748b'];
  let cursor = 0;
  const stops = items.map((item, index) => {
    const start = cursor;
    const slice = (item.valor / total) * 100;
    cursor += slice;
    return `${colors[index % colors.length]} ${start.toFixed(2)}% ${cursor.toFixed(2)}%`;
  });

  return (
    <div className="grid gap-6 md:grid-cols-[220px_1fr] md:items-center">
      <div
        className="mx-auto grid h-48 w-48 place-items-center rounded-full"
        style={{ background: `conic-gradient(${stops.join(', ')})` }}
      >
        <div className="grid h-28 w-28 place-items-center rounded-full bg-slate-950 text-center">
          <div>
            <p className="font-display text-3xl text-white">{formatNumber(items.length)}</p>
            <p className="text-xs text-slate-400">canais</p>
          </div>
        </div>
      </div>
      <div className="space-y-3">
        {items.map((item, index) => {
          const pct = Math.round((item.valor / total) * 100);
          return (
            <div key={item.label} className="grid grid-cols-[1fr_auto] items-center gap-3 text-sm">
              <span className="flex items-center gap-2 text-slate-200">
                <span className="h-3 w-3 rounded-full" style={{ backgroundColor: colors[index % colors.length] }} />
                {item.label}
              </span>
              <span className="font-semibold text-white">{pct}%</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function BusinessPulse({ snapshot }: { snapshot: RevenueIntelligenceSnapshot | null }) {
  const summary = snapshot?.summary;
  const hasData = hasBusinessData(snapshot);
  const conversionScore = hasData && summary ? Math.min(35, Math.max(0, Math.round(summary.conversao_total * 1.4))) : 0;
  const revenueScore = hasData && summary?.receita_total ? 20 : 0;
  const reservationScore = hasData && summary ? Math.min(25, summary.reservas_fechadas * 2) : 0;
  const marketingScore = hasData && snapshot ? Math.min(20, snapshot.receita_por_canal.length * 5) : 0;
  const score = Math.min(100, conversionScore + revenueScore + reservationScore + marketingScore);
  const label = !hasData ? 'Aguardando dados reais' : score >= 80 ? 'Muito saudavel' : score >= 60 ? 'Saudavel' : 'Em atencao';
  const components = [
    ['Receita', revenueScore, 20, summary ? formatCurrency(summary.receita_total) : formatCurrency(0)],
    ['Conversao', conversionScore, 35, `${(summary?.conversao_total ?? 0).toFixed(1)}%`],
    ['Marketing', marketingScore, 20, formatCurrency(snapshot?.remarketing.receita_recuperada ?? 0)],
    ['Atendimento', summary?.agentes_gerando_receita ?? 0, Math.max(summary?.agentes_gerando_receita ?? 0, 1), formatNumber(summary?.agentes_gerando_receita ?? 0)],
    ['Pos-venda', Math.round(snapshot?.remarketing.taxa_recuperacao ?? 0), 100, `${(snapshot?.remarketing.taxa_recuperacao ?? 0).toFixed(1)}%`],
  ] as const;

  return (
    <section className="rounded-2xl border border-white/10 bg-[radial-gradient(circle_at_15%_15%,rgba(34,211,238,0.12),transparent_32%),linear-gradient(145deg,rgba(15,23,42,0.94),rgba(2,6,23,0.76))] p-6 shadow-[0_24px_70px_rgba(0,0,0,0.28)]">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan-200">Score 0-100</p>
          <h2 className="mt-1 font-display text-2xl text-white">Business Pulse</h2>
        </div>
        <IconFrame icon={Gauge} tone="bg-violet-500/15 text-violet-200" size="sm" />
      </div>
      <div className="mt-6 grid gap-6 md:grid-cols-[190px_1fr] md:items-center">
        <div className="mx-auto grid h-44 w-44 place-items-center rounded-full p-2 shadow-[0_0_45px_rgba(34,197,94,0.13)]" style={{ background: `conic-gradient(#22c55e ${score * 3.6}deg, rgba(255,255,255,0.08) 0deg)` }}>
          <div className="grid h-32 w-32 place-items-center rounded-full border border-white/10 bg-slate-950 text-center">
            <div>
              <p className="font-display text-5xl text-white">{score}</p>
              <p className="text-xs font-medium text-slate-400">de 100</p>
            </div>
          </div>
        </div>
        <div className="space-y-2">
          <p className="text-sm text-slate-400">Saude do negocio</p>
          <p className="font-semibold text-emerald-300">{label}</p>
          {!hasData ? <p className="pb-2 text-sm text-slate-400">Sem dados reais suficientes para calcular a saude do negocio.</p> : null}
          {components.map(([name, value, max, display]) => (
            <div key={name} className="rounded-xl border border-white/10 bg-white/[0.04] px-3 py-2.5">
              <div className="mb-1 flex justify-between text-xs">
                <span className="text-slate-300">{name}</span>
                <span className="text-emerald-300">{display}</span>
              </div>
              <div className="h-1.5 rounded-full bg-white/10">
                <div className="h-1.5 rounded-full bg-emerald-400" style={{ width: `${Math.min(100, (value / max) * 100)}%` }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function FocusPanel({
  area,
  snapshot,
}: {
  area: RevenueAreaKey;
  snapshot: RevenueIntelligenceSnapshot | null;
}) {
  if (area === 'business-pulse') {
    return null;
  }

  if (area === 'pipeline') {
    const funnel = snapshot?.funil ?? [];
    const max = Math.max(...funnel.map((step) => step.total), 1);
    return (
      <section className="rounded-lg border border-white/10 bg-slate-950/55 p-5">
        <h2 className="font-display text-xl text-white">Funil comercial</h2>
        {funnel.length === 0 ? <EmptyState>Sem etapas de funil registradas.</EmptyState> : (
          <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-5">
            {funnel.map((step) => (
              <article key={step.etapa} className="rounded-lg border border-white/10 bg-white/[0.03] p-4">
                <p className="text-sm text-slate-300">{step.etapa}</p>
                <p className="mt-2 font-display text-3xl text-white">{formatNumber(step.total)}</p>
                <div className="mt-3 h-1.5 rounded-full bg-white/10">
                  <div className="h-1.5 rounded-full bg-violet-400" style={{ width: `${(step.total / max) * 100}%` }} />
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    );
  }

  if (area === 'leads' || area === 'reservations') {
    const rows = snapshot?.reservas ?? [];
    return (
      <section className="rounded-lg border border-white/10 bg-slate-950/55 p-5">
        <h2 className="font-display text-xl text-white">{area === 'leads' ? 'Leads e CRM' : 'Reservas'}</h2>
        {rows.length === 0 ? <EmptyState>Sem registros reais para esta view.</EmptyState> : (
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="text-left text-xs uppercase tracking-[0.12em] text-slate-500">
                <tr>
                  <th className="px-3 py-2">Cliente</th>
                  <th className="px-3 py-2">Canal</th>
                  <th className="px-3 py-2">Origem</th>
                  <th className="px-3 py-2">Valor</th>
                  <th className="px-3 py-2">Status</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={row.reserva} className="border-t border-white/10 text-slate-300">
                    <td className="px-3 py-3 font-semibold text-white">{row.cliente}</td>
                    <td className="px-3 py-3">{row.canal}</td>
                    <td className="px-3 py-3">{row.origem}</td>
                    <td className="px-3 py-3">{formatCurrency(row.valor)}</td>
                    <td className="px-3 py-3">{row.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    );
  }

  return (
    <section className="rounded-lg border border-white/10 bg-slate-950/55 p-5">
      <h2 className="font-display text-xl text-white">{revenueAreas.find((item) => item.key === area)?.label}</h2>
      <p className="mt-3 text-sm text-slate-400">
        View consolidada dentro de Revenue. Os blocos abaixo continuam usando dados reais do mesmo snapshot.
      </p>
    </section>
  );
}

export function RevenueIntelligencePage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [snapshot, setSnapshot] = useState<RevenueIntelligenceSnapshot | null>(null);
  const [series, setSeries] = useState<RevenueSeriesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState<(typeof periodOptions)[number]>(30);
  const [actionTab, setActionTab] = useState<'doing' | 'planned' | 'done'>('doing');
  const [assistantQuestion, setAssistantQuestion] = useState('');
  const rawArea = searchParams.get('view') ?? 'business-pulse';
  const currentArea: RevenueAreaKey =
    revenueAreaAliases[rawArea] ?? (revenueAreas.some((area) => area.key === rawArea) ? rawArea as RevenueAreaKey : 'business-pulse');

  function selectArea(area: RevenueAreaKey) {
    const next = new URLSearchParams(searchParams);
    next.set('view', area);
    setSearchParams(next, { replace: true });
  }

  useEffect(() => {
    let cancelled = false;
    const run = async () => {
      try {
        setLoading(true);
        setError(null);
        const granularity = days >= 90 ? 'weekly' : 'daily';
        const [snapshotData, seriesData] = await Promise.all([
          getRevenueIntelligence(days),
          getRevenueSeries(days, granularity),
        ]);
        if (!cancelled) {
          setSnapshot(normalizeRevenueSnapshot(snapshotData));
          setSeries(normalizeRevenueSeries(seriesData));
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Falha ao carregar Revenue');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };
    run();
    return () => {
      cancelled = true;
    };
  }, [days]);

  const summary = snapshot?.summary;
  const revenueByChannel = snapshot?.receita_por_canal ?? [];
  const revenueSeries = series?.points ?? [];
  const hasData = hasBusinessData(snapshot);

  const kpis = [
    {
      title: 'Receita no periodo',
      value: formatCurrency(summary?.receita_total ?? 0),
      detail: hasData ? 'Dados reais do periodo' : 'Sem dados reais',
      icon: CircleDollarSign,
      tone: 'bg-emerald-500/20 text-emerald-300',
    },
    {
      title: 'Reservas',
      value: formatNumber(summary?.reservas_fechadas ?? 0),
      detail: hasData ? 'Fechadas no periodo' : 'Sem reservas',
      icon: CalendarDays,
      tone: 'bg-violet-500/20 text-violet-300',
    },
    {
      title: 'Leads',
      value: formatNumber(summary?.leads_recebidos ?? 0),
      detail: hasData ? 'Recebidos no periodo' : 'Sem leads',
      icon: Users,
      tone: 'bg-blue-500/20 text-blue-300',
    },
    {
      title: 'Taxa de conversao',
      value: `${(summary?.conversao_total ?? 0).toFixed(1)}%`,
      detail: hasData ? 'Lead para reserva' : 'Sem base',
      icon: Percent,
      tone: 'bg-orange-500/20 text-orange-300',
    },
    {
      title: 'Ticket medio',
      value: formatCurrency(summary?.ticket_medio ?? 0),
      detail: hasData ? 'Calculado por reservas' : 'Sem ticket',
      icon: WalletCards,
      tone: 'bg-cyan-500/20 text-cyan-300',
    },
  ];

  const actionPlans = useMemo(() => {
    if (!snapshot || !hasBusinessData(snapshot)) {
      return [];
    }
    const plans: Array<{ title: string; detail: string; progress: number; status: string; date: string }> = [];
    if (snapshot.summary.conversao_total < 10 && snapshot.summary.leads_recebidos > 0) {
      plans.push({ title: 'Reduzir perda no funil', detail: 'Conversao abaixo de 10% no periodo.', progress: 35, status: 'Em andamento', date: `Ultimos ${days} dias` });
    }
    if (snapshot.receita_por_canal[0]) {
      plans.push({ title: `Priorizar ${snapshot.receita_por_canal[0].label}`, detail: 'Canal com maior receita registrada.', progress: 60, status: 'Planejada', date: `Ultimos ${days} dias` });
    }
    if (snapshot.summary.leads_recebidos > 0 && snapshot.summary.reservas_fechadas === 0) {
      plans.push({ title: 'Criar rotina de conversao', detail: 'Ha leads sem reservas fechadas.', progress: 20, status: 'Em andamento', date: `Ultimos ${days} dias` });
    }
    return plans;
  }, [days, snapshot]);

  if (loading) {
    return (
      <div className="grid min-h-[70vh] place-items-center">
        <Loader2 size={28} className="animate-spin text-cyan" />
      </div>
    );
  }

  if (error) {
    return <div className="rounded-lg border border-rose-500/30 bg-rose-500/10 p-5 text-rose-100">{error}</div>;
  }

  return (
    <div className="min-h-[calc(100vh-2rem)] rounded-[1.75rem] border border-white/10 bg-[radial-gradient(circle_at_10%_0%,rgba(124,58,237,0.16),transparent_30%),#050914] text-white shadow-[0_28px_100px_rgba(0,0,0,0.48)]">
      <div className="grid gap-8 p-5 md:p-7 xl:grid-cols-[minmax(0,1fr)_420px]">
        <main className="space-y-7">
          <header className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h1 className="font-display text-3xl text-white">Revenue</h1>
              <p className="mt-1 text-sm text-slate-400">Visao geral do seu negocio</p>
            </div>
            <div className="flex flex-col gap-3 md:flex-row md:items-center">
              <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-slate-300">
                <CalendarDays size={16} />
                <select
                  className="bg-transparent text-white outline-none"
                  value={days}
                  onChange={(event) => setDays(Number(event.target.value) as (typeof periodOptions)[number])}
                >
                  {periodOptions.map((option) => (
                    <option key={option} value={option} className="bg-slate-950">
                      Ultimos {option} dias
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </header>

          <nav className="flex gap-2 overflow-x-auto pb-1">
            {revenueAreas.map((area) => (
              <button
                key={area.key}
                type="button"
                onClick={() => selectArea(area.key)}
                className={[
                  'shrink-0 rounded-lg border px-3 py-2 text-sm font-semibold transition',
                  currentArea === area.key
                    ? 'border-violet-400/60 bg-violet-600 text-white'
                    : 'border-white/10 bg-slate-950/55 text-slate-300 hover:border-white/25 hover:text-white',
                ].join(' ')}
              >
                {area.label}
              </button>
            ))}
          </nav>

          <section className="grid gap-5 md:grid-cols-2 2xl:grid-cols-5">
            {kpis.map((card) => (
              <KpiCard key={card.title} {...card} />
            ))}
          </section>

          <section className="grid gap-6 2xl:grid-cols-[1.15fr_0.85fr]">
            <article className="rounded-2xl border border-white/10 bg-[linear-gradient(145deg,rgba(15,23,42,0.88),rgba(2,6,23,0.72))] p-6 shadow-[0_22px_65px_rgba(0,0,0,0.24)]">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <h2 className="font-display text-xl text-white">Receita</h2>
                  <p className="mt-1 text-sm text-slate-400">Receita diaria em BRL</p>
                </div>
                <span className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-1 text-xs text-slate-300">
                  {series?.granularity === 'weekly' ? 'Semanal' : 'Diario'}
                </span>
              </div>
              <RevenueLineChart points={revenueSeries} />
            </article>

            <article className="rounded-2xl border border-white/10 bg-[linear-gradient(145deg,rgba(15,23,42,0.88),rgba(2,6,23,0.72))] p-6 shadow-[0_22px_65px_rgba(0,0,0,0.24)]">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="font-display text-xl text-white">Origem das reservas</h2>
                <span className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-1 text-xs text-slate-300">Periodo</span>
              </div>
              <ReservationSources items={revenueByChannel} />
            </article>
          </section>

          <FocusPanel area={currentArea} snapshot={snapshot} />

          <section className="grid gap-6 2xl:grid-cols-[0.8fr_1.2fr]">
            <BusinessPulse snapshot={snapshot} />

            <article className="rounded-2xl border border-white/10 bg-[radial-gradient(circle_at_70%_20%,rgba(34,211,238,0.12),transparent_32%),linear-gradient(145deg,rgba(15,23,42,0.88),rgba(2,6,23,0.72))] p-6 shadow-[0_22px_65px_rgba(0,0,0,0.24)]">
              <div className="flex items-center justify-between">
                <h2 className="font-display text-2xl text-white">Top cidades por receita</h2>
                <IconFrame icon={MapPinned} tone="bg-cyan-400/12 text-cyan-200" size="sm" />
              </div>
              <div className="mt-5 grid gap-5 md:grid-cols-[220px_1fr] md:items-center">
                <div className="relative h-48 overflow-hidden rounded-2xl border border-white/10 bg-[linear-gradient(145deg,rgba(15,23,42,0.9),rgba(8,47,73,0.25))]">
                  <div className="absolute left-8 top-8 h-20 w-28 rounded-[45%] border border-cyan-200/20 bg-cyan-300/10" />
                  <div className="absolute bottom-8 right-8 h-24 w-24 rounded-[45%] border border-violet-200/20 bg-violet-300/10" />
                  <div className="absolute left-20 top-24 h-16 w-20 rounded-[45%] border border-emerald-200/20 bg-emerald-300/10" />
                  <span className="absolute left-[48%] top-[42%] grid h-11 w-11 place-items-center rounded-full bg-violet-500 text-white shadow-[0_12px_34px_rgba(124,58,237,0.4)]">
                    <MapPin strokeWidth={2.2} className="h-5 w-5 shrink-0" />
                  </span>
                </div>
                <EmptyState>Sem dados geograficos consolidados para exibir cidades.</EmptyState>
              </div>
            </article>
          </section>

          <section className="rounded-lg border border-white/10 bg-slate-950/55 p-5">
            <h2 className="font-display text-xl text-white">Control Room</h2>
            <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              <KpiCard
                icon={MessageCircle}
                title="Conversas abertas"
                value={formatNumber(Math.max((summary?.leads_recebidos ?? 0) - (summary?.reservas_fechadas ?? 0), 0))}
                detail="Derivado de leads sem reserva"
                tone="bg-emerald-500/20 text-emerald-300"
              />
              <KpiCard
                icon={Users}
                title="Atendentes online"
                value="Nao configurado"
                detail="Sem telemetria de presenca"
                tone="bg-slate-500/20 text-slate-300"
              />
              <KpiCard
                icon={Bot}
                title="IA em atendimento"
                value={formatNumber(summary?.agentes_gerando_receita ?? 0)}
                detail="Agentes com receita"
                tone="bg-blue-500/20 text-blue-300"
              />
              <KpiCard
                icon={ClipboardList}
                title="Reservas pendentes"
                value={formatNumber((snapshot?.reservas ?? []).filter((item) => item.status !== 'Fechada').length)}
                detail="Aguardando confirmacao"
                tone="bg-orange-500/20 text-orange-300"
              />
            </div>
          </section>
        </main>

        <aside className="space-y-7">
          <section className="rounded-[1.5rem] border border-violet-300/20 bg-[radial-gradient(circle_at_20%_0%,rgba(168,85,247,0.24),transparent_38%),linear-gradient(160deg,rgba(15,23,42,0.95),rgba(2,6,23,0.82))] p-6 shadow-[0_26px_78px_rgba(76,29,149,0.24)]">
            <div className="flex items-center gap-3">
              <IconFrame icon={Sparkles} tone="bg-violet-500/20 text-violet-100" />
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-violet-200">IA Insights</p>
                <h2 className="font-display text-2xl text-white">AXI Assistant</h2>
              </div>
            </div>
            <div className="mt-5 rounded-2xl border border-white/10 bg-white/[0.045] p-4">
              <p className="font-semibold text-white">Ola, vamos analisar seu Revenue.</p>
              <p className="mt-1 text-sm leading-5 text-slate-400">As sugestoes abrem o assistente usando os dados reais disponiveis da plataforma.</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {assistantPrompts.map((prompt) => (
                  <Link
                    key={prompt}
                    to="/app/assistant"
                    className="rounded-full border border-white/10 bg-slate-950/65 px-3 py-2 text-left text-xs font-medium text-slate-200 transition hover:border-violet-400/50 hover:text-white"
                  >
                    {prompt}
                  </Link>
                ))}
              </div>
              <div className="mt-5 flex gap-2 rounded-2xl border border-white/10 bg-slate-950/70 p-2">
                <input
                  value={assistantQuestion}
                  onChange={(event) => setAssistantQuestion(event.target.value)}
                  placeholder="Pergunte sobre leads, ROI ou reservas..."
                  className="min-w-0 flex-1 bg-transparent px-2 text-sm text-white outline-none placeholder:text-slate-500"
                />
                <Link
                  to="/app/assistant"
                  className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-violet-600 text-white shadow-[0_12px_28px_rgba(124,58,237,0.35)] transition hover:bg-violet-500"
                  aria-label="Enviar pergunta ao AXI Assistant"
                >
                  <Send size={17} className="h-[17px] w-[17px] shrink-0" />
                </Link>
              </div>
            </div>
            <Link
              to="/app/assistant"
              className="mt-5 flex items-center justify-between rounded-2xl border border-violet-300/35 bg-[linear-gradient(135deg,#7c3aed,#c026d3)] px-4 py-3.5 text-sm font-semibold text-white shadow-[0_18px_42px_rgba(124,58,237,0.32)] transition hover:brightness-110"
            >
              Abrir AXI Assistant
              <ChevronRight size={17} className="h-[17px] w-[17px] shrink-0" />
            </Link>
          </section>

          <section className="min-h-[390px] rounded-[1.5rem] border border-white/10 bg-[linear-gradient(145deg,rgba(15,23,42,0.94),rgba(2,6,23,0.78))] p-6 shadow-[0_24px_72px_rgba(0,0,0,0.28)]">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-200">Execucao</p>
                <h2 className="font-display text-2xl text-white">Plano de Acao</h2>
              </div>
              <IconFrame icon={Target} tone="bg-emerald-400/12 text-emerald-200" size="sm" />
            </div>
            <div className="mb-5 grid grid-cols-3 rounded-2xl border border-white/10 bg-slate-950/65 p-1">
              {[
                ['doing', 'Em andamento'],
                ['planned', 'Planejadas'],
                ['done', 'Concluidas'],
              ].map(([key, label]) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => setActionTab(key as 'doing' | 'planned' | 'done')}
                  className={[
                    'rounded-xl px-2 py-2 text-xs font-semibold transition',
                    actionTab === key ? 'bg-violet-600 text-white shadow-[0_12px_26px_rgba(124,58,237,0.24)]' : 'text-slate-400 hover:text-white',
                  ].join(' ')}
                >
                  {label}
                </button>
              ))}
            </div>
            {actionPlans.length === 0 ? (
              <div className="grid min-h-[220px] place-items-center rounded-2xl border border-dashed border-white/15 bg-white/[0.035] p-5 text-center">
                <div>
                  <div className="mx-auto w-fit">
                    <IconFrame icon={ClipboardList} tone="bg-violet-500/15 text-violet-200" size="lg" />
                  </div>
                  <p className="mt-4 text-sm font-semibold text-white">Sem acoes reais para este periodo</p>
                  <p className="mt-2 text-sm leading-5 text-slate-400">Quando houver sinais suficientes, esta area mostra titulo, descricao, progresso, status e data.</p>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {actionPlans.map((plan) => (
                  <article key={plan.title} className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="font-semibold text-white">{plan.title}</p>
                        <p className="mt-1 text-xs leading-5 text-slate-400">{plan.detail}</p>
                      </div>
                      <span className="inline-flex items-center gap-1 rounded-full border border-emerald-300/20 bg-emerald-400/10 px-2 py-1 text-[0.68rem] font-semibold text-emerald-200">
                        <Clock3 size={12} />
                        {plan.status}
                      </span>
                    </div>
                    <div className="mt-3 h-1.5 rounded-full bg-white/10">
                      <div className="h-1.5 rounded-full bg-violet-500" style={{ width: `${plan.progress}%` }} />
                    </div>
                    <div className="mt-2 flex items-center justify-between text-xs">
                      <span className="text-slate-400">{plan.date}</span>
                      <span className="inline-flex items-center gap-1 text-emerald-300">
                        <CheckCircle2 size={13} />
                        {plan.progress}%
                      </span>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>
        </aside>
      </div>
    </div>
  );
}

import { Loader2 } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';

import type { RevenueIntelligenceSnapshot, RevenueSeriesResponse } from '../../services/revenue.service';
import { getRevenueIntelligence, getRevenueSeries } from '../../services/revenue.service';
import { normalizeRevenueSnapshot, normalizeRevenueSeries } from '../../utils/dataHelpers';

const periodOptions = [7, 30, 90] as const;
const chartOptions = ['barras', 'linha', 'tabela'] as const;
const revenueAreas = [
  { key: 'geral', label: 'Geral' },
  { key: 'leads', label: 'Leads' },
  { key: 'conversoes', label: 'Conversoes' },
  { key: 'reservas', label: 'Reservas' },
  { key: 'roi', label: 'ROI' },
  { key: 'forecast', label: 'Forecast' },
  { key: 'funil', label: 'Funil' },
  { key: 'canais', label: 'Canais' },
  { key: 'pipelines', label: 'Pipelines' },
  { key: 'marketing', label: 'Marketing' },
  { key: 'agents', label: 'Agentes' },
] as const;

const channelIntegrations = ['WhatsApp', 'Instagram', 'TikTok', 'Google Ads', 'Site', 'Chatbot'];

const formatCurrency = (value: number) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);

function formatValue(value: number | string, type?: 'currency' | 'number' | 'percent' | 'multiplier') {
  if (typeof value === 'string') {
    return value;
  }
  if (type === 'currency') {
    return formatCurrency(value);
  }
  if (type === 'percent') {
    return `${value.toFixed(1)}%`;
  }
  if (type === 'multiplier') {
    return `${value.toFixed(1)}x`;
  }
  return value.toLocaleString('pt-BR');
}

function HorizontalBarList({
  title,
  data,
}: {
  title: string;
  data: Array<{ label: string; value: number }>;
}) {
  const maxValue = Math.max(...data.map((item) => item.value), 1);

  return (
    <section className="panel-base space-y-4">
      <header className="flex items-center justify-between">
        <h2 className="font-display text-2xl text-white">{title}</h2>
        <span className="text-xs uppercase tracking-[0.25em] text-cyan">Performance</span>
      </header>
      <div className="space-y-3">
        {data.map((item) => {
          const pct = Math.max(10, Math.round((item.value / maxValue) * 100));
          return (
            <article key={item.label} className="rounded-2xl border border-white/10 bg-white/5 p-3">
              <div className="mb-2 flex items-center justify-between text-sm">
                <span className="text-slate-200">{item.label}</span>
                <span className="font-semibold text-white">{formatCurrency(item.value)}</span>
              </div>
              <div className="h-2 rounded-full bg-white/10">
                <div
                  className="h-2 rounded-full bg-gradient-to-r from-cyan via-sky-400 to-emerald-300"
                  style={{ width: `${pct}%` }}
                />
              </div>
            </article>
          );
        })}
      </div>
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
  const [chartType, setChartType] = useState<(typeof chartOptions)[number]>('barras');
  const currentArea = revenueAreas.some((area) => area.key === searchParams.get('view'))
    ? searchParams.get('view')
    : 'geral';

  function selectArea(area: (typeof revenueAreas)[number]['key']) {
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
          setError(err instanceof Error ? err.message : 'Falha ao carregar Revenue Intelligence');
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

  const summaryCards = useMemo(() => {
    const summary = snapshot?.summary;
    return [
      { label: 'Receita total', value: summary?.receita_total ?? 0, type: 'currency' as const },
      { label: 'Reservas fechadas', value: summary?.reservas_fechadas ?? 0, type: 'number' as const },
      { label: 'Ticket medio', value: summary?.ticket_medio ?? 0, type: 'currency' as const },
      { label: 'Leads recebidos', value: summary?.leads_recebidos ?? 0, type: 'number' as const },
      { label: 'Conversao total', value: summary?.conversao_total ?? 0, type: 'percent' as const },
      { label: 'ROI estimado', value: summary?.roi_estimado ?? 0, type: 'multiplier' as const },
      { label: 'Remarketing recuperado', value: summary?.remarketing_recuperado ?? 0, type: 'currency' as const },
      { label: 'Agentes gerando receita', value: summary?.agentes_gerando_receita ?? 0, type: 'number' as const },
    ];
  }, [snapshot]);

  const reservations = snapshot?.reservas ?? [];
  const funnel = snapshot?.funil ?? [];
  const revenueByChannel = snapshot?.receita_por_canal ?? [];
  const revenueByAgent = snapshot?.receita_por_agente ?? [];
  const revenueSeries = series?.points ?? [];

  const remarketingStats = useMemo(() => {
    const remarketing = snapshot?.remarketing;
    return [
      { label: 'Leads em remarketing', value: remarketing?.leads_em_remarketing ?? 0 },
      { label: 'Leads reativados', value: remarketing?.leads_reativados ?? 0 },
      { label: 'Reservas recuperadas', value: remarketing?.reservas_recuperadas ?? 0 },
      { label: 'Receita recuperada', value: remarketing?.receita_recuperada ?? 0, type: 'currency' as const },
      { label: 'Taxa de recuperacao', value: remarketing?.taxa_recuperacao ?? 0, type: 'percent' as const },
      { label: 'Campanha mais forte', value: remarketing?.campanha_mais_forte ?? 'Sem dados' },
    ];
  }, [snapshot]);

  const maxFunnel = Math.max(...funnel.map((step) => step.total), 1);
  const maxSeriesRevenue = Math.max(...revenueSeries.map((point) => point.receita), 1);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 size={26} className="animate-spin text-cyan" />
      </div>
    );
  }

  if (error) {
    return <div className="panel-base m-6 text-coral">{error}</div>;
  }

  return (
    <div className="space-y-6 p-6">
      <section className="panel-base">
        <header className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-cyan">Central de Inteligencia</p>
            <h1 className="mt-2 font-display text-4xl text-white">Revenue Intelligence</h1>
            <p className="mt-2 max-w-3xl text-sm text-slate-300">
              Receita, leads, conversoes, reservas, ROI, forecast, funil, canais e operacao omnichannel em uma unica sala de decisao.
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              {revenueAreas.map((area) => (
                <button
                  key={area.key}
                  type="button"
                  onClick={() => selectArea(area.key)}
                  className={[
                    'rounded-2xl border px-4 py-2 text-sm font-semibold transition',
                    currentArea === area.key
                      ? 'border-cyan/40 bg-cyan/15 text-cyan'
                      : 'border-white/15 bg-white/5 text-slate-300 hover:border-white/30 hover:text-white',
                  ].join(' ')}
                >
                  {area.label}
                </button>
              ))}
            </div>
            <div className="mt-4 flex flex-wrap items-center gap-2">
              {periodOptions.map((option) => (
                <button
                  key={option}
                  type="button"
                  onClick={() => setDays(option)}
                  className={[
                    'rounded-full border px-3 py-1 text-xs font-semibold transition-colors',
                    days === option
                      ? 'border-cyan/40 bg-cyan/15 text-cyan'
                      : 'border-white/15 bg-white/5 text-slate-300 hover:border-white/30 hover:text-white',
                  ].join(' ')}
                >
                  {option} dias
                </button>
              ))}
              <span className="mx-1 hidden h-5 w-px bg-white/15 sm:block" />
              {chartOptions.map((option) => (
                <button
                  key={option}
                  type="button"
                  onClick={() => setChartType(option)}
                  className={[
                    'rounded-full border px-3 py-1 text-xs font-semibold capitalize transition-colors',
                    chartType === option
                      ? 'border-fuchsia-300/40 bg-fuchsia-300/15 text-fuchsia-100'
                      : 'border-white/15 bg-white/5 text-slate-300 hover:border-white/30 hover:text-white',
                  ].join(' ')}
                >
                  {option}
                </button>
              ))}
            </div>
          </div>
          <div className="rounded-2xl border border-cyan/30 bg-cyan/10 px-4 py-3 text-right">
            <p className="text-xs uppercase tracking-[0.2em] text-cyan">Meta mensal</p>
            <p className="mt-1 font-display text-2xl text-white">{formatCurrency(25000)}</p>
            <p className="text-xs text-slate-300">
              {Math.min(100, Math.round(((snapshot?.summary?.receita_total ?? 0) / 25000) * 100))}% atingido
            </p>
          </div>
        </header>

        <div className="mt-6 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {summaryCards.map((card) => (
            <article key={card.label} className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-xs uppercase tracking-[0.15em] text-slate-400">{card.label}</p>
              <p className="mt-2 font-display text-3xl text-white">{formatValue(card.value, card.type)}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <article className="panel-base space-y-4">
          <header className="flex items-center justify-between">
            <h2 className="font-display text-2xl text-white">IA Insights</h2>
            <span className="rounded-full border border-cyan/30 bg-cyan/10 px-3 py-1 text-xs font-semibold text-cyan">Sem mock</span>
          </header>
          <div className="grid gap-3 md:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-xs uppercase tracking-[0.16em] text-slate-400">Forecast</p>
              <p className="mt-2 font-display text-2xl text-white">{formatCurrency((snapshot?.summary?.receita_total ?? 0) * 1.18)}</p>
              <p className="mt-1 text-xs text-slate-400">Projecao simples baseada no ritmo atual; substituir por modelo real quando houver historico suficiente.</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-xs uppercase tracking-[0.16em] text-slate-400">Risco de funil</p>
              <p className="mt-2 font-display text-2xl text-white">{funnel.length > 1 ? `${Math.max(0, funnel[0].total - funnel[funnel.length - 1].total).toLocaleString('pt-BR')} perdas` : 'Sem dados'}</p>
              <p className="mt-1 text-xs text-slate-400">Derivado dos dados atuais do funil, sem chamada de IA simulada.</p>
            </div>
          </div>
        </article>

        <article className="panel-base space-y-4">
          <header className="flex items-center justify-between">
            <h2 className="font-display text-2xl text-white">Inbox Omnichannel</h2>
            <span className="rounded-full border border-emerald-300/30 bg-emerald-300/10 px-3 py-1 text-xs font-semibold text-emerald-200">IA / Humano</span>
          </header>
          <div className="grid gap-2 sm:grid-cols-2">
            {channelIntegrations.map((channel) => (
              <div key={channel} className="rounded-2xl border border-white/10 bg-white/5 p-3">
                <p className="font-semibold text-white">{channel}</p>
                <p className="mt-1 text-xs text-slate-400">Aguardando eventos reais do canal.</p>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="panel-base space-y-4">
        <header className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="font-display text-2xl text-white">Control Room em tempo real</h2>
            <p className="mt-1 text-sm text-slate-400">Visao operacional para alternar IA/Humano e acompanhar canais conectados.</p>
          </div>
          <div className="inline-flex rounded-2xl border border-white/10 bg-white/5 p-1">
            <button type="button" className="rounded-xl bg-cyan/15 px-4 py-2 text-sm font-bold text-cyan">IA</button>
            <button type="button" className="rounded-xl px-4 py-2 text-sm font-bold text-slate-300">Humano</button>
          </div>
        </header>
        <div className="grid gap-3 md:grid-cols-3">
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p className="text-xs uppercase tracking-[0.16em] text-slate-400">Canais ativos</p>
            <p className="mt-2 font-display text-3xl text-white">{revenueByChannel.length}</p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p className="text-xs uppercase tracking-[0.16em] text-slate-400">Conversoes</p>
            <p className="mt-2 font-display text-3xl text-white">{formatValue(snapshot?.summary?.conversao_total ?? 0, 'percent')}</p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p className="text-xs uppercase tracking-[0.16em] text-slate-400">Reservas</p>
            <p className="mt-2 font-display text-3xl text-white">{snapshot?.summary?.reservas_fechadas ?? 0}</p>
          </div>
        </div>
      </section>

      <section className="panel-base space-y-4">
        <header className="flex items-center justify-between">
          <h2 className="font-display text-2xl text-white">Receita historica</h2>
          <span className="text-xs uppercase tracking-[0.22em] text-cyan">
            {series?.granularity === 'weekly' ? 'Semanal' : 'Diaria'}
          </span>
        </header>
        {revenueSeries.length === 0 ? (
          <p className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-400">
            Sem pontos de receita no periodo selecionado.
          </p>
        ) : chartType === 'tabela' ? (
          <div className="overflow-x-auto rounded-2xl border border-white/10">
            <table className="min-w-full text-sm">
              <thead className="bg-white/[0.04] text-left text-xs uppercase tracking-[0.12em] text-slate-400">
                <tr>
                  <th className="px-4 py-3">Periodo</th>
                  <th className="px-4 py-3">Receita</th>
                  <th className="px-4 py-3">Reservas</th>
                  <th className="px-4 py-3">Leads</th>
                  <th className="px-4 py-3">Conversao</th>
                </tr>
              </thead>
              <tbody>
                {revenueSeries.map((point) => (
                  <tr key={`${point.start_date}-${point.label}`} className="border-t border-white/10 text-slate-200">
                    <td className="px-4 py-3 font-semibold text-white">{point.label}</td>
                    <td className="px-4 py-3">{formatCurrency(point.receita)}</td>
                    <td className="px-4 py-3">{point.reservas_fechadas}</td>
                    <td className="px-4 py-3">-</td>
                    <td className="px-4 py-3">-</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : chartType === 'linha' ? (
          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
            <div className="flex h-64 items-end gap-2 border-b border-l border-white/10 px-2">
              {revenueSeries.map((point) => {
                const pct = Math.max(8, Math.round((point.receita / maxSeriesRevenue) * 100));
                return (
                  <div key={`${point.start_date}-${point.label}`} className="flex h-full flex-1 flex-col justify-end gap-2">
                    <div className="mx-auto w-3 rounded-t-full bg-gradient-to-t from-fuchsia-500 to-cyan-300" style={{ height: `${pct}%` }} />
                    <p className="truncate text-center text-[10px] text-slate-500">{point.label}</p>
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6">
            {revenueSeries.map((point) => {
              const pct = Math.max(8, Math.round((point.receita / maxSeriesRevenue) * 100));
              return (
                <article key={`${point.start_date}-${point.label}`} className="rounded-2xl border border-white/10 bg-white/5 p-3">
                  <p className="text-xs uppercase tracking-[0.08em] text-slate-400">{point.label}</p>
                  <div className="mt-3 flex h-24 items-end rounded-xl bg-white/5 p-2">
                    <div className="w-full rounded-lg bg-gradient-to-t from-cyan to-emerald-300" style={{ height: `${pct}%` }} />
                  </div>
                  <p className="mt-3 text-sm font-semibold text-white">{formatCurrency(point.receita)}</p>
                  <p className="text-xs text-slate-400">{point.reservas_fechadas} reservas</p>
                </article>
              );
            })}
          </div>
        )}
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.35fr_0.65fr]">
        <article className="panel-base space-y-4">
          <header className="flex items-center justify-between">
            <h2 className="font-display text-2xl text-white">Reservas fechadas</h2>
            <span className="rounded-full bg-emerald-300/15 px-3 py-1 text-xs font-semibold text-emerald-300">
              Receita ativa
            </span>
          </header>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-white/10 text-left text-xs uppercase tracking-[0.1em] text-slate-400">
                  <th className="px-3 py-2">Reserva</th>
                  <th className="px-3 py-2">Cliente</th>
                  <th className="px-3 py-2">Canal</th>
                  <th className="px-3 py-2">Origem</th>
                  <th className="px-3 py-2">Valor</th>
                  <th className="px-3 py-2">Status</th>
                  <th className="px-3 py-2">Agente</th>
                </tr>
              </thead>
              <tbody>
                {reservations.map((row) => (
                  <tr key={row.reserva} className="border-b border-white/5 text-slate-200">
                    <td className="px-3 py-2 font-semibold text-white">{row.reserva}</td>
                    <td className="px-3 py-2">{row.cliente}</td>
                    <td className="px-3 py-2">{row.canal}</td>
                    <td className="px-3 py-2">{row.origem}</td>
                    <td className="px-3 py-2">{formatCurrency(row.valor)}</td>
                    <td className="px-3 py-2">
                      <span
                        className={[
                          'rounded-full px-2 py-1 text-xs font-semibold',
                          row.status === 'Fechada'
                            ? 'bg-emerald-300/20 text-emerald-300'
                            : 'bg-amber-300/20 text-amber-300',
                        ].join(' ')}
                      >
                        {row.status}
                      </span>
                    </td>
                    <td className="px-3 py-2">{row.agente_responsavel}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>

        <article className="panel-base space-y-3">
          <h2 className="font-display text-2xl text-white">Remarketing</h2>
          {remarketingStats.map((stat) => (
            <div key={stat.label} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
              <p className="text-xs uppercase tracking-[0.1em] text-slate-400">{stat.label}</p>
              <p className="mt-1 font-semibold text-white">{formatValue(stat.value as number | string, stat.type)}</p>
            </div>
          ))}
        </article>
      </section>

      <section className="grid gap-6">
        <article className="panel-base space-y-4">
          <header className="flex items-center justify-between">
            <h2 className="font-display text-2xl text-white">Funil comercial</h2>
            <span className="text-xs uppercase tracking-[0.2em] text-cyan">Leads para receita</span>
          </header>
          <div className="space-y-3">
            {funnel.map((step) => {
              const pct = Math.max(10, Math.round((step.total / maxFunnel) * 100));
              return (
                <article key={step.etapa} className="rounded-2xl border border-white/10 bg-white/5 p-3">
                  <div className="mb-2 flex items-center justify-between text-sm">
                    <p className="text-slate-200">{step.etapa}</p>
                    <p className="font-semibold text-white">{step.total}</p>
                  </div>
                  <div className="h-2 rounded-full bg-white/10">
                    <div className="h-2 rounded-full bg-gradient-to-r from-coral to-cyan" style={{ width: `${pct}%` }} />
                  </div>
                </article>
              );
            })}
          </div>
        </article>
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <HorizontalBarList
          title="Receita por canal"
          data={revenueByChannel.map((item) => ({ label: item.label, value: item.valor }))}
        />
        <HorizontalBarList
          title="Receita por agente"
          data={revenueByAgent.map((item) => ({ label: item.label, value: item.valor }))}
        />
      </section>
    </div>
  );
}

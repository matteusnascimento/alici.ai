import { Bot, Link2, Loader2, Megaphone, Sparkles } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useDashboard } from '../../hooks/useDashboard';
import type { DashboardOverview, DashboardUsage } from '../../services/dashboard.service';
import { getDashboardOverview, getDashboardUsage } from '../../services/dashboard.service';
import { listProjects } from '../../services/marketing.service';
import { listChannelIntegrations } from '../../services/integrations.service';
import type { MarketingProject } from '../../types/marketing';
import type { IntegrationProvider } from '../../services/integrations.service';

const formatCurrency = (value: number) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);

function UsageBar({ label, used, limit }: { label: string; used: number; limit: number }) {
  const pct = limit > 0 ? Math.min(100, Math.round((used / limit) * 100)) : 0;
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-slate-400">
        <span>{label}</span>
        <span>{used} / {limit}</span>
      </div>
      <div className="h-2 w-full rounded-full bg-white/10">
        <div
          className="h-2 rounded-full bg-gradient-to-r from-cyan to-cyan/60 transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export function DashboardPanel() {
  const { stats, loading, error } = useDashboard();
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [usage, setUsage] = useState<DashboardUsage | null>(null);
  const [projects, setProjects] = useState<MarketingProject[]>([]);
  const [integrations, setIntegrations] = useState<IntegrationProvider[]>([]);

  useEffect(() => {
    getDashboardOverview().then(setOverview).catch(() => {});
    getDashboardUsage().then(setUsage).catch(() => {});
    listProjects().then((p) => setProjects(p.slice(0, 3))).catch(() => {});
    listChannelIntegrations().then(setIntegrations).catch(() => {});
  }, []);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 size={24} className="animate-spin text-cyan" />
      </div>
    );
  }

  if (error) {
    return <div className="panel-base text-coral">{error}</div>;
  }

  return (
    <div className="grid gap-6 p-6 xl:grid-cols-[1.2fr_0.8fr]">
      {/* KPI cards */}
      <section className="panel-base grid gap-4 md:grid-cols-2">
        {[
          { label: 'Mensagens', value: stats?.total_messages ?? 0 },
          { label: 'Agentes', value: overview?.total_agents ?? stats?.total_agents ?? 0 },
          { label: 'Conversões', value: stats?.conversions ?? 0 },
          { label: 'Quotes', value: stats?.quotes ?? 0 },
        ].map(({ label, value }) => (
          <article key={label} className="rounded-3xl border border-white/10 bg-white/5 p-5">
            <p className="text-sm text-slate-300">{label}</p>
            <p className="mt-3 font-display text-4xl text-white">{value}</p>
          </article>
        ))}
      </section>

      {/* Revenue + plan */}
      <section className="panel-base space-y-4">
        <p className="text-sm uppercase tracking-[0.3em] text-cyan">Receita e tráfego</p>
        <div className="grid gap-4 sm:grid-cols-2">
          <article className="rounded-3xl border border-white/10 bg-white/5 p-5">
            <p className="text-sm text-slate-300">Revenue</p>
            <p className="mt-3 font-display text-4xl text-white">{formatCurrency(stats?.revenue ?? 0)}</p>
          </article>
          <article className="rounded-3xl border border-white/10 bg-white/5 p-5">
            <p className="text-sm text-slate-300">Clicks</p>
            <p className="mt-3 font-display text-4xl text-white">{stats?.clicks ?? 0}</p>
          </article>
        </div>
        {overview && (
          <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 flex items-center justify-between">
            <p className="text-xs text-slate-400">Plano atual</p>
            <span className="rounded-full bg-cyan/15 px-3 py-0.5 text-xs font-semibold text-cyan capitalize">
              {overview.current_plan}
            </span>
          </div>
        )}
      </section>

      {/* Usage */}
      {usage && (
        <section className="panel-base xl:col-span-2 space-y-3">
          <p className="text-sm uppercase tracking-[0.3em] text-cyan">Uso do plano</p>
          <UsageBar label="Mensagens" used={usage.messages_used} limit={usage.messages_limit} />
          <UsageBar label="Agentes" used={usage.agents_used} limit={usage.agents_limit} />
        </section>
      )}

      {/* Weekly bars */}
      {stats && stats.usage_bars.length > 0 && (
        <section className="panel-base xl:col-span-2">
          <p className="text-sm uppercase tracking-[0.3em] text-cyan">Atividade semanal</p>
          <div className="mt-8 grid grid-cols-2 gap-4 sm:grid-cols-4 lg:grid-cols-7">
            {stats.usage_bars.map((bar) => (
              <article key={bar.label} className="rounded-3xl border border-white/10 bg-white/5 p-4 text-center">
                <div className="mx-auto flex h-32 w-12 items-end rounded-full bg-white/5 p-2">
                  <div
                    className="w-full rounded-full bg-gradient-to-t from-coral to-cyan"
                    style={{ height: `${Math.max(14, bar.value * 10)}px` }}
                  />
                </div>
                <p className="mt-4 text-sm text-slate-300">{bar.label}</p>
                <p className="mt-1 font-semibold text-white">{bar.value}</p>
              </article>
            ))}
          </div>
        </section>
      )}

      {/* Quick access modules */}
      <section className="panel-base xl:col-span-2 grid gap-4 md:grid-cols-3">
        {/* Agents */}
        <div className="rounded-2xl border border-white/10 bg-white/5 p-5 space-y-3">
          <div className="flex items-center gap-2">
            <Bot size={16} className="text-cyan" />
            <p className="font-semibold text-white text-sm">Agentes</p>
            <span className="ml-auto text-xs text-slate-500">{overview?.active_agents ?? 0} ativos</span>
          </div>
          <Link
            to="/app/agents"
            className="block rounded-xl border border-white/10 px-3 py-2 text-xs text-cyan hover:bg-white/5"
          >
            Ver todos os agentes →
          </Link>
        </div>

        {/* Marketing */}
        <div className="rounded-2xl border border-white/10 bg-white/5 p-5 space-y-3">
          <div className="flex items-center gap-2">
            <Sparkles size={16} className="text-cyan" />
            <p className="font-semibold text-white text-sm">Marketing</p>
            <span className="ml-auto text-xs text-slate-500">{projects.length} projetos</span>
          </div>
          {projects.length > 0 ? (
            <ul className="space-y-1">
              {projects.map((p) => (
                <li key={p.id} className="truncate text-xs text-slate-300">{p.name}</li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-slate-500">Nenhum projeto ainda</p>
          )}
          <Link
            to="/app/marketing"
            className="block rounded-xl border border-white/10 px-3 py-2 text-xs text-cyan hover:bg-white/5"
          >
            Ir para Marketing →
          </Link>
        </div>

        {/* Integrations */}
        <div className="rounded-2xl border border-white/10 bg-white/5 p-5 space-y-3">
          <div className="flex items-center gap-2">
            <Link2 size={16} className="text-cyan" />
            <p className="font-semibold text-white text-sm">Integrações</p>
          </div>
          <div className="space-y-1">
            {integrations.map((p) => (
              <div key={p.provider} className="flex items-center justify-between text-xs">
                <span className="text-slate-300 capitalize">{p.provider}</span>
                <span className={p.connected_accounts > 0 ? 'text-green-400' : 'text-slate-500'}>
                  {p.connected_accounts > 0 ? '● conectado' : '○ off'}
                </span>
              </div>
            ))}
            {integrations.length === 0 && <p className="text-xs text-slate-500">Nenhuma integração</p>}
          </div>
          <Link
            to="/app/integrations"
            className="block rounded-xl border border-white/10 px-3 py-2 text-xs text-cyan hover:bg-white/5"
          >
            Gerenciar Integrações →
          </Link>
        </div>
      </section>
    </div>
  );
}


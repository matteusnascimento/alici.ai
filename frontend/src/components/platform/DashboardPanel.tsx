import { useDashboard } from '../../hooks/useDashboard';

const formatCurrency = (value: number) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);

export function DashboardPanel() {
  const { stats, loading, error } = useDashboard();

  if (loading) {
    return <div className="panel-base">Carregando dashboard...</div>;
  }

  if (error) {
    return <div className="panel-base text-coral">{error}</div>;
  }

  if (!stats) {
    return <div className="panel-base">Nenhuma métrica disponível.</div>;
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
      <section className="panel-base grid gap-4 md:grid-cols-2">
        {[
          ['Mensagens', stats.total_messages],
          ['Agentes', stats.total_agents],
          ['Conversões', stats.conversions],
          ['Quotes', stats.quotes],
        ].map(([label, value]) => (
          <article key={label} className="rounded-3xl border border-white/10 bg-white/5 p-5">
            <p className="text-sm text-slate-300">{label}</p>
            <p className="mt-3 font-display text-4xl text-white">{value}</p>
          </article>
        ))}
      </section>
      <section className="panel-base">
        <p className="text-sm uppercase tracking-[0.3em] text-cyan">Receita e tráfego</p>
        <div className="mt-5 grid gap-4 sm:grid-cols-2">
          <article className="rounded-3xl border border-white/10 bg-white/5 p-5">
            <p className="text-sm text-slate-300">Revenue</p>
            <p className="mt-3 font-display text-4xl text-white">{formatCurrency(stats.revenue)}</p>
          </article>
          <article className="rounded-3xl border border-white/10 bg-white/5 p-5">
            <p className="text-sm text-slate-300">Clicks</p>
            <p className="mt-3 font-display text-4xl text-white">{stats.clicks}</p>
          </article>
        </div>
      </section>
      <section className="panel-base xl:col-span-2">
        <p className="text-sm uppercase tracking-[0.3em] text-cyan">Usage Bars semanal</p>
        <div className="mt-8 grid grid-cols-2 gap-4 sm:grid-cols-4 lg:grid-cols-7">
          {stats.usage_bars.map((bar) => (
            <article key={bar.label} className="rounded-3xl border border-white/10 bg-white/5 p-4 text-center">
              <div className="mx-auto flex h-32 w-12 items-end rounded-full bg-white/5 p-2">
                <div className="w-full rounded-full bg-gradient-to-t from-coral to-cyan" style={{ height: `${Math.max(14, bar.value * 10)}px` }} />
              </div>
              <p className="mt-4 text-sm text-slate-300">{bar.label}</p>
              <p className="mt-1 font-semibold text-white">{bar.value}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}

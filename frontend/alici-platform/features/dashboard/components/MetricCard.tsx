import type { UsageMetric } from "@/types/dashboard";

interface MetricCardProps {
  metric: UsageMetric;
}

export function MetricCard({ metric }: MetricCardProps) {
  return (
    <article className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
      <p className="text-xs uppercase tracking-widest text-slate-400">{metric.title}</p>
      <p className="mt-3 text-3xl font-semibold text-slate-100">{metric.value}</p>
      {typeof metric.change === "number" ? (
        <p className="mt-2 text-sm text-emerald-400">+{metric.change}% vs ultimo periodo</p>
      ) : null}
    </article>
  );
}

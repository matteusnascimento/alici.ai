interface CostChartProps {
  data: number[];
}

export function CostChart({ data }: CostChartProps) {
  const labels = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"];

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
      <h3 className="text-sm font-semibold text-slate-200">Cost Trend</h3>
      <div className="mt-4 space-y-3">
        {data.map((value, index) => (
          <div key={labels[index] ?? index}>
            <div className="mb-1 flex justify-between text-xs text-slate-400">
              <span>{labels[index] ?? `D${index + 1}`}</span>
              <span>R$ {value}</span>
            </div>
            <div className="h-2 rounded-full bg-slate-800">
              <div
                className="h-2 rounded-full bg-amber-400"
                style={{ width: `${Math.min((value / 400) * 100, 100)}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

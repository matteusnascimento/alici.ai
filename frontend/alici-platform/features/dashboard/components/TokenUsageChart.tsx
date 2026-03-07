interface TokenUsageChartProps {
  data: number[];
}

export function TokenUsageChart({ data }: TokenUsageChartProps) {
  const max = Math.max(...data, 1);

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
      <h3 className="text-sm font-semibold text-slate-200">Token Usage</h3>
      <div className="mt-5 flex h-44 items-end gap-2">
        {data.map((value, index) => (
          <div key={index} className="flex flex-1 flex-col items-center gap-2">
            <div
              className="w-full rounded-t-md bg-sky-500"
              style={{ height: `${Math.max((value / max) * 160, 8)}px` }}
            />
          </div>
        ))}
      </div>
    </section>
  );
}

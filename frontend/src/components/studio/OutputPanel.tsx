interface OutputPanelProps {
  title: string;
  lines: string[];
}

export function OutputPanel({ title, lines }: OutputPanelProps) {
  return (
    <article className="rounded-2xl border border-white/10 bg-ink/40 p-4">
      <p className="text-xs uppercase tracking-[0.2em] text-cyan">{title}</p>
      <ul className="mt-3 space-y-2 text-sm text-slate-100">
        {lines.map((line) => (
          <li key={line} className="rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2">
            {line}
          </li>
        ))}
      </ul>
    </article>
  );
}

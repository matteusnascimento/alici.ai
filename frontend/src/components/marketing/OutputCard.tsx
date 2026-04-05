import type { ReactNode } from 'react';

interface OutputCardProps {
  label: string;
  value?: string;
  list?: string[];
  children?: ReactNode;
}

export function OutputCard({ label, value, list, children }: OutputCardProps) {
  return (
    <article className="rounded-2xl border border-white/10 bg-ink/40 p-4 transition duration-200 hover:border-cyan/40">
      <p className="text-xs uppercase tracking-[0.22em] text-cyan">{label}</p>
      {value ? <p className="mt-3 whitespace-pre-wrap text-sm leading-relaxed text-slate-100">{value}</p> : null}
      {list?.length ? (
        <ul className="mt-3 space-y-2 text-sm text-slate-100">
          {list.map((item) => (
            <li key={item} className="rounded-xl border border-white/5 bg-white/[0.03] px-3 py-2">
              {item}
            </li>
          ))}
        </ul>
      ) : null}
      {children}
    </article>
  );
}

import type { ReactNode } from 'react';

interface ToolResultSectionProps {
  title: string;
  subtitle: string;
  children: ReactNode;
}

export function ToolResultSection({ title, subtitle, children }: ToolResultSectionProps) {
  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
      <h2 className="font-display text-2xl text-white">{title}</h2>
      <p className="mt-2 text-sm text-slate-300">{subtitle}</p>
      <div className="mt-4">{children}</div>
    </section>
  );
}

import type { ReactNode } from 'react';

interface ToolFormSectionProps {
  title: string;
  subtitle: string;
  children: ReactNode;
}

export function ToolFormSection({ title, subtitle, children }: ToolFormSectionProps) {
  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
      <h2 className="font-display text-2xl text-white">{title}</h2>
      <p className="mt-2 text-sm text-slate-300">{subtitle}</p>
      <div className="mt-4 space-y-3">{children}</div>
    </section>
  );
}

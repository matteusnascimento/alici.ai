import type { ReactNode } from 'react';

interface SectionCardProps {
  title: string;
  description?: string;
  children: ReactNode;
  rightSlot?: ReactNode;
}

export function SectionCard({ title, description, children, rightSlot }: SectionCardProps) {
  return (
    <section className="rounded-3xl border border-white/10 bg-gradient-to-b from-white/10 to-white/[0.04] p-5 shadow-soft backdrop-blur md:p-6">
      <div className="mb-5 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h3 className="font-display text-xl text-white md:text-2xl">{title}</h3>
          {description ? <p className="mt-2 text-sm text-slate-300">{description}</p> : null}
        </div>
        {rightSlot}
      </div>
      {children}
    </section>
  );
}

import { Sparkles } from 'lucide-react';

interface EmptyStateProps {
  title: string;
  description: string;
}

export function EmptyState({ title, description }: EmptyStateProps) {
  return (
    <div className="flex min-h-[220px] flex-col items-center justify-center rounded-3xl border border-dashed border-white/15 bg-white/[0.02] px-6 text-center">
      <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-cyan/10 text-cyan">
        <Sparkles size={18} />
      </div>
      <p className="font-display text-lg text-white">{title}</p>
      <p className="mt-2 max-w-md text-sm text-slate-300">{description}</p>
    </div>
  );
}

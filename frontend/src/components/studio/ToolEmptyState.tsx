import { Sparkles } from 'lucide-react';

interface ToolEmptyStateProps {
  title: string;
  message: string;
}

export function ToolEmptyState({ title, message }: ToolEmptyStateProps) {
  return (
    <div className="rounded-3xl border border-dashed border-white/15 bg-white/[0.03] p-8 text-center">
      <div className="mx-auto mb-4 inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-cyan/10 text-cyan">
        <Sparkles size={18} />
      </div>
      <h3 className="font-display text-2xl text-white">{title}</h3>
      <p className="mx-auto mt-3 max-w-xl text-sm text-slate-300">{message}</p>
      <div className="mt-6 grid gap-3 sm:grid-cols-3">
        {['Mock preview #1', 'Mock preview #2', 'Mock preview #3'].map((card) => (
          <div key={card} className="rounded-2xl border border-white/10 bg-ink/40 p-4 text-left text-sm text-slate-200">
            {card}
          </div>
        ))}
      </div>
    </div>
  );
}

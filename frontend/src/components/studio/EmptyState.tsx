interface EmptyStateProps {
  title: string;
  description: string;
}

export function EmptyState({ title, description }: EmptyStateProps) {
  return (
    <div className="rounded-2xl border border-dashed border-white/15 bg-ink/40 p-8 text-center">
      <h3 className="font-display text-2xl text-white">{title}</h3>
      <p className="mx-auto mt-3 max-w-xl text-sm text-slate-300">{description}</p>
    </div>
  );
}

interface AccountHeaderProps {
  title: string;
  subtitle: string;
}

export function AccountHeader({ title, subtitle }: AccountHeaderProps) {
  return (
    <header className="rounded-3xl border border-white/10 bg-white/[0.03] p-5 md:p-6">
      <p className="text-xs uppercase tracking-[0.3em] text-cyan">AXI Account Center</p>
      <h1 className="mt-3 font-display text-3xl text-white">{title}</h1>
      <p className="mt-2 text-sm text-slate-300">{subtitle}</p>
    </header>
  );
}

interface SettingsGroupProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}

export function SettingsGroup({ title, subtitle, children }: SettingsGroupProps) {
  return (
    <section className="rounded-3xl border border-white/10 bg-gradient-to-b from-white/[0.045] to-white/[0.02] p-5">
      <h2 className="font-display text-2xl text-white">{title}</h2>
      {subtitle ? <p className="mt-1 text-sm text-slate-300">{subtitle}</p> : null}
      <div className="mt-4 space-y-2.5">{children}</div>
    </section>
  );
}

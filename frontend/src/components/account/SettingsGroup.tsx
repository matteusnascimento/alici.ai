interface SettingsGroupProps {
  title: string;
  children: React.ReactNode;
}

export function SettingsGroup({ title, children }: SettingsGroupProps) {
  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-4">
      <h2 className="mb-3 font-display text-2xl text-white">{title}</h2>
      <div className="space-y-2">{children}</div>
    </section>
  );
}

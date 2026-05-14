interface StudioInspectorPanelProps {
  title: string;
  children: React.ReactNode;
}

export function StudioInspectorPanel({ title, children }: StudioInspectorPanelProps) {
  return (
    <aside className="rounded-3xl border border-white/10 bg-[linear-gradient(180deg,rgba(7,14,32,0.95),rgba(11,22,42,0.92))] p-4">
      <p className="text-xs uppercase tracking-[0.2em] text-cyan-300">Inspector</p>
      <h3 className="mt-2 font-display text-lg text-white">{title}</h3>
      <div className="mt-4 space-y-3">{children}</div>
    </aside>
  );
}

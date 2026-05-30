interface StudioInspectorPanelProps {
  title: string;
  children: React.ReactNode;
}

export function StudioInspectorPanel({ title, children }: StudioInspectorPanelProps) {
  return (
    <aside className="rounded-3xl border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.085),rgba(255,255,255,0.035))] p-4 shadow-[var(--studio-tile-shadow)] backdrop-blur-xl">
      <p className="text-xs uppercase tracking-[0.2em] text-cyan-300">Inspector</p>
      <h3 className="mt-2 font-display text-lg font-bold text-white">{title}</h3>
      <div className="mt-4 space-y-3">{children}</div>
    </aside>
  );
}

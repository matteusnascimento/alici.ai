interface StudioBottomDockProps {
  children: React.ReactNode;
}

export function StudioBottomDock({ children }: StudioBottomDockProps) {
  return (
    <section className="rounded-3xl border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.075),rgba(255,255,255,0.035))] p-4 shadow-[var(--studio-tile-shadow)] backdrop-blur-xl">
      {children}
    </section>
  );
}

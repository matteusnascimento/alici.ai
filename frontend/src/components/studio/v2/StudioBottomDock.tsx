interface StudioBottomDockProps {
  children: React.ReactNode;
}

export function StudioBottomDock({ children }: StudioBottomDockProps) {
  return (
    <section className="rounded-3xl border border-white/10 bg-[linear-gradient(180deg,rgba(6,12,26,0.95),rgba(3,7,18,0.95))] p-4">
      {children}
    </section>
  );
}

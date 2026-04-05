interface StudioCanvasProps {
  title: string;
  subtitle: string;
  children?: React.ReactNode;
}

export function StudioCanvas({ title, subtitle, children }: StudioCanvasProps) {
  return (
    <section className="relative h-[520px] overflow-hidden rounded-3xl border border-cyan-300/20 bg-[radial-gradient(circle_at_20%_10%,rgba(0,212,255,0.16),transparent_44%),radial-gradient(circle_at_80%_30%,rgba(111,255,233,0.18),transparent_42%),linear-gradient(160deg,#040918,#0a1f3a)] p-6">
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:22px_22px] opacity-35" />
      <div className="relative z-10 h-full">
        <div className="mb-4">
          <h2 className="font-display text-2xl text-white">{title}</h2>
          <p className="text-sm text-slate-300">{subtitle}</p>
        </div>
        <div className="h-[calc(100%-52px)] rounded-2xl border border-white/15 bg-black/25 p-4">{children}</div>
      </div>
    </section>
  );
}

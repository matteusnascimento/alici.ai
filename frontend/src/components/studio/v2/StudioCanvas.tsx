interface StudioCanvasProps {
  title: string;
  subtitle: string;
  children?: React.ReactNode;
  toolbar?: React.ReactNode;
  selected?: boolean;
  footer?: React.ReactNode;
}

export function StudioCanvas({ title, subtitle, children, toolbar, selected = false, footer }: StudioCanvasProps) {
  return (
    <section className="relative min-h-[620px] overflow-hidden rounded-3xl border border-cyan-300/20 bg-[linear-gradient(180deg,#071121,#0b172b)] p-4 shadow-[0_18px_60px_rgba(0,0,0,0.25)]">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_18%_10%,rgba(0,212,255,0.16),transparent_34%),radial-gradient(circle_at_92%_18%,rgba(111,255,233,0.12),transparent_36%)]" />
      <div className="relative z-10 h-full">
        <div className="mb-4 flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <h2 className="font-display text-2xl text-white">{title}</h2>
            <p className="text-sm text-slate-300">{subtitle}</p>
          </div>
          {toolbar ? <div className="max-w-full">{toolbar}</div> : null}
        </div>
        <div className="relative min-h-[510px] overflow-hidden rounded-2xl border border-slate-300/70 bg-[#eef2f7] p-4 text-slate-950 shadow-inner">
          {children}
          {selected ? (
            <div className="pointer-events-none absolute inset-5 rounded-2xl border-2 border-[#7c3cff] shadow-[0_0_0_1px_rgba(255,255,255,0.9),0_0_32px_rgba(124,60,255,0.18)]">
              {['-left-1.5 -top-1.5', '-right-1.5 -top-1.5', '-bottom-1.5 -left-1.5', '-bottom-1.5 -right-1.5', 'left-1/2 -top-1.5 -translate-x-1/2', 'left-1/2 -bottom-1.5 -translate-x-1/2', '-left-1.5 top-1/2 -translate-y-1/2', '-right-1.5 top-1/2 -translate-y-1/2'].map((position) => (
                <span key={position} className={`absolute h-3 w-3 rounded-full border border-[#7c3cff] bg-white ${position}`} />
              ))}
            </div>
          ) : null}
        </div>
        {footer ? <div className="mt-3">{footer}</div> : null}
      </div>
    </section>
  );
}

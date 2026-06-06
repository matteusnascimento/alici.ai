interface SidebarLogoProps {
  expanded: boolean;
}

export function SidebarLogo({ expanded }: SidebarLogoProps) {
  return (
    <div
      className={[
        'relative overflow-hidden border border-white/10 bg-[linear-gradient(135deg,rgba(109,40,217,0.28)_0%,rgba(124,58,237,0.18)_45%,rgba(37,99,235,0.20)_100%)] shadow-[0_18px_45px_rgba(124,58,237,0.18)] backdrop-blur-[18px]',
        expanded ? 'rounded-[1.4rem] p-4' : 'mx-auto grid h-14 w-14 place-items-center rounded-2xl p-0',
      ].join(' ')}
    >
      <div className="pointer-events-none absolute -right-8 -top-10 h-24 w-24 rounded-full bg-cyan-300/10 blur-2xl" />
      <div className="pointer-events-none absolute -bottom-10 -left-8 h-24 w-24 rounded-full bg-violet-400/12 blur-2xl" />

      {expanded ? (
        <div className="relative">
          <h1 className="bg-[linear-gradient(90deg,#ffffff_0%,#a78bfa_45%,#67e8f9_100%)] bg-clip-text font-display text-[32px] font-extrabold leading-none tracking-[-0.04em] text-transparent">
            AXI
          </h1>
          <p className="mt-3 text-[11px] font-semibold leading-4 tracking-[0.12em] text-white/80">
            Artificial eXtreme Intelligence
          </p>
          <span className="mt-4 inline-flex rounded-full border border-cyan-300/20 bg-cyan-300/10 px-2 py-1 text-[10px] font-bold uppercase tracking-[0.08em] text-cyan-200">
            Business Pulse
          </span>
        </div>
      ) : (
        <span className="relative bg-[linear-gradient(90deg,#ffffff_0%,#a78bfa_45%,#67e8f9_100%)] bg-clip-text font-display text-2xl font-extrabold tracking-[-0.04em] text-transparent">
          AXI
        </span>
      )}
    </div>
  );
}

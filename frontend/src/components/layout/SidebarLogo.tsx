interface SidebarLogoProps {
  expanded: boolean;
}

export function SidebarLogo({ expanded }: SidebarLogoProps) {
  return (
    <div className="rounded-[1.4rem] border border-violet-300/20 bg-[radial-gradient(circle_at_20%_15%,rgba(168,85,247,0.36),transparent_42%),linear-gradient(145deg,rgba(255,255,255,0.14),rgba(255,255,255,0.035))] p-4 shadow-[0_22px_55px_rgba(88,28,135,0.26)]">
      <div className="flex items-center gap-3">
        <span className="grid h-14 w-14 shrink-0 place-items-center rounded-2xl border border-white/15 bg-[linear-gradient(135deg,#7c3aed,#c026d3_55%,#22d3ee)] font-display text-2xl text-white shadow-[0_16px_42px_rgba(168,85,247,0.36)]">
          A
        </span>
        {expanded ? (
          <div className="min-w-0">
            <p className="text-[0.68rem] font-semibold uppercase tracking-[0.28em] text-cyan-200">AXI</p>
            <h1 className="truncate font-display text-2xl leading-tight text-[var(--text-primary)]">Business Pulse</h1>
          </div>
        ) : null}
      </div>
      <div className={['overflow-hidden transition-all duration-300', expanded ? 'mt-3 max-h-24 opacity-100' : 'mt-0 max-h-0 opacity-0'].join(' ')}>
        <p className="text-xs leading-5 text-slate-300">Inteligencia comercial, receita e operacao em tempo real.</p>
      </div>
    </div>
  );
}

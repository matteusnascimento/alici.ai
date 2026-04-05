interface SidebarLogoProps {
  expanded: boolean;
}

export function SidebarLogo({ expanded }: SidebarLogoProps) {
  return (
    <div className="rounded-2xl border border-white/10 bg-gradient-to-b from-white/10 to-white/[0.03] p-4">
      <p className="text-xs uppercase tracking-[0.35em] text-cyan">AXI</p>
      <div className={['overflow-hidden transition-all duration-300', expanded ? 'mt-3 max-h-32 opacity-100' : 'mt-0 max-h-0 opacity-0'].join(' ')}>
        <h1 className="font-display text-2xl text-white">Control Room</h1>
        <p className="mt-2 text-xs text-slate-300">Operacao inteligente de chat, agentes e crescimento.</p>
      </div>
    </div>
  );
}

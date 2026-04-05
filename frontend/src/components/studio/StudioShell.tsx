import { Outlet } from 'react-router-dom';

import { StudioSidebar } from './StudioSidebar';

export function StudioShell() {
  return (
    <div className="space-y-6">
      <header className="rounded-3xl border border-white/10 bg-[radial-gradient(circle_at_top_right,_rgba(110,231,249,0.14),transparent_62%)] p-6">
        <p className="text-xs uppercase tracking-[0.3em] text-cyan">Plataforma AXI</p>
        <h1 className="mt-3 font-display text-3xl text-white">AXI Studio</h1>
        <p className="mt-2 text-sm text-slate-300">Criacao visual, campanhas e midia com IA em um unico workspace.</p>
      </header>

      <div className="grid gap-6 xl:grid-cols-[300px_1fr]">
        <StudioSidebar />
        <div className="space-y-4">
          <Outlet />
        </div>
      </div>
    </div>
  );
}

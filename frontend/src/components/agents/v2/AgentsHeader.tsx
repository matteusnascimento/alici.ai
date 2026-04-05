import { Link } from 'react-router-dom';

interface AgentsHeaderProps {
  onDuplicateTop: () => void;
}

export function AgentsHeader({ onDuplicateTop }: AgentsHeaderProps) {
  return (
    <header className="rounded-3xl border border-cyan-400/20 bg-[radial-gradient(circle_at_0%_0%,rgba(0,212,255,0.22),transparent_42%),linear-gradient(160deg,#041022,#0b2549)] p-6">
      <p className="text-xs uppercase tracking-[0.24em] text-cyan-300">Central de colaboradores digitais</p>
      <h1 className="mt-2 font-display text-4xl text-white">Agentes AXI</h1>
      <p className="mt-2 max-w-2xl text-sm text-slate-300">Crie, treine e coloque agentes de IA para trabalhar no seu negocio.</p>
      <div className="mt-5 flex flex-wrap gap-2">
        <Link to="/app/agents/create" className="rounded-xl bg-cyan px-4 py-2 text-sm font-semibold text-ink">Criar novo agente</Link>
        <button type="button" onClick={onDuplicateTop} className="rounded-xl border border-white/20 px-4 py-2 text-sm text-slate-100">Duplicar agente</button>
        <button type="button" className="rounded-xl border border-white/20 px-4 py-2 text-sm text-slate-100">Importar configuracao</button>
        <Link to="/app/agents/templates" className="rounded-xl border border-white/20 px-4 py-2 text-sm text-slate-100">Explorar templates</Link>
      </div>
    </header>
  );
}

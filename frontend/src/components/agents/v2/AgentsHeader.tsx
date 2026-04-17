import { Bot, Pause, Plus, Zap } from 'lucide-react';
import { Link } from 'react-router-dom';

interface AgentsHeaderProps {
  onDuplicateTop: () => void;
  totalAgents?: number;
  activeAgents?: number;
  pausedAgents?: number;
}

export function AgentsHeader({ onDuplicateTop, totalAgents = 0, activeAgents = 0, pausedAgents = 0 }: AgentsHeaderProps) {
  return (
    <header className="rounded-3xl border border-cyan-400/20 bg-[radial-gradient(circle_at_0%_0%,rgba(0,212,255,0.22),transparent_42%),linear-gradient(160deg,#041022,#0b2549)] p-6">
      <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-cyan-300">Central de colaboradores digitais</p>
          <h1 className="mt-2 font-display text-4xl text-white">Agentes AXI</h1>
          <p className="mt-2 max-w-2xl text-sm text-slate-300">Crie, treine e coloque agentes de IA para trabalhar no seu negocio.</p>
        </div>

        {/* KPI chips — mostra somente se já carregou (totalAgents > 0) */}
        {totalAgents > 0 && (
          <div className="flex shrink-0 flex-wrap gap-2">
            <span className="inline-flex items-center gap-1.5 rounded-2xl border border-white/15 bg-white/5 px-3 py-1.5 text-xs font-medium text-slate-200">
              <Bot size={13} className="text-cyan-300" />
              {totalAgents} {totalAgents === 1 ? 'agente' : 'agentes'}
            </span>
            <span className="inline-flex items-center gap-1.5 rounded-2xl border border-emerald-400/25 bg-emerald-500/10 px-3 py-1.5 text-xs font-medium text-emerald-200">
              <Zap size={13} className="text-emerald-300" />
              {activeAgents} {activeAgents === 1 ? 'ativo' : 'ativos'}
            </span>
            {pausedAgents > 0 && (
              <span className="inline-flex items-center gap-1.5 rounded-2xl border border-amber-400/25 bg-amber-500/10 px-3 py-1.5 text-xs font-medium text-amber-200">
                <Pause size={13} className="text-amber-300" />
                {pausedAgents} pausado{pausedAgents !== 1 && 's'}
              </span>
            )}
          </div>
        )}
      </div>

      <div className="mt-5 flex flex-wrap gap-2">
        <Link
          to="/app/agents/create"
          className="inline-flex items-center gap-1.5 rounded-xl bg-cyan px-4 py-2 text-sm font-semibold text-ink"
        >
          <Plus size={14} />
          Criar novo agente
        </Link>
        <button type="button" onClick={onDuplicateTop} className="rounded-xl border border-white/20 px-4 py-2 text-sm text-slate-100">Duplicar agente</button>
        <button type="button" className="rounded-xl border border-white/20 px-4 py-2 text-sm text-slate-100">Importar configuracao</button>
        <Link to="/app/agents/templates" className="rounded-xl border border-white/20 px-4 py-2 text-sm text-slate-100">Explorar templates</Link>
      </div>
    </header>
  );
}

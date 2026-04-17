import { ExternalLink, Pause, Play, Settings2, TestTube2 } from 'lucide-react';
import { useState } from 'react';
import { Link } from 'react-router-dom';

import type { AgentSummary } from '../../../types/agentsV2';
import { AgentStatusBadge } from './AgentStatusBadge';

interface AgentCardProps {
  agent: AgentSummary;
  onToggle: (agent: AgentSummary) => void;
  onDuplicate: (agent: AgentSummary) => void;
  onArchive: (agent: AgentSummary) => void;
  onDelete: (agent: AgentSummary) => void;
}

export function AgentCard({ agent, onToggle, onDuplicate, onArchive, onDelete }: AgentCardProps) {
  const status = agent.ativo ? 'ativo' : 'pausado';
  const [menuOpen, setMenuOpen] = useState(false);

  const borderColor = agent.ativo
    ? 'border-emerald-400/25'
    : 'border-white/10';

  return (
    <article className={`rounded-3xl border ${borderColor} bg-[linear-gradient(160deg,rgba(7,14,32,0.95),rgba(10,24,48,0.9))] p-5 shadow-[0_10px_30px_rgba(0,0,0,0.35)] transition hover:shadow-[0_14px_36px_rgba(0,0,0,0.45)]`}>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <p className="truncate font-display text-2xl text-white">{agent.nome}</p>
          <p className="mt-1 truncate text-sm text-slate-300">{agent.funcao}</p>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <AgentStatusBadge status={status} />
          <div className="relative">
            <button
              type="button"
              onClick={() => setMenuOpen((value) => !value)}
              className="rounded-xl border border-white/20 px-2 py-1 text-xs text-slate-100 hover:bg-white/10"
            >
              •••
            </button>
            {menuOpen ? (
              <div className="absolute right-0 top-9 z-20 w-44 rounded-xl border border-white/15 bg-[#0b1328] p-2 shadow-xl">
                <Link
                  to={`/app/agents/${agent.id}/overview`}
                  className="flex items-center gap-2 rounded-lg px-2 py-2 text-xs text-slate-100 hover:bg-white/10"
                  onClick={() => setMenuOpen(false)}
                >
                  <ExternalLink size={12} /> Abrir
                </Link>
                <Link
                  to={`/app/agents/${agent.id}/settings`}
                  className="flex items-center gap-2 rounded-lg px-2 py-2 text-xs text-slate-100 hover:bg-white/10"
                  onClick={() => setMenuOpen(false)}
                >
                  <Settings2 size={12} /> Editar
                </Link>
                <button
                  type="button"
                  className="flex w-full items-center gap-2 rounded-lg px-2 py-2 text-left text-xs text-slate-100 hover:bg-white/10"
                  onClick={() => {
                    setMenuOpen(false);
                    onDuplicate(agent);
                  }}
                >
                  Duplicar
                </button>
                <button
                  type="button"
                  className="flex w-full items-center gap-2 rounded-lg px-2 py-2 text-left text-xs text-slate-100 hover:bg-white/10"
                  onClick={() => {
                    setMenuOpen(false);
                    onArchive(agent);
                  }}
                >
                  Arquivar
                </button>
                <button
                  type="button"
                  className="flex w-full items-center gap-2 rounded-lg px-2 py-2 text-left text-xs text-rose-200 hover:bg-rose-500/15"
                  onClick={() => {
                    setMenuOpen(false);
                    onDelete(agent);
                  }}
                >
                  Excluir
                </button>
              </div>
            ) : null}
          </div>
        </div>
      </div>

      {/* Status strip */}
      <div className="mt-4 flex items-center gap-2">
        <span
          className={`h-2 w-2 rounded-full ${agent.ativo ? 'bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.7)]' : 'bg-amber-400/70'}`}
        />
        <span className="text-xs text-slate-400">
          {agent.ativo ? 'Operando agora' : 'Pausado — aguardando ativacao'}
        </span>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        <Link
          to={`/app/agents/${agent.id}/overview`}
          className="inline-flex items-center gap-1.5 rounded-xl border border-cyan-300/40 bg-cyan-500/10 px-3 py-2 text-xs font-semibold text-cyan-100 transition hover:bg-cyan-500/20"
        >
          <ExternalLink size={11} /> Abrir
        </Link>
        <Link
          to={`/app/agents/${agent.id}/test`}
          className="inline-flex items-center gap-1.5 rounded-xl border border-white/20 px-3 py-2 text-xs font-semibold text-slate-100 transition hover:bg-white/5"
        >
          <TestTube2 size={11} /> Testar
        </Link>
        <Link
          to={`/app/agents/${agent.id}/settings`}
          className="inline-flex items-center gap-1.5 rounded-xl border border-white/20 px-3 py-2 text-xs font-semibold text-slate-100 transition hover:bg-white/5"
        >
          <Settings2 size={11} /> Editar
        </Link>
        <button
          type="button"
          onClick={() => onToggle(agent)}
          className={`inline-flex items-center gap-1.5 rounded-xl border px-3 py-2 text-xs font-semibold transition ${
            agent.ativo
              ? 'border-amber-400/30 text-amber-200 hover:bg-amber-500/10'
              : 'border-emerald-400/30 text-emerald-200 hover:bg-emerald-500/10'
          }`}
        >
          {agent.ativo ? <Pause size={11} /> : <Play size={11} />}
          {agent.ativo ? 'Pausar' : 'Ativar'}
        </button>
      </div>
    </article>
  );
}

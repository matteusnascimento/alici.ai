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

  return (
    <article className="rounded-3xl border border-white/10 bg-[linear-gradient(160deg,rgba(7,14,32,0.95),rgba(10,24,48,0.9))] p-5 shadow-[0_10px_30px_rgba(0,0,0,0.35)]">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="font-display text-2xl text-white">{agent.nome}</p>
          <p className="mt-1 text-sm text-slate-300">{agent.funcao}</p>
        </div>
        <div className="flex items-center gap-2">
          <AgentStatusBadge status={status} />
          <div className="relative">
            <button
              type="button"
              onClick={() => setMenuOpen((value) => !value)}
              className="rounded-xl border border-white/20 px-2 py-1 text-xs text-slate-100"
            >
              ...
            </button>
            {menuOpen ? (
              <div className="absolute right-0 top-9 z-20 w-44 rounded-xl border border-white/15 bg-[#0b1328] p-2 shadow-xl">
                <Link
                  to={`/app/agents/${agent.id}/overview`}
                  className="block rounded-lg px-2 py-2 text-xs text-slate-100 hover:bg-white/10"
                  onClick={() => setMenuOpen(false)}
                >
                  Abrir
                </Link>
                <Link
                  to={`/app/agents/${agent.id}/settings`}
                  className="block rounded-lg px-2 py-2 text-xs text-slate-100 hover:bg-white/10"
                  onClick={() => setMenuOpen(false)}
                >
                  Editar
                </Link>
                <button
                  type="button"
                  className="block w-full rounded-lg px-2 py-2 text-left text-xs text-slate-100 hover:bg-white/10"
                  onClick={() => {
                    setMenuOpen(false);
                    onDuplicate(agent);
                  }}
                >
                  Duplicar
                </button>
                <button
                  type="button"
                  className="block w-full rounded-lg px-2 py-2 text-left text-xs text-slate-100 hover:bg-white/10"
                  onClick={() => {
                    setMenuOpen(false);
                    onArchive(agent);
                  }}
                >
                  Arquivar
                </button>
                <button
                  type="button"
                  className="block w-full rounded-lg px-2 py-2 text-left text-xs text-rose-200 hover:bg-rose-500/15"
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
      <div className="mt-4 grid grid-cols-2 gap-2 text-xs text-slate-300">
        <p className="rounded-xl border border-white/10 bg-white/5 px-2 py-2">Conexoes: em configuracao</p>
        <p className="rounded-xl border border-white/10 bg-white/5 px-2 py-2">Atividade: recente</p>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        <Link to={`/app/agents/${agent.id}/overview`} className="rounded-xl border border-cyan-300/40 px-3 py-2 text-xs font-semibold text-cyan-100">Abrir</Link>
        <Link to={`/app/agents/${agent.id}/test`} className="rounded-xl border border-white/20 px-3 py-2 text-xs font-semibold text-slate-100">Testar</Link>
        <Link to={`/app/agents/${agent.id}/settings`} className="rounded-xl border border-white/20 px-3 py-2 text-xs font-semibold text-slate-100">Editar</Link>
        <button type="button" onClick={() => onToggle(agent)} className="rounded-xl border border-white/20 px-3 py-2 text-xs font-semibold text-slate-100">{agent.ativo ? 'Pausar' : 'Ativar'}</button>
        <button type="button" onClick={() => onDuplicate(agent)} className="rounded-xl border border-white/20 px-3 py-2 text-xs font-semibold text-slate-100">Duplicar</button>
      </div>
    </article>
  );
}

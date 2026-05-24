import type { AgentOverview } from '../../../types/agentsV2';
import { AgentActivationStatusBadge } from './AgentActivationStatusBadge';

interface AgentOverviewHeaderProps {
  data: AgentOverview;
}

function formatDate(value: string) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? '-' : date.toLocaleString('pt-BR');
}

export function AgentOverviewHeader({ data }: AgentOverviewHeaderProps) {
  return (
    <header id="overview" className="rounded-3xl border border-cyan-300/20 bg-[radial-gradient(circle_at_top_right,rgba(34,211,238,0.18),rgba(15,23,42,0.95))] p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.25em] text-cyan-400/80">Workspace do agente</p>
          <h1 className="mt-1 font-display text-3xl font-bold text-white">{data.agent.nome}</h1>
          {data.agent.funcao ? <p className="mt-1 text-sm text-slate-300">{data.agent.funcao}</p> : null}
          <p className="mt-2 text-xs text-slate-500">Criado em {formatDate(data.agent.created_at)} · Atualizado em {formatDate(data.agent.updated_at)}</p>
        </div>
        <AgentActivationStatusBadge status={data.agent.status} />
      </div>
    </header>
  );
}

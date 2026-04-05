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
    <header id="overview" className="rounded-3xl border border-cyan-300/25 bg-[radial-gradient(circle_at_top_right,rgba(34,211,238,0.2),rgba(15,23,42,0.95))] p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-cyan-300">Home operacional do agente</p>
          <h1 className="mt-1 font-display text-3xl text-white">{data.agent.nome}</h1>
          <p className="text-sm text-slate-200">{data.agent.funcao}</p>
          <p className="mt-2 text-xs text-slate-300">Criado em {formatDate(data.agent.created_at)} · Atualizado em {formatDate(data.agent.updated_at)}</p>
        </div>
        <AgentActivationStatusBadge status={data.agent.status} />
      </div>
    </header>
  );
}

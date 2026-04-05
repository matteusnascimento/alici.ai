import type { AgentOverview } from '../../../types/agentsV2';
import { AgentStatusBadge } from './AgentStatusBadge';

interface AgentOverviewHeroProps {
  data: AgentOverview;
}

export function AgentOverviewHero({ data }: AgentOverviewHeroProps) {
  return (
    <header className="rounded-3xl border border-cyan-300/30 bg-[linear-gradient(160deg,#071229,#0f2d56)] p-5">
      <p className="text-xs uppercase tracking-[0.18em] text-cyan-300">Identidade do agente</p>
      <div className="mt-2 flex items-center justify-between">
        <div>
          <h1 className="font-display text-3xl text-white">{data.agent.nome}</h1>
          <p className="text-sm text-slate-200">{data.agent.funcao}</p>
        </div>
        <AgentStatusBadge status={data.agent.status} />
      </div>
    </header>
  );
}

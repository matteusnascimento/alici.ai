import type { AgentSetupStatus } from '../../../types/agentsV2';
import { AgentProgressRing } from './AgentProgressRing';

interface AgentReadinessCardProps {
  setup: AgentSetupStatus;
}

export function AgentReadinessCard({ setup }: AgentReadinessCardProps) {
  const missing = setup.total_steps - setup.completed_steps;

  return (
    <section className="rounded-3xl border border-white/10 bg-white/5 p-4">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-cyan-300">Prontidao operacional</p>
          <h3 className="mt-1 font-display text-2xl text-white">Setup do agente</h3>
          <p className="mt-2 text-sm text-slate-200">{setup.summary_message}</p>
          <p className="mt-1 text-xs text-slate-400">Etapas restantes: {Math.max(0, missing)}</p>
        </div>
        <AgentProgressRing value={setup.progress_percent} />
      </div>
    </section>
  );
}

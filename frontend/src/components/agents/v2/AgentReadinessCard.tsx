import type { AgentSetupStatus } from '../../../types/agentsV2';
import { AgentProgressRing } from './AgentProgressRing';

interface AgentReadinessCardProps {
  setup: AgentSetupStatus;
}

export function AgentReadinessCard({ setup }: AgentReadinessCardProps) {
  const missing = setup.total_steps - setup.completed_steps;
  const isReady = setup.activation_ready;

  return (
    <section className={`rounded-3xl border p-5 ${
      isReady
        ? 'border-emerald-400/25 bg-gradient-to-br from-emerald-500/10 to-white/[0.03]'
        : 'border-white/10 bg-white/[0.04]'
    }`}>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.22em] text-cyan-400/80">Prontidão operacional</p>
          <h3 className="mt-1 font-display text-2xl text-white">Setup do agente</h3>
          <p className="mt-2 text-sm leading-6 text-slate-300">{setup.summary_message}</p>
          {missing > 0 ? (
            <p className="mt-1 text-xs text-slate-500">{missing} etapa{missing !== 1 ? 's' : ''} restante{missing !== 1 ? 's' : ''}</p>
          ) : (
            <p className="mt-1 text-xs text-emerald-400">Tudo configurado ✓</p>
          )}
        </div>
        <AgentProgressRing value={setup.progress_percent} />
      </div>
    </section>
  );
}

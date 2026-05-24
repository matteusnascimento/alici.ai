import { Link } from 'react-router-dom';

import type { AgentRecommendedNextStep } from '../../../types/agentsV2';

interface AgentRecommendedNextStepCardProps {
  step: AgentRecommendedNextStep;
}

export function AgentRecommendedNextStepCard({ step }: AgentRecommendedNextStepCardProps) {
  return (
    <section className="rounded-3xl border border-cyan-300/30 bg-[linear-gradient(155deg,rgba(14,116,144,0.2),rgba(15,23,42,0.95))] p-4">
      <p className="text-xs uppercase tracking-[0.18em] text-cyan-300">Proximo passo recomendado</p>
      <h3 className="mt-1 font-display text-2xl text-white">{step.title}</h3>
      <p className="mt-2 text-sm text-slate-200">{step.description}</p>
      <Link to={step.route} className="mt-4 inline-block rounded-xl bg-cyan px-4 py-2 text-sm font-semibold text-slate-900">
        {step.cta}
      </Link>
    </section>
  );
}

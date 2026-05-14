import { Link } from 'react-router-dom';

export function AgentEmptyState() {
  return (
    <section className="rounded-3xl border border-cyan-300/30 bg-cyan-500/10 p-8 text-center">
      <p className="font-display text-3xl text-white">Seu primeiro agente comeca aqui</p>
      <p className="mt-2 text-sm text-slate-200">Monte um colaborador digital com onboarding guiado e ativacao assistida.</p>
      <Link to="/app/agents/create" className="mt-4 inline-block rounded-xl bg-cyan px-4 py-2 text-sm font-semibold text-ink">Criar agente</Link>
    </section>
  );
}

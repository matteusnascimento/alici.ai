import { AgentCreateWizard } from './AgentCreateWizard';

export function AgentCreatePage() {
  return (
    <div className="space-y-4">
      <header className="rounded-3xl border border-white/10 bg-white/5 p-5">
        <p className="text-xs uppercase tracking-[0.2em] text-cyan-300">Onboarding guiado</p>
        <h1 className="font-display text-3xl text-white">Criar agente</h1>
      </header>
      <AgentCreateWizard />
    </div>
  );
}

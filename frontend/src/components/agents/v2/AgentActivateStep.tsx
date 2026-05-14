interface AgentActivateStepProps {
  summary: {
    name: string;
    role: string;
    channels: string[];
    actions: string[];
    tested: boolean;
  };
}

export function AgentActivateStep({ summary }: AgentActivateStepProps) {
  return (
    <div className="space-y-3">
      <div className="rounded-2xl border border-white/15 bg-white/5 p-4 text-sm text-slate-200">
        <p><strong>Nome:</strong> {summary.name}</p>
        <p><strong>Funcao:</strong> {summary.role}</p>
        <p><strong>Canais:</strong> {summary.channels.join(', ') || 'Nenhum'}</p>
        <p><strong>Acoes:</strong> {summary.actions.join(', ') || 'Nenhuma'}</p>
        <p><strong>Teste:</strong> {summary.tested ? 'Concluido' : 'Pendente'}</p>
      </div>
      <p className="rounded-xl border border-cyan-300/30 bg-cyan-500/10 px-3 py-2 text-sm text-cyan-100">Seu agente esta pronto para ser ativado como colaborador digital.</p>
    </div>
  );
}

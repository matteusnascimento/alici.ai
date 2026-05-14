interface AgentActionCardProps {
  name: string;
  enabled: boolean;
  description: string;
  requirement: string;
  onToggle: () => void;
  onConfigure: () => void;
}

export function AgentActionCard({ name, enabled, description, requirement, onToggle, onConfigure }: AgentActionCardProps) {
  return (
    <article className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <p className="font-semibold text-white">{name}</p>
      <p className="mt-1 text-xs text-slate-300">{description}</p>
      <p className="mt-1 text-xs text-slate-500">Requer: {requirement}</p>
      <div className="mt-3 flex gap-2">
        <button type="button" onClick={onToggle} className="rounded-lg border border-cyan-300/40 px-3 py-1 text-xs text-cyan-100">{enabled ? 'Desativar' : 'Ativar'}</button>
        <button type="button" onClick={onConfigure} className="rounded-lg border border-white/20 px-3 py-1 text-xs text-slate-100">Configurar</button>
      </div>
    </article>
  );
}

interface AgentActionsStepProps {
  enabled: string[];
  onToggle: (action: string) => void;
}

const actions = [
  { title: 'Capturar lead', required: 'Cadastro interno' },
  { title: 'Criar reserva', required: 'Agenda' },
  { title: 'Enviar orcamento', required: 'Template de proposta' },
  { title: 'Consultar disponibilidade', required: 'Calendario' },
  { title: 'Encaminhar para humano', required: 'Canal humano' },
  { title: 'Acionar API', required: 'Credencial API' },
  { title: 'Enviar webhook', required: 'URL webhook' },
];

export function AgentActionsStep({ enabled, onToggle }: AgentActionsStepProps) {
  return (
    <div className="grid gap-3 md:grid-cols-2">
      {actions.map((action) => {
        const active = enabled.includes(action.title);
        return (
          <div key={action.title} className={`rounded-2xl border p-4 ${active ? 'border-cyan-300/40 bg-cyan-500/15' : 'border-white/15 bg-white/5'}`}>
            <p className="font-semibold text-white">{action.title}</p>
            <p className="mt-1 text-xs text-slate-300">Requer: {action.required}</p>
            <button type="button" onClick={() => onToggle(action.title)} className="mt-3 rounded-lg border border-white/20 px-3 py-1 text-xs text-slate-100">
              {active ? 'Desativar' : 'Ativar'}
            </button>
          </div>
        );
      })}
    </div>
  );
}

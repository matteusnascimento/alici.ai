interface AgentObjectiveStepProps {
  selected: string[];
  onToggle: (objective: string) => void;
}

const objectives = [
  'Responder clientes',
  'Converter leads',
  'Fechar reservas',
  'Tirar duvidas',
  'Encaminhar para humano',
  'Coletar informacoes',
  'Ajudar no suporte',
  'Gerar oportunidades',
];

export function AgentObjectiveStep({ selected, onToggle }: AgentObjectiveStepProps) {
  return (
    <div className="grid gap-3 md:grid-cols-2">
      {objectives.map((objective) => {
        const active = selected.includes(objective);
        return (
          <button key={objective} type="button" onClick={() => onToggle(objective)} className={`rounded-2xl border p-4 text-left ${active ? 'border-cyan-300/40 bg-cyan-500/15 text-cyan-100' : 'border-white/15 bg-white/5 text-slate-100'}`}>
            <p className="font-semibold">{objective}</p>
            <p className="mt-1 text-xs opacity-80">Objetivo operacional do agente.</p>
          </button>
        );
      })}
    </div>
  );
}

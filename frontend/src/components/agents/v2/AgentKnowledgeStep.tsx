interface AgentKnowledgeStepProps {
  instructions: string;
  onInstructions: (value: string) => void;
}

export function AgentKnowledgeStep({ instructions, onInstructions }: AgentKnowledgeStepProps) {
  const cards = [
    'Documentos da empresa',
    'Perguntas frequentes',
    'Informacoes importantes',
    'Servicos e produtos',
    'Materiais de apoio',
  ];

  return (
    <div className="space-y-3">
      <div className="grid gap-2 md:grid-cols-3">
        {cards.map((card) => (
          <div key={card} className="rounded-xl border border-white/15 bg-white/5 p-3 text-sm text-slate-100">
            <p className="font-semibold">{card}</p>
            <button type="button" className="mt-2 rounded-lg border border-cyan-300/40 px-3 py-1 text-xs text-cyan-100">Adicionar</button>
          </div>
        ))}
      </div>
      <div>
        <label className="text-sm text-slate-300">Instrucoes principais do agente</label>
        <textarea value={instructions} onChange={(event) => onInstructions(event.target.value)} className="mt-2 min-h-32 w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-white" />
      </div>
    </div>
  );
}

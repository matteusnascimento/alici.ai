import { AgentSandboxChat } from './AgentSandboxChat';

interface AgentTestStepProps {
  onRunScenario: (text: string) => void;
  result: {
    response: string;
    source: string;
    confidence_note: string;
    actions: Array<Record<string, unknown>>;
  } | null;
}

const scenarios = [
  'Quero saber o preco',
  'Quero fazer uma reserva',
  'Quero falar com alguem',
  'Tenho uma duvida',
  'Esse servico esta disponivel?',
];

export function AgentTestStep({ onRunScenario, result }: AgentTestStepProps) {
  const safeActions = Array.isArray(result?.actions) ? result.actions : [];

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        {scenarios.map((scenario) => (
          <button key={scenario} type="button" onClick={() => onRunScenario(scenario)} className="rounded-xl border border-white/20 px-3 py-2 text-xs text-slate-100">
            {scenario}
          </button>
        ))}
      </div>
      <AgentSandboxChat
        messages={result ? [{ role: 'user', text: scenarios[0] }, { role: 'assistant', text: result.response }] : [{ role: 'assistant', text: 'Execute um cenario para visualizar a resposta do agente.' }]}
      />
      {result ? (
        <div className="rounded-2xl border border-cyan-300/25 bg-cyan-500/10 p-3 text-sm text-cyan-100">
          <p>Fonte usada: {result.source}</p>
          <p className="mt-1">Nota de decisao: {result.confidence_note}</p>
          <p className="mt-1">Acoes acionadas: {safeActions.length}</p>
        </div>
      ) : null}
    </div>
  );
}

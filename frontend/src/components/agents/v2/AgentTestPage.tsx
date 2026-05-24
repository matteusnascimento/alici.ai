import { useState } from 'react';
import { useParams } from 'react-router-dom';

import { useRunAgentTest } from '../../../hooks/agentsV2/useRunAgentTest';
import { AgentSandboxChat } from './AgentSandboxChat';
import { AgentTracePanel } from './AgentTracePanel';

const scenarios = [
  'Quero saber o preco',
  'Quero fazer uma reserva',
  'Quero falar com alguem',
  'Tenho uma duvida',
  'Esse servico esta disponivel?',
];

export function AgentTestPage() {
  const params = useParams();
  const agentId = Number(params.id || 0);
  const [history, setHistory] = useState<Array<{ role: 'user' | 'assistant'; text: string }>>([]);
  const { result, loading, error, run } = useRunAgentTest(agentId);

  async function runScenario(text: string) {
    const response = await run({ text, scenario: 'manual', channel_type: 'api' });
    setHistory((current) => [...current, { role: 'user', text }, { role: 'assistant', text: response.response }]);
  }

  return (
    <div className="space-y-4">
      <header className="rounded-3xl border border-white/10 bg-white/5 p-4">
        <h1 className="font-display text-2xl text-white">Teste sandbox</h1>
        <p className="mt-1 text-sm text-slate-400">
          Este ambiente valida o comportamento do agente via canal sandbox/API. Canais como WhatsApp e Instagram exigem integracao real para testes externos.
        </p>
      </header>
      <div className="flex flex-wrap gap-2">
        {scenarios.map((scenario) => (
          <button key={scenario} type="button" onClick={() => void runScenario(scenario)} className="rounded-xl border border-white/20 px-3 py-2 text-xs text-slate-100">
            {scenario}
          </button>
        ))}
      </div>
      {loading ? <p className="text-slate-300">Executando teste...</p> : null}
      {error ? <p className="text-red-300">{error}</p> : null}
      <AgentSandboxChat messages={history.length > 0 ? history : [{ role: 'assistant', text: 'Rode um cenario para iniciar o sandbox.' }]} />
      {result ? <AgentTracePanel actions={result.actions} source={result.source} confidence={result.confidence_note} /> : null}
    </div>
  );
}

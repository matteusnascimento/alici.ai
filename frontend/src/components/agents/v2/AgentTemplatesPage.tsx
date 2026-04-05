import { useEffect, useState } from 'react';

import { createAgentV2 } from '../../../services/agentsV2.service';
import type { AgentSummary } from '../../../types/agentsV2';

const templates = [
  { id: 'support', nome: 'Atendimento Premium', funcao: 'Atendimento', descricao: 'Responde clientes e encaminha para humano.' },
  { id: 'sales', nome: 'Vendas Conversao', funcao: 'Vendas', descricao: 'Qualifica leads e conduz para proposta.' },
];

export function AgentTemplatesPage() {
  const [created, setCreated] = useState<AgentSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function applyTemplate(template: (typeof templates)[number]) {
    try {
      const item = await createAgentV2({
        nome: template.nome,
        funcao: template.funcao,
        tipo: template.funcao.toLowerCase(),
        linguagem: 'pt-BR',
        prompt: template.descricao,
        ativo: false,
      });
      setCreated(item.agent);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao criar template');
    }
  }

  return (
    <div className="space-y-4">
      <header className="rounded-3xl border border-white/10 bg-white/5 p-5">
        <h1 className="font-display text-3xl text-white">Templates de agentes</h1>
      </header>
      <div className="grid gap-3 md:grid-cols-2">
        {templates.map((template) => (
          <article key={template.id} className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p className="font-semibold text-white">{template.nome}</p>
            <p className="mt-1 text-xs text-slate-300">{template.descricao}</p>
            <button type="button" onClick={() => void applyTemplate(template)} className="mt-3 rounded-xl border border-cyan-300/40 px-3 py-2 text-xs text-cyan-100">Usar template</button>
          </article>
        ))}
      </div>
      {created ? <p className="text-sm text-emerald-300">Template aplicado: {created.nome}</p> : null}
      {error ? <p className="text-sm text-red-300">{error}</p> : null}
    </div>
  );
}
